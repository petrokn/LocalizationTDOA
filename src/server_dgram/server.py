import logging
import socket

import StringIO
import msgpack
import msgpack_numpy
import numpy
import math
import time
import pickle
from cPickle import loads
from scipy import linalg
from matplotlib import pyplot
from multiprocessing import Array
from src.logic import helpers
from src.logic.parallel_process import ProcessParallel
from scipy import *
from numpy import *

class Server:
    def __init__(self,
                 server_address,
                 server_port,
                 true_positions,
                 estimated_positions,
                 sensor_positions,
                 microphone_amount,
                 trials,
                 coordinates,
                 cores_amount):
        self.__x, self.__y, self.__z = coordinates
        self.__server_address = server_address
        self.__microphone_amount = microphone_amount
        self.__server_port = server_port
        self.__true_positions = true_positions
        self.__estimated_positions = estimated_positions
        self.__trials = trials
        self.__sensor_positions = sensor_positions
        self.__distances = []
        self.__time_delays = []
        self.__padding = []
        self.__cores_amount = cores_amount
        self.__microphone_data = None
        self.__raw_microphone_data = []

    def generate_data(self):
        self.generate_source_positions()
        self.generate_distances()
        self.prepare()

    def run(self, s):

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        server_address = (self.__server_address, self.__server_port)
        logging.info('Starting up on %s port %s', self.__server_address, self.__server_port)

        sock.bind(server_address)

        microphones_data = {}

        received_data_count = 0
        while received_data_count < self.__microphone_amount:
            logging.info('Waiting to receive message...')

            data, address = sock.recvfrom(65535 - 28)
            logging.info("Recived %s", len(data))
            if len(data) == 36:
                s[received_data_count] = microphones_data[data]
                received_data_count += 1
                logging.info("Received data from %s microphones", received_data_count)
            else:
                microphone_id = data[0:36]

            if not microphone_id in microphones_data:
                microphones_data[microphone_id] = data[36:]
            else:
                microphones_data[microphone_id] += data[36:]

        logging.info("Received data from all microphones")

    def generate_source_positions(self):
        logging.info('Generating sources positions.')

        for i in range(self.__trials):
            r = numpy.random.rand(1) * 50
            t = numpy.random.rand(1) * 2 * math.pi
            # r = 0.1 * 50
            # t = 0.2 * 50
            # z = 0.3 * 20
            x = r * math.cos(t)
            y = r * math.sin(t)
            z = numpy.random.rand(1) * 20
            self.__true_positions[i, 0] = x
            self.__true_positions[i, 1] = y
            self.__true_positions[i, 2] = z

        logging.info('Generated sources positions.')

    def generate_distances(self):
        logging.info('Generating distances.')

        self.__distances = numpy.zeros((self.__trials, self.__microphone_amount))
        for i in range(self.__trials):
            for j in range(self.__microphone_amount):
                x1 = self.__true_positions[i, 0]
                y1 = self.__true_positions[i, 1]
                z1 = self.__true_positions[i, 2]
                x2 = self.__sensor_positions[j, 0]
                y2 = self.__sensor_positions[j, 1]
                z2 = self.__sensor_positions[j, 2]
                self.__distances[i, j] = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

        logging.info('Generated distances.')

    def log_results(self):
        for trial_number in range(self.__trials):
            logging.info('Trial number: %d', trial_number + 1)

            logging.info('Estimated X = %.15f, Estimated Y = %.15f, Estimated Z = %.15f',
                         float(self.__estimated_positions[trial_number][0]),
                         float(self.__estimated_positions[trial_number][1]),
                         float(self.__estimated_positions[trial_number][2]))

            logging.info('True X = %.15f, True Y = %.15f, True Z = %.15f',
                         float(self.__true_positions[trial_number][0]),
                         float(self.__true_positions[trial_number][1]),
                         float(self.__true_positions[trial_number][2]))

    def draw_plot(self):
        pyplot.plot(self.__true_positions[:, 0], self.__true_positions[:, 1], 'bd', label='True position')
        pyplot.plot(self.__estimated_positions[:, 0], self.__estimated_positions[:, 1], 'r+',
                    label='Estimated position')
        pyplot.legend(loc='upper right', numpoints=1)
        pyplot.xlabel('X coordinate of target')
        pyplot.ylabel('Y coordinate of target')
        pyplot.title('TDOA Hyperbolic Localization')
        pyplot.axis([-50, 50, -50, 50])
        pyplot.show()

    def prepare(self):
        logging.info('Preparing stage started.')

        self.__time_delays = numpy.divide(self.__distances, 340.29)
        self.__padding = numpy.multiply(self.__time_delays, 44100)

        logging.info('Preparing stage ended.')

    def handle_retrieved_data(self, s):
        for i in range(self.__trials):
            x = self.__true_positions[i, 0]
            y = self.__true_positions[i, 1]
            z = self.__true_positions[i, 2]

            temp = []
            for j in range(self.__microphone_amount):
                temp.append(s[j])

            multi_track = numpy.array([loads(raw) for raw in temp])
            logging.info('Prepared all data.')
            logging.info('Started source localization.')

            x, y, z = self.locate(self.__sensor_positions, multi_track)

            logging.info('Localized source.')

            self.__estimated_positions[i, 0] = x
            self.__estimated_positions[i, 1] = y
            self.__estimated_positions[i, 2] = z

    def locate(self, sensor_positions, multitrack):
        s = sensor_positions.shape
        len = s[0]

        time_delays = numpy.zeros((len, 1))

        starts = time.time()

        if self.__cores_amount == 1:
            for p in range(len):
                time_delays[p] = helpers.time_delay_function(multitrack[0,], multitrack[p,])
        else:
            pp = ProcessParallel()

            outs = Array('d', range(len))

            ranges = []

            for result in helpers.per_delta(0, len, len / self.__cores_amount):
                ranges.append(result)

            for start, end in ranges:
                pp.add_task(helpers.time_delay_function_optimized, (start, end, outs, multitrack))

            pp.start_all()
            pp.join_all()

            for idx, res in enumerate(outs):
                time_delays[idx] = res

        ends = time.time()

        logging.info('%.15f passed for trial.', ends - starts)

        Amat = numpy.zeros((len, 1))
        Bmat = numpy.zeros((len, 1))
        Cmat = numpy.zeros((len, 1))
        Dmat = numpy.zeros((len, 1))

        for i in range(2, len):
            x1 = sensor_positions[0, 0]
            y1 = sensor_positions[0, 1]
            z1 = sensor_positions[0, 2]
            x2 = sensor_positions[1, 0]
            y2 = sensor_positions[1, 1]
            z2 = sensor_positions[1, 2]
            xi = sensor_positions[i, 0]
            yi = sensor_positions[i, 1]
            zi = sensor_positions[i, 2]
            Amat[i] = (1 / (340.29 * time_delays[i])) * (-2 * x1 + 2 * xi) - (1 / (340.29 * time_delays[1])) * (
                    -2 * x1 + 2 * x2)
            Bmat[i] = (1 / (340.29 * time_delays[i])) * (-2 * y1 + 2 * yi) - (1 / (340.29 * time_delays[1])) * (
                    -2 * y1 + 2 * y2)
            Cmat[i] = (1 / (340.29 * time_delays[i])) * (-2 * z1 + 2 * zi) - (1 / (340.29 * time_delays[1])) * (
                    -2 * z1 + 2 * z2)
            Sum1 = (x1 ** 2) + (y1 ** 2) + (z1 ** 2) - (xi ** 2) - (yi ** 2) - (zi ** 2)
            Sum2 = (x1 ** 2) + (y1 ** 2) + (z1 ** 2) - (x2 ** 2) - (y2 ** 2) - (z2 ** 2)
            Dmat[i] = 340.29 * (time_delays[i] - time_delays[1]) + (1 / (340.29 * time_delays[i])) * Sum1 - (1 / (
                    340.29 * time_delays[1])) * Sum2

        M = numpy.zeros((len + 1, 3))
        D = numpy.zeros((len + 1, 1))
        for i in range(len):
            M[i, 0] = Amat[i]
            M[i, 1] = Bmat[i]
            M[i, 2] = Cmat[i]
            D[i] = Dmat[i]

        M = numpy.array(M[2:len, :])
        D = numpy.array(D[2:len])

        D = numpy.multiply(-1, D)

        Minv = linalg.pinv(M)

        T = numpy.dot(Minv, D)
        x = T[0]
        y = T[1]
        z = T[2]

        return x, y, z

    @property
    def padding(self):
        return self.__padding

    @property
    def distances(self):
        return self.__distances

import logging
import socket
import sys
import numpy
import math
from matplotlib import pyplot


class Server:
    def __init__(self, server_address, server_port, true_positions, estimated_positions, microphone_amount, trials):
        self.__server_address = server_address
        self.__microphone_amount = microphone_amount
        self.__server_port = server_port
        self.__true_positions = true_positions
        self.__estimated_positions = estimated_positions
        self.__trials = trials
        self.__sensor_positions = []
        self.__distances = []
        self.__time_delays = []
        self.__padding = []

    def run(self):

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        server_address = (self.__server_address, self.__server_port)
        print >> sys.stderr, 'starting up on %s port %s' % server_address
        sock.bind(server_address)

        while True:
            print >> sys.stderr, '\nwaiting to receive message'
            data, address = sock.recvfrom(4096)

            print >> sys.stderr, 'received %s bytes from %s' % (len(data), address)
            print >> sys.stderr, data

            if data:
                sent = sock.sendto(data, address)
                print >> sys.stderr, 'sent %s bytes back to %s' % (sent, address)

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

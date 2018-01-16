from scikits.audiolab import wavread
import numpy
import math
from matplotlib import pyplot
from scipy import linalg
import time
from parallel_process import ProcessParallel
from multiprocessing import Array
from helpers import time_delay_func_paralel, perdelta
import logging

class Core:
    def __init__(self, audio, mic_amount, trials, proc_number):
        if proc_number <= 0 or mic_amount <= 0 or trials <= 0:
            raise ValueError('Parameters can''t be less then zero.')

        logging.basicConfig(format='%(levelname)s, %(asctime)s:%(message)s', filename='example.log', level=logging.INFO)
        logging.info('Starting core init.')

        self.proc_numer = proc_number

        # the magic of preparing audio data; from numpy arrays to flatten list with removed duplicated elements
        self.wave = wavread(audio)[0]  # removing wav technical data; only audio data stays
        self.wave = [list(pair) for pair in self.wave]
        audio_data = numpy.array(self.wave)
        self.wave = list(audio_data.flatten())
        self.wave = self.wave[::2]
        self.wave = numpy.array(self.wave).reshape(-1, 1)

        self.scale = 0.8 / max(self.wave)
        self.wave = numpy.multiply(self.scale, self.wave)

        self.Trials = trials
        self.Radius = 50
        self.mic_amount = mic_amount
        self.Theta = numpy.linspace(0, 2 * math.pi, self.mic_amount + 1)

        self.X = [self.Radius * math.cos(x) for x in self.Theta[0: -1]]
        self.Y = [self.Radius * math.sin(x) for x in self.Theta[0: -1]]

        self.Z = [-1 if z % 2 == 0 else 1 for z in range(self.mic_amount)]
        self.Z = [5 * z + 5 for z in self.Z]

        self.sensor_positions = numpy.column_stack((self.X, self.Y, self.Z))
        self.true_positions = numpy.zeros((self.Trials, 3))
        self.estimated_positions = numpy.zeros((self.Trials, 3))

        self.distances = []
        self.time_delays = []
        self.padding = []

        logging.info('Inited core.')

    def generate_source_positions(self):
        logging.info('Generating sources positions.')

        for i in range(self.Trials):
            #r = numpy.random.rand(1) * 50
            #t = numpy.random.rand(1) * 2 * math.pi
            r = 0.1 * 50
            t = 0.2 * 50
            x = r * math.cos(t)
            y = r * math.sin(t)
            z = 0.3 * 20
            #z = numpy.random.rand(1) * 20
            self.true_positions[i, 0] = x
            self.true_positions[i, 1] = y
            self.true_positions[i, 2] = z

        logging.info('Generated sources positions.')

    def generate_distances(self):
        logging.info('Generating distances.')

        self.distances = numpy.zeros((self.Trials, self.mic_amount))
        for i in range(self.Trials):
            for j in range(self.mic_amount):
                x1 = self.true_positions[i, 0]
                y1 = self.true_positions[i, 1]
                z1 = self.true_positions[i, 2]
                x2 = self.sensor_positions[j, 0]
                y2 = self.sensor_positions[j, 1]
                z2 = self.sensor_positions[j, 2]
                self.distances[i, j] = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

        logging.info('Generated distances.')

    def prepare(self):
        logging.info('Preparing stage started.')

        self.time_delays = numpy.divide(self.distances, 340.29)
        self.padding = numpy.multiply(self.time_delays, 44100)

        logging.info('Preparing stage ended.')

    def generate_signals(self):
        for i in range(self.Trials):
            x = self.true_positions[i, 0]
            y = self.true_positions[i, 1]
            z = self.true_positions[i, 2]

            mic_data = [numpy.vstack((numpy.zeros((int(round(self.padding[i, j])), 1)), self.wave)) for j in range(self.mic_amount)]
            lenvec = numpy.array([len(mic) for mic in mic_data])
            m = max(lenvec)
            c = numpy.array([m - mic_len for mic_len in lenvec])
            mic_data = [numpy.vstack((current_mic, numpy.zeros((c[idx], 1)))) for idx, current_mic in enumerate(mic_data)]
            mic_data = [numpy.divide(current_mic, self.distances[i, idx]) for idx, current_mic in enumerate(mic_data)]
            multitrack = numpy.array(mic_data)

            print 'prepared all data.'

            x, y, z = self.locate(self.sensor_positions, multitrack)

            self.estimated_positions[i, 0] = x
            self.estimated_positions[i, 1] = y
            self.estimated_positions[i, 2] = z

    def locate(self, sensor_positions, multitrack):
        s = sensor_positions.shape
        len = s[0]

        timedelayvec = numpy.zeros((len, 1))

        starts = time.time()

        if self.proc_numer == 1:
            for p in range(len):
                timedelayvec[p] = self.time_delay_func(multitrack[0, ], multitrack[p, ])
        else:
            pp = ProcessParallel()

            outs = Array('d', range(len))

            ranges = []

            for result in perdelta(0, len, len / self.proc_numer):
                ranges.append(result)

            for start, end in ranges:
                pp.add_task(time_delay_func_paralel, (start, end, outs, multitrack))

            pp.start_all()
            pp.join_all()

            for idx, res in enumerate(outs):
                timedelayvec[idx] = res

        ends = time.time()
        print (ends - starts), 'passed for trial'

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
            Amat[i] = (1/(340.29*timedelayvec[i]))*(-2*x1+2*xi) - (1/(340.29*timedelayvec[1]))*(-2*x1+2*x2)
            Bmat[i] = (1/(340.29*timedelayvec[i]))*(-2*y1+2*yi) - (1/(340.29*timedelayvec[1]))*(-2*y1+2*y2)
            Cmat[i] = (1/(340.29*timedelayvec[i]))*(-2*z1+2*zi) - (1/(340.29*timedelayvec[1]))*(-2*z1+2*z2)
            Sum1 = (x1**2)+(y1**2)+(z1**2)-(xi**2)-(yi**2)-(zi**2)
            Sum2 = (x1**2)+(y1**2)+(z1**2)-(x2**2)-(y2**2)-(z2**2)
            Dmat[i] = 340.29*(timedelayvec[i] - timedelayvec[1]) + (1/(340.29*timedelayvec[i]))*Sum1 - (1/(340.29*timedelayvec[1]))*Sum2

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

    @staticmethod
    def time_delay_func(x, y):
        print 'locating ...'
        c = numpy.correlate(x[:, 0], y[:, 0], "full")
        C, I = c.max(0), c.argmax(0)
        out = ((float(len(c))+1.0)/2.0 - I)/44100.0
        return out

    def draw_plot(self):
        pyplot.plot(self.true_positions[:, 0], self.true_positions[:, 1], 'bd', label='True pos')
        pyplot.plot(self.estimated_positions[:, 0], self.estimated_positions[:, 1], 'r+', label='Est pos')
        pyplot.legend(loc='upper right', numpoints=1)
        pyplot.xlabel('X coordinate of target')
        pyplot.ylabel('Y coordinate of target')
        pyplot.title('TDOA Hyperbolic Localization')
        pyplot.axis([-50, 50, -50, 50])
        pyplot.show()
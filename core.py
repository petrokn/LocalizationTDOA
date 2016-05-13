from scikits.audiolab import wavread
import numpy
from numpy import multiarray
import math
from matplotlib import pyplot
from scipy import linalg
import time


# TODO: refractor this madness
# base algorithm in MATLAB can be found at https://github.com/StevenJL/tdoa_localization/
class Core:
    def __init__(self, audio):
        # the magic of preparing audio data; from numpy arrays to flatten list with removed duplicated elements
        self.wave = wavread(audio)[0]  # removing wav technical data; only audio data stays
        self.wave = [list(pair) for pair in self.wave]
        audio_data = numpy.array(self.wave)
        self.wave = list(audio_data.flatten())
        self.wave = self.wave[::2]
        self.wave = numpy.array(self.wave).reshape(-1, 1)

        self.scale = 0.8 / max(self.wave)
        self.wave = numpy.multiply(self.scale, self.wave)

        self.Trials = 10
        self.Radius = 50
        self.N = 8
        self.Theta = numpy.linspace(0, 2 * math.pi, self.N + 1)

        self.X = [self.Radius * math.cos(x) for x in self.Theta[0: -1]]
        self.Y = [self.Radius * math.sin(x) for x in self.Theta[0: -1]]

        self.Z = [-1 if z % 2 == 0 else 1 for z in range(self.N)]
        self.Z = [5 * z + 5 for z in self.Z]

        self.Sen_position = numpy.column_stack((self.X, self.Y, self.Z))
        self.True_position = numpy.zeros((self.Trials, 3))
        self.Est_position = numpy.zeros((self.Trials, 3))

        self.Distances = []
        self.TimeDelay = []
        self.Padding = []

    def generate_source_positions(self):
        for i in range(self.Trials):
            r = numpy.random.rand(1) * 50
            t = numpy.random.rand(1) * 2 * math.pi
            x = r * math.cos(t)
            y = r * math.sin(t)
            z = numpy.random.rand(1) * 20
            self.True_position[i, 0] = x
            self.True_position[i, 1] = y
            self.True_position[i, 2] = z

    def generate_distances(self):
        self.Distances = numpy.zeros((self.Trials, 8))
        for i in range(self.Trials):
            for j in range(self.N):
                x1 = self.True_position[i, 0]
                y1 = self.True_position[i, 1]
                z1 = self.True_position[i, 2]
                x2 = self.Sen_position[j, 0]
                y2 = self.Sen_position[j, 1]
                z2 = self.Sen_position[j, 2]
                self.Distances[i, j] = math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

    def prepare(self):
        self.TimeDelay = numpy.divide(self.Distances, 340.29)
        self.Padding = numpy.multiply(self.TimeDelay, 44100)

    def generate_signals(self):
        for i in range(self.Trials):
            x = self.True_position[i, 0]
            y = self.True_position[i, 1]
            z = self.True_position[i, 2]
            xstr = str(round(x))
            ystr = str(round(y))
            zstr = str(round(z))
            istr = str(i)
            name = 'Trial_', istr, '_', xstr, '_', ystr, '_', zstr, '_mdove.wav'

            mic1 = numpy.vstack((numpy.zeros((int(round(self.Padding[i, 0])), 1)), self.wave))
            mic2 = numpy.vstack((numpy.zeros((int(round(self.Padding[i, 1])), 1)), self.wave))
            mic3 = numpy.vstack((numpy.zeros((int(round(self.Padding[i, 2])), 1)), self.wave))
            mic4 = numpy.vstack((numpy.zeros((int(round(self.Padding[i, 3])), 1)), self.wave))
            mic5 = numpy.vstack((numpy.zeros((int(round(self.Padding[i, 4])), 1)), self.wave))
            mic6 = numpy.vstack((numpy.zeros((int(round(self.Padding[i, 5])), 1)), self.wave))
            mic7 = numpy.vstack((numpy.zeros((int(round(self.Padding[i, 6])), 1)), self.wave))
            mic8 = numpy.vstack((numpy.zeros((int(round(self.Padding[i, 7])), 1)), self.wave))

            l1 = len(mic1)
            l2 = len(mic2)
            l3 = len(mic3)
            l4 = len(mic4)
            l5 = len(mic5)
            l6 = len(mic6)
            l7 = len(mic7)
            l8 = len(mic8)
            lenvec = numpy.array([l1, l2, l3, l4, l5, l6, l7, l8])
            m = max(lenvec)
            c = numpy.array([m-l1, m-l2, m-l3, m-l4, m-l5, m-l6, m-l7, m-l8])
            mic1 = numpy.vstack((mic1, numpy.zeros((c[0], 1))))
            mic2 = numpy.vstack((mic2, numpy.zeros((c[1], 1))))
            mic3 = numpy.vstack((mic3, numpy.zeros((c[2], 1))))
            mic4 = numpy.vstack((mic4, numpy.zeros((c[3], 1))))
            mic5 = numpy.vstack((mic5, numpy.zeros((c[4], 1))))
            mic6 = numpy.vstack((mic6, numpy.zeros((c[5], 1))))
            mic7 = numpy.vstack((mic7, numpy.zeros((c[6], 1))))
            mic8 = numpy.vstack((mic8, numpy.zeros((c[7], 1))))

            mic1 = numpy.divide(mic1, self.Distances[i, 0])
            mic2 = numpy.divide(mic2, self.Distances[i, 1])
            mic3 = numpy.divide(mic3, self.Distances[i, 2])
            mic4 = numpy.divide(mic4, self.Distances[i, 3])
            mic5 = numpy.divide(mic5, self.Distances[i, 4])
            mic6 = numpy.divide(mic6, self.Distances[i, 5])
            mic7 = numpy.divide(mic7, self.Distances[i, 6])
            mic8 = numpy.divide(mic8, self.Distances[i, 7])

            multitrack = numpy.array([mic1, mic2, mic3, mic4, mic5, mic6, mic7, mic8])

            start = time.time()
            x, y, z = self.locate(self.Sen_position, multitrack)
            end = time.time()
            print (end - start), 'passed for ', i, ' trial'
            self.Est_position[i, 0] = x
            self.Est_position[i, 1] = y
            self.Est_position[i, 2] = z

    def locate(self, Sen_position, multitrack):
        s = Sen_position.shape
        len = s[0]

        timedelayvec = numpy.zeros((len, 1))

        for p in range(len):
            timedelayvec[p] = self.time_delay_func(multitrack[0, ], multitrack[p, ])

        Amat = numpy.zeros((len, 1))
        Bmat = numpy.zeros((len, 1))
        Cmat = numpy.zeros((len, 1))
        Dmat = numpy.zeros((len, 1))

        for i in range(2, len):
            x1 = Sen_position[0, 0]
            y1 = Sen_position[0, 1]
            z1 = Sen_position[0, 2]
            x2 = Sen_position[1, 0]
            y2 = Sen_position[1, 1]
            z2 = Sen_position[1, 2]
            xi = Sen_position[i, 0]
            yi = Sen_position[i, 1]
            zi = Sen_position[i, 2]
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
        c = numpy.correlate(list(x.flatten()), list(y.flatten()), "full")
        #c = multiarray.correlate(x, y, "full")
        C, I = c.max(0), c.argmax(0)
        out = ((float(len(c))+1.0)/2.0 - I)/44100.0
        return out

    def draw_plot(self):
        pyplot.plot(self.True_position[:, 0], self.True_position[:, 1], 'bd',  label='True pos')
        pyplot.plot(self.Est_position[:, 0], self.Est_position[:, 1], 'r+', label='Est pos')
        pyplot.legend(loc='upper right', numpoints=1)
        pyplot.xlabel('X coordinate of target')
        pyplot.ylabel('Y coordinate of target')
        pyplot.title('TDOA Hyperbolic Localization')
        pyplot.axis([-50, 50, -50, 50])
        pyplot.show()



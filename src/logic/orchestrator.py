import numpy
import math
import uuid
from scikits.audiolab import wavread
from src.client.microphone_proxy import MicrophoneProxy
from src.server_dgram.server import Server


class Orchestrator:
    def __init__(self, config):
        # File name
        self.__audio = config["audio"]

        # Audio data
        self.__wave = []

        self.__proxies = []

        # Server data
        self.__trials = int(config["trials"])
        self.__cores_amount = int(config["cores_amount"])
        self.server = None
        self.__server_address = config["server_address"]
        self.__server_port = int(config["server_port"])
        self.__microphone_amount = int(config["microphone_amount"])
        self.__radius = int(config["radius"])
        self.__true_positions = None
        self.__estimated_positions = None
        self.__sensor_positions = None

    def retrieve_file_data(self):
        # removing header and second channel data
        wave = wavread(self.__audio)[0]
        wave = [list(pair) for pair in wave]
        audio_data = numpy.array(wave)
        wave = list(audio_data.flatten())
        wave = wave[::2]
        wave = numpy.array(wave).reshape(-1, 1)

        scale = 0.8 / max(wave)
        self.__wave = numpy.multiply(scale, wave)

    def init_server(self):
        theta = numpy.linspace(0, 2 * math.pi, self.__microphone_amount + 1)
        X = [self.__radius * math.cos(x) for x in theta[0: -1]]
        Y = [self.__radius * math.sin(x) for x in theta[0: -1]]
        Z = [-1 if z % 2 == 0 else 1 for z in range(self.__microphone_amount)]
        Z = [5 * z + 5 for z in Z]

        self.__sensor_positions = numpy.column_stack((X, Y, Z))
        self.__true_positions = numpy.zeros((self.__trials, 3))
        self.__estimated_positions = numpy.zeros((self.__trials, 3))

        self.server = Server(self.__server_address,
                             self.__server_port,
                             self.__true_positions,
                             self.__estimated_positions,
                             self.__sensor_positions,
                             self.__microphone_amount,
                             self.__trials,
                             (X, Y, Z),
                             self.__cores_amount)

    def send_data_to_server(self):
        for i in range(self.__trials):
            microphone_data = [numpy.vstack((numpy.zeros((int(round(self.server.padding[i, j])), 1)), self.__wave)) for
                               j in
                               range(self.__microphone_amount)]
            lenvec = numpy.array([len(mic) for mic in microphone_data])
            m = max(lenvec)
            c = numpy.array([m - mic_len for mic_len in lenvec])
            microphone_data = [numpy.vstack((current_mic, numpy.zeros((c[idx], 1)))) for idx, current_mic in
                               enumerate(microphone_data)]
            microphone_data = [numpy.divide(current_mic, self.server.distances[i, idx]) for idx, current_mic in
                               enumerate(microphone_data)]

            for j in range(self.__microphone_amount):
                self.__send_data_via_proxy(microphone_data[j])

    def __send_data_via_proxy(self, message):
        proxy = MicrophoneProxy(self.__server_address, self.__server_port, uuid.uuid4())
        self.__proxies.append(proxy)
        proxy.run(message)

    def locate(self,s):
        self.server.handle_retrieved_data(s)
        self.server.log_results()
        self.server.draw_plot()

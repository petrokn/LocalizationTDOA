import numpy
from scikits.audiolab import wavread

# noinspection PyUnresolvedReferences
from src.client.microphone_proxy import MicrophoneProxy


class Orchestrator:
    def __init__(self, audio, microphone_amount, server_address, server_port):
        self.__audio = audio
        self.__server_address = server_address
        self.__server_port = server_port
        self.__microphone_amount = microphone_amount
        self.__microphone_proxies = []
        self.__microphone_data = []
        self.__wave = []
        self.__proxies = []

    def handle_file_data(self):
        # removing header and second channel data
        wave = wavread(self.__audio)[0]
        wave = [list(pair) for pair in wave]
        audio_data = numpy.array(wave)
        wave = list(audio_data.flatten())
        wave = wave[::2]
        wave = numpy.array(wave).reshape(-1, 1)

        scale = 0.8 / max(wave)
        self.__wave = numpy.multiply(scale, wave)

    def send_data_to_server(self):
        for i in range(self.__microphone_amount):
            self.__send_data_via_proxy(self.__microphone_data[i])

    def __send_data_via_proxy(self, message):
        proxy = MicrophoneProxy(self.__server_address, self.__server_port)
        self.__proxies.append(proxy)
        proxy.send(message)

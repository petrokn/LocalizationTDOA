import numpy
from scikits.audiolab import wavread

# noinspection PyUnresolvedReferences
from src.client.microphone_proxy import MicrophoneProxy


class Orchestrator:
    def __init__(self, audio, microphone_amount, server_address, server_port):
        self.audio = audio
        self.server_address = server_address
        self.server_port = server_port
        self.microphone_amount = microphone_amount
        self.microphone_proxies = []
        self.microphone_data = []
        self.wave = []

    def handle_file_data(self):

        # removing header and second channel data
        wave = wavread(self.audio)[0]
        wave = [list(pair) for pair in wave]
        audio_data = numpy.array(wave)
        wave = list(audio_data.flatten())
        wave = wave[::2]
        wave = numpy.array(wave).reshape(-1, 1)

        scale = 0.8 / max(wave)
        self.wave = numpy.multiply(scale, wave)

    def spawn_microphones(self):
        for i in range(self.microphone_amount):
            self.send_data_via_udp(self.microphone_data[i])

    def send_data_via_udp(self, message):
        proxy = MicrophoneProxy(self.server_address, self.server_port)
        proxy.send(message)

import socket
import numpy
import sys
from scikits.audiolab import wavread


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

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        server_address = (self.server_address, self.server_port)
        # server_address = ('localhost', 10000)
        # message = 'This is the message.  It will be repeated.'

        try:
            # Send data
            print >> sys.stderr, 'sending "%s"' % message
            sent = sock.sendto(message, server_address)

            # Receive response
            print >> sys.stderr, 'waiting to receive'
            data, server = sock.recvfrom(4096)
            print >> sys.stderr, 'received "%s"' % data

        finally:
            print >> sys.stderr, 'closing socket'
            sock.close()

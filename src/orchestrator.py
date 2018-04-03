import numpy
from scikits.audiolab import wavread


class Orchestrator:
    def __init__(self, audio):

        # removing header and second channel data
        self.wave = wavread(audio)[0]
        self.wave = [list(pair) for pair in self.wave]
        audio_data = numpy.array(self.wave)
        self.wave = list(audio_data.flatten())
        self.wave = self.wave[::2]
        self.wave = numpy.array(self.wave).reshape(-1, 1)

        self.scale = 0.8 / max(self.wave)
        self.wave = numpy.multiply(self.scale, self.wave)

    def
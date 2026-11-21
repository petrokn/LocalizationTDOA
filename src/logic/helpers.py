import logging

import numpy
from scipy.io import wavfile

LOG_FORMAT = '%(levelname)s, PID: %(process)d, %(asctime)s:\t%(message)s'


def setup_logging(log_file=None):
    logging.basicConfig(format=LOG_FORMAT, filename=log_file, level=logging.INFO)


def load_wave(path):
    """Read a WAV file and return its first channel as a (N, 1) float column peak-scaled to 0.8."""
    _, data = wavfile.read(path)

    # scale integer PCM to [-1.0, 1.0) floats
    if numpy.issubdtype(data.dtype, numpy.integer):
        data = data / float(-numpy.iinfo(data.dtype).min)

    data = numpy.asarray(data, dtype=numpy.float64)

    # keep only the first channel of multichannel files
    if data.ndim > 1:
        data = data[:, 0]

    wave = data.reshape(-1, 1)
    return wave * (0.8 / numpy.max(wave))


def time_delay_function_optimized(start, end, outs, multi):
    for idx in range(start, end):
        logging.info('Locating...')

        c = numpy.correlate(multi[0,][:, 0], multi[idx,][:, 0], "full")
        I = c.argmax(0)
        outs[idx] = ((float(len(c)) + 1.0) / 2.0 - I) / 44100.0


def per_delta(start, end, delta):
    delta = max(1, delta)
    curr = start
    while curr < end and curr + delta < end:
        yield (curr, curr + delta)
        curr += delta
    yield (curr, end)


def time_delay_function(x, y):
    c = numpy.correlate(x[:, 0], y[:, 0], "full")
    I = c.argmax(0)
    out = ((float(len(c)) + 1.0) / 2.0 - I) / 44100.0
    return out

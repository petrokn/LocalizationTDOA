import numpy
import logging


def time_delay_funciton_optimized(start, end, outs, multi):
    for idx in range(start, end):
        logging.info('Locating...')

        c = numpy.correlate(multi[0,][:, 0], multi[idx,][:, 0], "full")
        C, I = c.max(0), c.argmax(0)
        outs[idx] = ((float(len(c)) + 1.0) / 2.0 - I) / 44100.0


def per_delta(start, end, delta):
    curr = start
    while curr < end and curr + delta < end:
        yield (curr, curr + delta)
        curr += delta
    yield (curr, end)


def time_delay_function(x, y):
    c = numpy.correlate(x[:, 0], y[:, 0], "full")
    C, I = c.max(0), c.argmax(0)
    out = ((float(len(c)) + 1.0) / 2.0 - I) / 44100.0
    return out
import numpy
from os import getpid


def time_delay_func_paralel(start, end, outs, multi):
    for idx in range(start, end):
        print 'locating ...', getpid()
        c = numpy.correlate(multi[0, ][:, 0], multi[idx, ][:, 0], "full")
        C, I = c.max(0), c.argmax(0)
        outs[idx] = ((float(len(c))+1.0)/2.0 - I)/44100.0


def perdelta(start, end, delta):
    curr = start
    while curr < end and curr + delta < end:
        yield (curr, curr + delta)
        curr += delta
    yield (curr, end)
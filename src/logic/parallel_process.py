import logging
from multiprocessing import Process

from src.logic import helpers


def _root_log_file():
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            return handler.baseFilename
    return None


def _run_with_logging(log_file, job, args):
    # spawned children (the default on macOS, Windows and, since 3.14, Linux)
    # don't inherit the parent's logging configuration
    helpers.setup_logging(log_file)
    job(*args)


class ProcessParallel(object):
    """
    To Process the jobs in separate interpreters
    """
    def __init__(self):
        self.processes = []

    def add_task(self, job, arg):
        self.processes.append(Process(target=_run_with_logging, args=(_root_log_file(), job, arg)))

    def start_all(self):
        """
        Starts the functions process all together.
        """
        for process in self.processes:
            process.start()

    def join_all(self):
        """
        Waits until all the processes executed.
        """
        for process in self.processes:
            process.join()

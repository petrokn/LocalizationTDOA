from multiprocessing import Process


class ProcessParallel(object):
    """
    To Process the jobs in separate interpreters
    """
    def __init__(self):
        self.processes = []

    def add_task(self, job, arg):
        self.processes.append(Process(target=job, args=arg))

    def start_all(self):
        """
        Starts the functions process all together.
        """
        [process.start() for process in self.processes]

    def join_all(self):
        """
        Waits until all the processes executed.
        """
        [process.join() for process in self.processes]

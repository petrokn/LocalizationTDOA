from multiprocessing import Process


class ProcessParallel(object):
    """
    To Process the  functions parallely

    """
    def __init__(self):
        self.processes = []

    def add_task(self, job, arg):
        proc = Process(target=job, args=arg)
        self.processes.append(proc)

    def start_all(self):
        """
        Starts the functions process all together.
        """
        [proc.start() for proc in self.processes]

    def join_all(self):
        """
        Waits untill all the functions executed.
        """
        [proc.join() for proc in self.processes]

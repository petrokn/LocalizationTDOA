import json
import logging
from multiprocessing import freeze_support
import multiprocessing
from src.logic.orchestrator import Orchestrator
from src.logic.parallel_process import ProcessParallel


def main():
    freeze_support()

    logging.basicConfig(format='%(levelname)s, PID: %(process)d, %(asctime)s:\t%(message)s', level=logging.INFO)

    config = json.load(open('server_config.json'))

    orchestrator = Orchestrator(config)
    orchestrator.retrieve_file_data()
    orchestrator.init_server()
    orchestrator.server.generate_data()

    manager = multiprocessing.Manager()
    s = manager.dict()

    pp = ProcessParallel()
    pp.add_task(orchestrator.server.run, (s,))
    pp.add_task(orchestrator.send_data_to_server, ())

    pp.start_all()
    pp.join_all()

    orchestrator.locate(s)


if __name__ == '__main__':
    main()

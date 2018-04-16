import json
import logging
from multiprocessing import freeze_support
import multiprocessing
import time
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
    received_data = manager.dict()

    pp = ProcessParallel()

    pp.add_task(orchestrator.server.run, (received_data,))
    pp.add_task(orchestrator.send_data_to_server, ())

    pp.start_all()
    starts = time.time()

    pp.join_all()

    orchestrator.locate(received_data)

    ends = time.time()

    logging.info('%.15f passed for SEND/RECEIVE/CALCULATE.', ends - starts)

    orchestrator.get_results()


if __name__ == '__main__':
    main()

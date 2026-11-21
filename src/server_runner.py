import json
import logging
import multiprocessing
import time
from multiprocessing import freeze_support
from pathlib import Path

from src.logic import helpers
from src.logic.orchestrator import Orchestrator
from src.logic.parallel_process import ProcessParallel

CONFIG_PATH = Path(__file__).with_name('server_config.json')


def main():
    freeze_support()

    helpers.setup_logging()

    with CONFIG_PATH.open() as config_file:
        config = json.load(config_file)

    # the audio path in the config is relative to the config file itself
    config["audio"] = str(CONFIG_PATH.parent / config["audio"])

    orchestrator = Orchestrator(config)
    orchestrator.retrieve_file_data()
    orchestrator.init_server()
    orchestrator.server.generate_data()

    manager = multiprocessing.Manager()
    received_data = manager.dict()
    server_ready = manager.Event()

    pp = ProcessParallel()

    pp.add_task(orchestrator.server.run, (received_data, server_ready))
    pp.add_task(orchestrator.send_data_to_server, (server_ready,))

    pp.start_all()
    starts = time.time()

    pp.join_all()

    orchestrator.locate(received_data)

    ends = time.time()

    logging.info('%.15f passed for SEND/RECEIVE/CALCULATE.', ends - starts)

    orchestrator.get_results()


if __name__ == '__main__':
    main()

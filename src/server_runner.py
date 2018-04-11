import json
import logging
from multiprocessing import freeze_support, cpu_count
from src.logic.orchestrator import Orchestrator


def main():
    freeze_support()

    logging.basicConfig(format='%(levelname)s, PID: %(process)d, %(asctime)s:\t%(message)s', level=logging.INFO)

    config = json.load(open('server_config.json'))

    orchestrator = Orchestrator(config)
    orchestrator.retrieve_file_data()
    orchestrator.init_server()
    orchestrator.server.generate_source_positions()
    orchestrator.server.generate_distances()
    orchestrator.server.prepare()
    orchestrator.server.generate_signals()
    orchestrator.display_results()


if __name__ == '__main__':
    main()

import json
import logging
from multiprocessing import freeze_support, cpu_count
from src.logic.orchestrator import Orchestrator


def main():
    freeze_support()

    logging.basicConfig(format='%(levelname)s, PID: %(process)d, %(asctime)s:\t%(message)s', level=logging.INFO)

    data = json.load(open('server_config.json'))

    orchestrator = Orchestrator(audio=data["audio"])


if __name__ == '__main__':
    main()

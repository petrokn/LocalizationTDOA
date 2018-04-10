import json
from pprint import pprint
from src.logic.orchestrator import Orchestrator


def main():
    data = json.load(open('server_config.json'))

    orchestrator = Orchestrator(audio=data["audio"])


if __name__ == '__main__':
    main()

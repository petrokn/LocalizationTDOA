from core import Core
from multiprocessing import freeze_support, cpu_count
import argparse
import logging

if __name__ == '__main__':
    freeze_support()

    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--mic_amount", type=int,
                        help="microphone amount")
    parser.add_argument("-p", "--proc_number", type=int,
                        help="process number")
    parser.add_argument("-t", "--trials", type=int,
                        help="trials number")
    parser.add_argument("-f", "--file", type=str,
                        help="file name")
    parser.add_argument("-l", "--log_file", type=str,
                        help="log file")

    args = parser.parse_args()

    if args.log_file:
        logging.basicConfig(format='%(levelname)s, PID: %(process)d, %(asctime)s:\t%(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(levelname)s, PID: %(process)d, %(asctime)s:\t%(message)s', filename=args.log_file,
                            level=logging.INFO)

    if args.proc_number:
        if args.proc_number <= 0:
            raise ValueError('proc_number can''t bel less then zero.')
        cores_to_use = args.proc_number
    else:
        cores_to_use = cpu_count()

    core = Core(args.file,
                mic_amount=args.mic_amount,
                trials=args.trials,
                proc_number=cores_to_use)

    core.generate_source_positions()
    core.generate_distances()
    core.prepare()
    core.generate_signals()

    for trial_number in range(core.trials):
        logging.info('Trial number: %d', trial_number + 1)

        logging.info('Estimated X = %.15f, Estimated Y = %.15f, Estimated Z = %.15f', float(core.estimated_positions[trial_number][0]),
                    float(core.estimated_positions[trial_number][1]),
                    float(core.estimated_positions[trial_number][2]))

        logging.info('True X = %.15f, True Y = %.15f, True Z = %.15f', float(core.true_positions[trial_number][0]),
                    float(core.true_positions[trial_number][1]),
                    float(core.true_positions[trial_number][2]))

    core.draw_plot()

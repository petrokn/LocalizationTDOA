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

    logging.info('est_x=%.15f, est_y=%.15f, est_z=%.15f', float(core.estimated_positions[0][0]),
                 float(core.estimated_positions[0][1]),
                 float(core.estimated_positions[0][2]))

    logging.info('true_x=%.15f, true_y=%.15f, true_z=%.15f', float(core.true_positions[0][0]),
                 float(core.true_positions[0][1]),
                 float(core.true_positions[0][2]))

    core.draw_plot()

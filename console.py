from core import Core
from multiprocessing import freeze_support
import argparse

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

    args = parser.parse_args()

    core = Core(args.file, mic_amount=args.mic_amount, trials=args.trials, proc_number=args.proc_number)
    core.generate_source_positions()
    core.generate_distances()
    core.prepare()
    core.generate_signals()

    print 'est_x=', float(core.estimated_positions[0][0]), 'est_y=', float(core.estimated_positions[0][1]), \
        'est_z=', float(core.estimated_positions[0][2]), 'true_x=', float(core.true_positions[0][0]),\
        'true_y=', float(core.true_positions[0][1]), 'true_z=', float(core.true_positions[0][2])

    core.draw_plot()

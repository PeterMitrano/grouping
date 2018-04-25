#!/usr/bin/env python3

import argparse
import datetime
from response_processing.util import *


def main():
    parser = argparse.ArgumentParser("prints a tree of times for each experiment & trial")
    parser.add_argument("dumpfile", help="The output of \"flask dumpdb --outfile=dump.json\"")
    parser.add_argument("--verbose", "-v", help="print each indvidual trial time", action="store_true")

    args = parser.parse_args()

    experiments = load_by_experiment(args.dumpfile)

    # print the information
    print("{:>8s}, {:>14s}, {:>7s}, {:>7s}, {:>6s}, {:>34s}, {:>26s}".format("# trials", "total time", "mean", "median", "stddev", "experiment id", "stamp"))
    for experiment_id, trials_by_experiment in experiments.items():
        total_time_s = 0
        trial_times = []
        for trial in trials_by_experiment:
            trial_time_s = float(trial["data"]["duration_seconds"])
            total_time_s += trial_time_s
            trial_times.append(trial_time_s)
        mean_time_s = np.mean(trial_times)
        median_time_s = np.median(trial_times)
        deviation = np.std(trial_times)
        total_time_formatted = str(datetime.timedelta(seconds=total_time_s))
        num_trials = len(trial_times)
        stamp = trials_by_experiment[0]["stamp"]
        print("{:8d}, {:14s}, {:7.3f}, {:7.3f}, {:.3f}, {:34s}, {:26s}".format(num_trials, total_time_formatted, mean_time_s,
                                                                         median_time_s, deviation, experiment_id,
                                                                         stamp))
        if args.verbose:
            print("total experiments:", len(trials_by_experiment))
            for trial in trials_by_experiment:
                trial_time_s = float(trial["data"]["duration_seconds"])
                trial_time_formatted = str(datetime.timedelta(seconds=trial_time_s))
                db_id = trial["id"]
                print("  {:s} ({:d})".format(trial_time_formatted, db_id))


if __name__ == "__main__":
    main()

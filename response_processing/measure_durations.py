#!/usr/bin/env python3

import argparse
import datetime
import json


def main():
    parser = argparse.ArgumentParser("prints a tree of times for each experiment & trial")
    parser.add_argument("dumpfile", help="The output of \"flask dumpdb --outfile=dump.json\"")
    parser.add_argument("--verbose", "-v", help="print each indvidual trial time", action="store_true")

    args = parser.parse_args()

    trials = json.load(open(args.dumpfile, "r"))

    # group by experiment into a dict
    experiments = {}
    for trial in trials:
        if trial["experiment_id"] not in experiments:
            experiments[trial["experiment_id"]] = []
        experiments[trial["experiment_id"]].append(trial)

    # print the information
    for experiment_id, trials_by_experiment in experiments.items():
        total_time_s = 0
        for trial in trials_by_experiment:
            trial_time_s = float(trial["data"]["duration_seconds"])
            total_time_s += trial_time_s
        total_time_formatted = str(datetime.timedelta(seconds=total_time_s))
        stamp = trial["stamp"]
        print("{:s} ({:s}, {:s})".format(total_time_formatted, experiment_id, stamp))
        if args.verbose:
            for trial in trials_by_experiment:
                trial_time_s = float(trial["data"]["duration_seconds"])
                trial_time_formatted = str(datetime.timedelta(seconds=trial_time_s))
                db_id = trial["id"]
                print("  {:s} ({:d})".format(trial_time_formatted, db_id))



if __name__ == "__main__":
    main()

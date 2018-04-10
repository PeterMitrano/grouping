#!/usr/bin/env python3

import argparse

import matplotlib.pyplot as plt

from response_processing.util import *


def main():
    parser = argparse.ArgumentParser("plots the final responses from a json dump of responses.")
    parser.add_argument("dumpfile", help="The output of \"flask dumpdb --outfile=dump.json\"")

    args = parser.parse_args()

    responses_by_url = load_by_url(args.dumpfile)

    for url, trials in responses_by_url.items():
        for i, trial in enumerate(trials):
            final_response = [float(t['timestamp']) for t in trial['data']['final_response']]

            if len(final_response) == 1:
                print(trial['experiment_id'])

            plt.figure()
            plt.title(url)
            plt.xlabel('time (seconds')
            plt.ylabel('response')
            ys = np.ones(len(final_response)) * i
            plt.scatter(final_response, ys)

    plt.show()


if __name__ == '__main__':
    main()

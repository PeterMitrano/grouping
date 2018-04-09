#!/usr/bin/env python3

import json
import numpy as np
import sqlite3
import argparse
import matplotlib.pyplot as plt

from interface.interface.interface import SAMPLES_URL_PREFIX


def main():
    parser = argparse.ArgumentParser("plots the final responses from a sqlite3 database of responses.")
    parser.add_argument('database', help='sqlite3 database file of survey responses downloaded from the server')

    args = parser.parse_args()

    # open the database
    db = sqlite3.connect(args.database, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row

    responses_cur = db.execute('SELECT url, data FROM responses')
    entries = responses_cur.fetchall()

    sample_responses_dict = {}
    for entry in entries:
        url = entry[0]
        response = json.loads(entry[1])
        name = url.strip(SAMPLES_URL_PREFIX)
        group_times_s = [r['timestamp'] for r in response['final_response']]
        if name not in sample_responses_dict:
            sample_responses_dict[name] = []
        sample_responses_dict[name].append(group_times_s)

    if len(sample_responses_dict) > 10:
        print("There are more than 10 responses. You probably don't want to run this script. Aborting.")
        return

    for sample, responses in sample_responses_dict.items():
        if len(responses) > 0:
            plt.figure()
            plt.title(sample)
            plt.xlabel('time (seconds')
            plt.ylabel('response')
            for i, response in enumerate(responses):
                ys = np.ones(len(response)) * i
                plt.scatter(response, ys)

    plt.show()


if __name__ == '__main__':
    main()

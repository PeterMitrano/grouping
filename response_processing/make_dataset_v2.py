#!/usr/bin/env python3

import os
import json
import sqlite3
import numpy as np
import argparse

from madmom.custom_processors import LabelOutputProcessor
from madmom.features.tf_beats import TfRhythmicGroupingPreProcessor
from madmom.processors import _process, IOProcessor

from interface.interface.interface import SAMPLES_URL_PREFIX


def main():
    parser = argparse.ArgumentParser("merges a csv of survey responses, and a sqlite3 database of responses.")
    parser.add_argument('database', help='sqlite3 database file of survey responses downloaded from the server')
    parser.add_argument('samples_folder', help='a folder with all the samples from the database')
    parser.add_argument('outfile', help='output file (EX: train_dataset.npz)')
    parser.add_argument('--fps', action='store', type=float, default=100, help='frames per second [default=100]')

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

    data = []
    labels = []
    sample_names = []
    for sample_name, responses in sample_responses_dict.items():
        sample_path = os.path.join(args.samples_folder, sample_name)
        preprocessor = TfRhythmicGroupingPreProcessor()
        if not os.path.exists(sample_path):
            raise ValueError("Sample path {} does not exist.".format(sample_path))

        infile = open(sample_path, 'rb')

        label_processor = LabelOutputProcessor(responses, args.fps)

        # create an IOProcessor
        processor = IOProcessor(preprocessor, label_processor)
        sample_data, sample_labels = _process((processor, infile, None, vars(args)))
        data.append(sample_data)
        labels.append(sample_labels)
        sample_names.append(sample_name)

    np.savez(args.outfile, x=data, labels=labels, sample_names=sample_names)


if __name__ == '__main__':
    main()

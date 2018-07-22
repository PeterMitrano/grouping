#!/usr/bin/env python
import json
import os
import numpy as np
import argparse
from urllib.parse import urlparse

from madmom.custom_processors import LabelOutputProcessor
from madmom.features.tf_beats import TfRhythmicGroupingPreProcessor
from madmom.processors import _process, IOProcessor

from response_processing import util


def main():
    parser = argparse.ArgumentParser("merges a csv of survey responses, and a sqlite3 database of responses.")
    parser.add_argument("dumpfile", help="The output of \"flask dumpdb --outfile=dump.json\"")
    parser.add_argument("samples", help="folder with the actual mp3 samples")
    parser.add_argument('outfile', help='output file (EX: train_dataset.npz)')
    parser.add_argument('--fps', action='store', type=float, default=100, help='frames per second [default=100]')

    args = parser.parse_args()

    trials = json.load(open(args.dumpfile, "r"))['dataset']

    data = []
    labels = []
    sample_names = []
    for trial in trials:
        final_response = [r['timestamp'] for r in trial['data']['final_response']]
        sample_url = trial['url']

        o = urlparse(sample_url)
        sample_name = os.path.split(o.path)[-1]
        preprocessor = TfRhythmicGroupingPreProcessor()

        infile = os.path.join(args.samples, sample_name)

        print(infile)

        label_processor = LabelOutputProcessor(final_response, args.fps)

        # create an IOProcessor
        processor = IOProcessor(preprocessor, label_processor)
        sample_data, sample_labels = _process((processor, infile, None, vars(args)))
        data.append(sample_data)

        if sample_data.shape[1] != data[0].shape[1]:
            print("Shapes do not match, ", data[0].shape, sample_data.shape, "Skipping.")
            data.pop()
            continue

        labels.append(sample_labels)
        sample_names.append(sample_name)

    np.savez(args.outfile, x=data, labels=labels, sample_names=sample_names)


if __name__ == '__main__':
    main()

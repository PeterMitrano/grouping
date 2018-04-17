#!/usr/bin/env python3

import os
import numpy as np
import argparse
from urllib.parse import urlparse

from madmom.custom_processors import LabelOutputProcessor
from madmom.features.tf_beats import TfRhythmicGroupingPreProcessor
from madmom.processors import _process, IOProcessor

from interface.interface.interface import SAMPLES_URL_PREFIX
from response_processing import util


def main():
    parser = argparse.ArgumentParser("merges a csv of survey responses, and a sqlite3 database of responses.")
    parser.add_argument("dumpfile", help="The output of \"flask dumpdb --outfile=dump.json\"")
    parser.add_argument('samples_folder', help='a folder with all the samples from the database')
    parser.add_argument('outfile', help='output file (EX: train_dataset.npz)')
    parser.add_argument('--fps', action='store', type=float, default=100, help='frames per second [default=100]')

    args = parser.parse_args()

    responses_by_url = util.load_by_url(args.dumpfile)
    final_responses_by_url = util.get_final_responses(responses_by_url)

    data = []
    labels = []
    sample_names = []
    for sample_url, final_responses in final_responses_by_url.items():
        o = urlparse(sample_url)
        sample_name = os.path.split(o.path)[-1]
        sample_path = os.path.join(args.samples_folder, sample_name)
        preprocessor = TfRhythmicGroupingPreProcessor()
        if not os.path.exists(sample_path):
            raise ValueError("Sample path {} does not exist.".format(sample_path))

        infile = open(sample_path, 'rb')

        label_processor = LabelOutputProcessor(final_responses, args.fps)

        # create an IOProcessor
        processor = IOProcessor(preprocessor, label_processor)
        sample_data, sample_labels = _process((processor, infile, None, vars(args)))
        data.append(sample_data)
        labels.append(sample_labels)
        sample_names.append(sample_name)

    np.savez(args.outfile, x=data, labels=labels, sample_names=sample_names)


if __name__ == '__main__':
    main()

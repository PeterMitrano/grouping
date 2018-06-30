#!/usr/bin/env python3

import argparse
import json

from response_processing import util


def main():
    parser = argparse.ArgumentParser(
        "converts json dump of responses to just the final responses collected for each sample")
    parser.add_argument("dumpfile", help="The output of \"flask dumpdb --outfile=dump.json\"")
    parser.add_argument("outfile", help="The new output file to create (JSON)")

    args = parser.parse_args()

    responses_by_url = util.load_by_url(args.dumpfile)
    final_responses_by_url = util.get_final_responses_list(responses_by_url)

    with open(args.outfile, 'w') as outfile:
        json.dump(final_responses_by_url, outfile)


if __name__ == '__main__':
    main()

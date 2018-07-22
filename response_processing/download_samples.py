#!/usr/bin/env python3

import os
import argparse
import shutil
from urllib.parse import urlparse
import urllib3

from response_processing import util


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    parser = argparse.ArgumentParser("download all samples references in dumpfile")
    parser.add_argument("dumpfile", help="The output of \"flask dumpdb --outfile=dump.json\"")
    parser.add_argument('outfolder', help='output folder to put samples in')

    args = parser.parse_args()

    responses_by_url = util.load_by_url(args.dumpfile)
    final_responses_by_url = util.get_final_responses(responses_by_url)

    for sample_url, final_responses in final_responses_by_url.items():
        o = urlparse(sample_url)
        sample_name = os.path.split(o.path)[-1]
        outfile = os.path.join(args.outfolder, sample_name)

        if os.path.isfile(outfile):
            print("skipping", outfile)
            continue

        print(sample_url, '->', outfile)

        http = urllib3.PoolManager()

        with http.request('GET', sample_url, preload_content=False) as r, open(outfile, 'wb') as out_file:
            shutil.copyfileobj(r, out_file)


if __name__ == '__main__':
    main()

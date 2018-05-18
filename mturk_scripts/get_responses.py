#!/usr/bin/env python3

import argparse
import sys
from pprint import pprint

import boto3
import botocore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('hit_id',  help='hit ID')
    parser.add_argument('--profile_name', '-p', default='mturk_barton', help='profile name in ~/.aws/credentials file')
    parser.add_argument('--live', '-l', help="set true to post real hits instead of sandbox hits", action="store_true")
    parser.add_argument('--status', '-s', help="status", default='Submitted')
    args = parser.parse_args()

    create_hits_in_live = False

    environments = {
        "live": {
            "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
            "preview": "https://www.mturk.com/mturk/preview",
            "manage": "https://requester.mturk.com/mturk/manageHITs",
            "reward": "0.00"
        },
        "sandbox": {
            "endpoint": "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
            "preview": "https://workersandbox.mturk.com/mturk/preview",
            "manage": "https://requestersandbox.mturk.com/mturk/manageHITs",
            "reward": "0.50"
        },
    }
    mturk_environment = environments["live"] if create_hits_in_live else environments["sandbox"]

    session = boto3.Session(profile_name=args.profile_name)
    client = session.client(service_name='mturk', region_name='us-east-1', endpoint_url=mturk_environment['endpoint'])

    try:
        results = client.list_assignments_for_hit(HITId=args.hit_id, AssignmentStatuses=[args.status])
        pprint(results)
    except botocore.exceptions.ClientError as e:
        print(e)

    return 0


if __name__ == "__main__":
    sys.exit(main())

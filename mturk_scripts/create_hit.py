#!/usr/bin/env python3

import argparse
from time import sleep
import sys
from pprint import pprint

import boto3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('question_xml_filename',  help='XML file containing the details of the ExternalQuestion')
    parser.add_argument('--profile_name', '-p', default='mturk_barton', help='profile name in ~/.aws/credentials file')
    parser.add_argument('--live', '-l', help="set true to post real hits instead of sandbox hits", action="store_true")
    parser.add_argument('--num-hits', '-n', help="number of hits assignments to create", default=1, type=int)
    args = parser.parse_args()

    create_hits_in_live = args.live

    environments = {
        "live": {
            "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
            "preview": "https://www.mturk.com/mturk/preview",
            "manage": "https://requester.mturk.com/mturk/manageHITs",
            "reward": "1.50"
        },
        "sandbox": {
            "endpoint": "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
            "preview": "https://workersandbox.mturk.com/mturk/preview",
            "manage": "https://requestersandbox.mturk.com/mturk/manageHITs",
            "reward": "1.50"
        },
    }
    mturk_environment = environments["live"] if create_hits_in_live else environments["sandbox"]

    # restrict to mturk workers that have 80% hit accept rate
    worker_requirements = [
        {
            'QualificationTypeId': '000000000000000000L0',
            'Comparator': 'GreaterThanOrEqualTo',
            'IntegerValues': [80],
            'RequiredToPreview': True,
        },
        {
            'QualificationTypeId': '00000000000000000071',
            'Comparator': 'EqualTo',
            'LocaleValues': [
                {
                    'Country': 'US'
                },
            ],
        },
    ]

    session = boto3.Session(profile_name=args.profile_name)
    client = session.client(service_name='mturk', region_name='us-east-1', endpoint_url=mturk_environment['endpoint'])
    question_xml = open(args.question_xml_filename, "r").read()
    major_version = 0
    minor_version = 0
    description = 'Listen to 15 samples of music, each 8 seconds long, and annotate groups of notes.\n ' \
                  'version: {:d}.{:d}'.format(major_version, minor_version)

    # Create the HIT
    days = 60 * 60 * 24
    hours = 60 * 60
    response = client.create_hit(
        MaxAssignments=args.num_hits,
        LifetimeInSeconds=int(3*days),  # amount of time that can elapse between creation and acceptance of the HIT
        AssignmentDurationInSeconds=int(1*hours),  # amount of time they can work on the HIT for
        Reward=mturk_environment['reward'],
        Title='Annotate Groupings in Music Clips',
        Keywords='data, music, audio, listening, easy, research',
        Description=description,
        Question=question_xml,
        QualificationRequirements=worker_requirements,
        AutoApprovalDelayInSeconds=1*days,  # the time we get to reject a response
    )

    # Wait for it to be posted
    print("waiting for HIT to become available...")
    sleep(10)

    # The response included several fields that will be helpful later
    hit_type_id = response['HIT']['HITTypeId']
    hit_id = response['HIT']['HITId']
    print("\nCreated HIT: {}".format(hit_id))

    print("\nYou can work the HIT here:")
    print(mturk_environment['preview'] + "?groupId={}".format(hit_type_id))

    print("\nAnd see results here:")
    print(mturk_environment['manage'])

    while True:
        c = input("press enter to poll results")
        if c == 'q':
            break
        results = client.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted'])
        pprint(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())

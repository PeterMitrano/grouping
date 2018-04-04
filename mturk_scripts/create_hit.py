#!/usr/bin/env python3

import argparse
import sys
import boto3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('question_xml_filename',  help='XML file containing the details of the ExternalQuestion')
    parser.add_argument('--profile_name', '-p', default='mturk', help='profile name in ~/.aws/credentials file')
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

    # restrict to mturk workers that have 80% hit accept rate
    worker_requirements = [{
        'QualificationTypeId': '000000000000000000L0',
        'Comparator': 'GreaterThanOrEqualTo',
        'IntegerValues': [80],
        'RequiredToPreview': True,
    }]

    session = boto3.Session(profile_name=args.profile_name)
    client = session.client(service_name='mturk', region_name='us-east-1', endpoint_url=mturk_environment['endpoint'])
    question_xml = open(args.question_xml_filename, "r").read()
    major_version = 0
    minor_version = 0
    description = 'Listen to 10 samples of music, each 8 seconds long, and annotate the different groupings.\n ' \
                  'version: {:d}.{:d}'.format(major_version, minor_version)

    # Create the HIT
    response = client.create_hit(
        MaxAssignments=1,
        LifetimeInSeconds=2*60*60,  # amount of time that can elapse between creation and acceptance of the HIT
        AssignmentDurationInSeconds=15*3*60,  # amount of time they can work on the HIT for
        Reward=mturk_environment['reward'],
        Title='Annotate Groupings in Music Clips',
        Keywords='data, music, audio, listening, easy, research',
        Description=description,
        Question=question_xml,
        QualificationRequirements=worker_requirements,
        AutoApprovalDelayInSeconds=24*60*60,  # gives us 24 hours to reject a response
    )

    # The response included several fields that will be helpful later
    hit_type_id = response['HIT']['HITTypeId']
    hit_id = response['HIT']['HITId']
    print("\nCreated HIT: {}".format(hit_id))

    print("\nYou can work the HIT here:")
    print(mturk_environment['preview'] + "?groupId={}".format(hit_type_id))

    print("\nAnd see results here:")
    print(mturk_environment['manage'])

    return 0


if __name__ == "__main__":
    sys.exit(main())

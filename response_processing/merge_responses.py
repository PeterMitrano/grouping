import argparse


def main():
    parser = argparse.ArgumentParser("merges a csv of survey responses, and a sqlite3 database of responses.")
    parser.add_argument('survery_responses', 'csv file of survery responses downloaded from google sheets')
    parser.add_argument('database_responses', 'sqlite3 database file of survey responses downloaded from the server')

    args = parser.parse_args()


if __name__ == '__main__':
    main()

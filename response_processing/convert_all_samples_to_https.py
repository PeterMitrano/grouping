#!/usr/bin/env python3

import sqlite3
import argparse


def main():
    parser = argparse.ArgumentParser("plots the final responses from a sqlite3 database of responses.")
    parser.add_argument('database', help='sqlite3 database file of survey responses downloaded from the server')

    args = parser.parse_args()

    # open the database
    db = sqlite3.connect(args.database, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row

    samples_cur = db.execute('SELECT url FROM samples')
    samples_urls = samples_cur.fetchall()
    responses_cur = db.execute('SELECT url FROM responses')
    responses_urls = responses_cur.fetchall()

    for url in samples_urls:
        url = url[0]
        new_url = url.replace("http:", "https:", 1)
        db.execute('UPDATE samples SET url = ? WHERE url = ?', [new_url, url])

    for url in responses_urls:
        url = url[0]
        new_url = url.replace("http:", "https:", 1)
        db.execute('UPDATE responses SET url = ? WHERE url = ?', [new_url, url])

    db.commit()


if __name__ == "__main__":
    main()

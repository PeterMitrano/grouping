import json
import os
import shutil
import sqlite3
from collections import OrderedDict
from datetime import datetime

import click
from colorama import init, Fore, Style
from flask import Flask, render_template, g, request, Response, url_for, redirect

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'interface.db'),
    SECRET_KEY='C796D37C6D491E8F0C6E9B83EED34C15C0F377F9F0F3CBB3216FBBF776DA6325',
    USERNAME='admin',
    PASSWORD='password'
))

DEFAULT_SAMPLES_PER_PARTICIPANT = 10
SAMPLES_URL_PREFIX = 'https://users.wpi.edu/~mprlab/grouping/data/samples/'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')


@app.cli.command('dumpdb')
@click.option('--outfile', help="name for output file containing the responses database", type=click.Path())
def dumpdb_command(outfile):
    """ Print the database (can save to CSV) """
    dump_db(outfile)


@app.cli.command('load')
def initdb_command():
    """Loads new samples into the samples table."""
    success = load()

    if success:
        dump_db(False)


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    success = init_db()

    if success:
        dump_db(False)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    db = get_db()

    y = input("Are you sure you want to DELETE ALL DATA and re-initialize the database? [y/n]")
    if y != 'y' and y != 'Y':
        print("Aborting.")
        return False

    # apply the schema
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    load()

    db.commit()

    print(Fore.RED + "Database Initialized" + Style.RESET_ALL)
    return True


def load():
    db = get_db()

    # insert all the files from the file system
    sample_names = open(APP_STATIC + "/samples/index.txt").readlines()
    for sample_name in sample_names:
        sample_name = sample_name.strip("\n")
        sample_url = SAMPLES_URL_PREFIX + sample_name
        try:
            db.execute('INSERT INTO samples (url, count) VALUES (?, ?) ', [sample_url, 0])
            print(Fore.BLUE, end='')
            print("Added", sample_url)
            print(Fore.RESET, end='')
        except sqlite3.IntegrityError:
            # skip this because the sample already exists!
            print(Fore.YELLOW, end='')
            print("Skipped", sample_url)
            print(Fore.RESET, end='')

    db.commit()

    return True


def dump_db(outfile_name):
    # for pretty terminal output
    init()

    db = get_db()

    if outfile_name:
        outfile = open(outfile_name, 'w')
    else:
        outfile = open(os.devnull, 'w')

    def print_samples_db():
        samples_cur = db.execute('SELECT url, count FROM samples ORDER BY count ASC')
        entries = samples_cur.fetchall()

        # figure out dimensions
        url_w = "30"
        count_w = "5"

        header_format = "{:<" + url_w + "." + url_w + "s} {:s}"
        header = header_format.format("URL", "count")
        w = len(header)
        row_format = "{:<" + url_w + "." + url_w + "s} {:<" + count_w + "d}"

        print(Fore.GREEN + "Dumping Database" + Style.RESET_ALL)

        print("=" * w)
        print(header)
        print("=" * w)
        for entry in entries:
            url = entry[0]
            url = url.strip(SAMPLES_URL_PREFIX)
            count = entry[1]
            print(row_format.format(url, count))
        print("=" * w)

    def print_response_db():
        responses_cur = db.execute('SELECT * FROM responses ORDER BY stamp DESC')
        entries = responses_cur.fetchall()

        json_out = []

        headers = OrderedDict()
        headers['id'] = 3
        headers['url'] = 20
        headers['ip_addr'] = 9
        headers['stamp'] = 27
        term_size = shutil.get_terminal_size((100, 20))
        total_width = term_size.columns
        headers['data'] = max(total_width - sum(headers.values()) - len(headers), 0)
        fmt = ""
        for k, w in headers.items():
            fmt += "{:<" + str(w) + "." + str(w) + "s} "
        fmt = fmt.strip(' ')
        header = fmt.format(*headers.keys())
        print("=" * total_width)
        print(header)
        for entry in entries:
            response = json.loads(entry[4])
            json_out.append({
                'id': entry[0],
                'url': entry[1],
                'ip_addr': entry[2],
                'stamp': str(entry[3]),
                'data': json.loads(entry[4])})
            cols = [str(col) for col in entry]
            cols[1] = cols[1].strip(SAMPLES_URL_PREFIX)
            data = "["
            for d in response['final_response']:
                s = "%0.2f, " % d['timestamp']
                if len(data + s) > headers['data'] - 4:
                    data += "..., "
                    break
                data += s
            if len(data) == 1:
                cols[-1] = data + "]"
            else:
                cols[-1] = data[:-2] + "]"
            print(fmt.format(*cols))
        print("=" * total_width)

        json.dump(json_out, outfile, indent=2)

    print_samples_db()
    print_response_db()


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/responses', methods=['POST'])
def responses():
    db = get_db()
    req_data = request.get_json()
    samples = req_data['samples']
    ip_addr = request.remote_addr
    stamp = datetime.now()

    sample_responses = req_data['responses']
    for idx, data in enumerate(sample_responses):
        url = samples[idx]['url']
        # sort the final response by timestamps for sanity
        sorted_final_response = sorted(data['final_response'], key=lambda d: d['timestamp'])
        data['final_response'] = sorted_final_response
        db.execute('INSERT INTO responses (url, ip_addr, stamp, data) VALUES (?, ?, ?, ?)',
                   [url, ip_addr, stamp, json.dumps(data)])

    for sample in samples:
        db.execute('UPDATE samples SET count = count + 1 WHERE url= ?', [sample['url']])

    db.commit()

    data = {'status': 'ok'}
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    return resp


@app.route('/survey', methods=['GET'])
def survey():
    samples_per_participant = int(request.args.get('samples_per_participant', DEFAULT_SAMPLES_PER_PARTICIPANT))
    return render_template('survey.html', samples_per_participant=samples_per_participant)


@app.route('/welcome', methods=['GET'])
def welcome():
    samples_per_participant = int(request.args.get('samples_per_participant', DEFAULT_SAMPLES_PER_PARTICIPANT))
    return render_template('welcome.html', samples_per_participant=samples_per_participant)


@app.route('/thankyou', methods=['GET'])
def thank_you():
    return render_template('thankyou.html')


@app.route('/manage', methods=['GET'])
def manage():
    return render_template('manage.html')


@app.route('/', methods=['GET'])
def root():
    return redirect(url_for('welcome'))


@app.route('/interface', methods=['GET'])
def interface():
    db = get_db()
    cur = db.execute('SELECT url, count FROM samples ORDER BY count ASC')
    entries = cur.fetchall()
    samples_per_participant = int(request.args.get('samples_per_participant', DEFAULT_SAMPLES_PER_PARTICIPANT))
    if samples_per_participant <= 0 or samples_per_participant > 30:
        return render_template('error.html', reason='Number of samples per participant must be between 1 and 30')
    elif len(entries) < samples_per_participant:
        return render_template('error.html', reason='Not samples available for response.')
    else:
        samples = [{'url': e[0]} for e in entries[:samples_per_participant]]
        return render_template('interface.html', samples=json.dumps(samples))


if __name__ == '__main__':
    app.run()

#!/usr/bin/env python3

from flask import Flask, render_template, url_for
import json

app = Flask(__name__)


@app.route('/thankyou.html', methods=['GET'])
def thankyou():
    return render_template('thankyou.html')


@app.route('/', methods=['GET'])
def index():
    samples = ["18_Guitalele.mp3", "peter_gt_01.mp3"]
    prefix_url = url_for('static', filename='samples/')
    samples = [prefix_url + sample for sample in samples]
    return render_template('index.html', samples=json.dumps(samples))


if __name__ == '__main__':
    app.run(debug=True)

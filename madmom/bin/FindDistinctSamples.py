#!/usr/bin/env python

import argparse
from time import sleep
import os
import sys
import wave

import numpy as np
import pyaudio


def play(full_path):
    wav_file = wave.open(full_path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wav_file.getsampwidth()),
                    channels=wav_file.getnchannels(),
                    rate=wav_file.getframerate(),
                    output=True)

    chunk = 1024
    data = wav_file.readframes(chunk)
    while len(data) > 0:
        data = wav_file.readframes(chunk)
        stream.write(data)

    stream.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('samples_dir', help='samples directory')
    args = parser.parse_args()

    if not os.path.exists(args.samples_dir):
        print("Samples directory does not exist: ", args.samples_dir)

    # create a list of pairs of samples
    files = os.listdir(args.samples_dir)
    n = len(files)
    cov = np.zeros((n, n))
    p = np.random.permutation(n)
    q = np.random.permutation(n)
    file_indeces = []
    for p_ in p:
        for q_ in q:
            if p_ != q_:
                file_indeces.append((p_, q_))
    np.random.shuffle(file_indeces)

    # sub sample so this doesn't take hours
    samples = 50
    to_remove = []

    for i, j in file_indeces[:samples]:
        full_path_a = os.path.join(args.samples_dir, files[i])
        full_path_b = os.path.join(args.samples_dir, files[j])

        while True:
            play(full_path_a)
            sleep(0.2)
            play(full_path_b)
            while True:
                inp = input("Similarity between {} and {}? ".format(files[i], files[j]))
                if inp == 'r':
                    break
                try:
                    s = int(inp)
                except ValueError:
                    continue
                break
            if inp != 'r':
                break

        s = int(inp)
        if s >= 5:
            to_remove.append((files[i], files[j]))
        cov[i][j] = s

    print(cov)
    print(to_remove)
    np.savetxt("cov.csv", cov)


if __name__ == '__main__':
    sys.exit(main())

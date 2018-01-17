from pydub import AudioSegment, generators
import sys
import os
import argparse
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help='input file')
    parser.add_argument("outfile", help='output file')
    args=parser.parse_args()

    SAMPLE_LENGTH = 7000 # milliseconds

    song = AudioSegment.from_mp3(args.infile)
    start_time = np.random.uniform(0, song.duration_seconds*500)
    sample = song[start_time:start_time + SAMPLE_LENGTH]
    noise = generators.WhiteNoise().to_audio_segment(duration=500, volume=-30)
    clip = noise + sample
    clip.export(args.outfile)

if __name__=='__main__':
    sys.exit(main())

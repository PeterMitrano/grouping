#!/usr/bin/env python

from pydub import AudioSegment, generators
from multiprocessing import Pool
import sys
import os
import argparse
import numpy as np


def generate_samples_for_file(infile, args):
    sample_length_ms = 8000  # milliseconds
    fade_length_ms = 500

    song = AudioSegment.from_mp3(infile)

    num_samples = int(
        (song.duration_seconds * 1000 / sample_length_ms) * args.sample_percentage)  # 0.25 is fairly arbitrary
    for sample_idx in range(num_samples):
        start_time_ms = np.random.uniform(0, (song.duration_seconds * 1000 - sample_length_ms))
        end_time_ms = start_time_ms + sample_length_ms;
        clip = song[start_time_ms:end_time_ms]

        # enveloping and fading. noise is possible but not used in this case
        if args.noise:
            noise_length_ms = 1000
            quiet = -45
            noise = generators.WhiteNoise().to_audio_segment(duration=noise_length_ms, volume=quiet)
            clip = noise.append(clip, crossfade=noise_length_ms / 2)
            clip = clip.append(noise, crossfade=noise_length_ms / 2)

        clip = clip.fade_in(duration=fade_length_ms)
        clip = clip.fade_out(duration=fade_length_ms)

        # export file
        infile_short = os.path.basename(infile)[:8]
        outfile = os.path.join(args.outdir, infile_short + '_' + str(sample_idx) + '.mp3')
        print('exporting ', outfile, '...')
        exported_file = clip.export(outfile, tags={'start_time': start_time_ms, 'stop_time': end_time_ms})


def main():
    parser = argparse.ArgumentParser("sample_generator.py",
                                     epilog="This program generates the samples from a set of MP3 files.")
    parser.add_argument('infiles', help='input files (use globbing)', nargs='*')
    parser.add_argument('outdir', help='output directory')
    parser.add_argument('--workers', '-w', default=1, type=int, help="number of workers to use")
    parser.add_argument('--sample-percentage', '-n', type=float, default=0.25, help="percentage of samples")
    parser.add_argument('--noise', action='store_true', help='add noise')
    args = parser.parse_args()

    if not os.path.isdir(args.outdir):
        print("[{:s}] is not a directory.".format(args.outdir))
        return

    pool = Pool(processes=args.workers)
    func_args = [(f, args) for f in args.infiles]
    result = pool.starmap_async(generate_samples_for_file, func_args)
    result.wait()


if __name__ == '__main__':
    sys.exit(main())

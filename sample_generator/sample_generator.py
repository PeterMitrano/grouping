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

    num_samples = int((song.duration_seconds * 1000 / sample_length_ms) * 0.25)  # 0.25 is fairly arbitrary
    for sample_idx in range(num_samples):
        start_time = np.random.uniform(0, song.duration_seconds * 500)
        clip = song[start_time:start_time + sample_length_ms]

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
        clip.export(outfile)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infiles', help='input files', nargs='*')
    parser.add_argument('outdir', help='output directory')
    parser.add_argument('--workers', '-w', default=4, type=int, help="number of worker process to use")
    parser.add_argument('--number-of-samples', '-n', type=int, help='number of samples to make from each clip. \
                                                                     Otherwise, we sample based on the song length')
    parser.add_argument('--noise', action='store_true', help='add noise')
    args = parser.parse_args()

    pool = Pool(processes=args.workers)
    func_args = [(f, args) for f in args.infiles]
    result = pool.starmap_async(generate_samples_for_file, func_args)
    result.wait()


if __name__ == '__main__':
    sys.exit(main())

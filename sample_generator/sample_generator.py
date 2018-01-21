from pydub import AudioSegment, generators, effects
import sys
import os
import argparse
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help='input file')
    parser.add_argument("outfile", help='output file. we will append a number to the basename.')
    parser.add_argument("--number-of-samples", "-n", type=int, help='number of samples to make from each clip. \
                                                                     Otherwise, we sample based on the song length')
    parser.add_argument("--noise", action='store_true', help='add noise')
    args = parser.parse_args()

    sample_length_ms = 8000  # milliseconds
    fade_length_ms = 500

    song = AudioSegment.from_mp3(args.infile)

    base, ext = os.path.splitext(args.outfile)

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
        outfile = base + "_" + str(sample_idx) + ext
        clip.export(outfile)


if __name__ == '__main__':
    sys.exit(main())

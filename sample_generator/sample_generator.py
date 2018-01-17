from pydub import AudioSegment, generators, effects
import sys
import argparse
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help='input file')
    parser.add_argument("outfile", help='output file')
    parser.add_argument("--noise", action='store_true', help='add noise')
    args = parser.parse_args()

    sample_length = 8000  # milliseconds
    noise_length = 1000
    fade_length = 250
    quiet = -45

    song = AudioSegment.from_mp3(args.infile)
    start_time = np.random.uniform(0, song.duration_seconds * 500)
    clip = song[start_time:start_time + sample_length]
    noise = generators.WhiteNoise().to_audio_segment(duration=noise_length, volume=quiet)

    # enveloping and fading
    if args.noise:
        clip = noise.append(clip, crossfade=noise_length / 2)
        clip = clip.append(noise, crossfade=noise_length / 2)
    clip = clip.fade_in(duration=fade_length)
    clip = clip.fade_out(duration=fade_length)

    # export file
    # clip = noise + clip + noise
    clip.export(args.outfile)


if __name__ == '__main__':
    sys.exit(main())

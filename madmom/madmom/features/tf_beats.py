from functools import partial
import numpy as np
import sys

from ..processors import ParallelProcessor
from .beats import SequentialProcessor
from ..audio.signal import SignalProcessor, FramedSignalProcessor
from ..audio.spectrogram import (FilteredSpectrogramProcessor, LogarithmicSpectrogramProcessor,
                                 SpectrogramDifferenceProcessor)
from ..audio.stft import ShortTimeFourierTransformProcessor
from ..ml.nn import NeuralNetworkEnsemble
from ..models import DOWNBEATS_BLSTM


class TfRhythmicGroupingProcessor(SequentialProcessor):

    def __init__(self, **kwargs):
        # pylint: disable=unused-argument

        # define pre-processing chain
        sig = SignalProcessor(num_channels=1, sample_rate=44100)

        # process the multi-resolution spec & diff in parallel
        multi = ParallelProcessor([])
        frame_sizes = [1024, 2048, 4096]
        num_bands = [3, 6, 12]
        for frame_size, num_bands in zip(frame_sizes, num_bands):
            frames = FramedSignalProcessor(frame_size=frame_size, fps=100)
            stft = ShortTimeFourierTransformProcessor()  # caching FFT window
            filt = FilteredSpectrogramProcessor(num_bands=num_bands, fmin=30, fmax=17000, norm_filters=True)
            spec = LogarithmicSpectrogramProcessor(mul=1, add=1)
            diff = SpectrogramDifferenceProcessor(diff_ratio=0.5, positive_diffs=True, stack_diffs=np.hstack)

            # process each frame size with spec and diff sequentially
            multi.append(SequentialProcessor([frames, stft, filt, spec, diff]))

        # stack the features and processes everything sequentially
        pre_processor = SequentialProcessor([sig, multi, np.hstack])

        # process the pre-processed signal with a NN ensemble
        nn = NeuralNetworkEnsemble.load(DOWNBEATS_BLSTM, **kwargs)

        # use only the beat & downbeat (i.e. remove non-beat) activations
        act = partial(np.delete, obj=0, axis=1)

        # instantiate a SequentialProcessor
        super(TfRhythmicGroupingProcessor, self).__init__([pre_processor, nn, act])


class TfRhythmicGroupingPreProcessor(SequentialProcessor):

    def __init__(self, **kwargs):
        # pylint: disable=unused-argument

        # define pre-processing chain
        sig = SignalProcessor(num_channels=1, sample_rate=44100)

        # process the multi-resolution spec & diff in parallel
        multi = ParallelProcessor([])
        # frame size of 1024 means 1024 samples per frame, and with 44100 samples per second
        # that equals 23.22 milliseconds per frame
        frame_sizes = kwargs.get('frame_sizes', [1024, 2048, 4096])
        num_bands_list = [3, 6, 12]
        for frame_size, num_bands in zip(frame_sizes, num_bands_list):
            frames = FramedSignalProcessor(frame_size=frame_size, fps=100)
            stft = ShortTimeFourierTransformProcessor()  # caching FFT window
            filt = FilteredSpectrogramProcessor(num_bands=num_bands, fmin=30, fmax=17000, norm_filters=True)
            spec = LogarithmicSpectrogramProcessor(mul=1, add=1)
            diff = SpectrogramDifferenceProcessor(diff_ratio=0.5, positive_diffs=True, stack_diffs=np.hstack)

            # process each frame size with spec and diff sequentially
            multi.append(SequentialProcessor([frames, stft, filt, spec, diff]))

        # instantiate a SequentialProcessor
        super(TfRhythmicGroupingPreProcessor, self).__init__([sig, multi, np.hstack])

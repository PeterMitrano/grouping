import matplotlib.pyplot as plt
import numpy as np

from madmom.processors import OutputProcessor


class LabelOutputProcessor(OutputProcessor):
    """ saved arbitrary data instance. """

    def __init__(self, response, fps):
        self.response = response
        self.fps = fps

    def process(self, data, output, **kwargs):
        # pylint: disable=arguments-differ
        # Go through each frame in data, associate responses with that frame, and produce labels
        n_frames = data.shape[0]
        labels = np.zeros(n_frames)
        frame_sizes = kwargs.get('frame_sizes', [1024, 2048, 4096])
        max_frame_size = int((max(frame_sizes) / 44100) * self.fps)

        for marker_time in self.response:
            center_frame_idx = int(marker_time * self.fps)
            window = np.hanning(max_frame_size)
            start = max(center_frame_idx - max_frame_size//2, 0)
            stop = min(center_frame_idx + max_frame_size//2, n_frames - 1)
            for i in range(start, stop):
                labels[i] = window[i - start]

        return data, labels


class SaveOutputProcessor(OutputProcessor):
    """ saved arbitrary data instance. """

    def process(self, data, output, **kwargs):
        # pylint: disable=arguments-differ
        print("saving data to file: {}".format(output))
        np.save(output, data)
        return data


class ImShowOutputProcessor(OutputProcessor):
    """ saved arbitrary data instance. """

    def process(self, data, output=None, **kwargs):
        # pylint: disable=arguments-differ
        plt.imshow(data.T)
        plt.show()
        return data


class PlotActivationsProcessor(OutputProcessor):
    def process(self, data, output=None, **kwargs):
        import matplotlib.pyplot as plt

        start_idx = kwargs.get('start_idx', 0)
        end_idx = kwargs.get('end_idx', -1)

        if end_idx == -1:
            end_idx = data.shape[0]

        t = range(start_idx, end_idx)
        print("plotting from {} to {}".format(start_idx, end_idx))

        plt.plot(t, data[start_idx:end_idx, 0], label='beat')
        plt.plot(t, data[start_idx:end_idx, 1], label='down beat')
        plt.title("Softmax Activations")
        plt.legend(loc=2)
        plt.show()

        return data

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('--start-idx', default=0, type=int, help='frame number to start plotting at')
        parser.add_argument('--end-idx', default=-1, type=int, help='frame number to stop plotting at')

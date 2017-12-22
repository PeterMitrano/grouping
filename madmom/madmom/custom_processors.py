import matplotlib.pyplot as plt
import numpy as np

from madmom.processors import OutputProcessor


class LabelOutputProcessor(OutputProcessor):
    """ saved arbitrary data instance. """

    def __init__(self, all_responses, fps):
        self.all_responses = all_responses
        self.fps = fps

    def process(self, data, output, **kwargs):
        # pylint: disable=arguments-differ
        # Go through each frame in data, associate responses with that frame, and produce labels
        labels = np.zeros(data.shape[0])
        frame_sizes = kwargs.get('frame_sizes', [1024, 2048, 4096])
        max_frame_size = max(frame_sizes)
        max_frame_duration_s = max_frame_size / 441000  # standard sample rate of audio
        for i, frame in enumerate(data):
            # Each frame contains audio feature for 1024, 2048, and 4096 samples.
            # the 4096 samples is the widest frame length. It spans 92.88 ms in time (max_frame_duration_s).
            # we first compute the time interface of this frame
            count = 0
            t_center = i * 1 / self.fps
            t0 = t_center - max_frame_duration_s / 2
            t1 = t_center + max_frame_duration_s / 2

            # iterate over each time this clip was presented
            for responses in self.all_responses:
                # iterate over each unique response (time they hit space bar)
                for response in responses:
                    # convert from milliseconds to seconds
                    response = response / 1000

                    # modulus by the length of the clip
                    clip_length = data.shape[0] / float(kwargs.get('fps', 0))
                    response = response % clip_length

                    # If this response falls within the time range of our frame use it as a label
                    # Note one response may fall within the range of a few sequential frames
                    if t0 < response < t1:
                        window_center_idx = max_frame_size / 2
                        window_idx = int((response - t0) * max_frame_size / max_frame_duration_s)
                        w = np.hanning(max_frame_size)[window_idx]
                        labels[i] = 1 * w
                        break
                if labels[i] > 0:
                    break
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

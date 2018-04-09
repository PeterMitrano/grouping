import json
import numpy as np


def load(json_filename):
    trials = json.load(open(json_filename, "r"))

    # group by experiment into a dict
    experiments = {}
    for trial in trials:
        if trial["experiment_id"] not in experiments:
            experiments[trial["experiment_id"]] = []
        experiments[trial["experiment_id"]].append(trial)

    return experiments


def remove_blacklisted_experiments_inplace(experiments):
    blacklisted_ids = [
        "19::57::dc::4f::38::63::58::ee::e8",
        "79::71::78:: c::b9::1b::5c::3b",
        "8d::67::f5::cd::1b::8c::07::78::e4",
    ]
    for experiment_id in blacklisted_ids:
        try:
            del experiments[experiment_id]
        except KeyError:
            # it's already gone--great!
            pass

    return experiments


def get_final_responses(experiments):
    """
    Convert the result of load() to numpy arrays of final times
    :param experiments:
    :return:
    """
    final_responses = {}
    for experiment_id, trials_by_experiment in experiments.items():
        final_responses[experiment_id] = []
        for trial in trials_by_experiment:
            final_response = [float(t['timestamp']) for t in trial['data']['final_response']]
            final_response = np.array(final_response)
            final_responses[experiment_id].append(final_response)
    return final_responses


def flatten_final_responses(final_responses):
    flat_final_responses = []
    for _, responses in final_responses.items():
        for response in responses:
            flat_final_responses.append(response)

    return flat_final_responses

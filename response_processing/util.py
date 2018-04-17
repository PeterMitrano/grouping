import json
import numpy as np

blacklisted_ids = [
    "19::57::dc::4f::38::63::58::ee::e8",
    "79::71::78:: c::b9::1b::5c::3b",
    "8d::67::f5::cd::1b::8c::07::78::e4",
    "EXPERIMENT_ID_NOT_AVAILABLE",
    "EXPERIMENT_ID_NOT_AVAILABL",
    "f0::f8::ba::c8::f4::30::c2::89::ad",
]


def load_by_experiment(json_filename):
    trials = json.load(open(json_filename, "r"))

    # group by experiment into a dict
    responses_by_experiment = {}
    for trial in trials:
        experiment_id = trial["experiment_id"]
        if experiment_id in blacklisted_ids:
            continue
        if experiment_id not in responses_by_experiment:
            responses_by_experiment[experiment_id] = []
        responses_by_experiment[experiment_id].append(trial)

    return responses_by_experiment


def load_by_url(json_filename):
    trials = json.load(open(json_filename, "r"))

    # group by experiment into a dict
    responses_by_url = {}
    for trial in trials:
        url = trial["url"]
        experiment_id = trial["experiment_id"]
        if experiment_id in blacklisted_ids:
            continue
        if url not in responses_by_url:
            responses_by_url[url] = []
        responses_by_url[url].append(trial)

    return responses_by_url


def get_final_responses(experiments):
    """
    Convert the result of load() to numpy arrays of final times
    :param experiments:
    :return:
    """
    final_responses = {}
    for key, trials_by_experiment in experiments.items():
        final_responses[key] = []
        for trial in trials_by_experiment:
            final_response = [float(t['timestamp']) for t in trial['data']['final_response']]
            final_response = np.array(final_response)
            final_responses[key].append(final_response)
    return final_responses


def flatten_final_responses(final_responses):
    flat_final_responses = []
    for _, responses in final_responses.items():
        for response in responses:
            flat_final_responses.append(response)

    return flat_final_responses

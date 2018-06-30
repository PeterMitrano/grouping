import json
import numpy as np


def load_by_experiment(json_filename):
    trials = json.load(open(json_filename, "r"))['dataset']

    # group by experiment into a dict
    responses_by_experiment = {}
    for trial in trials:
        experiment_id = trial["experiment_id"]
        if experiment_id not in responses_by_experiment:
            responses_by_experiment[experiment_id] = []
        responses_by_experiment[experiment_id].append(trial)

    return responses_by_experiment


def load_by_url(json_filename):
    trials = json.load(open(json_filename, "r"))['dataset']

    # group by experiment into a dict
    responses_by_url = {}
    for trial in trials:
        url = trial["url"]
        if url not in responses_by_url:
            responses_by_url[url] = []
        responses_by_url[url].append(trial)

    return responses_by_url


def get_final_responses_list(experiments):
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
            final_responses[key].append(final_response)
    return final_responses

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

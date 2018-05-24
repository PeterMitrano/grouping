import json
import numpy as np

blacklisted_ids = [
    "19::57::dc::4f::38::63::58::ee::e8",
    "79::71::78:: c::b9::1b::5c::3b",
    "8d::67::f5::cd::1b::8c::07::78::e4",
    "EXPERIMENT_ID_NOT_AVAILABLE",
    "EXPERIMENT_ID_NOT_AVAILABL",
    "testing",
    "f0::f8::ba::c8::f4::30::c2::89::ad",
    "e7::a5::46::9a::a5::98::aa::aa::77",
    "b9::7e::55::c6::d6::91::31::6a::31",
    "20::26::4f::c2::a3::0a::47::c4::d5",
    "13::07::b5::0e::51::37::29::39::0c",
    "ef::b4::d1::3a::12::cb::62::ef::19",
    "79::71::78::%20c::b9::1b::5c::3b",
    "fe::9f::fe::b8::79::41::12::7d::fd",
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

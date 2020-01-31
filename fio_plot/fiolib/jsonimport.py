import json
import os
import sys
from typing import List


def is_json_file(file) -> bool:
    return file.endswith('.json')


def list_json_files(settings) -> List[str]:
    """List all JSON files that matches the command line settings."""
    prefix = settings['rw'] + '-'
    absolute_dir = os.path.abspath(settings['input_directory'])
    files = os.listdir(absolute_dir)

    json_files = list(map(lambda f: os.path.join(absolute_dir, f),
                          filter(lambda f: f.startswith(prefix),
                                 filter(is_json_file, files))))

    if len(json_files) == 0:
        print("Could not find any (matching) JSON files in the specified directory " + str(absolute_dir))
        sys.exit(1)

    return json_files


def import_json_data(filename):
    """Returns a dictionary of imported JSON data."""
    with open(filename) as json_data:
        d = json.load(json_data)
    return d


def import_json_dataset(fileset):
    """Returns a list of imported raw JSON data for every file in the fileset.
    """
    d = []
    for f in fileset:
        d.append(import_json_data(f))
    return d


def get_nested_value(dictionary, key):
    """This function reads the data from the FIO JSON file based on the supplied
    key (which is often a nested path within the JSON file).
    """
    for item in key:
        dictionary = dictionary[item]
    return dictionary


def get_json_mapping(mode):
    """ This function contains a hard-coded mapping of FIO nested JSON data
    to a flat dictionary.
    """
    root = ['jobs', 0]
    jobOptions = root + ['job options']
    data = root + [mode]
    dictionary = {
        'iodepth': (jobOptions + ['iodepth']),
        'numjobs': (jobOptions + ['numjobs']),
        'rw': (jobOptions + ['rw']),
        'bw': (data + ['bw']),
        'iops': (data + ['iops']),
        'iops_stddev': (data + ['iops_stddev']),
        'lat_ns': (data + ['lat_ns', 'mean']),
        'lat_stddev': (data + ['lat_ns', 'stddev']),
        'latency_ms': (root + ['latency_ms']),
        'latency_us': (root + ['latency_us']),
        'latency_ns': (root + ['latency_ns'])
    }

    return dictionary


def remove_prefix(text: str, prefix: str):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def get_flat_json_mapping(settings, dataset):
    """This function returns a list of simplified dictionaries based on the
    data within the supplied json data."""
    kind = settings['rw']
    mode = kind
    if kind == 'randrw':
        if settings['filter'][0]:
            mode = settings['filter'][0]
            kind = mode
        else:
            print("When processing 'randrw' data, a -f filter (read/write) must also be specified.")
            exit(1)
    elif kind == 'read' or kind == 'write':
        mode = kind
    else:
        mode = remove_prefix(kind, 'rand')
    mapping = get_json_mapping(mode)

    stats = []
    for record in dataset:
        actual_mode = get_nested_value(record, ('jobs', 0, 'job options', 'rw'))
        if actual_mode != kind:
            print("Mode mismatch, expected '{}' but was '{}'".format(kind, actual_mode))
            assert False
        row = {
            'iodepth': get_nested_value(record, mapping['iodepth']),
            'numjobs': get_nested_value(record, mapping['numjobs']),
            'rw': get_nested_value(record, mapping['rw']),
            'bw': get_nested_value(record, mapping['bw']),
            'iops': get_nested_value(record, mapping['iops']),
            'iops_stddev': get_nested_value(record, mapping['iops_stddev']),
            'lat': get_nested_value(record, mapping['lat_ns']),
            'lat_stddev': get_nested_value(record, mapping['lat_stddev']),
            'latency_ms': get_nested_value(record, mapping['latency_ms']),
            'latency_us': get_nested_value(record, mapping['latency_us']),
            'latency_ns': get_nested_value(record, mapping['latency_ns']),
            'type': mode
        }
        stats.append(row)
    return stats

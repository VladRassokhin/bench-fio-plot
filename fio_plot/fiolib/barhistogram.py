#!/usr/bin/env python3
import functools
import operator
import os

import matplotlib.pyplot as plt
import numpy as np

import fiolib.shared_chart as shared
import fiolib.supporting as supporting


def sort_latency_keys(latency):
    """The FIO latency data has latency buckets and those are sorted ascending.
    The millisecond data has a >=2000 bucket which cannot be sorted in a 'normal'
    way, so it is just stuck on top. This function returns a list of sorted keys.
    """
    placeholder = ""
    tmp = []
    for item in latency:
        if item == '>=2000':
            placeholder = ">=2000"
        else:
            tmp.append(item)

    tmp.sort(key=int)
    if placeholder:
        tmp.append(placeholder)
    return tmp


def sort_latency_data(latency_dict):
    """The sorted keys from the sort_latency_keys function are used to create
    a sorted list of values, matching the order of the keys."""
    keys = latency_dict.keys()
    values = {'keys': None, 'values': []}
    sorted_keys = sort_latency_keys(keys)
    values['keys'] = sorted_keys
    for key in sorted_keys:
        values['values'].append(latency_dict[key])
    return values


def autolabel(rects, axis):
    """This function puts a value label on top of a 2d bar. If a bar is so small
    it's barely visible, if at all, the label is omitted."""
    fontsize = 6
    for rect in rects:
        height = rect.get_height()
        if height >= 1:
            axis.text(rect.get_x() + rect.get_width() / 2., 1 +
                      height, '{}%'.format(int(height)),
                      ha='center', fontsize=fontsize)
        elif height > 0.1:
            axis.text(rect.get_x() + rect.get_width() /
                      2., 1 + height, "{:3.2f}%".format(height), ha='center', fontsize=fontsize)


def chart_latency_histogram(settings, dataset):
    """This function is responsible to draw the 2D latency histogram,
    (a bar chart)."""
    numjobs = settings['numjobs']
    if not numjobs or len(numjobs) != 1:
        print("Expected only single numjob, got: " + str(numjobs))
        exit(1)
    iodepth = settings['iodepth']
    if not iodepth or len(iodepth) != 1:
        print("Expected only single iodepth, got: " + str(iodepth))
        exit(1)
    rw = settings['rw']
    numjobs = int(numjobs[0])
    iodepth = int(iodepth[0])
    record_set = shared.get_record_set_histogram(dataset, rw, iodepth, numjobs)

    # We have to sort the data / axis from low to high
    sorted_result_ms = sort_latency_data(record_set['data']['latency_ms'])
    sorted_result_us = sort_latency_data(record_set['data']['latency_us'])
    sorted_result_ns = sort_latency_data(record_set['data']['latency_ns'])

    all_keys = functools.reduce(operator.iconcat, [
        (round(float('0.' + k), 3) for k in sorted_result_us['keys']),
        sorted_result_us['keys'],
        (k + 'k' for k in sorted_result_ms['keys'])
    ], [])

    all_values = functools.reduce(operator.iconcat, [
        sorted_result_ns['values'],
        sorted_result_us['values'],
        sorted_result_ms['values']
    ], [])

    # This is just to use easier to understand variable names
    x_series = all_keys

    # Create the plot
    fig, ax1 = plt.subplots()
    fig.set_size_inches(10, 6)

    # Make the positioning of the bars for ns/us/ms
    x_pos = np.arange(0, len(x_series), 1)
    width = 1

    # Draw the bars
    colors = functools.reduce(operator.iconcat, [
        'r' * len(sorted_result_ns['values']),
        'b' * len(sorted_result_us['values']),
        'g' * len(sorted_result_ms['values']),
    ], [])
    rects = ax1.bar(x_pos, all_values, width, color=colors)

    # Configure the axis and labels
    ax1.set_ylabel('Percentage of I/O')
    ax1.set_xlabel("Latency (µs)")
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(x_series)
    ax1.xaxis.set_tick_params(rotation=45)

    # Make room for labels by scaling y-axis up (max is 100%)
    ax1.set_ylim(0, 100 * 1.1)

    # Configure the title
    settings['type'] = ""
    supporting.create_title_and_sub(settings, plt, ['type', 'filter'])

    # puts a percentage above each bar (ns/us/ms)
    autolabel(rects, ax1)

    fig.text(0.75, 0.03, settings['source'])

    plt.tight_layout(rect=[0, 0.00, 0.95, 0.95])
    title = settings['title'].replace(" ", '-').replace("/", '-')
    name = f"{title}-hist-lat-{rw}-j{numjobs}-qd{iodepth}.png"
    if os.path.isfile(name):
        print(f"File '{name}' already exists")
        exit(1)
    fig.savefig(name, dpi=settings['dpi'])

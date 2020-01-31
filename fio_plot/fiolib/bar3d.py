#!/usr/bin/env python3
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.axis3d import Axis

import fiolib.shared_chart as shared
import fiolib.supporting as supporting


# Removing axes margin on 3D graphs
# From https://stackoverflow.com/a/52404426/1039742
def _get_coord_info_new(self, renderer):
    mins, maxs, cs, deltas, tc, highs = self._get_coord_info_old(renderer)
    correction = deltas * [0, 0, 1.0 / 4]
    mins += correction
    maxs -= correction
    return mins, maxs, cs, deltas, tc, highs


if not hasattr(Axis, "_get_coord_info_old"):
    Axis._get_coord_info_old = Axis._get_coord_info
Axis._get_coord_info = _get_coord_info_new


def plot_3d(settings, dataset):
    """This function is responsible for plotting the entire 3D plot.
    """

    if not settings['type']:
        print("The type of data must be specified with -t (iops/lat).")
        exit(1)
    if len(settings['type']) != 1:
        print("Expected single type of data to be specified with -t (iops/lat).")
        exit(1)

    dataset_types = shared.get_dataset_types(dataset)
    metric = settings['type'][0]
    rw = settings['rw']
    iodepth = dataset_types['iodepth']
    numjobs = dataset_types['numjobs']
    data = shared.get_record_set_3d(settings, dataset, dataset_types,
                                    rw, metric)
    # pprint.pprint(data)

    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection=Axes3D.name)
    fig.set_size_inches(15, 10)

    lx = len(iodepth)
    ly = len(numjobs)

    # Ton of code to scale latency
    if metric == 'lat':
        scale_factors = []
        for row in data['values']:
            scale_factor = supporting.get_scale_factor(row)
            scale_factors.append(scale_factor)
        largest_scale_factor = supporting.get_largest_scale_factor(
            scale_factors)
        # pprint.pprint(largest_scale_factor)

        scaled_values = []
        for row in data['values']:
            result = supporting.scale_yaxis_latency(
                row, largest_scale_factor)
            scaled_values.append(result['data'])
        z_axis_label = largest_scale_factor['label']
    else:
        scaled_values = data['values']
        z_axis_label = metric

    n = np.array(scaled_values, dtype=float)

    size = lx * 0.05  # thickness of the bar
    xpos_orig = np.arange(0, lx, 1)
    ypos_orig = np.arange(0, ly, 1)

    xpos = np.arange(0, lx, 1)
    ypos = np.arange(0, ly, 1)
    xpos, ypos = np.meshgrid(xpos - size / 2, ypos - size / 2)

    # Convert positions to 1D array
    xpos_f = xpos.flatten(order='C')
    ypos_f = ypos.flatten(order='C')
    zpos = np.zeros(lx * ly)

    # Positioning and sizing of the bars
    dx = np.full(lx * ly, size)
    dy = dx.copy()
    dz = n.flatten(order='F')
    values = dz / (dz.max())

    # Create the 3D chart with positioning and colors
    cmap = plt.get_cmap('rainbow', len(values))
    colors = cm.rainbow(values)
    ax1.bar3d(xpos_f, ypos_f, zpos, dx, dy, dz, color=colors)

    # Create the color bar to the right
    norm = mpl.colors.Normalize(vmin=0, vmax=dz.max())
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    res = fig.colorbar(sm, fraction=0.046, pad=0.04)
    res.ax.set_title(z_axis_label)

    # Set tics for x/y axis
    float_x = [float(x) for x in (xpos_orig)]

    ax1.xaxis.set_ticks(float_x)
    ax1.yaxis.set_ticks(ypos_orig)
    ax1.xaxis.set_ticklabels(iodepth)
    ax1.yaxis.set_ticklabels(numjobs)
    ax1.set_zlim(bottom=0)

    # axis labels
    fontsize = 16
    ax1.set_xlabel('iodepth', fontsize=fontsize)
    ax1.set_ylabel('numjobs', fontsize=fontsize)
    ax1.set_zlabel(z_axis_label, fontsize=fontsize)

    [t.set_verticalalignment('center_baseline') for t in ax1.get_yticklabels()]
    [t.set_verticalalignment('center_baseline') for t in ax1.get_xticklabels()]

    ax1.zaxis.labelpad = 25

    tick_label_font_size = 12
    for t in ax1.xaxis.get_major_ticks():
        t.label.set_fontsize(tick_label_font_size)

    for t in ax1.yaxis.get_major_ticks():
        t.label.set_fontsize(tick_label_font_size)

    ax1.zaxis.set_tick_params(pad=10)
    for t in ax1.zaxis.get_major_ticks():
        t.label.set_fontsize(tick_label_font_size)

    # title
    supporting.create_title_and_sub(
        settings, plt, skip_keys=['iodepth', 'numjobs'], sub_x_offset=0.57, sub_y_offset=1.05)

    fig.text(0.75, 0.03, settings['source'])

    plt.tight_layout()
    plt.savefig(settings['title'] + '-3d-' + metric + '-' + str(rw) + '.png')
    plt.close('all')

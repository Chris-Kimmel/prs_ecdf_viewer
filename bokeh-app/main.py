from os.path import join, dirname
import datetime
from base64 import b64decode
from io import BytesIO

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, DataRange1d, Select, FileInput, Spinner
from bokeh.palettes import Blues4
from bokeh.plotting import figure

STATISTICS = ['record_min_temp', 'actual_min_temp', 'average_min_temp', 'average_max_temp', 'actual_max_temp', 'record_max_temp']
N_BINS = 100
SPINNER_MAX = 9200

def make_plot_2(source):
    plot = figure(plot_width=800, tools="", toolbar_location=None)

    lines1 = plot.line(x='x', y='y1', source=source, legend="Dataset 1", line_color='red')
    lines2 = plot.line(x='x', y='y2', source=source, legend="Dataset 2", line_color='blue')

    # fixed attributes
    plot.title.text = 'asdf'
    plot.xaxis.axis_label = 'p-value'
    plot.yaxis.axis_label = "eCDF"
    plot.axis.axis_label_text_font_style = "bold"
    # plot.x_range = DataRange1d(range_padding=0.0) # not sure what this does
    plot.grid.grid_line_alpha = 0.3

    return plot

def update_plot(attrname, old, new):
    # pylint: disable=W
    city = city_select.value
    plot.title.text = "Weather data for " + cities[city]['title']

    src = get_dataset(df, cities[city]['airport'], distribution_select.value)
    source.data.update(src.data)

def get_csv(stream):
    df = pd.read_csv(stream, index_col=0, header=0)
    df.columns = df.columns.astype(int)
    df = df.reset_index(drop=True)

    return df

def update_file_1(attrname, old, new):
    global whole_dset_1
    print('Processing new file1')
    file_stream = BytesIO(b64decode(file_select_1.value))
    df = get_csv(file_stream)
    whole_dset_1 = {}
    for key, value in df.items():
        arr = value.dropna().to_numpy().ravel()
        n = len(arr)
        hist, bins = np.histogram(arr, bins=N_BINS)
        whole_dset_1[key] = hist.cumsum()/n
    print('Done processing file1')

def update_file_2(attrname, old, new):
    global whole_dset_2
    print('Processing new file2')
    file_stream = BytesIO(b64decode(file_select_1.value))
    df = get_csv(file_stream)
    whole_dset_2 = {}
    for key, value in df.items():
        arr = value.dropna().to_numpy().ravel()
        n = len(arr)
        hist, bins = np.histogram(arr, bins=N_BINS)
        whole_dset_2[key] = hist.cumsum()/n
    print('Done processing file2')

def update_pos(attrname, old, new):
    print('Updating position')
    pos = pos_spinner.value
    x_data = np.linspace(0, 1, N_BINS)
    y_data_1 = whole_dset_1.get(pos, np.ones(N_BINS))
    y_data_2 = whole_dset_2.get(pos, np.ones(N_BINS))
    new_data = ColumnDataSource({'x': x_data, 'y1': y_data_1, 'y2': y_data_2}) # Delete this line

    print(pos)
    print(x_data)
    print(y_data_1)
    print(whole_dset_1.keys())

    to_plot.data = {'x': x_data, 'y1': y_data_1, 'y2': y_data_2}
    print('Done updating position')

whole_dset_1 = {}
whole_dset_2 = {}

to_plot = ColumnDataSource({'x': [], 'y1': [], 'y2': []})

file_select_1 = FileInput()
file_select_2 = FileInput()
pos_spinner = Spinner(low=0, high=SPINNER_MAX)

plot = make_plot_2(to_plot)

file_select_1.on_change('value', update_file_1)
file_select_2.on_change('value', update_file_2)
pos_spinner.on_change('value', update_pos)

controls = column(pos_spinner, file_select_1, file_select_2)

curdoc().add_root(row(plot, controls))
curdoc().title = "Per-read Stats Viewer"

import numpy as np
from os.path import abspath, basename
from os import curdir

from traits.api \
     import Bool, Button, File, Float, HasTraits, \
     Instance, List, Property, String, DelegatesTo

from traitsui.api \
     import CancelButton, Group, Item, ListEditor, \
     OKButton, SetEditor, StatusItem, View, ListStrEditor

from chaco.api \
     import ArrayPlotData, Plot

from Calterm_III_tools \
     import open_DAQ_file

main_view = View(
    Group(
        Group(
             Item(name='file_to_open',
                  label='Data File',
                  style='custom',
                  show_label=False),
            Group(
                Item('add_source_button',
                     label='Add Source',
                     show_label=False),
                Item(name='align_button',
                     label="Align Data",
                     show_label=False),
                Item(name='plot_button',
                     label="Plot",
                     show_label=False),
                Item(name='save_button',
                     label="Save",
                     show_label=False),
                orientation="vertical"),
            orientation="horizontal"),
        Group(
            Item(name='data_source_list',
                 style='readonly',
                 show_label=False,
                 editor=ListStrEditor(
                     selected='selected_data_source',
                     editable=False,
                     title='Data Sources')),
            Group(
                Item('delete_button',
                     label='Delete',
                     show_label=False,
                     enabled_when='selected_data_source is not None'),
                Item('channel_select_button',
                     label='Channels...',
                     show_label=False,
                     enabled_when='selected_data_source is not None'),
                Item('gain_set_button',
                     label='Gains...',
                     show_label=False,
                     enabled_when='selected_data_source is not None'),
                orientation='vertical'),
            orientation='horizontal'),
        orientation="vertical"),
    title="Calterm III data alignment and analysis",
    height=500,
    width=450,
    buttons=[OKButton])

channels_view = View(
    Item(name='selected_channels',
         show_label=False,
         style='custom',
         editor=SetEditor(
             name='channel_names',
             ordered=True,
             can_move_all=True,
             left_column_title="Available channels",
             right_column_title="Channels to plot")),
    title="Select channels to plot",
    buttons=[OKButton, CancelButton])

file_open_view = View(
    Item(name='file_to_open',
         style='simple',
         show_label=False),
    buttons=[OKButton, CancelButton])

parameter_view = View(
    Item(name='selected_params',
         show_label=False,
         style='custom',
         editor=SetEditor(
             name='parameter_names',
             ordered=True,
             can_move_all=True,
             left_column_title="Available parameters",
             right_column_title="Parameters to plot")),
    title="Select parameters to plot",
    buttons=[OKButton, CancelButton])

gains_view = View(
    Item(name='channels',
         style='custom',
         #editor=TableEditor()),
         editor=ListEditor(use_notebook=True)),
    title="Set the gains for each channel",
    buttons=[OKButton, CancelButton])


class DataSource(HasTraits):
    '''
    data source containing a filename, an ArrayPlotData structure for
    plotting in Chaco
    '''
    a_p_data = Instance(ArrayPlotData)
    file_name = File
    channel_names = Property
    channel_gains = Property
    selected_channels = List(String)

    def __init__(self, **kwargs):
        if 'file_name' in kwargs:
            filename = kwargs.pop('file_name')
            self.load_file(filename)
        self.file_name = filename

    def _a_p_data_default(self):
        return ArrayPlotData()

    def __repr__(self):
        return basename(self.file_name)

    def _get_channel_names(self):
        return self.a_p_data.arrays.keys()

    ## def _get_parameter_units(self):
    ##     return [n.unit for n in self.parameters]

    ## def _get_channel_gains(self):
    ##     return [n.gain for n in self.channels]

    def load_file(self, filename):
        time, data, err = open_DAQ_file(filename)
        if not err:
            self.a_p_data.set_data('time', time)
            for name in data.dtype.names:
                self.a_p_data.set_data(name, data[name])
        else:
            print "Deal with the error here."


class calterm_data_viewer(HasTraits):
    """
    This is the user interface for plotting results from data acquisition
    supplemented with log file data from Calterm III, the Cummins ECM
    interface application. The UI is built with Enthought's Traits and TraitsUI
    """
    ## UI elements
    add_source_button = Button()
    align_button = Button()
    channel_select_button = Button()
    delete_button = Button()
    gain_set_button = Button()
    plot_button = Button()
    save_button = Button()
    channel_names = DelegatesTo('selected_data_source')

    file_to_open = File(value=abspath(curdir))

    data_source_list = List(Instance(DataSource))
    selected_data_source = Instance(DataSource)

    def _add_source_button_fired(self):
        if self.file_to_open == '':
            return
        d_s = DataSource(file_name=self.file_to_open)
        self.data_source_list.append(d_s)

    def _delete_button_fired(self):
        self.data_source_list.remove(self.selected_data_source)

    def _channel_select_button_fired(self):
        self.selected_data_source.edit_traits(view=channels_view)

    def _gain_set_button_fired(self):
        self.selected_data_source.edit_traits(view=gains_view)

    ## def _plot_button_fired(self):
    ##     import matplotlib as mpl
    ##     import matplotlib.pyplot as plt

    ##     pad = 0.05
    ##     fig_width = 8.5
    ##     ax_left = 0.18
    ##     ax_width = 0.75

    ##     #Count how many axes need to be plotted
    ##     num_axes = 0 + self.sensor_data.loaded
    ##     #ax[i].set_ylabel(self.selected_param

    ##     if self.log_data.loaded:
    ##         num_axes += len(self.selected_params)
    ##     if not(num_axes):
    ##         print "No files loaded or no parameters selected.\n"
    ##         return

    ##     fig_height = 11   ## 2. * num_axes + 1.5
    ##     fig = plt.figure(1, figsize=[fig_width, fig_height])
    ##     fig.clf()

    ##     #calculate the geometry for displaying the axes
    ##     total_pad = pad * (num_axes + 1)
    ##     ax_height = (1. - total_pad) / num_axes
    ##     ax_bottom = np.linspace(pad, 1. - (ax_height + pad), num_axes)
    ##     ax_top = ax_bottom + ax_height
    ##     ax = {}

    ##     for i in range(num_axes - self.sensor_data.loaded):
    ##         ax[i] = fig.add_axes([ax_left, ax_bottom[i], ax_width, ax_height])
    ##         ax[i].plot(self.log_data.time - self.log_data.time[0],
    ##                    self.log_data.data[self.selected_params[i]])
    ##         ax[i].set_ylabel(self.selected_params[i].replace('_', ' '))

    ##     i = num_axes - 1
    ##     if self.sensor_data.loaded:
    ##         ax[i] = fig.add_axes([ax_left, ax_bottom[i], ax_width, ax_height])
    ##         for j in range(len(self.selected_channels)):
    ##             ax[i].plot(self.sensor_data.time,
    ##                        self.sensor_data.data[self.selected_channels[j]] \
    ##                        * self.selected_channels_gains[j],
    ##                        label=self.selected_channels[j].replace('_', ' '))
    ##         ax[i].set_xlabel('Time (s)')
    ##         ax[i].set_ylabel('Sensor Current (nA)')
    ##         ax[i].legend(loc='best')
    ##     fig.show()

    def start(self):
        self.configure_traits(view=main_view)

if __name__ == '__main__':
    f = calterm_data_viewer()
    f.start()

import numpy as np
from os.path import abspath, basename
from os import curdir

from traits.api \
     import Bool, Button, DelegatesTo, Dict, File, Float, HasTraits, \
     Instance, List, Property, String

from traitsui.api \
     import CancelButton, Group, Item, ListEditor, \
     OKButton, SetEditor, StatusItem, View, ListStrEditor

from chaco.api \
     import ArrayPlotData, Plot

from Calterm_III_tools \
     import open_DAQ_file

## Main view is the primary application window called from command
## line initiation.
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
                Item('ds_details_button',
                     label='Data Source Details...',
                     show_label=False,
                     enabled_when='selected_data_source is not None'),
                Item('ch_details_button',
                     label='Ch. Details...',
                     show_label=False,
                     enabled_when='selected_data_source is not None'),
                orientation='vertical'),
            orientation='horizontal'),
        orientation="vertical"),
    title="Calterm III data alignment and analysis",
    height=500,
    width=450,
    buttons=[OKButton])

## channels_view = View(
##     Item(name='selected_channels',
##          show_label=False,
##          style='custom',
##          editor=SetEditor(
##              name='channels',
##              ordered=True,
##              can_move_all=True,
##              left_column_title="Available channels",
##              right_column_title="Channels to plot")),
##     title="Select channels to plot",
##     buttons=[OKButton, CancelButton])

## Channel edit view is called from the main view when the Channel details
## button is selected.
channel_edit_sub_view = View(
    Group(
        ## Item(name="name"),
        Item(name="display_name"),
        Item(name="gain"),
        Item(name="units"),
        orientation="vertical"))

ch_details_view = View(
    Item(name='selected_channels',
         show_label=False,
         style='custom',
         editor=ListEditor(
             use_notebook=True,
             deletable=True,
             page_name='.name',
             view=channel_edit_sub_view
             ),
         resizable=True),
    title="Edit details for each channel",
    resizable=True,
    buttons=[OKButton, CancelButton])

ds_details_view = View(
    Group(
        Item(name="file_name",
             label='file',
             style='readonly'),
        Item(name="name", label='data source name'),
        Item(name="collapsed", label='collapse plots'),
        Item(name='selected_channels',
             show_label=False,
             style='custom',
             editor=SetEditor(
                 name='channels',
                 ordered=True,
                 can_move_all=True,
                 left_column_title="Available channels",
                 right_column_title="Channels to plot")),
        orientation="vertical"),
    title="Edit data source details.",
    buttons=[OKButton, CancelButton])


class Channel(HasTraits):
    """
    Display information about the channels contained in a data source:
    name - (read-only) name to use to reference the array in a_p_data
    display_name - name to display on plots
    gain - a float value to apply to the selected channel
    units - units will be displayed in parentheses on the y-axis after
            display_name
    """

    def __repr__(self):
        return self.name
    name = String
    display_name = String
    gain = Float
    units = String


class DataSource(HasTraits):
    '''
    data source containing a filename, an ArrayPlotData structure for
    plotting in Chaco
    '''
    a_p_data = Instance(ArrayPlotData)
    file_name = File
    channel_names = Property
    selected_channels = List(Channel)
    channels = List(Channel)
    collapsed = Bool(False)
    name = String

    def __init__(self, **kwargs):
        filename = kwargs.get('file_name', '')
        if filename:
            self.load_file(filename)
        self.file_name = filename
        self.name = basename(filename)

    def _a_p_data_default(self):
        return ArrayPlotData()

    def __repr__(self):
        return self.name

    def _get_channel_names(self):
        return self.a_p_data.arrays.keys()

    def load_file(self, filename):
        time, data, units, err = open_DAQ_file(filename)
        if not err:
            self.a_p_data.set_data('time', time)
            for name in data.dtype.names:
                self.a_p_data.set_data(name, data[name])
            #for name in self.channel_names:
                if units is not None:
                    ch_units = units['name']
                else:
                    ch_units = ''
                temp_chan = Channel(
                    name=name,
                    display_name=name,
                    gain=1.0,
                    units=ch_units)
                self.channels.append(temp_chan)
        else:
            print "Deal with the error here."


class calterm_data_viewer(HasTraits):
    """
    This is the user interface for plotting results from data acquisition
    supplemented with log file data from Calterm III, the Cummins ECM
    interface application. The UI is built with Enthought's Traits and
    TraitsUI 
    """
    ## UI elements
    add_source_button = Button()
    align_button = Button()
    ds_details_button = Button()
    ## channel_select_button = Button()
    delete_button = Button()
    ch_details_button = Button()
    plot_button = Button()
    save_button = Button()

    #channel_names = DelegatesTo('selected_data_source')

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

    ## def _channel_select_button_fired(self):
    ##     self.selected_data_source.edit_traits(view=channels_view)

    def _ch_details_button_fired(self):
        self.selected_data_source.edit_traits(view=ch_details_view)

    def _ds_details_button_fired(self):
        self.selected_data_source.edit_traits(view=ds_details_view)

    def _plot_button_fired(self):
        import matplotlib as mpl
        import matplotlib.pyplot as plt

        pad = 0.05
        fig_width = 8.5
        ax_left = 0.18
        ax_width = 0.75

        #Count how many axes need to be plotted
        num_axes = 0 
        for ds in self.data_source_list:
            if ds.collapsed:
                num_axes += 1
            else:
                num_axes += len(ds.selected_channels)
        print "num axes = " + str(num_axes)

        fig_height = 11   ## 2. * num_axes + 1.5
        fig = plt.figure(1, figsize=[fig_width, fig_height])
        fig.clf()

        #calculate the geometry for displaying the axes
        total_pad = pad * (num_axes + 1)
        ax_height = (1. - total_pad) / num_axes
        ax_bottom = np.linspace(pad, 1. - (ax_height + pad), num_axes)
        ax_top = ax_bottom + ax_height
        ax = []
        i = -1
        for ds in self.data_source_list:
            time = ds.a_p_data['time'] - ds.a_p_data['time'][0]
            isFirst = True
            for ch in ds.selected_channels:
                if isFirst or not ds.collapsed:
                    i += 1
                    ax.append(fig.add_axes([ax_left, ax_bottom[i],
                                            ax_width, ax_height]))
                    ax[i].set_xlabel('Time (s)')
                    ax[i].set_ylabel(ch.display_name)
                    ax[i].legend(loc='best')
                    isFirst = False
                ax[i].plot(time, ds.a_p_data[ch.name],
                           label=ch.display_name)


        fig.show()

    def start(self):
        self.configure_traits(view=main_view)

if __name__ == '__main__':
    f = calterm_data_viewer()
    f.start()

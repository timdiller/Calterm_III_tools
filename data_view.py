import numpy as np
from os.path import abspath, basename
from os import curdir

from traits.api \
     import Bool, Button, File, Float, HasTraits, Instance, List, \
     Property, String
from traitsui.api \
     import CancelButton, Group, Item, ListEditor, OKButton, SetEditor, \
     StatusItem, View, ListStrEditor
from chaco.api \
     import ArrayPlotData, Plot

from Calterm_III_tools \
     import open_DAQ_file

class Channel(HasTraits):
    name = String
    unit = String
    gain = Float(1.0)

#class Channel(Parameter):


class DataSource(HasTraits):
    '''
    data source containing a filename, an ArrayPlotData structure for
    plotting in Chaco
    '''
    a_p_data = ArrayPlotData()
    file_name = File()

    ## channels = List(Channel)
    ## channels_disp = List
    ## channel_names = Property(List(String), depends_on=['channels'])
    ## channel_units = Property(List(String), depends_on=['channels'])

    ## channels = List(Channel)
    ## channel_names = Property(List(String), depends_on=['channels'])
    ## channel_gains = Property(List(String), depends_on=['channels'])
    ## selected_channels = List
    ## selected_channels_gains = Property(List(Float),
    ##                                    depends_on=['selected_channels'])


    def __repr__(self):
        return basename(self.file_name)

    def _get_channel_names(self):
        return [n.name for n in self.parameters]

    ## def _get_parameter_units(self):
    ##     return [n.unit for n in self.parameters]

    ## def _get_channel_names(self):
    ##     return [n.name for n in self.channels]

    ## def _get_channel_gains(self):
    ##     return [n.gain for n in self.channels]

    ## def _channel_gains_changed(self):
    ##     print "setting gains.\n"
    ##     print self.channel_gains
    ##     for n in range(self.channel_gains):
    ##         self.channels[n].gain = channel_gains[n]

    ## def _get_selected_channels_gains(self):
    ##     return [self.channel_gains[self.channel_names.index(n)]
    ##             for n in self.selected_channels]

    def _file_name_changed(self, filename):
        time, data, err = open_DAQ_file(filename)
        if not err:
            self.a_p_data.set_data('time',time)
            for name in data.dtype.names:
                self.a_p_data.set_data(name,data[name])
        else:
            print "Deal with the error here."
            ##self.log_data.loaded = False

                #def _data_file_changed(self):
        ## from os.path import splitext
        ## DEFAULT_GAIN = 1.875  ## nA/V
        ## DEFAULT_UNIT = 'nA'

        ## [self.sensor_data.time, self.sensor_data.data] = \
        ##                         fileopen[splitext(self.data_file)[1]]()
        ## for i in self.sensor_data.data.dtype.names:
        ##     self.channels.append(Channel(name=i,
        ##                                  gain=DEFAULT_GAIN,
        ##                                  unit=DEFAULT_UNIT))
        ## self.sensor_data.loaded = True
        ## self.configure_traits(view='channel_view')


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

    file_to_open = File(value=abspath(curdir))

    data_source_list = List(Instance(DataSource))

    main_view = View(
        Group(
            Group(
                Item(name='data_source_list',
                     style='readonly',
                     show_label=False,
                     editor=ListStrEditor()),
                Group(
                    Item('delete_button',
                         label='Delete',
                         show_label=False),
                    Item('channel_select_button',
                         label='Channels...',
                         show_label=False),
                    Item('gain_set_button',
                         label='Gains...',
                         show_label=False),
                    orientation='vertical'),
                orientation='horizontal'),
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
            orientation="vertical"),
        title="Calterm III data alignment and analysis",
        height=500,
        width=450,
        buttons=[OKButton])

    file_open_view = View(Item(name='file_to_open',
                               style='simple',
                               show_label=False),
                          buttons=[OKButton, CancelButton])

#    def _file_to_open_changed(self):
    def _add_source_button_fired(self):
        #self.configure_traits(view='file_open_view')
        if self.file_to_open == '':
            return
        d_s = DataSource(file_name=self.file_to_open)
        self.data_source_list.append(d_s)
#        self.file_to_open = ''


##     parameter_view = View(
##         Item(name='selected_params',
##              show_label=False,
##              style='custom',
##              editor=SetEditor(name='parameter_names',
##                               ordered=True,
##                               can_move_all=True,
##                               left_column_title="Available parameters",
##                               right_column_title="Parameters to plot")),
##         title="Select parameters to plot",
##         buttons=[OKButton, CancelButton])

##     channel_view = View(
##         Item(name='selected_channels',
##              show_label=False,
##              style='custom',
##              editor=SetEditor(name='channel_names',
##                               ordered=True,
##                               can_move_all=True,
##                               left_column_title="Available channels",
##                               right_column_title="Channels to plot")),
##         title="Select channels to plot",
##         buttons=[OKButton, CancelButton])

##     gains_view = View(
##         Item(name='channels',
##              style='custom',
## #             editor=TableEditor()),
##              editor=ListEditor(use_notebook=True)),
##         title="Set the gains for each channel",
##         buttons=[OKButton, CancelButton])

    ## def _param_select_button_fired(self):
    ##     self.configure_traits(view='parameter_view')

    ## def _channel_select_button_fired(self):
    ##     self.configure_traits(view='channel_view')

    ## def _gain_set_button_fired(self):
    ##     self.configure_traits(view='gains_view')

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
        self.configure_traits(view='main_view')

if __name__ == '__main__':
    f = calterm_data_viewer()
    f.start()

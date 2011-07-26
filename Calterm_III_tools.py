
import numpy as np

from traits.api \
    import HasTraits, Float, Bool, String, List, Property, File, \
    Button, Str
from traitsui.api \
    import View, Group, Item, OKButton, CancelButton, SetEditor, \
    ListEditor, StatusItem
#from enthought.chaco.api import * #Plot, ArrayPlotData, jet
#from enthought.enable.api import *
#from enthought.chaco.tools.api import *
##import wx
import matplotlib as mpl
import matplotlib.pyplot as plt
##mpl.use('WXAgg',warn=False)

def convert_date(date_str):
    '''
    Converter function for the genfromtxt import. Return a float in decimal
    seconds from a "DLA_Timestamp" of the form hh:mm:ss.ssss.
    The first instance is passed a string of "1" so a check is necessary
    before splitting the string.
    '''
    d = date_str.split(':')
    if len(d) > 2:
        return 3600.*float(d[0]) + \
               60.*float(d[1]) + \
               float(d[2])
    else:
        return float(d)
def check_calterm_log_file_format(filename):
    '''
    Check to be sure the provided file has the proper format.
    Calterm III log files typically have the following header:
    
    Log File Version ,2.3
    6/16/2011 2:28:03 PM
    Log Mode ,Log When Any Data Received
    ,CaltermVersion,3.2.0.023
    ,ScreenMonitorType,RequestReceive
    ,Initial Monitor Rate,1 Milliseconds
    --------------------------
    Parameter Name, ...
    Units, ...
    Source Address, ...
    '''
    f = open(filename)
    header_first_word = []
    for i in range(11):
        header_first_word.append(f.readline().split(',')[0])
    f.close()

    if header_first_word[7:10] == ['Parameter Name','Units','Source Address']:
        err = None
    else:
        err = "File not written by Calterm III. Try *.log.csv file"
        print err
        print header_first_word
    return err


def import_calterm_log_parameter_names(filename):
    '''
    Read the Calterm III log file and return parameter names and units as a
    comma separated string - the form useful for genfromtxt().
    To use the names as a list use n.split(",").
    '''
    f = open(filename)
    header = []
    for i in range(7):
        f.readline()
    names_raw = f.readline()
    units_raw = f.readline()
    f.close()
    return [names_raw.strip('\r\n'), units_raw.strip('\r\n')]

def import_calterm_log_file(filename):
    '''
    Open a comma-separated-variable file output by Cummins Calterm III
    software and return a time arrary and a structured, named array for the other
    parameters.
    The Calterm III log file has 10 header lines. The variable names are given
    on the 8th line, the units on the 9th, and the memory address on the 10th.
    The returned result is an ndarray with named dtypes. The columns can be
    accessed as expected:

    l["DLA_Timestamp"] - this column appears in every log file
    l["Engine_Speed"] - a useful piece of information
    etc.
    '''
    
    err = check_calterm_log_file_format(filename)
    if err:
        print err
        return [None, None, err]
    else:
        f = open(filename)
        data = np.genfromtxt(f, delimiter=',',
                             unpack=True,
                             skip_header=10,
                             usecols=range(1,38),
                             names=import_calterm_log_parameter_names(filename)[0],
                             converters={1:convert_date})
        f.close()
        if 'DLA_Timestamp' in data.dtype.names:
            return [data['DLA_Timestamp'], data, err]
        else:
            print "DLA_Timestamp not found. Parameters found include the following:"
            print data.dtype.names

class Parameter(HasTraits):
    name = String
    unit = String

class Channel(Parameter):
    gain = Float

class Data(HasTraits):
    loaded = Bool(False)
    data = np.asarray([])
    time = np.asarray([])
        
class calterm_data_viewer(HasTraits):
    """
    This is the user interface for plotting results from data acquisition
    supplemented with log file data from Calterm III, the Cummins ECM
    interface application. The UI is built with Enthought's Traits and TraitsUI
    """

    parameters = List(Parameter)
    selected_params = List
    parameter_names = Property(List(String), depends_on=['parameters'])
    parameter_units = Property(List(String), depends_on=['parameters'])
    def _get_parameter_names(self):
        return [n.name for n in self.parameters]
    def _get_parameter_units(self):
        return [n.unit for n in self.parameters]

    channels = List(Channel)
    channel_names = Property(List(String), depends_on=['channels'])
    channel_gains = Property(List(String), depends_on=['channels'])
    selected_channels = List
    selected_channels_gains = Property(List(Float), depends_on=['selected_channels'])
    def _get_channel_names(self):
        return [n.name for n in self.channels]
    def _get_channel_gains(self):
        return [n.gain for n in self.channels]
    def _channel_gains_changed(self):
        print "setting gains.\n"
        print self.channel_gains
        for n in range(self.channel_gains):
            self.channels[n].gain = channel_gains[n]
    def _get_selected_channels_gains(self):
        return [self.channel_gains[self.channel_names.index(n)] for n in self.selected_channels]
    
    ## UI elements
    align_button = Button()
    plot_button = Button()
    save_button = Button()
    
    param_select_button = Button()
    channel_select_button = Button()
    gain_set_button = Button()

    sensor_data = Data()
    log_data = Data()
    
    data_file = File(filter = ['csv'])
    log_file = File(filter = ['csv'])

    data_file_status = Str('none loaded')
    log_file_status = Str('none loaded')

    # The text being edited:
    text = Str

    # The current length of the text being edited:
    length = Property( depends_on = 'text' )

    # The current time:
    time = Str

    main_view = View(
        Group(
            Group(
                Group(
                    Item(name = 'data_file',
                         style = 'simple'),
                    Item('channel_select_button',
                         label = 'Ch. Select',
                         show_label = False),
                    Item('gain_set_button',
                         label = 'Gain Set',
                         show_label = False),
                    orientation = 'horizontal'),
                Group(
                    Item(name='log_file',
                         style='simple'),
                    Item('param_select_button',
                         label='Parameter Select',
                         show_label=False),
                    orientation='horizontal'),
                orientation='vertical'),
            Group(
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
        statusbar = [StatusItem(name = 'data_file_status', width=85),
                     StatusItem(name = 'log_file_status', width=85)],
        title = "Calterm III data alignment and analysis",
        buttons = [OKButton])

    parameter_view = View(
        Item(name='selected_params',
             show_label=False,
             style='custom',
             editor=SetEditor(name='parameter_names',
                              ordered=True,
                              can_move_all=True,
                              left_column_title="Available parameters",
                              right_column_title="Parameters to plot")),
        title = "Select parameters to plot",
        buttons = [OKButton, CancelButton])

    channel_view = View(
        Item(name='selected_channels',
             show_label=False,
             style='custom',
             editor=SetEditor(name='channel_names',
                              ordered=True,
                              can_move_all=True,
                              left_column_title="Available channels",
                              right_column_title="Channels to plot")),
        title = "Select channels to plot",
        buttons = [OKButton, CancelButton])

    gains_view = View(
        Item(name='channels',
             style='custom',
#             editor=TableEditor()),
             editor=ListEditor(use_notebook=True)),
        title = "Set the gains for each channel",
        buttons = [OKButton, CancelButton])

    def _log_file_changed(self):
        [self.log_data.time, self.log_data.data, err] = import_calterm_log_file(self.log_file)
        if not err:
            self.log_data.loaded = True
            [p,u] = import_calterm_log_parameter_names(self.log_file)
            p_raw = p.split(',')
            u_raw = u.split(',')
            self.parameters = []
            for i in range(len(p_raw)):
                self.parameters.append(Parameter(name=p_raw[i], unit=u_raw[i]))
            self.configure_traits(view='parameter_view')
        else:
            print "Deal with the error here."
            self.log_data.loaded = False

    def _param_select_button_fired(self):
        self.configure_traits(view='parameter_view')

    def _channel_select_button_fired(self):
        self.configure_traits(view='channel_view')

    def _gain_set_button_fired(self):
        self.configure_traits(view='gains_view')

    def _data_file_changed(self):
        from os.path import splitext
        DEFAULT_GAIN = 1.875 #nA/V
        DEFAULT_UNIT = 'nA'

        def npz_open():
            npz = np.load(self.data_file)
            return([npz['time'], npz['data']])
            
        def csv_open():
            import re
            f = open(self.data_file)
            date_str = f.readline()
            step_str = f.readline()
            [a,b] = re.split("=",step_str.strip('\r\n'))
            step = float(b)
            del a,b
            data = np.genfromtxt(f,delimiter=',', unpack=True, names=True)
            f.close()
            length  = data.shape[0]
            time = np.linspace(0,step * (length - 1),length)
            return([time, data])

        fileopen = {'.npz':npz_open,
                    '.csv':csv_open,
                    }
        [self.sensor_data.time, self.sensor_data.data] = fileopen[splitext(self.data_file)[1]]()
        for i in self.sensor_data.data.dtype.names:
            self.channels.append(Channel(name=i, gain=DEFAULT_GAIN, unit=DEFAULT_UNIT))
        self.sensor_data.loaded = True
        self.configure_traits(view='channel_view')

    def _plot_button_fired(self):
        pad = 0.05
        fig_width = 8.5
        ax_left = 0.18
        ax_width = 0.75
        
        #Count how many axes need to be plotted
        num_axes = 0 + self.sensor_data.loaded
        if self.log_data.loaded:
            num_axes += len(self.selected_params)
        if not(num_axes):
            print "No files loaded or no parameters selected.\n"
            return
        
        fig_height = 11# 2. * num_axes + 1.5
        fig = plt.figure(1, figsize=[fig_width, fig_height])
        fig.clf()

        #calculate the geometry for displaying the axes
        total_pad = pad * (num_axes + 1)
        ax_height = (1. - total_pad) / num_axes
        ax_bottom = np.linspace(pad, 1. - (ax_height + pad), num_axes)
        ax_top = ax_bottom + ax_height
        ax = {}

        for i in range(num_axes - self.sensor_data.loaded):
            ax[i] = fig.add_axes([ax_left, ax_bottom[i], ax_width, ax_height])
            ax[i].plot(self.log_data.time - self.log_data.time[0],
                       self.log_data.data[self.selected_params[i]])
            ax[i].set_ylabel(self.selected_params[i].replace('_', ' '))
            #ax[i].set_ylabel(self.selected_param

        i = num_axes-1
        if self.sensor_data.loaded:
            ax[i] = fig.add_axes([ax_left, ax_bottom[i], ax_width, ax_height])
            for j in range(len(self.selected_channels)):
                ax[i].plot(self.sensor_data.time,
                           self.sensor_data.data[self.selected_channels[j]] * self.selected_channels_gains[j],
                           label=self.selected_channels[j].replace('_', ' '))
            ax[i].set_xlabel('Time (s)')
            ax[i].set_ylabel('Sensor Current (nA)')
            ax[i].legend(loc='best')

    def start(self):
        self.configure_traits(view='main_view')

if __name__ == '__main__':
    f=calterm_data_viewer()
    f.start()

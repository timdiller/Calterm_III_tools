import numpy as np

from enthought.traits.api import * 
from enthought.traits.ui.api import * #View,Group,Item
from enthought.traits.ui.menu import OKButton,CancelButton
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

def import_calterm_log_parameter_names(filename):
    '''
    Read the Calterm III log file and return parameter names and units as a
    comma separated string - the form useful for genfromtxt().
    To use the names as a list use n.split(",").
    '''
    f = open(filename)
    for i in range(7):
        f.readline()
    names_raw = f.readline()
    units_raw = f.readline()
    f.close()
    return [names_raw.strip('\r\n'), units_raw.strip('\r\n')]

def import_calterm_log_file(filename):
    '''
    Open a comma-separated-variable file output by Cummins Calterm III
    software and return a structured, named array for analysis.
    The Calterm III log file has 10 header lines. The variable names are given
    on the 8th line, the units on the 9th, and the memory address on the 10th.
    The returned result is an ndarray with named dtypes. The columns can be
    accessed as expected:

    l["DLA_Timestamp"] - this column appears in every log file
    l["Engine_Speed"] - a useful piece of information
    etc.
    '''
    
    f = open(filename)
    l = np.genfromtxt(f, delimiter=',',
                      unpack=True,
                      skip_header=10,
                      usecols=range(1,38),
                      names=import_calterm_log_parameter_names(filename)[0],
                      converters={1:convert_date})
    f.close()
    return l

class Parameter(HasTraits):
    name = String
    unit = String

class Data(HasTraits):
    filename = File()
    loaded = Bool(False)
    data = np.asarray([])
    time = np.asarray([])
        
class calterm_data_viewer(HasTraits):
    """
    """

    ## from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
    ## from matplotlib.figure import Figure
    ## from matplotlib.backends.backend_wx import NavigationToolbar2Wx

    parameters = List(Parameter)
    selected_params = List
    parameter_names = Property(List(String), depends_on=['parameters'])

    def _get_parameter_names(self):
        return [n.name for n in self.parameters]
    
    ## UI elements
    align_button = Button()
    plot_button = Button()
    save_button = Button()
    
    load_data_button = Button()
    load_log_button = Button()
    
    data_file = File(filter = ['csv'])
    log_file = File(filter = ['csv'])

    main_view = View(
        Group(
            Group(
                Group(
                    Item(name = 'data_file',
                         style = 'simple'),
                    ## Item('load_data_button',
                    ##      label = 'Load',
                    ##      show_label = False),
                    orientation = 'horizontal'),
                Group(
                    Item(name='log_file',
                         style='simple'),
                    ## Item('load_log_button',
                    ##      label='Load',
                    ##      show_label=False),
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
        buttons = [OKButton])

#    def _load_log_button_fired(self):
    def _log_file_changed(self):
        [p,u] = import_calterm_log_parameter_names(self.log_file)
        p_raw = p.split(',')
        u_raw = u.split(',')
        self.parameters = []
        for i in range(len(p_raw)):
            self.parameters.append(Parameter(name=p_raw[i],unit=u_raw[i]))
        self.configure_traits(view='parameter_view')
        self.log = import_calterm_log_file(self.log_file)

    def _data_file_changed(self):
        from os.path import splitext

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
            time = np.arange(0,step*length,step)
            return([time, data])

        fileopen = {'.npz':npz_open,
                    '.csv':csv_open,
                    }
        [self.time, self.data] = fileopen[splitext(self.data_file)[1]]()

    def _plot_button_fired(self):
        fig = plt.figure(1)
        plt.plot(self.time,self.data[self.data.dtype.names[0]])

    def start(self):
        self.configure_traits(view='main_view')

if __name__ == '__main__':
    f=calterm_data_viewer()
    f.start()

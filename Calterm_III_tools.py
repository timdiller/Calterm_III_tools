import numpy as np

from enthought.traits.api import * 
from enthought.traits.ui.api import * #View,Group,Item
from enthought.traits.ui.menu import OKButton,CancelButton
from enthought.chaco.api import * #Plot, ArrayPlotData, jet
from enthought.enable.api import *
from enthought.chaco.tools.api import *
import numpy as np
##import wx
##import matplotlib as mpl
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
    Read the Calterm III log file and return line 8 in a form useful for
    genfromtxt().
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
        
class calterm_data_viewer(HasTraits):
    """
    """

    ## from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
    ## from matplotlib.figure import Figure
    ## from matplotlib.backends.backend_wx import NavigationToolbar2Wx

    parameters = List(Parameter)
    parameter_names = Property(List(String), depends_on=['parameters'])
    my_params = List

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

    view1 = View(
        Group(
            Group(
                Group(
                    Item(name = 'data_file',
                         style = 'simple',
                         editor = FileEditor()),
                    Item('load_data_button',
                         label = 'Load',
                         show_label = False),
                    orientation = 'horizontal'),
                Group(
                    Item(name='log_file',
                         style='simple',
                         editor=FileEditor()),
                    Item('load_log_button',
                         label='Load',
                         show_label=False),
                    orientation='horizontal'),
                Item(name='my_params',
                     show_label=False,
                     style='simple',
                     editor=SetEditor(name='parameter_names',
                                      can_move_all=True,
                                      left_column_title="Available parameters",
                                      right_column_title="Parameters to plot")),
                orientation='vertical'),
            Group(
                Item(name='align_button'),
                Item(name='plot_button'),
                Item(name='save_button'),
                orientation="vertical"),
            orientation="horizontal"),
        title = "Calterm III data alignment and analysis",
        buttons = [OKButton])

    def __init__(self):
        """
        need to change this to offer a load dialog on startup. for
        development and debugging, just load the data from an npz
        save file.

        axes are added to the figure here under the handle self.axes.
        
        """
        p1 = Parameter(name="parameter 1", unit="unit1")
        p2 = Parameter(name="parameter 2")
        p3 = Parameter(name="parameter 3")
        
        self.parameters=[p1, p2, p3]

    def start(self):
        self.configure_traits()

if __name__ == '__main__':
    f=calterm_data_viewer()
    f.start()

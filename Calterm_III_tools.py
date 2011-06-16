import numpy as np

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
    
def import_calterm_log_file(filename):
    '''
    Open a comma-separated-variable file output by Cummins Calterm III
    software and return a structured, named array for analysis.
    The Calterm III log file has 10 header lines. The variable names are given
    on the 8th line, the units on the 9th, and the memory address on the 10th.
    '''
    
    f_l = open(filename)
    names_raw = f_l.readlines()[7]
    f_l.seek(0)
    l = np.genfromtxt(f_l, delimiter=',',
                      unpack=True,
                      skip_header=10,
                      usecols=range(1,38),
                      names=names_raw.strip('\r\n'),
                      converters={1:convert_date})
    f_l.close()
    return l


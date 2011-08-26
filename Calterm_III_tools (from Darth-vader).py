def convert_DLA(date_str):
    '''
    Converter function for the genfromtxt import. Return a float in decimal
    seconds from a "DLA_Timestamp" of the form hh:mm:ss.ssss.
    The first instance is passed a string of "1" so a check is necessary
    before splitting the string.
    '''
    d = date_str.split(':')
    if len(d) > 2:
        return 3600. * float(d[0]) + \
               60. * float(d[1]) + \
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
    file_pointer = open(filename)
    header_first_word = []
    for i in range(11):
        header_first_word.append(file_pointer.readline().split(',')[0])
    file_pointer.close()

    if header_first_word[7:10] == ['Parameter Name',
                                   'Units', 'Source Address']:
        err = None
    else:
        err = "File not written by Calterm III. Try *.log.csv file"
        print err
        print header_first_word
    return err


def import_calterm_log_param_names(filename):
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
    software and return a time arrary and a structured, named array
    for the other parameters.
    The Calterm III log file has 10 header lines. The variable names are given
    on the 8th line, the units on the 9th, and the memory address on the 10th.
    The returned result is an ndarray with named dtypes. The columns can be
    accessed as expected:

    l["DLA_Timestamp"] - this column appears in every log file
    l["Engine_Speed"] - a useful piece of information
    etc.
    '''
    import numpy as np

    err = check_calterm_log_file_format(filename)
    if err:
        print err
        return [None, None, err]
    else:
        f = open(filename)
        data = np.genfromtxt(f, delimiter=',',
                unpack=True,
                skip_header=10,
                usecols=range(1, 38),
                names=import_calterm_log_param_names(filename)[0],
                converters={1: convert_DLA})
        f.close()
        if 'DLA_Timestamp' in data.dtype.names:
            return [data['DLA_Timestamp'], data, err]
        else:
            err = "DLA_Timestamp not found. Parameters found include" \
                  "the following:"
            print err, data.dtype.names
            return [None, None, err]



import pandas as pd
import os
import re
import numpy as np

file_name = 'Solar.fmf'
# file_name = 'Faraday.fmf'
file_name = 'Dynamik-Numerik-Drift.fmf'

def readFMF(file_name, returnMeta = False):
    '''
    Function reads in a fmf file and returns pandas.dataframe

    Note: only works if files in in same folder,

    Author:Michael Zhang - UoA
    Date: 10-02-2019
    :param file_name: String, filename of the file to be read, - including the .fmf extention.
    :param returnMeta: Boolean, to return dictionary of the metadata or not.
    :return: dataframe of the data located inside the fmffiles.
    '''

    # Patterns for regular expressions
    pat_general_header = '\[(.*)\]'
    pat_data_header = '\[\*data(.*?)\]'
    pat_dictionary = "(.*?)\: (.*)"
    pat_table_def = '\[\*table definitions\]'
    pat_comment = "\A(;)"

    # Paths to files and folders
    path_module = os.path.dirname(os.path.abspath(file_name))
    path_file = path_module + '/' + file_name
    path_temp_file = path_module +  '/' + 'temp' + file_name

    # Open file
    # the code could be changed to read as is to save memory
    with open(path_file, "r") as file_handle_read:
        file_contents = file_handle_read.readlines()
    file_handle_read.close()

    # Remove comments
    file_contents_filtered = []
    file_handle_write = open(path_temp_file, "w+")

    for lnum, line in enumerate(file_contents):
        if re.match(pat_comment, str.lower(line)):
            continue
        else:
            file_handle_write.write(line)
            file_contents_filtered.append(line)
    file_handle_write.close()

    isMultiple = False  # does the file contains multiple tables?
    lnum_data_headers = []
    dict_headers = {}

    for lnum, line in enumerate(file_contents_filtered):
        if re.match(pat_general_header, str.lower(line)):
            # Finds headers
            mm = re.match(pat_general_header, str.lower(line))
            # Assigns some intermediate data
            lnum_data_headers.append(lnum)
            dict_headers[mm[1]] = {'line_number': lnum}
            dict_headers[mm[1]].update({'header_number': len(lnum_data_headers)})
            current_header = mm[1]
            if re.match(pat_table_def, str.lower(line)):
                isMultiple = True
            continue

        if re.match(pat_dictionary, str.lower(line)):
            # Finds the dicitonary key value pairs
            mm = re.match(pat_dictionary, str.lower(line))
            # Adds them to the dictionary
            dict_headers[current_header][mm[1]] = mm[2]

    lnum_data_headers.append(lnum + 1)
    len_sections = np.diff(lnum_data_headers)  # length of each section

    list_data = []

    if isMultiple:
        num_tables = dict_headers['*table definitions'].__len__() - 2
        table_keys = list(dict_headers['*table definitions'].keys())

        for table in range(num_tables):
            table_symbol = dict_headers['*table definitions'][table_keys[table + 2]]
            pat_data_header_symbol = '\[\*data\: ' + table_symbol + '\]'
            for lnum, line in enumerate(file_contents_filtered):
                if re.match(pat_data_header_symbol, str.lower(line)):
                    column_names = list(dict_headers['*data definitions: ' + table_symbol].keys())
                    startline = dict_headers['*data: ' + table_symbol]['line_number'] + 1
                    nrows = len_sections[dict_headers['*data: ' + table_symbol]['header_number'] - 1] - 1
                    list_data.append(pd.read_csv(path_temp_file, names=column_names[2:], skiprows=startline, nrows = nrows, delimiter='\t'))
    else: #if single table
        for lnum, line in enumerate(file_contents_filtered):
            if re.match(pat_data_header, str.lower(line)):
                # Finds the data header
                mm = re.match(pat_data_header, str.lower(line))
                if(mm[1] == ''):
                    # if not the data definintions one
                    column_names = list(dict_headers['*data definitions'].keys())
                    startline = dict_headers['*data']['line_number'] + 1
                    nrows = len_sections[dict_headers['*data']['header_number'] - 1] - 1
                    # Save to df
                    list_data = pd.read_csv(path_temp_file, names =column_names[2:], skiprows=startline, nrows = nrows, delimiter='\t')

    os.remove(path_temp_file)

    if returnMeta:
        return list_data, dict_headers
    else:
        return list_data


print(readFMF(file_name, 1))
# print(lnum_data_headers)
# print(dict_headers)

import pandas as pd
import os
import re

### Paths to files and folders
path_module = os.path.dirname(os.path.abspath(__file__))
path_project = os.path.normpath(os.path.join(path_module, '..'))

name_file = 'Solar.fmf'
# name_file = 'Faraday.fmf'

path_folder = os.path.join(path_project, ('quantities/'))
path_file = path_folder + name_file
print(path_file)

### Open, read in save, and close
# the code could be changed to read as is to save memory - probably not an issue nowdays.
with open(path_file, "r") as file_handle:
    file_contents = file_handle.readlines()
file_handle.close()
# print(len(file_contents))

### Patterns for regular expressions
pat_general_header = '\[(.*)\]'
pat_data_header = '\[\*data(.*?)\]'
pat_data_def_header = '\[\*data definition(.*?)\]'
pat_dictionary = "(.*?)\: (.*)"
pat_comment = "\A(;)"

# lnum_data_headers = []
dict_headers = {}

for lnum, line in enumerate(file_contents):
    # print(line)
    if re.match(pat_comment, str.lower(line)):
        # Ignores comments
        # print("Comment")
        continue
    if re.match(pat_dictionary, str.lower(line)):
        # Finds the dicitonary key value pairs
        mm = re.match(pat_dictionary, str.lower(line))
        # print(mm[0])
        # print(mm[1])
        # print(mm[2])
        # print('dict')
        # Adds them to the dictionary
        dict_headers[current_header][mm[1]] = mm[2]
    if re.match(pat_general_header, str.lower(line)):
        # Finds headers
        # print('header')
        mm = re.match(pat_general_header, str.lower(line))
        # print(mm[0])
        # print(mm[1])
        dict_headers[mm[1]] = {'line_number': lnum}
        current_header = mm[1]
    if re.match(pat_data_header, str.lower(line)):
        # Finds the data header
        mm = re.match(pat_data_header, str.lower(line))
        # print(mm[1])
        # lnum_data_headers.append(lnum)
        if(mm[1] == ''):
            # if not the data definintions one
            # print('data')
            column_names = list(dict_headers['*data definitions'].keys())
            # print(column_names[1:])
            # Save to df
            df_data = pd.read_csv(path_file, names = column_names[1:], skiprows=lnum + 1, delimiter='\t')
        # print(mm[2])
    # if (line_number == 7):
    #     print('hi')
    #     break

    # data.append(numbers_float[col])

print(lnum)
print(lnum_data_headers)
print(dict_headers)
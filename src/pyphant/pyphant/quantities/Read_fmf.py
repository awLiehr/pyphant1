import pandas as pd
import os
import re

###
path_module = os.path.dirname(os.path.abspath(__file__))
path_project = os.path.normpath(os.path.join(path_module, '..'))


name_file = 'Solar.fmf'
# name_file = 'Faraday.fmf'

path_folder = os.path.join(path_project, ('quantities/'))
path_file = path_folder + name_file
print(path_file)

###
with open(path_file, "r") as file_handle:
    file_contents = file_handle.readlines()
file_handle.close()
print(len(file_contents))

###

lnum_headers = []
lnum_data_headers = []

pat_general_header = '\[(.*)\]'
pat_data_header = '\[\*data(.*?)\]'
pat_dictionary = "(.*?)\: (.*)"
pat_comment = "\A(;)"

dictionary = {}

for lnum, line in enumerate(file_contents):
    # print(line)
    if re.match(pat_comment, str.lower(line)):
        print("Comment")
        continue
    if re.match(pat_dictionary, str.lower(line)):
        mm = re.match(pat_dictionary, str.lower(line))
        # print(mm[0])
        # print(mm[1])
        # print(mm[2])
        # print('dict')
        dictionary[mm[1]] = mm[2]
    if re.match(pat_general_header, str.lower(line)):
        print('header')
        mm = re.match(pat_general_header, str.lower(line))
        # print(mm[0])
        print(mm[1])
        lnum_headers.append(lnum)
    if re.match(pat_data_header, str.lower(line)):
        # print('eh')
        mm = re.match(pat_data_header, str.lower(line))
        # print(mm[0])
        print(mm[1])
        lnum_data_headers.append(lnum)
        if(mm[1] == ''):
            print('data')
            df_data = pd.read_csv(path_file, header = None, skiprows=lnum + 1, delimiter='\t')
        # print(mm[2])
    # if (line_number == 7):
    #     print('hi')
    #     break

    # data.append(numbers_float[col])

print(lnum)
# return data
print(lnum_headers)
print(lnum_data_headers)
print(dictionary)
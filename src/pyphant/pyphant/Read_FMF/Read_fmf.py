from .pint_array import *  # since its not pint 0.10 yet
# import pint

import pandas as pd
import re
import numpy as np


def readFMF(path_file, returnMetaData=False):
    """
    Function reads in a fmf file and returns pandas.dataframe

    Author:Michael Zhang - UoA
    Date: 10-02-2019
    :param path_file: String, filename of the file to be read, - including the .fmf extention.
    :param returnMetaData: Boolean, to return dictionary of the metadata or not.
    :return: dataframe of the data located inside the fmffiles. (if multiple, a list of dataframes)
    :return: (optional) dictionary of the fmffiles metadata.
    """

    file_meta_data = obtainFileMetaData(path_file)

    list_dataframe = fileToDataframe(file_meta_data, path_file)

    if returnMetaData:
        return list_dataframe, file_meta_data
    else:
        return list_dataframe


def obtainFileMetaData(path_file):
    """
    Reads/scans file scrapes meta data and puts into a dictionary

    # Author: Michael Zhang - UoA
    # Date: 10 - 02 - 2019
    :param path_file: String, filename of the file to be read, - including the .fmf extention.
    :return: dictonary
    """

    file_meta_data = {}

    # Open file
    with open(path_file, "r") as file_handle_read:
        file_contents = file_handle_read.readlines()
    file_handle_read.close()

    # read first line
    fmf_version, char_comment, delimiter = preParseData2(file_contents[0])  # from loadFMF

    # enter information from first line
    file_meta_data['file_info'] = {'file_name': path_file,
                                   'fmf_version': fmf_version,
                                   'comment_character': char_comment,
                                   'delimiter': delimiter,
                                   'isMultiple': False}

    # pattern regular expression
    rexpr_comment = re.compile(r"^%s.*" % (char_comment,))
    rexpr_general_header = r'\[(.*)\]'
    rexpr_dictionary = r"(.*?)\: (.*)"
    rexpr_table_def = r'\[\*table definitions\]'

    lnum_data_headers = []

    file_meta_data['file_info']['section_info'] = {}

    # go through the contents of file
    for lnum, line in enumerate(file_contents):
        if re.match(rexpr_comment, line):
            # Skip comments
            try:
                # produces error only if comments exist before first header,
                # but doesn't matter since this fixes the csv_read portion of the code anyway
                file_meta_data['file_info']['section_info'][current_header]['comments'] += 1
            except UnboundLocalError:
                continue
            continue

        if re.match(rexpr_general_header, line, flags=re.IGNORECASE):
            # Finds headers
            m = re.match(rexpr_general_header, line, flags=re.IGNORECASE)

            # Assigns some intermediate data
            lnum_data_headers.append(lnum)
            file_meta_data['file_info']['section_info'][m[1]] = {'line_number': lnum}
            file_meta_data['file_info']['section_info'][m[1]]['comments'] = 0
            file_meta_data[m[1]] = {}
            current_header = m[1]

            # if has more than one table
            if re.match(rexpr_table_def, line, flags=re.IGNORECASE):
                file_meta_data['file_info']['isMultiple'] = True
            continue

        if re.match(rexpr_dictionary, line, flags=re.IGNORECASE):
            # Finds the dicitonary key value pairs
            m = re.match(rexpr_dictionary, line, flags=re.IGNORECASE)

            # Adds them to the dictionary under the right section
            file_meta_data[current_header][m[1]] = m[2]

    lnum_data_headers.append(lnum + 1)

    # Assigns the section length information through the difference between section line numbers.
    len_sections = np.diff(lnum_data_headers)  # length of each section
    for i, x in enumerate(file_meta_data['file_info']['section_info']):
        file_meta_data['file_info']['section_info'][x].update({'length': int(len_sections[i])})

    return file_meta_data


def fileToDataframe(file_meta_data, path_file):
    """
    Function that converts the data from a file (csvread) into a pandas dataframe.
    then turns it into a pintArray (with units)

    Author:Michael Zhang - UoA
    Date: 10-03-2019
    :param file_meta_data: the dictionary of file meta data
    :param path_file: string of path to temporary file (the one without comments)
    :return:
    """

    # if multiple tables
    if file_meta_data['file_info']['isMultiple']:
        list_data = []
        for table_symbol in file_meta_data['*table definitions'].values():
            dataframe = pd.read_csv(path_file,
                                    names=file_meta_data['*data definitions: ' + table_symbol].keys(),
                                    skiprows=file_meta_data['file_info']['section_info']['*data: ' + table_symbol][
                                                 'line_number'] + 1,
                                    nrows=file_meta_data['file_info']['section_info']['*data: ' + table_symbol][
                                              'length'] -
                                          file_meta_data['file_info']['section_info']['*data: ' + table_symbol][
                                              'comments'] - 1,
                                    delimiter=file_meta_data['file_info']['delimiter'],
                                    comment=str(file_meta_data['file_info']['comment_character']),
                                    )
            list_data.append(pintify(dataframe, file_meta_data['*data definitions: ' + table_symbol]))

    else:  # if single table
        # Save to df
        dataframe = pd.read_csv(path_file,
                                names=file_meta_data['*data definitions'].keys(),
                                skiprows=file_meta_data['file_info']['section_info']['*data']['line_number'] + 1,
                                nrows=file_meta_data['file_info']['section_info']['*data']['length'] -
                                      file_meta_data['file_info']['section_info']['*data']['comments'] - 1,
                                delimiter=file_meta_data['file_info']['delimiter'],
                                comment=str(file_meta_data['file_info']['comment_character']),
                                )
        # print(dataframe)

        # Units
        list_data = pintify(dataframe, file_meta_data['*data definitions'])
    return list_data


def pintify(dataframe, file_section_meta_data):
    """
    Function loads in a df with associated label/units and transforms it into a pint datafframe (Pandas Extension Array)

    Reference: https://pint.readthedocs.io/en/latest/pint-pandas.html

    Author:Michael Zhang - UoA
    Date: 10-03-2019
    :param dataframe: dataframe of the data
    :param file_section_meta_data: dictionary of the data labels/headers/units
    :return: PintArray
    :param dataframe:
    :param file_section_meta_data:
    :return:
    """
    # empty string array
    units = np.empty(len(file_section_meta_data), dtype=object)

    for i, n in enumerate(list(file_section_meta_data.values())):
        # finds the units in
        m = re.match(r"(.*)\[(.*)\]", n)
        try:
            units[i] = str(m[2])
        except TypeError:
            units[i] = "dimensionless"

    # dictionary of data series
    dict_series = {}
    for i, name in enumerate(file_section_meta_data.keys()):
        try:
            dict_series.update({name: pd.Series(dataframe[name], dtype=("pint[" + units[i] + "]"))})
        except:
            warnings.warn(units[i] + ' not recognised as a unit in pint, using dimensionless instead')
            dict_series.update({name: pd.Series(dataframe[name], dtype="pint[dimensionless]")})

    # pint array
    array_pint = pd.DataFrame(dict_series)
    return array_pint


def preParseData2(line):
    """
    Obtained and adapted from LoadFMF.py

    :param line: fileline - the first of the fmf file
    :return: infomation about the file.
    """
    localVar = {'fmf-version': '1.1', 'coding': 'utf-8', 'delimiter': '\t'}
    char_comment = ';'
    # if line.startswith(str(codecs.BOM_UTF8)):
    #     line = line.lstrip(str(codecs.BOM_UTF8))
    if line[0] == ';' or line[0] == '#':
        char_comment = line[0]
        items = [var.strip().split(':') for var
                 in line.split('-*-')[1].split(';')]
        try:
            for key, value in items:
                localVar[key.strip()] = value.strip()
                if localVar[key.strip()] == 'whitespace':
                    localVar[key.strip()] = r'\s{1,}'
                if localVar[key.strip()] == 'semicolon':
                    localVar[key.strip()] = ';'
        except ValueError as e:
            from sys import exit
            exit('%s\nPlease, check syntax of headline, presumably a key \
                    and its value are not separated by a colon.' % e)

    return str(localVar['fmf-version']), char_comment, str(localVar['delimiter'])
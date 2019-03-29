from pyphant.Read_FMF.pint_array import *  # since its not pint 0.10 yet


def write_fmf(filename, fmf_version, data, meta_data,
              comment=";", encoding=None, delimiter=None, formatting="%G"):
    """
    Write a fmf file from given inputs
    :param filename: string to save file as
    :param fmf_version: number
    :param data: dataframe of data if single, or dictionary of dataframes with keys as table symbol
            - pintarrays also accepted
    :param meta_data: nested dictionary of sections with key value pairs
    :param comment: string - comment character
    :param encoding: string - encoding
    :param delimiter: string accepts "whitespace", "\t" etc
    :param formatting: string %f syntax if single dataframe or :f syntax if multiple dataframes
    :return: fmf file.
    """
    file_handle = create_file(filename)

    # appends the header/first line to the file
    append_header(file_handle, fmf_version, comment, encoding, delimiter)

    # appends the sections, with section headers and key:value pairs
    append_section(file_handle, meta_data)

    # appends the data
    append_tables(file_handle, data, formatting, delimiter)

    if isinstance(data, dict):
        # check if the keys in data are the same as the values in table definitions
        check_table_symbols(data, meta_data)

    # close file
    file_handle.close()

    return filename


def create_file(filename):
    """
    :param filename: string may contain .fmf or not
    :return: filehandle to the file
    """
    # if a fmf suffix is not specified
    if not (re.search(r"(?i)\.fmf", filename)):
        filename += ".fmf"

    # creates a new file
    filehandle = open(filename, "w+")
    # filehandle.close()
    # filehandle = open(filename, "a")
    return filehandle


def append_header(fh, fmf_version, comment, encoding, delimiter):
    """
    Writes the header line

    :param fh: filehandle
    :param fmf_version: number,
    :param comment: string comment chaaracter
    :param encoding: string
    :param delimiter: string
    """

    if (delimiter == "\t"):
        delimiter = "\\t"

    header_string = comment + " -*- fmf-version: " + str(fmf_version)

    if encoding:
        header_string += "; encoding: " + encoding

    if delimiter:
        header_string += "; delimiter: " + delimiter

    header_string += " -*- \n"
    fh.write(header_string)


def append_section(fh, meta_data):
    """
    appends the section header and corresponding keyvalue pairs

    :param fh: filehandle
    :param meta_data: nested dictionary of sections and keyvalue pairs.
    """
    # check if necessay sections are avaliable
    check_sections(meta_data)

    for section in meta_data:
        sectionheader = "[" + str(section) + "]\n"
        fh.write(sectionheader)
        for k in meta_data[section].keys():
            keyvalue = str(k) + ": " + str(meta_data[section][k]) + "\n"
            fh.write(keyvalue)

    # check whether all the necessary sections are here, *reference, (*table definitions), (*data definintions)


def append_tables(fh, data, formatting, delimiter):
    """
    finds whether it is a single dataframe or multiple before appends dataframe into the fmf file

    :param fh: filehandle
    :param data: single dataframe/pintarray or a dictionary of dataframe/pintarrays with the key = symbol
    :param formatting: string - if different formatting of dataframe is required
    :param delimiter: string- seperator used when writing the data.
    """
    if delimiter is None:
        delimiter = "\t"
    elif delimiter == "whitespace":
        delimiter = "    "

    # if single dataframe
    if isinstance(data, pd.DataFrame):
        fh.write('[*data]\n')
        append_table(fh, data, formatting, delimiter)

    # if dictionary of dataframes
    elif isinstance(data, dict):
        for table in data:
            fh.write('[*data: ' + str(table) + ']\n')
            append_table(fh, data[table], formatting, delimiter)
    else:
        warnings.warn("data argument is not a dataframe/pintarray or dictionary of dataframe/pintarrays")


def append_table(fh, dataframe, formatting, delimiter):
    """
    appends dataframe into the fmf file
    Still not 100% that this actually works.
    :param fh: filehandle
    :param dataframe: dataframe/pint array
    :param formatting: string - fomatting of number when writing to file
    :param delimiter: string- seperator used when writing the data.
    """

    num_col = len(dataframe.columns)
    for index, row in dataframe.iterrows():
        line = ''
        for i, cell in enumerate(row):
            try:
                # if pintarray with number
                line += ("{" + formatting + "}").format(cell.magnitude)
            except AttributeError:
                if isinstance(cell, str):
                    # else if dataframe with string
                    line += cell
                else:
                    # else if dataframe with number
                    line += ("{" + formatting + "}").format(cell)
            except ValueError:
                # else if pintarray with string
                line += str(cell.magnitude)

            if i < num_col - 1:
                line += str(delimiter)

        line += '\n'
        fh.write(line)


def check_sections(metadata):
    """
    Check whether the required number of sections (to define a fmf) are inputed, display warning if not.

    :param metadata:
    """
    isMulti = False
    hasReference = False
    hasDefinitions = 0

    headers = metadata.keys()
    for h in headers:
        if h == "*table definitions":
            isMulti = True
        if h == "*reference":
            hasReference = True

    if isMulti:
        symbols = metadata["*table definitions"].values()
        for s in symbols:
            for h in headers:
                if h == ("*data definitions: " + s):
                    hasDefinitions += 1
        hasDefinitions = (hasDefinitions == len(symbols))
    else:
        for h in headers:
            if h == "*data definitions":
                hasDefinitions = True

    if not hasReference:
        warnings.warn("cannot find '*reference' section")
    if not hasDefinitions:
        warnings.warn("cannot find all '*data definitions' section(s)")


def check_table_symbols(dataframes, metadata):
    """
    Function to check if the table definition symbols are consistent with the data table symbol inputs,
     display warning if not

    :param dataframes: dict of dataframes with symbol as key
    :param metadata: metadata containing infomation about the table defintions
    """
    key_symbols = dataframes.keys()
    try:
        value_symbols = metadata['*table definitions'].values()

        if not set(list(key_symbols)) == set(list(value_symbols)):
            warnings.warn("Table definitions symbols not equal to the dataframe symbols")

    except KeyError:
        warnings.warn("Cannot find key/section *table definitions, thus cannot check consistency of table symbols")

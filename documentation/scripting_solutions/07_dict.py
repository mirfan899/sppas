#!/usr/bin python
"""

:author:       Brigitte Bigi
:date:         2016-May-07
:contact:      brigitte.bigi@gmail.com
:license:      GPL, v3
:copyright:    Copyright (C) 2016  Brigitte Bigi

:summary:      Simple script to manipulate dictionaries: SAMPA to IPA converter.

"""
import codecs
import sys

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

#myfile="C:\phonemes.csv"
myfile = "phonemes.csv"

# ----------------------------------------------------------------------------


def read_file(filename):
    """ Get the content of a file.

    :param filename: (str) Name of the file to read, including path.
    :returns: List of lines

    """
    with codecs.open(filename, 'r', encoding="utf8") as f:
        return f.readlines()

# ----------------------------------------------------------------------------


def extract_dict_from_lines(lines, col_key, col_value):
    """ Extract a dictionary from the columns of a list of lines.

    :param lines: (list)
    :param col_key: (str)
    :param col_value: (str)

    """
    # Check if everything is normal:
    my_dict = dict()
    if col_key < 0 or col_value < 0:
        print("Error. Bad column number.")
        return my_dict

    for line in lines:
        # Get columns in a list
        columns = line.split(';')
        # Check if the given column values are normal!
        if len(columns) > col_key and len(columns) > col_value:
            the_key = columns[col_key].strip()
            the_value = columns[col_value].strip()
            # Add the new pair in the dict. If the key is already
            # existing, it will be updated with the new value!
            my_dict[the_key] = the_value
        else:
            print("Warning. Bad number of columns for line: {0}".format(line))

    return my_dict

# ----------------------------------------------------------------------------

if __name__ == '__main__':

    lines = read_file(myfile)

    # before doing something, check the data!
    if not len(lines):
        print('Hum... the file was empty!')
        sys.exit(0)

    sampa_dict = extract_dict_from_lines(lines, 1, 2)
    my_list = ['a', 'b', 'c', 'd', 'e', 'f', 'E', 'g', 'a~', 'S']
    for phone in my_list:
        if phone in sampa_dict:
            print("Sampa phoneme {:s} is IPA {:s}.".format(phone, sampa_dict[phone]))
        else:
            print("Sampa phoneme {:s} has no IPA!".format(phone))

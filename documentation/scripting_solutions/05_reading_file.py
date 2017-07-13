#!/usr/bin python
"""

:author:       Brigitte Bigi
:date:         2016-May-07
:contact:      brigitte.bigi@gmail.com
:license:      GPL, v3
:copyright:    Copyright (C) 2016  Brigitte Bigi

:summary:      Simple script to open and read a file.

"""
import codecs
import sys

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

#myfile="C:\phonemes.csv"
myfile="phonemes.csv"

# ----------------------------------------------------------------------------


def read_file(filename):
    """ Get the content of a file with utf-8 encoding.

    :param filename: (str) Name of the file to read, including path.
    :returns: List of strings

    """
    with codecs.open(filename, 'r', encoding="utf8") as fp:
        return fp.readlines()

# ----------------------------------------------------------------------------

if __name__ == '__main__':

    lines = read_file(myfile)

    # before doing something, check the data!
    if len(lines) == 0:
        print('Hum... the file was empty!')
        sys.exit(0)

    # print the lines
    for line in lines:
        print(line.strip())

    # do something with the lines
    vowels = list()
    for line in lines:
        columns = line.split(';')
        if columns[0] == "vowels":
            vowels.append(columns[1])

    # then do something on the list of vowels...

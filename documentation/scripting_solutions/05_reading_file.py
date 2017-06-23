#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Simple script to open and read a file.

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
    """ Read the whole file, return lines into a list.

    @param filename (string) Name of the file to read, including path.
    @return List of str

    """
    with codecs.open(filename, 'r', encoding="utf8") as f:
        return f.readlines()

# ----------------------------------------------------------------------------

lines = read_file(myfile)

# before doing something, check the data!
if len(lines) == 0:
    print('Hum... the file was empty!')
    sys.exit(0)

# do something with the lines
vowels = list()
for l in lines:
    columns = l.split(';')
    if columns[0] == "vowels":
        vowels.append(columns[1])

# then do something on the list of vowels...

# ----------------------------------------------------------------------------

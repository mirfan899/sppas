#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Simple script to manipulate dictionaries: SAMPA to IPA converter.

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
    @return List of lines

    """
    with codecs.open(filename, 'r', encoding="utf8") as f:
        return f.readlines()

# ----------------------------------------------------------------------------

def extract_dict_from_lines(lines, colkey, colvalue):
    """ Extract a dictionary from the columns of a list of lines. """

    # Check if everything is normal:
    mydict = {}
    if colkey < 0 or colvalue < 0:
        print("Error. Bad column number.")
        return mydict

    for l in lines:
        # Get columns
        columns = l.split(';')
        # Check if the given columns values are normal!
        if len(columns) > colkey and len(columns) > colvalue:
            thekey = columns[colkey].strip()
            thevalue = columns[colvalue].strip()
            # Add the new pair in the dict. If the key is already
            # existing, it will be updated with the new value!
            mydict[thekey] = thevalue
        else:
            print("Warning. Bad number of columns for line: {0}".format(l))
    return mydict

# ----------------------------------------------------------------------------

lines = read_file(myfile)

# before doing something, check the data!
if not len(lines):
    print('Hum... the file was empty!')
    sys.exit(0)

sampadict = extract_dict_from_lines(lines, 1, 2)
mylist = ['a', 'b', 'c', 'd', 'e', 'f', 'E', 'g', 'a~', 'S']
for phone in mylist:
    if phone in sampadict:
        print("Sampa phoneme{0} is IPA {1}.".format(phone, sampadict[phone]))
    else:
        print("Sampa phoneme {0} has no IPA!".format(phone))

# ----------------------------------------------------------------------------

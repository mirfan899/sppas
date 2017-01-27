#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Simple script to get how many vowels are in a list of phonemes.

""" 

import codecs
import sys
import codecs

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

def extract_list_from_lines(lines, pattern):
    """ Extract a list from lines if lines match with pattern.  """

    mylist = []
    for l in lines:
        columns = l.split(';')
        if columns[0].strip() == pattern:
            mylist.append(columns[1].strip())

    return mylist

# ----------------------------------------------------------------------------

def count_elements(referencelist, tocountlist):
    """ Return how many elements of a list are in the reference list. """

    n = 0
    for x in tocountlist:
        if x in referencelist:
            n = n + 1
    return n

# ----------------------------------------------------------------------------

lines = read_file(myfile)

# before doing something, check the data!
if len(lines) == 0:
    print('Hum... the file was empty!')
    sys.exit(0)

vowels = extract_list_from_lines(lines, "vowels")
mylist = ['a', 'b', 'c', 'd', 'e', 'f', 'E', 'g', 'a~', 'S']

print("In my list, there are {:d} vowels.".format(count_elements(vowels,mylist)))
print("In my list, there are {:d} fricatives.".format(count_elements(extract_list_from_lines(lines, "fricatives"),mylist)))

# ----------------------------------------------------------------------------

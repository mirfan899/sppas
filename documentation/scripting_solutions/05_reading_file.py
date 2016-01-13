# ----------------------------------------------------------------------------
# Author: Brigitte Bigi
# Date: April,17th,2015
# Brief: Simple script to get how many vowels are in a list of phonemes.
# ----------------------------------------------------------------------------

import codecs
import sys

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

#myfile="C:\Users\Brigitte\Desktop\pythonscripts\phonemes.csv"
myfile="phonemes.csv"

# ----------------------------------------------------------------------------

def read_file(filename):
    """
    Read the whole file, return lines into a list.

    @param filename (string) Name of the file to read, including path.
    @return List of lines

    """
    with codecs.open(filename, 'r', encoding="utf8") as f:
        return f.readlines()

# ----------------------------------------------------------------------------


lines = read_file(myfile)

# before doing something, check the data!
if not len(lines):
    print 'Hum... the file was empty!'
    sys.exit(0)

# do something with the lines
vowels = []
for l in lines:
    columns = l.split(';')
    if columns[0] == "vowels":
        vowels.append(columns[1])

# ----------------------------------------------------------------------------

#!/usr/bin python
"""

:author:       Brigitte Bigi
:date:         2016-May-07
:contact:      brigitte.bigi@gmail.com
:license:      GPL, v3
:copyright:    Copyright (C) 2016  Brigitte Bigi

:summary:      Simple script to open a file, then read and print its content.

""" 

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

#myfile="C:\phonemes.csv"
myfile="phonemes.csv"


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

if __name__ == '__main__':

    # Open the file
    f = open(myfile)
    # Read the content line by line wit a loop
    for line in f:
        # do something with the line stored in variable "line"
        print(line.strip())
    f.close()

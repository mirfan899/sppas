#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Simple script to open and read a file.

""" 

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

#myfile="C:\phonemes.csv"
myfile="phonemes.csv"


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

f = open(myfile)
for l in f:
    # do something with the line stored in variable l
    print l.strip()
f.close()

# ----------------------------------------------------------------------------

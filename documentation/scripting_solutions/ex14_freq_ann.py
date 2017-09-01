#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Open an annotated file and print information about tiers.

"""
import wx
import sys
import os.path
sys.path.append(os.path.join("..", ".."))

import sppas.src.annotationdata.aio as trsaio
from ex12_tiers_info_wx import wxAskItem, wxGetDir, wxGetFile, checkExtension, wxShowErrorMessage

# ----------------------------------------------------------------------------
# WX Functions
# ----------------------------------------------------------------------------


def wxGetPattern():
    """ Open a TextEntryDialog and return a string. """

    pattern = ''
    dialog = wx.TextEntryDialog(None, "Pattern to count:")
    if dialog.ShowModal() == wx.ID_OK:
        pattern = dialog.GetValue()
    dialog.Destroy()
    return pattern


# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------


def printFreqAnn(filename, pattern):
    """ Print the number of occurrences of a pattern in each tier of a file. """

    print("Take a look at file {:s}:".format(filename))
    trs = trsaio.read(filename)
    pattern = pattern.strip()

    for tier in trs:
        c = 0
        for ann in tier:
            if ann.GetLabel().GetValue() == pattern:
                c += 1
        print(" Tier {:s}: {:d}".format(tier.GetName(), c))


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    """ This is the main function. """

    # Get the pattern to find
    pattern = wxGetPattern()
    if not len(pattern):
        sys.exit(0)

    # Ask whether the script will be applied on one file or
    # on all files of a directory.
    message = "Apply the script on:"
    choices = ['a single file', 'all files in a directory']
    item = wxAskItem(message, choices)

    if item == -1:
        sys.exit(0)

    elif item == 0:
        # Get a filename
        filename = wxGetFile()
        # the user said OK or Cancel?
        if not len(filename):
            sys.exit(0)
        # Verify if the extension is correct
        if not checkExtension(filename):
            wxShowErrorMessage("Un-recognized file extension.")
            sys.exit(1)
        # Now, do the job!
        printFreqAnn(filename, pattern)

    elif item == 1:
        # Get a directory name
        dirname = wxGetDir()
        # Get the list of expected files in this directory
        files = [f for f in os.listdir(dirname) if checkExtension(f)]
        # Now, do the job, for each file!
        for f in files:
            printFreqAnn(os.path.join(dirname, f), pattern)
            # Let the result until a key is pressed.
            raw_input("Press a key to continue")

    # Let the result until a key is pressed.
    raw_input("Press a key to exit")


# ----------------------------------------------------------------------------
# This is the python entry point:
# Here, we start the wxpython application and ask to execute the main function.
if __name__ == '__main__':
    app = wx.App()
    main()
    app.MainLoop()

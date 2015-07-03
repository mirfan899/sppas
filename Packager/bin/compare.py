#!/usr/bin/env python2
"""
 *  author: Brigitte Bigi
 *  date:   October, 2014
 *  brief:  Compare transcriptions of two folders
"""

import os
import sys
import getopt
from os.path import *

SPPAS = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

import annotationdata.io
from annotationdata import Transcription

# ---------------------------------------------------------------------------
# Generic Functions
# ---------------------------------------------------------------------------

def usage(output):
    """
    Write the usage on an output .
    @param output is a string representing the output (for example: sys.stdout)
    """
    output.write('compare.py \n')
    output.write('      -r folder     Input for the Reference\n')
    output.write('      -t folder     Input for the Test\n')
    output.write('      -v value      Verbosity level: 0 is low, 1 is medium, 2 is high\n')
    output.write('      -d value      Delta value to compare points (=2*radius)\n')
    output.write('      --persist     Do not stop after the first error: print all errors.\n')
    output.write('      --help        Print help then exit the program.\n')

# End usage
# ----------------------------------------------------------------------

def quit(message, status):
    """
    Exit this program.
    @param message is a text to communicate to the user on sys.stderr.
    @param status is an integer of the status exit value
    """
    sys.stderr.write('compare.py. '+message)
    sys.exit(status)

# End quit
# ----------------------------------------------------------------------

def get_files(directory,extension):
    """
    Get the list of files of a specific extension.
    """
    mylist = []
    for r, d, f in os.walk(directory):
        for files in f:
            if files.lower().endswith(extension.lower()) is True:
                mylist.append(join(r,files))
    return mylist

# End get_files
# ----------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Compare is here
# ---------------------------------------------------------------------------

def printerrors(verbose, aref, ahyp, message):
    if verbose>1:
        print " ... ...",aref
        print " ... ...",ahyp
    if verbose>0:
        print " ... ...",message


def compare_annotations(aref, ahyp, delta=0.2, verbose=1):

    # Compare annotation type
    if ahyp.GetLocation().IsPoint() != aref.GetLocation().IsPoint():
        printerrors(verbose, aref, ahyp, "Different annotation types.")
        return False

    # Compare labels
    if not ahyp.GetLabel().GetValue() == aref.GetLabel().GetValue():
        printerrors(verbose, aref, ahyp, "Different annotation labels.")
        return False

    # Compare time
    if ahyp.GetLocation().IsInterval() is True:
        aref.GetLocation().GetBegin().SetRadius(delta/2.)
        ahyp.GetLocation().GetBegin().SetRadius(delta/2.)
        aref.GetLocation().GetEnd().SetRadius(delta/2.)
        ahyp.GetLocation().GetEnd().SetRadius(delta/2.)
        if ahyp.GetLocation().GetBegin() != aref.GetLocation().GetBegin():
            printerrors(verbose, aref, ahyp, "Different annotation Begin value.")
            return False
        if ahyp.GetLocation().GetEnd() != aref.GetLocation().GetEnd():
            printerrors(verbose, aref, ahyp, "Different annotation End value.")
            return False
    else:
        aref.GetLocation().GetPoint().SetRadius(delta/2.)
        ahyp.GetLocation().GetPoint().SetRadius(delta/2.)
        if ahyp.GetLocation().GetPoint() != aref.GetLocation().GetPoint():
            printerrors(verbose, aref, ahyp, "Different annotation Point value.")
            return False

    return True


def compare_tiers(Tierref, Tierhyp, delta=0.2, verbose=1, persist=False):
    """
    Compare two tiers.
    Comparison is performed using (in this order):
        1. tier' sizes (nb of intervals);
        2. annotations: type, then:
           2.1 label, begin time, end time if interval;
           2.2 label, time if point.
        Names are not compared!
    @param Tierref is the reference transcription
    @param Tierhyp is the hypothesis transcription
    @param delta is the acceptable delta time value
    @param verbose is the verbosity level (0=None, 1=Medium, 2=High),
           used to print a diagnosis on stdout
    @return True if both tiers (ref and hyp) are identical
    """
    if verbose>1:
        print " ... ... Reference  tier name: ",Tierref.GetName()
        print " ... ... Hypothesis tier name: ",Tierhyp.GetName()

    # Compare tier size
    if not Tierref.GetSize() == Tierhyp.GetSize():
        if verbose>0:
            print " ... ... Reference  tier size: "+str(Tierref.GetSize())
            print " ... ... Hypothesis tier size: "+str(Tierhyp.GetSize())
        return False

    diagnosis = True
    # For each annotation
    for (aref,ahyp) in zip(Tierref,Tierhyp):
        res = compare_annotations(aref,ahyp,delta,verbose)
        if res is False:
            diagnosis = False
        if res is False and persist is False:
             return False

    return diagnosis


def compare_trs(Trsref, Trshyp, delta=0.2, verbose=1, persist=False):
    """
    Compare two transcriptions.
    Comparison is performed using (in this order):
        1. transcription sizes (nb of tiers);
        2. tier' sizes (nb of intervals);
        3. annotations: type, then:
           3.1 label, begin time, end time if interval;
           3.2 label, time if point.
        Names are not compared!
    @param Trsref is the reference transcription
    @param Trshyp is the hypothesis transcription
    @param delta is the acceptable delta time value (= 2*Redius)
    @param verbose is the verbosity level (0=None, 1=Medium, 2=High),
           used to print a diagnosis on stdout
    @return True if both transcriptions (ref and hyp) are identical
    """
    diagnosis = True

    # Compare transcription size (nb of tiers)
    if Trshyp.GetSize() != Trsref.GetSize():
        if verbose>0:
            print " ... Reference  transcription size: "+str(Trsref.GetSize())
            print " ... Hypothesis transcription size: "+str(Trshyp.GetSize())
        return False

    # For each tier
    for (reftier,hyptier) in zip (Trsref,Trshyp):
        res = compare_tiers(reftier, hyptier, delta, verbose, persist)
        if res is False:
            diagnosis = False
        if res is False and persist is False:
            return False

    return diagnosis



def comparext(reference, test, extension, delta, verbose, persist):
    """
    Main function to compare.
    Return the number of files which are different.
    """
    listref  = get_files(reference, extension)
    listtest = get_files(test, extension)

    if len(listref) != len(listtest):
        print "[ ERROR ] Not the same number of files in ref and hyp."
        print "  REF:  ",len(listref)
        print "  TEST: ",len(listtest)
        sys.exit(1)

    if len(listtest)==0:
        print " [ ERROR ] No hypothesis file."
        sys.exit(1)

    err = 0
    for i in range(len(listref)):
        if verbose>0:
            print " Reference: "+listref[i]
        reftrs = annotationdata.io.read( listref[i] )

        try:
            if verbose>0:
                print " Test: "+listtest[i]
            testtrs = annotationdata.io.read( listtest[i] )
            res = compare_trs(reftrs, testtrs, delta, verbose, persist)
            if res is False :
                if verbose>0:
                    print " [ ERROR ]"
                err = err + 1
        except Exception as e:
            print str(e), " [ ERROR ] "

    return err


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 1:
        # stop the program and print an error message
        usage(sys.stderr)
        sys.exit(1)

    # Get options (if any...)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:t:v:d:", ["help", "persist"])
    except getopt.GetoptError, err:
        # Print help information and exit:
        quit("Error: "+str(err)+".\nUse option --help for any help.\n", 1)

    # Variables
    reference = None
    test = None
    verbose = 1
    delta = 0.2
    persist = False

    # Extract options
    for o, a in opts:
        if o == "-r":
            reference = str(a)
        elif o == "-t":
            test = str(a)
        elif o == "-v":
            verbose = int(a)
        elif o == "-d":
            delta = float(a)
        elif o == "--persist":
            persist = True
        elif o == "--help": # need help
            print 'Help'
            usage(sys.stdout)
            sys.exit()

    # Check
    if not reference and not test:
        usage(sys.stderr)
        sys.exit(1)

    if delta < 0.0:
        delta = 0.2

    if verbose < 0:
        verbose = 1


    # Now, compare...

    errors = 0

    print "##### Compare Phonetization ##### "
    errors += comparext(reference, test, "-phon.TextGrid", delta, verbose, persist)

    print "##### Compare Alignment ##### "
    errors += comparext(reference, test, "-palign.TextGrid", delta, verbose, persist)

    print "##### Compare Syllabification ##### "
    errors += comparext(reference, test, "-salign.TextGrid", delta, verbose, persist)

    print "##### Compare Momel/INTSINT ##### "
    errors += comparext(reference, test, ".momel.TextGrid", delta, verbose, persist)

    sys.exit(errors)

# ---------------------------------------------------------------------------


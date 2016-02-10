#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://www.lpl-aix.fr/~bigi/sppas
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2016  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: comparesegmentations.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
import codecs
import os.path
from argparse import ArgumentParser
import subprocess

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.append(SPPAS)

from   annotationdata.transcription import Transcription
import annotationdata.io

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

vowels = [ "a","e","i","o","u","y","A","E","I","M","O","Q","U","V","Y","a~","e~","i~","o~","O~","u~","U~","eu","EU","{","}","@","1","2","3","6","7","8","9","&","3:r","OI","@U","eI","ai","aI","au","aU","aj","aw","ei","ew","ia","ie","io","ja","je","jo","ju","oj","ou","ua","uo","wa","we","wi","wo","ya","ye","yu" ]
consonants = [ "b","b_<","c","d","d`","f","g","g_<","h","j","k","l","l`","m","n","n`","p","q","r","r`","s","s`","t","t`","v","w","x","z","z`","B","C","D","F","G","H","J","K","L","M","N","O","R","S","T","W","X","Z","4","5","?","ts","tS","dz","dZ","tK","kp","Nm","rr","ss","ts_h","k_h","p_h","t_h","ts_hs","tss" ]

# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Functions to manage input annotated files

def get_tier( filename, tieridx ):
    """
    Returns the tier of the given index in an annotated filename,
    or None if some error occurs..
    """
    try:
        trsinput = annotationdata.io.read( filename )
    except Exception:
        return None
    if tieridx < 0 or tieridx >= trsinput.GetSize():
        return None
    return trsinput[ tieridx ]

def get_tiers(reffilename,hypfilename,refidx,hypidx):
    """
    Returns 2 tiers: reference and hypothesis from 2 given annotated files,
    or None if some error occurs.
    """
    reftier = get_tier(reffilename, refidx)
    hyptier = get_tier(hypfilename, hypidx)
    if reftier.GetSize() != hyptier.GetSize():
        return (None,None)
    return reftier,hyptier

# ----------------------------------------------------------------------------
# Functions to estimate the Unit Boundary Positioning Accuracy.

def _eval_index(step,value):
    m = (value % step ) # Estimate the rest
    d = (value-m)       # Make "d" an entire value
    index = d/step      # evaluate the index depending on step
    return int(index)

def _inc(vector,idx):
    if idx >= len(vector):
        toadd = idx-len(vector)+1
        vector.extend([0]*toadd)
    vector[idx] = vector[idx] + 1

def ubpa(vector,text,filename):
    """
    Estimates the Unit Boundary Positioning Accuracy,
    and write the result into a file.

    @param vector contains the list of the delta values.
    @param text is one of "Duration", "Position Start", ...
    @param filename is the file to write the result.
    """
    step = 0.01
    tabNeg = []
    tabPos = []

    for delta in vector:
        if delta > 0.:
            idx = _eval_index(step,delta)
            _inc(tabPos,idx)
        else:
            idx = _eval_index(step,delta*-1.)
            _inc(tabNeg,idx)

    with codecs.open(filename, "w", "utf8") as fp:
        fp.write( "|--------------------------------------------| \n" )
        fp.write( "|      Unit Boundary Positioning Accuracy    | \n" )
        fp.write( "|            Delta=T(hyp)-T(ref)             | \n" )
        fp.write( "|--------------------------------------------| \n" )
        i=len(tabNeg)-1
        for value in reversed(tabNeg):
            percent = ((value*100.)/(len(vector)-1))
            fp.write( "|  Delta-%s < -%.3f: "%(text,((i+1)*step)) )
            fp.write( "%d (%.2f%%) \n"%(value,percent) )
            i = i - 1
        fp.write( "|--------------------------------------------| \n" )
        for i,value in enumerate(tabPos):
            percent = round(((value*100.)/(len(vector)-1)),3)
            fp.write( "|  Delta-%s < +%.3f: "%(text,((i+1)*step)) )
            fp.write( "%d (%.2f%%)\n"%(value,percent) )
        fp.write( "|--------------------------------------------| \n" )

# ----------------------------------------------------------------------------
# Function to draw the evaluation as BoxPlots (using an R script)

def test_R():
    """
    Test if Rscript is available as a command of the system.
    """
    try:
        NULL = open(os.devnull, "w")
        subprocess.call(['Rscript'], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        return False
    return True


def exec_Rscript(filenamed,filenames,filenamee,rscriptname,pdffilename):
    """
    Write the R script to draw boxplots from the given files, then
    execute it, and delete it.

    @param pdffilename is the file with the result.
    """
    with codecs.open(rscriptname,"w","utf8") as fp:
        fp.write("#!/usr/bin/env Rscript \n")
        fp.write("# Title: Boxplot for phoneme alignments evaluation \n")
        fp.write("\n")
        fp.write("args <- commandArgs(trailingOnly = TRUE) \n")
        fp.write("\n")
        fp.write("# Get datasets \n")
        fp.write('dataD <- read.csv("%s",header=TRUE,sep=",") \n'%filenamed)
        fp.write('dataPS <- read.csv("%s",header=TRUE,sep=",") \n'%filenames)
        fp.write('dataPE <- read.csv("%s",header=TRUE,sep=",") \n'%filenamee)
        fp.write("\n")
        fp.write("# Define Output file \n")
        fp.write('pdf(file="%s", paper="a4") \n'%pdffilename)
        fp.write("\n")
        fp.write("# Control plotting style \n")
        fp.write("par(mfrow=c(3,1))    # only one line and one column \n")
        fp.write("par(cex.lab=1.2)     # controls the font size of the axis title \n")
        fp.write("par(cex.axis=1.2)    # controls the font size of the axis labels \n")
        fp.write("par(cex.main=1.6)    # controls the font size of the title \n")
        fp.write("\n")
        fp.write("# Then, plot: \n")
        fp.write("boxplot(dataD$DeltaD~dataD$PhoneD, \n")
        fp.write('   main="Delta Duration",             # graphic title \n')
        fp.write('   ylab="T(automatic) - T(manual)",   # y axis title \n')
        fp.write('   #range=0,                          # use min and max for the whisker \n')
        fp.write('   outline = FALSE,                   # REMOVE OUTLIERS \n')
        fp.write('   border="blue", \n')
        fp.write('   ylim=c(-0.05,0.05), \n')
        fp.write('   col="pink") \n')
        fp.write("   abline(0,0) \n")
        fp.write("\n")
        fp.write('boxplot(dataPS$DeltaS~dataPS$PhoneS, \n')
        fp.write('   main="Delta Start Position", \n')
        fp.write('   ylab="T(automatic) - T(manual)", \n')
        fp.write('   outline = FALSE, \n')
        fp.write('   border = "blue", \n')
        fp.write('   ylim=c(-0.05,0.05), \n')
        fp.write('   col = "pink") \n')
        fp.write('   abline(0,0) \n')
        fp.write("\n")
        fp.write('boxplot(dataPE$DeltaE~dataPE$PhoneE, \n')
        fp.write('   main="Delta End Position", \n')
        fp.write('   ylab="T(automatic) - T(manual)", \n')
        fp.write('   outline = FALSE,  \n')
        fp.write('   border="blue", \n')
        fp.write('   ylim=c(-0.05,0.05), \n')
        fp.write('   col="pink") \n')
        fp.write('abline(0,0) \n')
        fp.write('graphics.off() \n')
        fp.write("\n")

    command = "Rscript "+rscriptname
    try:
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        line = p.communicate()
    except OSError as e:
        os.remove(rscriptname)
        return e

    os.remove(rscriptname)
    if retval != 0:
        return line

    return ""


def boxplot( deltaposB, deltaposE, deltaposD, extras, outname, vector, name ):
    """
    Create a PDF file with boxplots, but selecting only a subset of phonemes.

    @param vector is the list of phonemes
    """
    filenamed = outname+"-delta-duration-"+name+".csv"
    filenames = outname+"-delta-position-start-"+name+".csv"
    filenamee = outname+"-delta-position-end-"+name+".csv"

    fpb = codecs.open( filenames, "w", 'utf8')
    fpe = codecs.open( filenamee, "w", 'utf8')
    fpd = codecs.open( filenamed, "w", 'utf8')
    fpb.write("PhoneS,DeltaS\n")
    fpe.write("PhoneE,DeltaE\n")
    fpd.write("PhoneD,DeltaD\n")
    for i,extra in enumerate(extras):
        etiquette = extra[0]
        tag       = extra[2]
        if etiquette in vector:
            if tag != 0:
                fpb.write("%s,%f\n"%(etiquette,deltaposB[i]))
            if tag != -1:
                fpe.write("%s,%f\n"%(etiquette,deltaposE[i]))
            fpd.write("%s,%f\n"%(etiquette,deltadur[i]))
    fpb.close()
    fpe.close()
    fpd.close()

    message = exec_Rscript(filenamed,filenames,filenamee,outname+".R",outname+"-delta-"+name+".pdf")

    os.remove(filenamed)
    os.remove(filenames)
    os.remove(filenamee)
    return message


# ----------------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Verify and extract args:

parser = ArgumentParser(usage="%s -fr ref -fh hyp [options]" % os.path.basename(PROGRAM), description="... a script to compare two segmentations, in the scope of evaluating an hypothesis vs a reference.")

parser.add_argument("-fr", metavar="file", required=True,  help='Input annotated file/directory name of the reference.')
parser.add_argument("-fh", metavar="file", required=True,  help='Input annotated file/directory name of the hypothesis.')
parser.add_argument("-tr", metavar="file", type=int, default=1, required=False, help='Tier number of the reference (default=1).')
parser.add_argument("-th", metavar="file", type=int, default=1, required=False, help='Tier number of the hypothesis (default=1).')
parser.add_argument("-o",  metavar="path", required=False, help='Path for the output files.')
parser.add_argument("--quiet", action='store_true', help="Disable the verbosity." )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Global variables

idxreftier = args.tr - 1
idxhyptier = args.th - 1
files = []      # List of tuples: (reffilename,hypfilename)
deltadur  = []  # Duration of each phoneme
deltaposB = []  # Position of the beginning boundary of each phoneme
deltaposE = []  # Position of the end boundary of each phoneme
deltaposM = []  # Position of the center of each phoneme
extras = []     # List of tuples: (evaluated phoneme,hypothesis file names, a tag)

# ----------------------------------------------------------------------------
# Prepare file names to be analyzed, as a list of tuples (ref,hyp)

outpath = None
if args.o:
    outpath = args.o
    if not os.path.exists(outpath):
        os.mkdir(outpath)

if os.path.isfile( args.fh ) and os.path.isfile( args.fr ):
    hypfilename,extension = os.path.splitext( args.fh )
    outbasename = os.path.basename( hypfilename )
    if outpath is None:
        outpath = os.path.dirname( hypfilename )
    outname = os.path.join( outpath, outbasename )

    files.append( (os.path.basename(args.fr),os.path.basename(args.fh)) )
    refdir = os.path.dirname( args.fr )
    hypdir = os.path.dirname( args.fh )

elif os.path.isdir( args.fh ) and os.path.isdir( args.fr ):
    if outpath is None:
        outpath = args.fh
    outname = os.path.join( outpath, "phones")

    refdir = args.fr
    hypdir = args.fh

    reffiles=[]
    hypfiles=[]
    for fr in os.listdir( args.fr ):
        if os.path.isfile( os.path.join(refdir,fr) ):
            reffiles.append( fr )
    for fh in os.listdir( args.fh ):
        if os.path.isfile( os.path.join(hypdir,fh) ):
            hypfiles.append( os.path.basename(fh) )

    for fr in reffiles:
        basefr,extfr = os.path.splitext( fr )
        if not extfr.lower() in annotationdata.io.extensions:
            continue
        for fh in hypfiles:
            basefh,extfh = os.path.splitext( fh )
            if not extfh.lower() in annotationdata.io.extensions:
                continue
            if fh.startswith( basefr ):
                files.append( (fr,fh) )

else:
    print "Both reference and hypothesis must be of the same type: file or directory."
    sys.exit(1)

if args.quiet is False: print "Results will be stored in:",outname

# ----------------------------------------------------------------------------
# Evaluate the delta from the hypothesis to the reference
# Delta = T(hyp) - T(ref)

for f in files:

    fr = os.path.join(refdir,f[0])
    fh = os.path.join(hypdir,f[1])

    reftier,hyptier = get_tiers(fr, fh, idxreftier, idxhyptier)
    if reftier is None or hyptier is None:
        continue
    if args.quiet is False:
        print "Hypothesis:",f[1],"vs Reference:",f[0],"->",reftier.GetSize()," phonemes."

    # ----------------------------------------------------------------------------
    # Compare boundaries and durations of annotations.

    i = 0
    imax = reftier.GetSize()-1

    for rann,hann in zip(reftier,hyptier):
        etiquette = rann.GetLabel().GetValue()
        # begin
        rb = rann.GetLocation().GetBegin().GetValue()
        hb = hann.GetLocation().GetBegin().GetValue()
        deltab = hb-rb
        # end
        re = rann.GetLocation().GetEnd().GetValue()
        he = hann.GetLocation().GetEnd().GetValue()
        deltae = he-re
        # middle
        rm = rb + (re-rb)/2.
        hm = hb + (he-hb)/2.
        deltam = hm-rm
        # duration
        rd = rann.GetLocation().GetDuration().GetValue()
        hd = hann.GetLocation().GetDuration().GetValue()
        deltad = hd-rd

        tag = 1
        if i==0:
            tag = 0
        elif i==imax:
            tag = -1

        # Add new values into vectors, to evaluate the accuracy
        deltaposB.append(deltab)
        deltaposE.append(deltae)
        deltaposM.append(deltam)
        deltadur.append(deltad)
        extras.append( (etiquette,fh,tag) )

        i = i + 1

# ----------------------------------------------------------------------------
# Save delta values into output files

fpb = codecs.open( os.path.join(outname)+"-delta-position-start.txt", "w", 'utf8')
fpe = codecs.open( os.path.join(outname)+"-delta-position-end.txt", "w", 'utf8')
fpm = codecs.open( os.path.join(outname)+"-delta-position-middle.txt", "w", 'utf8')
fpd = codecs.open( os.path.join(outname)+"-delta-duration.txt",  "w", 'utf8')

fpb.write("Phone Delta Filename\n")
fpe.write("Phone Delta Filename\n")
fpm.write("Phone Delta Filename\n")
fpd.write("Phone Delta Filename\n")

for i,extra in enumerate(extras):
    etiquette = extra[0]
    filename  = extra[1]
    if tag != 0:
        fpb.write("%s %f %s\n"%(etiquette,deltaposB[i],filename))
    if tag != -1:
        fpe.write("%s %f %s\n"%(etiquette,deltaposE[i],filename))
    fpm.write("%s %f %s\n"%(etiquette,deltaposM[i],filename))
    fpd.write("%s %f %s\n"%(etiquette,deltadur[i],filename))

fpb.close()
fpe.close()
fpm.close()
fpd.close()

# ----------------------------------------------------------------------------
# Estimates the Unit Boundary Positioning Accuracy

ubpa(deltaposB,"PositionStart", outname+"-eval-position-start.txt")
ubpa(deltaposE,"PositionEnd",   outname+"-eval-position-end.txt")
ubpa(deltaposE,"PositionMiddle",outname+"-eval-position-middle.txt")
ubpa(deltadur, "Duration",      outname+"-eval-duration.txt")

# ----------------------------------------------------------------------------
# Draw BoxPlots of the accuracy via an R script

if test_R() is False:
    sys.exit(0)

message = boxplot( deltaposB, deltaposE, deltadur, extras, outname, vowels, "vowels")
if len(message)>0 and args.quiet is False:
    print message

message = boxplot( deltaposB, deltaposE, deltadur, extras, outname, consonants, "consonants")
if len(message)>0 and args.quiet is False:
    print message

others = []
for extra in extras:
    etiquette = extra[0]
    if not (etiquette in vowels or etiquette in consonants or etiquette in others):
        others.append(etiquette)

if len(others)>0:
    message = boxplot( deltaposB, deltaposE, deltadur, extras, outname, others, "others")
    if len(message)>0 and args.quiet is False:
        print message

# ----------------------------------------------------------------------------

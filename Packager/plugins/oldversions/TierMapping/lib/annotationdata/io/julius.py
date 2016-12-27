#!/usr/bin/env python2
# -*- coding: iso-8859-15 -*-
#
# Copyright (C) 2013  Brigitte Bigi
#
# This file is part of SPPAS.
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
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.


import re
import os
import codecs
import glob

from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.annotation import Annotation
from annotationdata.label.silence import Silence


class JuliusIO( Transcription ):
    """ Represents a set of Julius output alignments.
    """

    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """ Creates a new juliusIO instance.
        """
        Transcription.__init__(self, name, coeff, mintime, maxtime)


    # ################################################################ #
    # Input
    # ################################################################ # 

    def __clean(self,sstr):
        __s = sstr.strip()
        __s = re.sub("\s+" , " ", __s)
        return __s


    def read_list(self,filename):
        """ Read a list file (units start and end time).
            Parameters:
                - filename is the list file name.
            Exception:   IOError
            Return:      none
        """
        try:
            encoding='utf-8'
            fp = codecs.open(filename, 'r', encoding)
        except IOError,e:
            raise IOError("Input IPUs read list error: " + str(e) + "\n")
        _units = []
        # Each line corresponds to an inter-pausal unit,
        # with a couple 'start end' of float values.
        for line in fp:
            line = self.__clean(line)
            _tab = line.split(" ")
            if len(_tab)>=2:
                _units.append( (float(_tab[0]),float(_tab[1])) )
            elif len(_tab)==1:
                # last line indicates the duration of the wav file.
                _units.append( (float(_tab[0]),0.) )
        fp.close()
        return _units

    # End read_list
    # ------------------------------------------------------------------


    def read_palign(self, filename):
        """ Read an alignment file.
            Parameters:
                - filename is the input file (a Julius output).
            Exception:   IOError
            Return:      2 lists of tuples:
            (start-time end-time phoneme)
            (start-time end-time word)
        """
        _phonalign = []
        _wordalign = []
        try:
            encoding='utf-8'
            fp = codecs.open(filename, 'r', encoding)
        except IOError,e:
            raise IOError("Input error with file " + filename + ": " + str(e) + "\n")

        # Each line is either a new annotation or nothing interesting!
        phonidx = -1     # phoneme index
        loc_s = 0 # phoneme start time
        loc_e = 0 # phoneme end time
        phonlist = []
        for line in fp:
            if line.find("=== begin forced alignment ===")>-1:
                phonidx = 0
            elif line.find('=== end forced alignment ===')>-1:
                phonidx = -1
            elif line.find("phseq1:")>-1:
                line = line[7:]
                wordseq = line.split('|')
                # get indexes of each word
                wordlist = []
                _idx = -1
                for i in range(len(wordseq)):
                    _wrdphseq = wordseq[i].strip().split(" ")
                    _idx += len(_wrdphseq)
                    wordlist.append( _idx )
                # get the list of phonemes (without word segmentation)
                line = line.replace('|','')
                line = self.__clean(line)
                phonlist = line.split(' ')
            elif line.startswith('[') and phonidx>-1:
                # New phonemes
                line = line[:line.find(']')]
                line = line.replace("[","")
                line = line.replace("]","")
                line = self.__clean(line)
                tab = line.split(" ")
                # Column 1: begin time ; column 2: end time; 
                # ATTENTION: Julius indicates time in centiseconds!
                loc_s = (float( tab[0] ) / 100.0)
                loc_e = (float( tab[1] ) / 100.0)
                _phonalign.append( (loc_s, loc_e) )
        fp.close()

        wordidx = 0      # word index
        wordloc_s  = 0.  # word start time
        _modifiedphonalign = []
        loc_s = 0
        loc_e = 0
        nextloc_s = 0
        for phonidx in range( len(_phonalign) ):
            loc_e = _phonalign[phonidx][1]
            if phonidx < (len(_phonalign)-1):
                nextloc_s = _phonalign[phonidx+1][0]
            else:
                nextloc_s = 0.0
            # Attention... loc_s must be equal to the last loc_e
            if loc_e < nextloc_s:
                # Since SPPAS 1.4.4, I was setting next loc_s to the current loc_e 
                # I tried to the average between both values.
                # loc_e = ( nextloc_s + loc_e ) / 2.0
                # Better results if I set the current loc_e as the next loc_s
                loc_e = nextloc_s
            _modifiedphonalign.append( (loc_s, loc_e, phonlist[phonidx]) )
            loc_s = loc_e
            # add also the word?
            if phonidx == wordlist[wordidx]:
                _wordalign.append( (wordloc_s, loc_e, wordseq[wordidx].strip().replace(" ",".")) )
                wordidx = wordidx + 1
                wordloc_s = loc_e

        # last word
        if len(wordseq)-1 == wordidx:
            _wordalign.append( (wordloc_s, loc_e, wordseq[wordidx].strip().replace(" ",".")) )

        return (_modifiedphonalign,_wordalign)

    # End read_palign
    # ------------------------------------------------------------------


    def write_palign(self,tokenslist,alignments,outputfile):
        """ Write an alignment file.
            Parameters:
                - tokenslist is a list with the phonetization of each token
                - alignments is a list of tuples: (start-time end-time phoneme)
                - outputfile is the output file name (a Julius-like output).
            Exception:   IOError
            Return:      none
        """
        # Write output result:
        try:
            encoding='utf-8'
            fp = codecs.open(outputfile, 'w', encoding)
        except IOError as e:
            raise e

        fp.write("----------------------- System Information begin ---------------------\n")
        fp.write("\n") 
        fp.write("                         SPPAS Basic Alignment\n")
        fp.write("\n") 
        fp.write("----------------------- System Information end -----------------------\n")
        fp.write("### Recognition: 1st pass\n")
        fp.write("pass1_best_wordseq: ")
        for i in range(len(tokenslist)):
            fp.write(str(i)+" ")
        fp.write("\n")
        fp.write("pass1_best_phonemeseq: ")
        for i in range(len(tokenslist)-1):
            fp.write(str(tokenslist[i])+" | ")
        fp.write(str(tokenslist[len(tokenslist)-1])+"\n")
        fp.write("### Recognition: 2nd pass\n")
        fp.write("ALIGN: === phoneme alignment begin ===\n")
        fp.write("wseq1: ")
        for i in range(len(tokenslist)):
            fp.write(str(i)+" ")
        fp.write("\n")
        fp.write("phseq1: ")
        for i in range(len(tokenslist)-1):
            fp.write(str(tokenslist[i])+" | ")
        fp.write(str(tokenslist[len(tokenslist)-1])+"\n")
        fp.write("=== begin forced alignment ===\n")
        fp.write("-- phoneme alignment --\n")
        fp.write(" id: from  to    n_score    unit\n")
        fp.write(" ----------------------------------------\n")
        for i in range(len(alignments)):
            tv1,tv2,phon = alignments[i]
            fp.write("[ %d " % tv1)
            fp.write(" %d]" % tv2)
            fp.write(" -30.000000 "+str(phon)+"\n")
        fp.write("=== end forced alignment ===\n")
        fp.close()

    # End write_palign
    # ------------------------------------------------------------------


    def read(self, dirname, listfilename, expend=True, extend=False, tokens=True):
        """ Read a set of alignment files and set it as a tier in a transcription.
            Parameters:
                - dirname is the input directory containing a set of unit
                - alignment files (Julius outputs).
                - expend last phoneme to the unit duration
                - extend only concerns the silence at the end of the file
            Exception:   IOError, Exception
            Return:      none
        """
        # Verify if the directory exists
        if not os.path.exists( dirname):
            raise IOError("Missing directory " + dirname+". \n")

        # Create 3 new tiers
        itemp = self.NewTier("PhonAlign")
        if tokens==True:
            itemt = self.NewTier("PhnTokAlign")
            itemw = self.NewTier("TokensAlign")

        # Read the file.list (the list of units + the wav duration)
        units = []
        try:
            units = self.read_list( listfilename )
        except Exception,e:
            raise IOError("Get list of tracks: "+str(e))

        # Get all unit alignment file names (default file names of wavsil.write_tracks())
        dirlist = glob.glob(os.path.join(dirname, "track_*palign"))
        ntracks = len(dirlist)
        if ntracks==0:
            raise IOError('No tracks aligned')

        # The number of alignment files must correspond 
        # to the number of units in the "list" file.
        if (len(units)-1) != ntracks:
            raise IOError('inconsistency between expected nb of tracks '+str(len(units)-1)+' and nb track files '+str(ntracks))

        # Explore each unit to get alignments
        wavend,unitend = units[ntracks] # Get the wav duration
        track = 1
        loc_e = 0.
        while track <= ntracks:

            # Get real start and end time values of this unit.
            unitstart,unitend = units[(track-1)]

            if track==1:
                # A silence to start?
                if unitstart>0.:
                    time = TimeInterval(TimePoint(0.), TimePoint(unitstart))
                    annotation = Annotation(time, Silence("#"))
                    itemp.Append(annotation)
                    if tokens==True:
                        itemt.Append(annotation.Copy())
                        itemw.Append(annotation.Copy())
            else:
                if loc_e < unitstart: ##Ajout incertain le 22/09/2012
                    # Add an empty interval between 2 units...
                    time = TimeInterval(TimePoint(loc_e), TimePoint(unitstart))
                    annotation = Annotation(time, Silence("#"))
                    itemp.Append(annotation)
                    if tokens==True:
                        itemt.Append(annotation.Copy())
                        itemw.Append(annotation.Copy())

            # Get phoneme alignments and put them into the tier
            trackname = os.path.join(dirname, "track_%06d.palign"%track)
            try:
                (_phonannots,_wordannots) = self.read_palign( trackname )
                # phonemes
                idx = 1
                for loc_s,loc_e,label in _phonannots:
                    loc_s += unitstart
                    # last phoneme... extend to the wav duration?
                    if idx==len(_phonannots) and track==ntracks and extend==True:
                        loc_e = wavend
                    # last unit phoneme... extend to the unit duration?
                    elif idx==len(_phonannots) and expend==True:
                        loc_e = unitend
                    else:
                        loc_e += unitstart

                    time = TimeInterval(TimePoint(loc_s), TimePoint(loc_e))
                    annotation = Annotation(time, Label(label))
                    itemp.Append(annotation)
                    idx += 1
            except Exception:
                time = TimeInterval(TimePoint(unitstart), TimePoint(unitend))
                annotation = Annotation(time, Label("* * ALIGNMENT ERROR * *"))
                itemp.Append(annotation)

            # Get phoneme alignments and put them into the TOKEN'S tier
            if tokens==True:
                try:
                    # for tokens
                    transname = os.path.join(dirname, "track_%06d.trans"%track)
                    encoding='utf-8'
                    f = codecs.open(transname, 'r', encoding)
                    readtokens = f.readline()
                    # Remove multiple spaces
                    f.close()
                    readtokens = re.sub("[ ]+", " ", readtokens)
                    tokenlist = readtokens.strip().split(" ")

                    idx = 1
                    for loc_s,loc_e,label in _wordannots:
                        loc_s += unitstart
                        # last phontoken... extend to the wav duration?
                        if idx==len(_wordannots) and track==ntracks and extend==True:
                            loc_e = wavend
                        # last phon-word... extend to the unit duration?
                        elif idx==len(_wordannots) and expend==True:
                            loc_e = unitend
                        else:
                            loc_e += unitstart

                        time = TimeInterval(TimePoint(loc_s), TimePoint(loc_e))
                        annotation = Annotation(time, Label(label))
                        itemt.Append(annotation)
                        if len(tokenlist)==len(_wordannots):
                            time = TimeInterval(TimePoint(loc_s), TimePoint(loc_e))
                            annotation = Annotation(time, Label(tokenlist[idx-1]))
                            itemw.Append(annotation)
                        idx += 1
                except Exception:
                    time = TimeInterval(TimePoint(unitstart), TimePoint(unitend))
                    annotation = Annotation(time, Label("* * ALIGNMENT ERROR * *"))
                    itemw.Append(annotation)

            track += 1

        # A silence at the end?
        # ... Extend the transcription to the end of the wav.
        if (loc_e+0.01) < wavend:
            try:
                time = TimeInterval(TimePoint(loc_e), TimePoint(wavend))
                annotation = Annotation(time, Silence("#"))
                itemp.Append(annotation)
            except Exception:
                raise IOError('Error with the wav duration, for track '+str(track-1))
            if tokens==True:
                try:
                    itemt.Append(annotation.Copy())
                    itemw.Append(annotation.Copy())
                except Exception:
                    raise IOError('Error with the wav duration, for track '+str(track-1))

    # End read
    # ------------------------------------------------------------------   

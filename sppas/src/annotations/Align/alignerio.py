#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
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
# File: alignerio.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import logging
import os
import codecs
import re
import glob

from annotationdata.transcription  import Transcription
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point    import TimePoint
from annotationdata.annotation     import Annotation
from annotationdata.label.label    import Label
from annotationdata.label.text     import Text
from sp_glob import encoding

from resources.rutils import ToStrip

# ----------------------------------------------------------------------------

class AlignerIO( Transcription ):
    """
    Read/Write time-aligned files.

    """
    # List of file extensions this class is able to read and/or write.
    EXTENSIONS = [ 'palign', 'mlf' ]

    # ------------------------------------------------------------------------

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new AlignerIO instance.

        @param name (string) name of the aligner

        """
        Transcription.__init__(self, name, mintime, maxtime)

    # ------------------------------------------------------------------------

    def read_list(self,filename):
        """
        Read a list file (units start and end time).

        @param filename is the list file name.
        @raise IOError

        """
        with codecs.open(filename, 'r', encoding) as fp:
            lines = fp.readlines()

        _units = []
        # Each line corresponds to a track,
        # with a couple 'start end' of float values.
        for line in lines:
            line = ToStrip(line)
            _tab = line.split(" ")
            if len(_tab)>=2:
                _units.append( (float(_tab[0]),float(_tab[1])) )
            elif len(_tab)==1:
                # last line indicates the duration of the wav file.
                _units.append( (float(_tab[0]),0.) )

        return _units

    # ------------------------------------------------------------------

    def read(self, dirname, listfilename, mapping, tokens=True):
        """
        Read a set of alignment files and set it as a tier in a transcription.

        @param dirname is the input directory containing a set of unit

        """
        radius = 0.005

        # Verify if the directory exists
        if not os.path.exists( dirname ):
            raise IOError("Missing directory: " + dirname+".\n")

        # Create new tiers
        itemp = self.NewTier("PhonAlign")
        if tokens is True:
            itemw = self.NewTier("TokensAlign")

        # Read the file.list (the list of units + the wav duration)
        units = []
        try:
            units = self.read_list( listfilename )
        except Exception as e:
            raise IOError("Get list of tracks: "+str(e))

        # Get all unit alignment file names (default file names of write_tracks())
        dirlist  = glob.glob( os.path.join(dirname, "track_*palign") )
        dirlist += glob.glob( os.path.join(dirname, "track_*mlf") )
        ntracks = len(dirlist)
        if ntracks == 0:
            raise IOError('No tracks were time-aligned.')

        # The number of alignment files must correspond
        # to the number of units in the "list" file.
        if (len(units)-1) != ntracks:
            raise IOError('Inconsistency between expected nb of tracks '+str(len(units)-1)+' and nb track files '+str(ntracks))

        # Explore each unit to get alignments
        wavend,unitend = units[ntracks] # Get the wav duration
        track = 1
        loc_s = 0.
        loc_e = 0.
        while track <= ntracks:

            # Get real start and end time values of this unit.
            unitstart,unitend = units[(track-1)]

            # Silences were not time-aligned. We add back them now.
            if loc_e < unitstart:
                # An empty interval between 2 units...
                time = TimeInterval(TimePoint(loc_e,radius), TimePoint(unitstart,radius))
                annotation = Annotation(time, Label("#"))
                itemp.Append(annotation)
                if tokens is True:
                    itemw.Append(annotation.Copy())

            # Get phoneme alignments and put them into the tier

            try:
                basename = os.path.join(dirname, "track_%06d"%track)
                (_phonannots,_wordannots) = self.read_aligned(basename)

                # Map-back the phone set
                mapping.set_keepmiss( True )
                mapping.set_reverse( False )

                for i,p in enumerate(_phonannots):
                    (loc_s,loc_e,label,score) = p
                    label = mapping.map_entry(label)

                    # shift to the real value, from the start of the unit
                    loc_s += unitstart
                    loc_e += unitstart

                    # force last phoneme to reach to the end of the unit
                    if i == (len(_phonannots)-1):
                        loc_e = unitend

                    # append phoneme in the tier
                    annotation = Annotation(TimeInterval(TimePoint(loc_s,radius), TimePoint(loc_e,radius)), Label(Text(label,score)))
                    itemp.Append(annotation)

            except Exception as e:
                #import traceback
                #print(traceback.format_exc())
                if unitstart < unitend:
                    annotation = Annotation(TimeInterval(TimePoint(unitstart,radius), TimePoint(unitend,radius)), Label(""))
                    itemp.Append(annotation)

            # Tokens
            if tokens is True:
                try:

                    for i,t in enumerate(_wordannots):
                        (loc_s,loc_e,label,score) = t
                        loc_s += unitstart
                        loc_e += unitstart
                        if i==(len(_wordannots)-1):
                            loc_e = unitend

                        annotationw = Annotation(TimeInterval(TimePoint(loc_s,radius), TimePoint(loc_e,radius)), Label(label,score))
                        itemw.Append(annotationw)

                except Exception:
                    if unitstart < unitend:
                        itemw.Append(Annotation(TimeInterval(TimePoint(unitstart,radius), TimePoint(unitend,radius))))

            track += 1
        # End while
        # A silence at the end?
        # ... Extend the transcription to the end of the wav.
        if (loc_e+0.01) < wavend:
            try:
                time = TimeInterval(TimePoint(loc_e,radius), TimePoint(wavend,0.))
                annotation = Annotation(time, Label("#"))
                itemp.Append(annotation)
            except Exception as e:
                raise IOError('Error %s with the audio file duration, for track %d.'%(str(e),(track-1)))
            if tokens is True:
                try:
                    itemw.Append(annotation.Copy())
                except Exception as e:
                    raise IOError('Error %s with the audio file duration, for track %d.'%(str(e),(track-1)))

        # Adjust Radius
        if itemp.GetSize()>1:
            itemp[-1].GetLocation().SetEndRadius(0.)
            if tokens is True:
                itemw[-1].GetLocation().SetEndRadius(0.)

        if tokens is True:
            try:
                self._hierarchy.addLink('TimeAlignment', itemp, itemw)
            except Exception as e:
                logging.info('Error while assigning hierarchy between phonemes and tokens: %s'%(str(e)))
                pass

    # ------------------------------------------------------------------

    def read_aligned(self, basename):
        """
        Find an aligned file and read it.

        @param basename (str - IN) Track file name without extension
        @return Two lists of tuples with phones and words

        """
        for ext in AlignerIO.EXTENSIONS:
            trackname = basename + "." + ext
            if os.path.isfile(trackname) is True:
                if ext == "palign":
                    return self.read_palign( trackname )
                else:
                    return self.read_mlf( trackname )

        raise IOError('No time-aligned file for %s'%basename)

    # ------------------------------------------------------------------

    def read_palign(self, filename):
        """
        Read an alignment file in the standard format of Julius CSR engine.

        @param filename (str - IN) The input file name.
        @return Two lists of tuples:
            - (start-time end-time phoneme score)
            - (start-time end-time word score)

        """
        _phonalign = []
        _wordalign = []

        phonidx = -1     # phoneme index
        loc_s = 0.       # phoneme start time
        loc_e = 0.       # phoneme end time
        phonlist = []
        wordseq  = []
        scores   = []

        with codecs.open(filename, 'r', encoding) as fp:
            lines = fp.readlines()

        for line in lines:
            # Each line is either a new annotation or nothing interesting!
            line = ToStrip(line)

            if line.startswith("=== begin forced alignment ==="):
                phonidx = 0

            elif line.startswith("=== end forced alignment ==="):
                phonidx = -1

            elif line.startswith("phseq1:"):
                line = line[7:]
                line = ToStrip(line)

                wordseq = line.split('|')
                # get indexes of each word
                wordlist = []
                _idx = -1
                for w in wordseq:
                    _wrdphseq = w.strip().split()
                    _idx += len(_wrdphseq)
                    wordlist.append( _idx )
                # get the list of phonemes (without word segmentation)
                line = line.replace('|','')
                line = ToStrip(line)
                phonlist = line.split()

            elif line.startswith('cmscore1:'):
                line = line[9:]
                # confidence score of the pronunciation of each token
                scores = [float(s) for s in line.split()]
                if len(scores)==0:
                    scores = [0]

            elif line.startswith('sentence1:'):
                line = line[10:]
                # each token
                tokens = line.split()
                if len(tokens)==0:
                    tokens = [""]

            elif line.startswith('[') and phonidx>-1:
                # New phonemes
                line = line.replace("[","")
                line = line.replace("]","")
                line = ToStrip(line)
                tab = line.split(" ")
                # Column 1: begin time
                # Column 2: end time
                # Column 3: score of the segmentation (log proba)
                # Column 4: triphone used
                # ATTENTION: Julius indicates time in centiseconds!
                loc_s = (float( tab[0] ) / 100.)
                loc_e = (float( tab[1] ) / 100.)
                if len(tab)>3:
                    _phonalign.append( (loc_s, loc_e, phonlist[phonidx], tab[2]) )
                else:
                    _phonalign.append( (loc_s, loc_e, "", tab[2]) )
                phonidx = phonidx+1

        # Put real phoneme and adjust time values
        # Create wordalign
        wordidx = 0     # word index
        wordloc_s = 0.  # word start time
        _modifiedphonalign = [] # the real phoneme segmentation... we hack...
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
                loc_e = nextloc_s
            _modifiedphonalign.append( (loc_s, loc_e, _phonalign[phonidx][2], _phonalign[phonidx][3]) )

            loc_s = loc_e
            # add also the word?
            if phonidx == wordlist[wordidx]:
                _wordalign.append( (wordloc_s, loc_e, tokens[wordidx],scores[wordidx]) )
                wordidx = wordidx + 1
                wordloc_s = loc_e

        # last word, or the only entry in case of empty interval...
        if len(wordseq)-1 == wordidx:
            _wordalign.append( (wordloc_s, loc_e, tokens[wordidx-1],scores[wordidx-1]))

        return (_modifiedphonalign,_wordalign)

    # ------------------------------------------------------------------

    def read_mlf(self, filename):
        """
        Read an alignment file (a mlf file).

        @param filename: is the input file (a HVite mlf output file).
        @raise IOError
        @return: 2 lists of tuples:
            - (start-time end-time phoneme -30)
            - (start-time end-time word 0)

        """
        phon = []
        word = []
        samplerate=10e6

        with codecs.open(filename, 'r', encoding) as source:

            line = source.readline() # header
            while True: # loop over text
                #name = re.match('\"(.*)\"', source.readline().rstrip())
                name = source.readline().rstrip()
                if name:
                    first = True
                    wmrkp = ''
                    wmrk = ''
                    wsrt = 0.
                    wend = 0.
                    while 1: # loop over the lines in each grid
                        line = source.readline().rstrip().split()

                        if len(line) == 5: # word on this line
                            if first is True:
                                pmin = round(float(line[0]) / samplerate, 5)
                                first = False
                            else:
                                pmin = round(float(line[0]) / samplerate, 5) + 0.005
                            pmax = round(float(line[1]) / samplerate, 5) + 0.005
                            if pmin != pmax: # for sp
                                phon.append( (pmin, pmax, line[2], -30.) )
                            if wmrk:
                                wmrkp = wmrkp[:-1]
                                word.append( ( wsrt, wend, wmrk, 0) )
                            wmrkp = line[2] + '-'
                            wmrk = line[4]
                            wsrt = pmin
                            wend = pmax

                        elif len(line) == 4: # just phone
                            if first is True:
                                pmin = round(float(line[0]) / samplerate, 5)
                                first = False
                            else:
                                pmin = round(float(line[0]) / samplerate, 5) + 0.005
                            pmax = round(float(line[1]) / samplerate, 5) + 0.005
                            wmrkp = wmrkp + line[2] + "-"
                            if line[2] == 'sp' and pmin != pmax:
                                if wmrk:
                                    wmrkp = wmrkp[:-1]
                                    word.append( (wsrt, wend, wmrk, 0) )
                                wmrk = line[2]
                                wmrkp = ''
                                wsrt = pmin
                                wend = pmax
                            elif pmin != pmax: # for sp
                                phon.append( (pmin, pmax, line[2], -30) )
                            wend = pmax

                        else: # it's a period
                            wmrkp = wmrkp[:-1]
                            word.append( (wsrt, wend - 0.005, wmrk, 0) )
                            break
                else:
                    break

        # Before returning the result... must check if HVite added silences
        # at the beginning and at the end of the IPU (if any, remove them).
        if len(word)>0:
            if "SENT" in word[0][2]:
                newword = (word[0][0], word[1][1], word[1][2], word[1][3])
                newphon = (phon[0][0], phon[1][1], phon[1][2], phon[1][3])
                word.pop(0)
                phon.pop(0)
                word.pop(0)
                phon.pop(0)
                word.insert(0,newword)
                phon.insert(0,newphon)
            if "SENT" in word[-1][2]:
                word.pop()
                phon.pop()

        return (phon,word)

    # ------------------------------------------------------------------

    def write_palign(self, phoneslist, tokenslist, alignments, outputfilename):
        """
        Write an alignment output file.

        @param phoneslist (list) List with the phonetization of each token
        @param tokenslist (list) List with each token
        @param alignments (list) List of tuples: (start-time end-time phoneme)
        @param outputfilename (str) The output file name (a Julius-like output).

        """
        if len(tokenslist) != len(phoneslist):
            tokenslist = ["w_"+str(i+1) for i in range(len(phoneslist))]

        with codecs.open(outputfilename, 'w', encoding) as fp:

            fp.write("----------------------- System Information begin ---------------------\n")
            fp.write("\n")
            fp.write("                         SPPAS Basic Alignment\n")
            fp.write("\n")
            fp.write("----------------------- System Information end -----------------------\n")

            fp.write("\n### Recognition: 1st pass\n")

            fp.write("pass1_best: ")
            fp.write("%s\n"%" ".join(tokenslist))

            fp.write("pass1_best_wordseq: ")
            fp.write("%s\n"%" ".join(tokenslist))

            fp.write("pass1_best_phonemeseq: ")
            fp.write("%s\n"%" | ".join(phoneslist))

            fp.write("\n### Recognition: 2nd pass\n")

            fp.write("ALIGN: === phoneme alignment begin ===\n")

            fp.write("sentence1: ")
            fp.write("%s\n"%" ".join(tokenslist))

            fp.write("wseq1: ")
            fp.write("%s\n"%" ".join(tokenslist))

            fp.write("phseq1: ")
            fp.write("%s\n"%" | ".join(phoneslist))

            fp.write("cmscore1: ")
            fp.write("%s\n"%("0.000 "*len(phoneslist)))

            fp.write("=== begin forced alignment ===\n")
            fp.write("-- phoneme alignment --\n")
            fp.write(" id: from  to    n_score    unit\n")
            fp.write(" ----------------------------------------\n")
            for tv1,tv2,phon in alignments:
                fp.write("[ %d " % tv1)
                fp.write(" %d]" % tv2)
                fp.write(" -30.000000 "+str(phon)+"\n")
            fp.write("=== end forced alignment ===\n")

            fp.close()

    # ------------------------------------------------------------------

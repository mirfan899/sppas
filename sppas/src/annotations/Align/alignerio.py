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
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

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

# ----------------------------------------------------------------------------
ENCODING='utf-8'
# ----------------------------------------------------------------------------

class AlignerIO( Transcription ):
    """
    Create a Transcription() object from a set of alignment files.

    """

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new Aligner IO instance.

        @param alignerid (string) name of the aligner

        """
        Transcription.__init__(self, name, mintime, maxtime)

    # End __init__
    # ------------------------------------------------------------------------


    def read_list(self,filename):
        """
        Read a list file (units start and end time).

        @param filename is the list file name.
        @raise IOError

        """
        try:
            fp = codecs.open(filename, 'r', ENCODING)
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


    def read(self, dirname, listfilename, mapping, expend=True, extend=False, tokens=True):
        """
        Read a set of alignment files and set it as a tier in a transcription.

        @param dirname is the input directory containing a set of unit
        @param expend last phoneme to the unit duration
        @param extend only concerns the silence at the end of the file

        @raise IOError
        @raise Exception

        """
        radius = 0.005

        # Verify if the directory exists
        if not os.path.exists( dirname):
            raise IOError("Missing directory " + dirname+". \n")

        # Create 3 new tiers
        itemp = self.NewTier("PhonAlign")
        if tokens is True:
            itemt = self.NewTier("PhnTokAlign")
            itemw = self.NewTier("TokensAlign")

        # Read the file.list (the list of units + the wav duration)
        units = []
        try:
            units = self.read_list( listfilename )
        except Exception as e:
            raise IOError("Get list of tracks: "+str(e))

        # Get all unit alignment file names (default file names of write_tracks())
        dirlist = glob.glob(os.path.join(dirname, "track_*palign"))
        dirlist += glob.glob(os.path.join(dirname, "track_*mlf"))
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
                    time = TimeInterval(TimePoint(0.,0.), TimePoint(unitstart,radius))
                    annotation = Annotation(time, Label("#"))
                    itemp.Append(annotation)
                    #print "Append in phonemes 1:",annotation

                    if tokens is True:
                        #print "Append in tokensw and tokenst 1:",annotation
                        itemt.Append(annotation.Copy())
                        itemw.Append(annotation.Copy())

            else:
                if loc_e < unitstart:
                    # Add an empty interval between 2 units...
                    time = TimeInterval(TimePoint(loc_e,radius), TimePoint(unitstart,radius))
                    annotation = Annotation(time, Label("#"))
                    #print "Append in phonemes 2:",annotation
                    itemp.Append(annotation)

                    if tokens is True:
                        #print "Append in tokensw and tokenst 2:",annotation
                        itemt.Append(annotation.Copy())
                        itemw.Append(annotation.Copy())

            # Get phoneme alignments and put them into the tier

            try:
                trackname = os.path.join(dirname, "track_%06d.palign"%track)
                if not os.path.isfile(trackname):
                    trackname = os.path.join(dirname, "track_%06d.mlf"%track)
                    (_phonannots,_wordannots) = self.read_mlf( trackname )
                else:
                    (_phonannots,_wordannots) = self.read_palign( trackname )

                # Map-back the phoneset
                mapping.set_keepmiss( True )
                mapping.set_reverse( False )
                i = 0
                for t in _phonannots:
                    _phonannots[i] = (t[0], t[1], mapping.map_entry(t[2]), t[3])
                    i = i+1

                # Map-back the phoneset
                i = 0
                for t in _wordannots:
                    _wordannots[i] = (t[0], t[1], mapping.map(t[2]))
                    i = i+1

                # phonemes
                idx = 1
                for loc_s,loc_e,label,score in _phonannots:

                    # Assign real end value
                    loc_s += unitstart
                    # last phoneme... extend to the wav duration?
                    if idx==len(_phonannots) and track==ntracks and extend is True:
                        loc_e = wavend
                    # last unit phoneme... extend to the unit duration?
                    elif idx==len(_phonannots) and expend is True:
                        loc_e = unitend
                    else:
                        loc_e += unitstart

                    annotation = Annotation(TimeInterval(TimePoint(loc_s,radius), TimePoint(loc_e,radius)), Label(Text(label,score)))
                    itemp.Append(annotation)
                    idx += 1
            except Exception:
                if unitstart<unitend:
                    annotation = Annotation(TimeInterval(TimePoint(unitstart,radius), TimePoint(unitend,radius)), Label(""))
                    itemp.Append(annotation)
                    #print " *** exception Append in phonemes:",annotation

            # Get phoneme alignments and put them into the TOKEN'S tier

            if tokens is True:
                try:
                    # for tokens
                    transname = os.path.join(dirname, "track_%06d.trans"%track)
                    f = codecs.open(transname, 'r', ENCODING)
                    readtokens = f.readline()
                    # Remove multiple spaces
                    f.close()
                    readtokens = re.sub("[ ]+", " ", readtokens)
                    tokenlist = readtokens.strip().split(" ")

                    idx = 1
                    for loc_s,loc_e,label in _wordannots:
                        loc_s += unitstart
                        # last phontoken... extend to the wav duration?
                        if idx==len(_wordannots) and track==ntracks and extend is True:
                            loc_e = wavend
                        # last phon-word... extend to the unit duration?
                        elif idx==len(_wordannots) and expend==True:
                            loc_e = unitend
                        else:
                            loc_e += unitstart

                        if len(tokenlist) == len(_wordannots):
                            annotationt = Annotation(TimeInterval(TimePoint(loc_s,radius), TimePoint(loc_e,radius)), Label(label))
                            #print "Append in tokenst 3:",annotationt
                            itemt.Append(annotationt)
                            annotationw = Annotation(TimeInterval(TimePoint(loc_s,radius), TimePoint(loc_e,radius)), Label(tokenlist[idx-1]))
                            #print "Append in tokensw 3:",annotationw
                            itemw.Append(annotationw)

                        idx = idx + 1
                except Exception:
                    if unitstart<unitend:
                        itemt.Append(Annotation(TimeInterval(TimePoint(unitstart,radius), TimePoint(unitend,radius))))
                        itemw.Append(Annotation(TimeInterval(TimePoint(unitstart,radius), TimePoint(unitend,radius))))
                        #print " *** exception Append in tokennw and tokenst:",Annotation(TimeInterval(TimePoint(unitstart,radius), TimePoint(unitend,radius)))

            track += 1
        # End while
        # A silence at the end?
        # ... Extend the transcription to the end of the wav.
        if (loc_e+0.01) < wavend:
            try:
                time = TimeInterval(TimePoint(loc_e,radius), TimePoint(wavend,0.))
                annotation = Annotation(time, Label("#"))
                itemp.Append(annotation)
                #itemp.SetRadius(0.005)
            except Exception as e:
                raise IOError('Error %s with the wav duration, for track %d.'%(str(e),(track-1)))
            if tokens is True:
                try:
                    itemt.Append(annotation.Copy())
                    itemw.Append(annotation.Copy())
                except Exception as e:
                    raise IOError('Error %s with the wav duration, for track %d.'%(str(e),(track-1)))

        # Adjust Radius
        if itemp.GetSize()>1:
#             itemp.SetRadius(0.005)
#             itemp[0].GetLocation().GetBegin().SetRadius(0.)
            itemp[-1].GetLocation().SetEndRadius(0.)
            if tokens is True:
#                 itemt.SetRadius(0.005)
#                 itemw.SetRadius(0.005)
#                 itemt[0].GetLocation().GetBegin().SetRadius(0.) # first timepoint
                itemt[-1].GetLocation().SetEndRadius(0.)  # last
#                 itemw[0].GetLocation().GetBegin().SetRadius(0.)
                itemw[-1].GetLocation().SetEndRadius(0.)

        if tokens is True:
            try:
                self._hierarchy.addLink('TimeAlignment', itemp, itemt)
            except Exception as e:
                logging.info('Error while assigning hierarchy between phonemes and tokens: %s'%(str(e)))
                pass
            try:
                self._hierarchy.addLink('TimeAssociation', itemt, itemw)
            except Exception as e:
                logging.info('Error while assigning hierarchy between tokens and phntokens: %s'%(str(e)))
                pass

    # End read
    # ------------------------------------------------------------------


    def read_palign(self, filename):
        """
        Read an alignment file.

        @param filename: is the input file (a Julius output).
        @raise IOError:
        @return: 2 lists of tuples:
            - (start-time end-time phoneme score)
            - (start-time end-time word)

        """
        _phonalign = []
        _wordalign = []
        try:
            fp = codecs.open(filename, 'r', ENCODING)
        except IOError,e:
            raise IOError("Input error with file " + filename + ": " + str(e) + "\n")

        # Each line is either a new annotation or nothing interesting!
        phonidx = -1     # phoneme index
        loc_s = 0        # phoneme start time
        loc_e = 0        # phoneme end time
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
                line = line.replace("[","")
                line = line.replace("]","")
                line = self.__clean(line)
                tab = line.split(" ")
                # Column 1: begin time
                # Column 2: end time
                # Column 3: score
                # Column 4: triphone used
                # ATTENTION: Julius indicates time in centiseconds!
                loc_s = (float( tab[0] ) / 100.)
                loc_e = (float( tab[1] ) / 100.)
                _phonalign.append( (loc_s, loc_e, tab[3], tab[2]) )

        fp.close()

        # Put real phoneme and adjust time values
        wordidx = 0      # word index
        wordloc_s  = 0.  # word start time
        _modifiedphonalign = [] # the real phoneme (not the triphone)
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
            # But difficulty to interpret Julius values...
            if loc_e < nextloc_s:
                # Since SPPAS 1.4.4, I was setting next loc_s to the current loc_e
                # I tried to the average between both values.
                # loc_e = ( nextloc_s + loc_e ) / 2.0
                # I got better results if I set the current loc_e as the next loc_s
                # loc_e = nextloc_s
                # AND FINALLY, THE BEST IS:
                loc_e = nextloc_s + ( ( nextloc_s - loc_e) / 2.0 )

            _modifiedphonalign.append( (loc_s, loc_e, phonlist[phonidx], _phonalign[phonidx][3]) )
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


    def read_mlf(self, filename):
        """
        Read an alignment file (a mlf file).

        @param filename: is the input file (a HVite mlf output file).
        @raise IOError
        @return: 2 lists of tuples:
            - (start-time end-time phoneme)
            - (start-time end-time word)

        """
        phon = []
        word = []
        phontok = []
        samplerate=10e6

        with codecs.open(filename, 'r', ENCODING) as source:

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
                                word.append( ( wsrt, wend, wmrk) )
                                phontok.append( ( wsrt, wend, wmrkp) )
                            wmrkp = line[2] + '.'
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
                            wmrkp = wmrkp + line[2] + '.'
                            if line[2] == 'sp' and pmin != pmax:
                                if wmrk:
                                    wmrkp = wmrkp[:-1]
                                    word.append( (wsrt, wend, wmrk) )
                                    phontok.append( (wsrt, wend, wmrkp) )
                                wmrk = line[2]
                                wmrkp = ''
                                wsrt = pmin
                                wend = pmax
                            elif pmin != pmax: # for sp
                                phon.append( (pmin, pmax, line[2], -30) )
                            wend = pmax

                        else: # it's a period
                            wmrkp = wmrkp[:-1]
                            word.append( (wsrt, wend - 0.005, wmrk) )
                            phontok.append( (wsrt, wend - 0.005, wmrkp) )
                            break
                else:
                    break

        # Before returning the result... must check if HVite added silences
        # at the beginning and at the end of the IPU (if any, remove them).
        if len(word)>0:
            if "SENT" in word[0][2]:
                newword = (phontok[0][0], phontok[1][1], phontok[1][2])
                newphon = (phon[0][0], phon[1][1], phon[1][2], phon[1][3])
                phontok.pop(0)
                phon.pop(0)
                phontok.pop(0)
                phon.pop(0)
                phontok.insert(0,newword)
                phon.insert(0,newphon)
            if "SENT" in word[-1][2]:
                phontok.pop()
                phon.pop()

        return (phon,phontok)

    # End read_mlf
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------

    def __clean(self,sstr):
        __s = sstr.strip()
        __s = re.sub("\s+" , " ", __s)
        return __s

    # ------------------------------------------------------------------

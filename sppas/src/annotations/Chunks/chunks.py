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
# File: chunks.py
# ----------------------------------------------------------------------------

import os
import logging


import sppas.src.annotationdata.aio
import sppas.src.audiodata.autils as autils
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.label.text import Text
from sppas.src.resources.patterns import Patterns
from sppas.src.resources.rutils import to_strip
from sppas.src.resources.mapping import Mapping

import sppas.src.annotations.Align.aligners as aligners
from ..Align.aligners.alignerio import AlignerIO
from .. import UNKSTAMP
from .spkrate import SpeakerRate
from .anchors import AnchorTier

# ----------------------------------------------------------------------------

class Chunks( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Write tokenized-phonetized segments from Tiers.

    """
    def __init__(self, model):
        """

        """
        self._aligner = aligners.instantiate(model,"julius")
        self._aligner.set_infersp(False)
        self._aligner.set_outext("walign")

        # Map phoneme names from  SAMPA model-specific
        mappingfilename = os.path.join( model, "monophones.repl")
        if os.path.isfile( mappingfilename ):
            try:
                self._mapping = Mapping( mappingfilename )
            except Exception:
                self._mapping = Mapping()
        else:
            self._mapping = Mapping()

        self._alignerio  = AlignerIO()
        self._spkrate    = SpeakerRate()
        self._radius = 0.005

        self.N = 5     # initial N-gram to search the anchors
        self.NMIN = 3  # minimum N-gram to search the anchors
        self.W = 6.    # initial windows delay to search the anchors
        self.WMIN = 3. # minimum windows delay to search the anchors
        self.NBT = 12  # maximum number of tokens for chunks (and holes)
        self.ANCHORS = True   # Append anchors into the result
        self.SILENCES = False # Search automatically silences before anchors

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_ngram_init(self):
        return self.N

    def get_ngram_min(self):
        return self.NMIN

    def get_windelay_init(self):
        return self.W

    def get_windelay_min(self):
        return self.WMIN

    def get_chunk_maxsize(self):
        return self.NBT

    def get_anchors(self):
        return self.ANCHORS

    def get_silences(self):
        return self.SILENCES

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set_ngram_init(self, N):
        if N < 2 or N > 20:
            raise ValueError('Bad value for N-gram.')
        self.N = N

    def set_ngram_min(self, N):
        if N < 2 or N > 20:
            raise ValueError('Bad value for N-gram.')
        self.NMIN = N

    def set_windelay_init(self, W):
        if W < 1. and W > 60.:
            raise ValueError('Bad value for a window delay.')
        self.W = W

    def set_windelay_min(self, W):
        if W < 1. and W > 60.:
            raise ValueError('Bad value for a window delay.')
        self.WMIN = W

    def set_chunk_maxsize(self, T):
        if T < 2 and T > 200:
            raise ValueError('Bad value for a chunk size.')
        self.NBT = T

    def set_anchors(self, value):
        self.ANCHORS = bool(value)

    def set_silences(self, value):
        self.SILENCES = bool(value)

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def create_chunks(self, inputaudio, phontier, toktier, diralign):
        """
        Create time-aligned tiers from raw intput tiers.

        @param phontier (Tier - IN) the tier with phonetization
        @param toktier  (Tier - IN) the tier with tokenization to split
        @param diralign (str - IN) the directory to work.

        """
        trsoutput = Transcription("Chunks")

        # Extract the audio channel
        channel = autils.extract_audio_channel( inputaudio,0 )
        channel = autils.format_channel( channel,16000,2 )

        # Extract the lists of tokens and their corresponding pronunciations
        pronlist = self._tier2raw( phontier,map=True ).split()
        toklist  = self._tier2raw( toktier, map=False ).split()
        if len(pronlist) != len(toklist):
            raise IOError("Inconsistency between the number of items in phonetization %d and tokenization %d."%(len(pronlist),len(toklist)))

        # At a first stage, we'll find anchors.
        anchortier = AnchorTier()
        anchortier.set_duration( channel.get_duration() )
        anchortier.set_extdelay(1.)
        anchortier.set_outdelay(0.5)

        # Search silences and use them as anchors.
        if self.SILENCES is True:
            anchortier.append_silences( channel )

        # Estimates the speaking rate (amount of tokens/sec. in average)
        self._spkrate.eval_from_duration( channel.get_duration(), len(toklist) )

        # Multi-pass ASR to find anchors
        A = -1      # number of anchors in the preceding pass
        N = self.N  # decreasing N-gram value
        W = self.W  # decreasing window length

        while A != anchortier.GetSize() and anchortier.check_holes_ntokens( self.NBT ) is False:

            anchortier.set_windelay( W )
            A = anchortier.GetSize()

            logging.debug(" =========================================================== ")
            logging.debug(" Number of anchors: %d"%A)
            logging.debug(" N: %d"%N)
            logging.debug(" W: %d"%W)

            # perform ASR and append new anchors in the anchor tier (if any)
            self._asr(toklist, pronlist, anchortier, channel, diralign, N)

            # append the anchor tier as intermediate result
            if self.ANCHORS is True and A != anchortier.GetSize():
                self._append_tier(anchortier,trsoutput)
                sppas.src.annotationdata.aio.write( os.path.join(diralign,"ANCHORS-%d.xra"%anchortier.GetSize()),trsoutput )

            # prepare next pass
            W = max(W-1., self.WMIN)
            N = max(N-1,  self.NMIN)

        # Then, anchors are exported as tracks.
        tiert = anchortier.export(toklist)
        tiert.SetName("Chunks-Tokenized")
        tierp = anchortier.export(pronlist)
        tierp.SetName("Chunks-Phonetized")
        trsoutput.Append(tiert)
        trsoutput.Append(tierp)

        return trsoutput

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _append_tier(self, tier, trs):
        """
        Append a copy of Tier in self.

        """
        copytier = Tier("Anchors-"+str(tier.GetSize()))
        for a in tier:
            ac = a.Copy()
            try:
                copytier.Append( ac )
            except Exception:
                logging.debug("Append of annotation in tier failed: %s"%ac)

        trs.Append(copytier)

    # ------------------------------------------------------------------------

    def _asr(self, toklist, pronlist, anchortier, channel, diralign, N):
        """
        Windowing on the audio to perform ASR and find anchors.

        """
        # init
        fromtime  = 0.
        totime    = float(N)
        fails     = 0
        maxtime = channel.get_duration()

        # windowing
        logging.debug(" ... Windowing the audio file:")
        while fromtime < maxtime and fails < 3:

            try:
                # Fix exact time range of this window...
                (fromtime,totime) = anchortier.fix_window(fromtime)
                if totime > maxtime:
                    totime = maxtime
                if fromtime >= totime:
                    logging.debug('Stop windowing: %f %f.'%(fromtime,totime))
                    break

                # Fix token range of this window...
                (fromtoken,totoken) = self._fix_trans_interval(fromtime,totime,toklist,anchortier)
                if fromtoken >= len(toklist):
                    break

                logging.debug(" ... ... window: ")
                logging.debug("... ... ... time  from %.4f to %.4f."%(fromtime,totime))
                logging.debug("... ... ... token from %d to %d."%(fromtoken,totoken))
                logging.debug("... ... ... REF: %s"%(" ".join( toklist[fromtoken:totoken] )))
                logging.debug("... ... ... HYP: ")

                # Fix anchors of this window
                anchors = self._fix_window_asr(fromtime, totime, fromtoken, totoken, channel, pronlist, toklist, diralign, N)

                if len(anchors) > 0:
                    self._add_anchors( anchors, anchortier )
                    # Prepare next window
                    fromtime = anchors[-1][1]
                    fails = 0
                else:
                    fromtime = totime
                    logging.debug("... ... ... No anchor found.")

            except Exception:
                # try your luck in the next window...
                import traceback
                logging.info("%s"%str(traceback.format_exc()))
                fromtime = totime
                fails = fails + 1

    # ------------------------------------------------------------------------

    def _fix_trans_interval(self, fromtime, totime, toklist, anchortier):
        """
        Fix the window on the transcript.

        """
        # previous and following anchors
        af = anchortier.near_indexed_anchor( fromtime, -1 )
        at = anchortier.near_indexed_anchor( totime,    1 )

        fexact = False
        wdelay = totime-fromtime
        ntokens = self._spkrate.ntokens(wdelay)+1

        # an anchor is not too far away before
        if af is not None and af.GetLocation().GetEnd() >= (fromtime-wdelay):
            # we have an exact position in the token list
            fromtoken = af.GetLabel().GetTypedValue() + 1
            fexact = True
        else:
            # we approximate with the speaking rate
            fromtoken = max(0, self._spkrate.ntokens( fromtime ) - ntokens)

        # an anchor is not too far away after
        if at is not None and at.GetLocation().GetBegin() <= (totime+wdelay):
            # we have an exact position in the token list
            totoken = at.GetLabel().GetTypedValue() - 1
        else:
            # we approximate with the speaking rate
            if fexact is True:
                totoken = min(len(toklist), fromtoken + int(1.5*ntokens))
            else:
                totoken = min(len(toklist), self._spkrate.ntokens( totime ) + ntokens)

        # ...
        if fromtoken >= totoken:
            fromtoken = max(0, fromtoken-1)
            totoken   = min(len(toklist), fromtoken+2)

        return (fromtoken,totoken)

    # ------------------------------------------------------------------------

    def _fix_window_asr(self, fromtime, totime, fromtoken, totoken, channel, pronlist, toklist, diralign, N):
        """
        Fix asr result in a window.
        Return the list of anchors the ASR found in that window.

        """
        # create audio file
        fnw = os.path.join(diralign, "asr")
        fna = os.path.join(diralign, "asr.wav")
        trackchannel = autils.extract_channel_fragment( channel, fromtime, totime, 0.2)
        autils.write_channel( fna, trackchannel )

        # call the ASR engine to recognize tokens of this track
        self._aligner.set_phones( " ".join( pronlist[fromtoken:totoken] ) )
        self._aligner.set_tokens( " ".join(  toklist[fromtoken:totoken] ) )
        self._aligner.run_alignment(fna, fnw, N)

        # get the tokens time-aligned by the ASR engine
        wordalign = self._alignerio.read_aligned(fnw)[1]  # (starttime,endtime,label,score)
        wordalign = self._adjust_asr_result(wordalign, fromtime, 0.2)

        # ignore the last word: we can't know if the word is entire or was cut
        if len(wordalign) > 3:
            wordalign.pop()

        # list of tokens the ASR automatically time-aligned
        tman = [token for token in toklist[fromtoken:totoken]]
        # list of tokens manually transcribed
        tasr = [(token,score) for (start,end,token,score) in wordalign]

        # Find matching tokens: the anchors
        matchingslist = self._fix_matchings_list( tman,tasr,N )

        anchors = []
        for match in matchingslist:
            i  = match[0]   # ref
            hi = match[1]   # hyp
            s = wordalign[hi][0]
            e = wordalign[hi][1]
            anchors.append( (s,e,fromtoken+i) )

        return anchors

    # ------------------------------------------------------------------------

    def _adjust_asr_result(self, wordsalign, fromtime, silence):
        """
        Adapt wordsalign: remove <s> and </s> then adjust time values.

        """
        # shift all time values of "silence" delta
        for i in range(len(wordsalign)):
            wordsalign[i][0] = wordsalign[i][0] - silence
            wordsalign[i][1] = wordsalign[i][1] - silence

        # remove the first <s> and the last </s>
        wordsalign.pop(0)
        wordsalign.pop()

        if len(wordsalign) == 0:
            raise IOError("The ASR failed to find tokens.")

        # the first token was recognized during the silence we prepended!!!!
        if wordsalign[0][1] < 0:
            wordsalign.pop(0)
            wordsalign[0][0] = 0.

        # the first token was starting during the silence we prepended.
        wordsalign[0][0] = max( 0. , wordsalign[0][0] )

        # shift all local time values to the real time values in the audioinput
        for i in range(len(wordsalign)):
            wordsalign[i][0] = wordsalign[i][0] + fromtime
            wordsalign[i][1] = wordsalign[i][1] + fromtime
            logging.debug("... ... ... ... %s - %f"%(wordsalign[i][2],wordsalign[i][3]))

        return wordsalign

    # ------------------------------------------------------------------------

    def _fix_matchings_list(self, ref, hyp, N ):
        """
        Create the list of matches between ref and hyp.

        """
        pattern = Patterns()
        pattern.set_ngram( N )
        m3 = pattern.ngram_matches( ref,hyp )

        if len( m3 ) == 0:
            return []

        # Search for the lowest/highest values in ref/hyp:
        listref = [ v[0] for v in m3 ]
        listhyp = [ v[1] for v in m3 ]
        minr = min( listref )
        maxr = max( listref )
        newref = ref[minr:maxr+1]
        minh = min( listhyp )
        maxh = max( listhyp )
        newhyp = hyp[minh:maxh+1]

        # Do some hypothesis were found several times in the reference?
        if len(listhyp) > len(list(set(listhyp))):

            pattern.set_ngram( N+2 )
            newm3 = pattern.ngram_matches( ref,hyp )
            listref = [ v[0] for v in m3 ]
            listhyp = [ v[1] for v in m3 ]
            if len(listhyp) > len(list(set(listhyp))):
                newm3 = []

        else:
            newm3 = m3

        m1 = []
        if len(hyp) < N:
            pattern = Patterns()
            pattern.set_score(0.9)
            pattern.set_ngram(1)
            pattern.set_gap(1)
            m1 = pattern.ngram_alignments( newref,newhyp )

        return sorted(list(set(m1+newm3)))

    # ------------------------------------------------------------------------

    def _add_anchors(self, anchorlist, anchortier):
        """
        Add anchors in the anchor tier

        """
        if len(anchorlist) == 0:
            return

        logging.debug('... ... ... Anchors:')
        for (s,e,i) in anchorlist:

            # provide overlaps with a previous anchor
            previ = anchortier.Near( s,-1 )
            if previ != -1:
                prevann = anchortier[previ]
                if prevann.GetLocation().GetEnd().GetMidpoint() > s:
                    if prevann.GetLabel().IsSilence():
                        prevann.GetLocation().GetEnd().SetMidpoint(s)
                        if prevann.GetLocation().GetEnd() < prevann.GetLocation().GetBegin():
                            anchortier.Pop(previ)
                    else:
                        s = prevann.GetLocation().GetEnd().SetMidpoint(s)

            # provide overlaps with a following anchor
            nexti = anchortier.Near( e,1 )
            if nexti != -1:
                nextann = anchortier[nexti]
                if nextann.GetLocation().GetBegin().GetMidpoint() < e:
                    if nextann.GetLabel().IsSilence():
                        nextann.GetLocation().GetBegin().SetMidpoint(e)
                        if nextann.GetLocation().GetEnd() < nextann.GetLocation().GetBegin():
                            anchortier.Pop(nexti)
                    else:
                        e = nextann.GetLocation().GetBegin().SetMidpoint(e)

            valid = True
            # previous index must be lesser
            p = anchortier.near_indexed_anchor( s,-1 )
            if p is not None:
                pidx = p.GetLabel().GetTypedValue()
                if i <= pidx:
                    valid = False
                else:
                    # solve a small amount of issues...
                    # duration between the previous and the one we want to add
                    deltatime = s-p.GetLocation().GetEnd().GetMidpoint()
                    if deltatime < 0.2:
                        if (i-10) > pidx:
                            valid=False

            # next index must be higher
            n = anchortier.near_indexed_anchor(e, 1)
            if n is not None and i >= n.GetLabel().GetTypedValue():
                valid = False

            # add the anchor
            if valid is True:
                time  = TimeInterval(TimePoint(s),TimePoint(e))
                label = Label( Text(i,data_type="int") )
                anchortier.Add( Annotation(time,label) )
                logging.debug("... ... ... ... Add: %f %f %d"%(s,e,i))
            else:
                logging.debug("... ... ... ... ... Ignore: %f %f %d"%(s,e,i))

        # Then, fill the very evident holes
        anchortier.fill_evident_holes()

    # ------------------------------------------------------------------------

    def _tier2raw( self,tier,map=False ):
        """
        Return all interval contents into a single string.

        """
        # Map phonemes from SAMPA to the expected ones.
        self._mapping.set_keep_miss(True)
        self._mapping.set_reverse(True)

        raw = ""
        for i,ann in enumerate(tier):
            if ann.GetLabel().IsEmpty() is True:
                logging.info("WARNING: Found an empty annotation label at index %d"%i)
                raw = raw + " sil"
            else: #if ann.GetLabel().IsSilence() is False:
                besttext = ann.GetLabel().GetValue()
                if map is True:
                    besttext = self._mapping.map( besttext )

                if UNKSTAMP in besttext:
                    besttext = besttext.replace(UNKSTAMP, "sil")
                raw = raw + " " + besttext

        return to_strip(raw)

# --------------------------------------------------------------------------

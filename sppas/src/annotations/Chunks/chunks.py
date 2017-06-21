# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.annotations.Chuncks.chunks.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import os
import logging

from sppas import unk_stamp
import sppas.src.annotationdata.aio
import sppas.src.audiodata.autils as autils
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.label.text import Text
from sppas.src.resources.patterns import sppasPatterns
from sppas.src.resources.mapping import sppasMapping
from sppas.src.utils.makeunicode import sppasUnicode

import sppas.src.annotations.Align.aligners as aligners
from ..Align.aligners.alignerio import AlignerIO
from .spkrate import SpeakerRate
from .anchors import AnchorTier

# ----------------------------------------------------------------------------


class Chunks(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Write tokenized-phonetized segments from Tiers.

    """
    def __init__(self, model):
        """ Creates a Chunks instance.
        
        :param model: Acoustic model

        """
        self._aligner = aligners.instantiate(model, "julius")
        self._aligner.set_infersp(False)
        self._aligner.set_outext("walign")

        # Map phoneme names from  SAMPA model-specific
        mappingfilename = os.path.join(model, "monophones.repl")
        if os.path.isfile(mappingfilename):
            try:
                self._mapping = sppasMapping(mappingfilename)
            except Exception:
                self._mapping = sppasMapping()
        else:
            self._mapping = sppasMapping()

        self._alignerio = AlignerIO()
        self._spkrate = SpeakerRate()
        self._radius = 0.005

        self.N = 5      # initial N-gram to search the anchors
        self.NMIN = 3   # minimum N-gram to search the anchors
        self.W = 6.     # initial windows delay to search the anchors
        self.WMIN = 3.  # minimum windows delay to search the anchors
        self.NBT = 12   # maximum number of tokens for chunks (and holes)
        self.ANCHORS = True    # Append anchors into the result
        self.SILENCES = False  # Search automatically silences before anchors

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

    def set_ngram_init(self, n):
        if n < 2 or n > 20:
            raise ValueError('Bad value for N-gram.')
        self.N = n

    def set_ngram_min(self, n):
        if n < 2 or n > 20:
            raise ValueError('Bad value for N-gram.')
        self.NMIN = n

    def set_windelay_init(self, w):
        if w < 1. or w > 60.:
            raise ValueError('Bad value for a window delay.')
        self.W = w

    def set_windelay_min(self, w):
        if w < 1. or w > 60.:
            raise ValueError('Bad value for a window delay.')
        self.WMIN = w

    def set_chunk_maxsize(self, t):
        if t < 2 or t > 200:
            raise ValueError('Bad value for a chunk size.')
        self.NBT = t

    def set_anchors(self, value):
        self.ANCHORS = bool(value)

    def set_silences(self, value):
        self.SILENCES = bool(value)

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def create_chunks(self, inputaudio, phontier, toktier, diralign):
        """ Create time-aligned tiers from raw intput tiers.

        :param inputaudio: (str) Name of the audio file
        :param phontier: (Tier) the tier with phonetization
        :param toktier:  (Tier) the tier with tokenization to split
        :param diralign: (str) the working directory to store temporary data.

        """
        trsoutput = Transcription("Chunks")

        # Extract the audio channel
        channel = autils.extract_audio_channel(inputaudio, 0)
        channel = autils.format_channel(channel, 16000, 2)

        # Extract the lists of tokens and their corresponding pronunciations
        pronlist = self._tier2raw(phontier, map=True).split()
        toklist = self._tier2raw(toktier, map=False).split()
        if len(pronlist) != len(toklist):
            raise IOError("Inconsistency between the number of items in "
                          "phonetization %d and tokenization %d." % (len(pronlist), len(toklist)))

        # At a first stage, we'll find anchors.
        anchor_tier = AnchorTier()
        anchor_tier.set_duration(channel.get_duration())
        anchor_tier.set_ext_delay(1.)
        anchor_tier.set_out_delay(0.5)

        # Search silences and use them as anchors.
        if self.SILENCES is True:
            anchor_tier.append_silences(channel)

        # Estimates the speaking rate (amount of tokens/sec. in average)
        self._spkrate.eval_from_duration(channel.get_duration(), len(toklist))

        # Multi-pass ASR to find anchors
        nb_anchors = -1      # number of anchors in the preceding pass
        ngram = self.N  # decreasing N-gram value
        win_length = self.W  # decreasing window length

        while nb_anchors != anchor_tier.GetSize() and anchor_tier.check_holes_ntokens(self.NBT) is False:

            anchor_tier.set_win_delay(win_length)
            nb_anchors = anchor_tier.GetSize()

            logging.debug(" =========================================================== ")
            logging.debug(" Number of anchors: %d" % nb_anchors)
            logging.debug(" N-gram:   %d" % ngram)
            logging.debug(" W-length: %d" % win_length)

            # perform ASR and append new anchors in the anchor tier (if any)
            self._asr(toklist, pronlist, anchor_tier, channel, diralign, ngram)

            # append the anchor tier as intermediate result
            if self.ANCHORS is True and nb_anchors != anchor_tier.GetSize():
                Chunks._append_tier(anchor_tier, trsoutput)
                out_name = os.path.join(diralign, "ANCHORS-%d.xra" % anchor_tier.GetSize())
                sppas.src.annotationdata.aio.write(out_name, trsoutput)

            # prepare next pass
            win_length = max(win_length-1., self.WMIN)
            ngram = max(ngram-1, self.NMIN)

        # Then, anchors are exported as tracks.
        tiert = anchor_tier.export(toklist)
        tiert.SetName("Chunks-Tokenized")
        tierp = anchor_tier.export(pronlist)
        tierp.SetName("Chunks-Phonetized")
        trsoutput.Append(tiert)
        trsoutput.Append(tierp)

        return trsoutput

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    @staticmethod
    def _append_tier(tier, trs):
        """ Append a copy of Tier in trs.

        """
        copy_tier = Tier("Anchors-"+str(tier.GetSize()))
        for a in tier:
            ac = a.Copy()
            try:
                copy_tier.Append(ac)
            except Exception:
                logging.debug("Append of annotation in tier failed: %s" % ac)

        trs.Append(copy_tier)

    # ------------------------------------------------------------------------

    def _asr(self, toklist, pronlist, anchor_tier, channel, diralign, N):
        """ Windowing on the audio to perform ASR and find anchors.

        """
        # init
        from_time = 0.
        to_time = float(N)
        fails = 0
        max_time = channel.get_duration()

        # windowing
        logging.debug(" ... Windowing the audio file:")
        while from_time < max_time and fails < 3:

            try:
                # Fix exact time range of this window...
                from_time, to_time = anchor_tier.fix_window(from_time)
                if to_time > max_time:
                    to_time = max_time
                if from_time >= to_time:
                    logging.debug('Stop windowing: %f %f.' % (from_time, to_time))
                    break

                # Fix token range of this window...
                from_token, to_token = self._fix_trans_interval(from_time, to_time, toklist, anchor_tier)
                if from_token >= len(toklist):
                    break

                logging.debug(" ... ... window: ")
                logging.debug("... ... ... time  from %.4f to %.4f." % (from_time, to_time))
                logging.debug("... ... ... token from %d to %d." % (from_token, to_token))
                logging.debug("... ... ... REF: %s" % (" ".join(toklist[from_token:to_token])))
                logging.debug("... ... ... HYP: ")

                # Fix anchors of this window
                anchors = self._fix_window_asr(from_time,
                                               to_time,
                                               from_token,
                                               to_token,
                                               channel,
                                               pronlist,
                                               toklist,
                                               diralign,
                                               N)

                if len(anchors) > 0:
                    Chunks._add_anchors(anchors, anchor_tier)
                    # Prepare next window
                    from_time = anchors[-1][1]
                    fails = 0
                else:
                    from_time = to_time
                    logging.debug("... ... ... No anchor found.")

            except Exception:
                # try your luck in the next window...
                import traceback
                logging.info("%s" % str(traceback.format_exc()))
                from_time = to_time
                fails += 1

    # ------------------------------------------------------------------------

    def _fix_trans_interval(self, from_time, to_time, toklist, anchor_tier):
        """ Fix the window on the transcript.

        """
        # previous and following anchors
        af = anchor_tier.near_indexed_anchor(from_time, -1)
        at = anchor_tier.near_indexed_anchor(to_time, 1)

        fexact = False
        wdelay = to_time-from_time
        ntokens = self._spkrate.ntokens(wdelay)+1

        # an anchor is not too far away before
        if af is not None and af.GetLocation().GetEnd() >= (from_time-wdelay):
            # we have an exact position in the token list
            from_token = af.GetLabel().GetTypedValue() + 1
            fexact = True
        else:
            # we approximate with the speaking rate
            from_token = max(0, self._spkrate.ntokens(from_time) - ntokens)

        # an anchor is not too far away after
        if at is not None and at.GetLocation().GetBegin() <= (to_time+wdelay):
            # we have an exact position in the token list
            to_token = at.GetLabel().GetTypedValue() - 1
        else:
            # we approximate with the speaking rate
            if fexact is True:
                to_token = min(len(toklist), from_token + int(1.5*ntokens))
            else:
                to_token = min(len(toklist), self._spkrate.ntokens(to_time) + ntokens)

        # ...
        if from_token >= to_token:
            from_token = max(0, from_token-1)
            to_token = min(len(toklist), from_token+2)

        return from_token, to_token

    # ------------------------------------------------------------------------

    def _fix_window_asr(self, from_time, to_time, from_token, to_token, channel, pronlist, toklist, diralign, N):
        """
        Fix asr result in a window.
        Return the list of anchors the ASR found in that window.

        """
        # create audio file
        fnw = os.path.join(diralign, "asr")
        fna = os.path.join(diralign, "asr.wav")
        trackchannel = autils.extract_channel_fragment(channel, from_time, to_time, 0.2)
        autils.write_channel(fna, trackchannel)

        # call the ASR engine to recognize tokens of this track
        self._aligner.set_phones(" ".join(pronlist[from_token:to_token]))
        self._aligner.set_tokens(" ".join( toklist[from_token:to_token]))
        self._aligner.run_alignment(fna, fnw, N)

        # get the tokens time-aligned by the ASR engine
        wordalign = self._alignerio.read_aligned(fnw)[1]  # (starttime,endtime,label,score)
        wordalign = Chunks._adjust_asr_result(wordalign, from_time, 0.2)

        # ignore the last word: we can't know if the word is entire or was cut
        if len(wordalign) > 3:
            wordalign.pop()

        # list of tokens the ASR automatically time-aligned
        tman = [token for token in toklist[from_token:to_token]]
        # list of tokens manually transcribed
        tasr = [(token, score) for (start, end, token, score) in wordalign]

        # Find matching tokens: the anchors
        matchingslist = Chunks._fix_matchings_list(tman, tasr, N)

        anchors = []
        for match in matchingslist:
            i = match[0]    # ref
            hi = match[1]   # hyp
            s = wordalign[hi][0]
            e = wordalign[hi][1]
            anchors.append((s, e, from_token+i))

        return anchors

    # ------------------------------------------------------------------------

    @staticmethod
    def _adjust_asr_result(wordsalign, from_time, silence):
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
        wordsalign[0][0] = max(0., wordsalign[0][0])

        # shift all local time values to the real time values in the audioinput
        for i in range(len(wordsalign)):
            wordsalign[i][0] = wordsalign[i][0] + from_time
            wordsalign[i][1] = wordsalign[i][1] + from_time
            logging.debug("... ... ... ... %s - %f" % (wordsalign[i][2], wordsalign[i][3]))

        return wordsalign

    # ------------------------------------------------------------------------

    @staticmethod
    def _fix_matchings_list(ref, hyp, N):
        """ Create the list of matches between ref and hyp.

        """
        pattern = sppasPatterns()
        pattern.set_ngram(N)
        m3 = pattern.ngram_matches(ref, hyp)

        if len(m3) == 0:
            return []

        # Search for the lowest/highest values in ref/hyp:
        listref = [v[0] for v in m3]
        listhyp = [v[1] for v in m3]
        minr = min(listref)
        maxr = max(listref)
        newref = ref[minr:maxr+1]
        minh = min(listhyp)
        maxh = max(listhyp)
        newhyp = hyp[minh:maxh+1]

        # Do some hypothesis were found several times in the reference?
        if len(listhyp) > len(list(set(listhyp))):

            pattern.set_ngram(N+2)
            newm3 = pattern.ngram_matches(ref, hyp)
            listref = [v[0] for v in m3]
            listhyp = [v[1] for v in m3]
            if len(listhyp) > len(list(set(listhyp))):
                newm3 = []

        else:
            newm3 = m3

        m1 = []
        if len(hyp) < N:
            pattern = sppasPatterns()
            pattern.set_score(0.9)
            pattern.set_ngram(1)
            pattern.set_gap(1)
            m1 = pattern.ngram_alignments(newref, newhyp)

        return sorted(list(set(m1+newm3)))

    # ------------------------------------------------------------------------

    @staticmethod
    def _add_anchors(anchorlist, anchor_tier):
        """ Add anchors in the anchor tier

        """
        if len(anchorlist) == 0:
            return

        logging.debug('... ... ... Anchors:')
        for (s,e,i) in anchorlist:

            # provide overlaps with a previous anchor
            previ = anchor_tier.Near(s, -1)
            if previ != -1:
                prevann = anchor_tier[previ]
                if prevann.GetLocation().GetEnd().GetMidpoint() > s:
                    if prevann.GetLabel().IsSilence():
                        prevann.GetLocation().GetEnd().SetMidpoint(s)
                        if prevann.GetLocation().GetEnd() < prevann.GetLocation().GetBegin():
                            anchor_tier.Pop(previ)
                    else:
                        s = prevann.GetLocation().GetEnd().SetMidpoint(s)

            # provide overlaps with a following anchor
            nexti = anchor_tier.Near(e, 1)
            if nexti != -1:
                nextann = anchor_tier[nexti]
                if nextann.GetLocation().GetBegin().GetMidpoint() < e:
                    if nextann.GetLabel().IsSilence():
                        nextann.GetLocation().GetBegin().SetMidpoint(e)
                        if nextann.GetLocation().GetEnd() < nextann.GetLocation().GetBegin():
                            anchor_tier.Pop(nexti)
                    else:
                        e = nextann.GetLocation().GetBegin().SetMidpoint(e)

            valid = True
            # previous index must be lesser
            p = anchor_tier.near_indexed_anchor(s, -1)
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
                            valid = False

            # next index must be higher
            n = anchor_tier.near_indexed_anchor(e, 1)
            if n is not None and i >= n.GetLabel().GetTypedValue():
                valid = False

            # add the anchor
            if valid is True:
                time = TimeInterval(TimePoint(s), TimePoint(e))
                label = Label(Text(i, data_type="int"))
                anchor_tier.Add(Annotation(time, label))
                logging.debug("... ... ... ... Add: %f %f %d" % (s, e, i))
            else:
                logging.debug("... ... ... ... ... Ignore: %f %f %d" % (s, e, i))

        # Then, fill the very evident holes
        anchor_tier.fill_evident_holes()

    # ------------------------------------------------------------------------

    def _tier2raw(self, tier, mapp=False):
        """ Return all interval contents into a single string.

        """
        # Map phonemes from SAMPA to the expected ones.
        self._mapping.set_keep_miss(True)
        self._mapping.set_reverse(True)

        raw = ""
        for i, ann in enumerate(tier):
            if ann.GetLabel().IsEmpty() is True:
                logging.info("WARNING: Found an empty annotation label at index %d" % i)
                raw = raw + " sil"
            else:  # if ann.GetLabel().IsSilence() is False:
                besttext = ann.GetLabel().GetValue()
                if mapp is True:
                    besttext = self._mapping.map(besttext)

                if unk_stamp in besttext:
                    besttext = besttext.replace(unk_stamp, "sil")
                raw = raw + " " + besttext

        return sppasUnicode(raw).to_strip()

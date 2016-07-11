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
# File: tracks.py
# ----------------------------------------------------------------------------

import os
import logging
import codecs

import annotations.Align.aligners as aligners
from annotations.Align.aligners.alignerio import AlignerIO
from annotations.Align.spkrate import SpeakerRate
from annotations.Align.anchors import AnchorTier

from annotationdata.transcription  import Transcription
from annotationdata.tier           import Tier
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point    import TimePoint
from annotationdata.annotation     import Annotation
from annotationdata.label.label    import Label
from annotationdata.label.text     import Text

import audiodata.autils as autils

from resources.slm.ngramsmodel import START_SENT_SYMBOL, END_SENT_SYMBOL
from resources.patterns import Patterns
from resources.rutils import ToStrip

from sp_glob import encoding
from sp_glob import UNKSTAMP

# ----------------------------------------------------------------------


class TrackNamesGenerator():
    def __init__(self):
        pass

    def audiofilename(self, trackdir, tracknumber):
        return os.path.join(trackdir, "track_%.06d.wav" % tracknumber)

    def phonesfilename(self, trackdir, tracknumber):
        return os.path.join(trackdir, "track_%.06d.pron" % tracknumber)

    def tokensfilename(self, trackdir, tracknumber):
        return os.path.join(trackdir, "track_%.06d.term" % tracknumber)

    def alignfilename(self, trackdir, tracknumber, ext=None):
        if ext is None:
            return os.path.join(trackdir, "track_%.06d" % tracknumber)
        return os.path.join(trackdir, "track_%.06d.%s" % (tracknumber,ext))

# ----------------------------------------------------------------------------

class TrackSplitter( Transcription ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Write tokenized-phonetized segments from Tiers.

    """
    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new SegmentsOut instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)
        self._radius = 0.005
        self._tracknames = TrackNamesGenerator()
        self._aligntrack = None
        self._alignerio = AlignerIO()
        self._spkrate  = SpeakerRate()

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set_tracksnames( self, tracknames ):
        """
        Set the TrackNamesGenerator().

        """
        self._tracknames = tracknames

    # ------------------------------------------------------------------------

    def set_trackalign( self, ta ):
        """
        Set the aligner, required to create tracks (if any).

        """
        self._aligntrack = ta

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def split(self, inputaudio, phontier, toktier, diralign):
        """
        Main method to write tracks from the given data.

        @param inputaudio (src - IN) File name of the audio file.
        @param phontier  (Tier - IN) Tier with phonetization to split
        @param toktier   (Tier - IN) Tier with tokenization to split
        @param diralign   (str - IN) Directory to put units.

        @return List of tracks with (start-time end-time)

        """
        if phontier.IsTimeInterval() is False:
            if self._aligntrack is None or self._aligntrack.get_aligner() != "julius":
                raise IOError("The phonetization tier is not of type TimeInterval and the aligner can't perform this segmentation.")
            else:
                (t,p) = self.create_tier_tracks(inputaudio, phontier, toktier, diralign)
                tracks = self.write_text_tracks(p, t, diralign)
        else:
            tracks = self.write_text_tracks(phontier, toktier, diralign)

        self.write_audio_tracks(inputaudio, tracks, diralign)

        return tracks

    # ------------------------------------------------------------------------

    def write_text_tracks(self, phontier, toktier, diralign):
        """
        Write tokenization and phonetization of tiers into separated track files.

        @param phontier (Tier - IN) time-aligned tier with phonetization to split
        @param toktier  (Tier - IN) time-aligned tier with tokenization to split
        @param diralign (str - IN) the directory to write tracks.

        """
        tokens = True
        if toktier is None:
            toktier = phontier.Copy()
            tokens = False
        if phontier.GetSize() != toktier.GetSize():
            raise IOError('Inconsistency between the number of intervals of tokenization (%d) and phonetization (%d) tiers.'%(phontier.GetSize(),toktier.GetSize()))

        units = []
        for annp,annt in zip(phontier,toktier):

            b = annp.GetLocation().GetBegin().GetMidpoint()
            e = annp.GetLocation().GetEnd().GetMidpoint()
            units.append( (b,e) )

            # Here we write only the text-label with the best score,
            # we don't care about alternative text-labels
            fnp = self._tracknames.phonesfilename(diralign, len(units))
            textp = annp.GetLabel().GetValue()
            self._write_text_track( fnp, textp )

            fnt = self._tracknames.tokensfilename(diralign, len(units))
            label = annt.GetLabel()
            if tokens is False and label.IsSpeech() is True:
                textt = " ".join( ["w_"+str(i+1) for i in range(len(textp.split()))] )
            else:
                textt = label.GetValue()
            self._write_text_track( fnt, textt )

        return units

    # ------------------------------------------------------------------------

    def write_audio_tracks(self, inputaudio, units, diralign, silence=0.):
        """
        Write the first channel of an audio file into separated track files.
        Re-sample to 16000 Hz, 16 bits.

        @param inputaudio (src - IN) File name of the audio file.
        @param units     (list - IN) List of tuples (start-time,end-time) of tracks.
        @param diralign   (str - IN) Directory to write audio tracks.
        @param silence   float - IN) Duration of a silence to surround the tracks.

        """
        channel = autils.extract_audio_channel( inputaudio,0 )
        channel = autils.format_channel( channel,16000,2 )

        for track,u in enumerate(units):
            (s,e) = u
            trackchannel = autils.extract_channel_fragment( channel, s, e, silence)
            trackname    = self._tracknames.audiofilename(diralign, track+1)
            autils.write_channel(trackname, trackchannel)

    # ------------------------------------------------------------------------

    def create_tier_tracks(self, inputaudio, phontier, toktier, diralign):
        """
        Create time-aligned tiers from raw intput tiers.

        @param phontier (Tier - IN) the tier with phonetization
        @param toktier  (Tier - IN) the tier with tokenization to split
        @param diralign (str - IN) the directory to work.

        """
        message = ""
        logging.debug( "Find automatically tracks for audio file: %s"%inputaudio)

        # Extract the audio channel
        channel = autils.extract_audio_channel( inputaudio,0 )
        channel = autils.format_channel( channel,16000,2 )

        # Extract the lists of tokens and their corresponding pronunciations
        pronlist = self._tier2raw( phontier ).split()
        toklist  = self._tier2raw( toktier ).split()
        if len(pronlist) != len(toklist):
            raise IOError("Inconsistency between the number of items in phonetization %d and tokenization %d."%(len(pronlist),len(toklist)))

        # At a first stage, we'll find anchors
        anchortier = AnchorTier()
        anchortier.set_duration( channel.get_duration() )

        # Search silences and use them as anchors.
        anchortier.append_silences( channel )
        speechduration = channel.get_duration()

        # Estimates the speaking rate (amount of tokens/sec. in average)
        self._spkrate.eval_from_duration( speechduration, len(toklist) )

        # Windowing to find anchors
        nbanchors    = anchortier.GetSize()
        newnbanchors = -1
        try:
            #while newnbanchors != nbanchors:
                nbanchors = anchortier.GetSize()
                logging.debug(" =========================================================== ")
                logging.debug(" Number of anchors: %d"%nbanchors)
                self._asr(toklist, pronlist, anchortier, channel, diralign)
                newnbanchors = anchortier.GetSize()
        except Exception as e:
            message = str(e)

        # OK, we found anchors... now:
        # - remove overlaps
        tiert = self.NewTier("TokenizedChunks")
        tierp = self.NewTier("PhonetizedChunks")

        for ann in anchortier:
            at = ann.Copy()
            ap = ann.Copy()
            # fix overlaps
            if at.GetLocation().GetBegin().GetMidpoint() < tiert.GetEnd().GetMidpoint():
                radius = tiert.GetEnd().GetMidpoint() - at.GetLocation().GetBegin().GetMidpoint()
                radius = radius/2.
                try:
                    at.GetLocation().SetBegin( tiert.GetEnd() )
                    at.GetLocation().GetBegin().SetRadius( radius )
                    ap.GetLocation().SetBegin( tierp.GetEnd() )
                    ap.GetLocation().GetBegin().SetRadius( radius )
                    tiert.GetEnd().SetRadius( radius )
                    tierp.GetEnd().SetRadius( radius )
                except Exception:
                    pass
            #
            if ann.GetLabel().IsSilence() is False:
                i = ann.GetLabel().GetTypedValue()
                if i != -1:
                    at.GetLabel().SetValue( toklist[i] )
                    ap.GetLabel().SetValue( pronlist[i] )

            try:
                tiert.Append(at)
                tierp.Append(ap)
            except Exception:
                pass

        return (tiert,tierp)


    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _asr(self, toklist, pronlist, anchortier, channel, diralign):
        """
        Windowing on the audio to find anchors.

        """
        # Set the aligner: only julius can do that (for now)
        aligner = aligners.instantiate(self._aligntrack.get_model(),"julius")
        aligner.set_infersp(False)
        aligner.set_outext("walign")

        # init
        fromtime  = 0.
        totime    = 0.
        fails = 0
        maxtime = channel.get_duration()

        # windowing
        logging.debug(" ... Windowing the audio file:")
        while fromtime < maxtime:

            if fails > 3:
                logging.debug("The search of anchors failed too often. Stop process at time: %f"%fromtime)
                break
                #raise Exception("The search of anchors failed too often. Stop process at time: %f"%fromtime)

            try:
                # Fix boundaries of this window...
                (fromtime,totime) = anchortier.fix_window(fromtime)
                if totime > maxtime:
                    totime = maxtime
                if fromtime >= totime:
                    logging.debug('Stop windowing: %f %f.'%(fromtime,totime))
                    break

                # Fix "exact" position of fromtoken,totoken depends on
                # fromtime,totime, then surrounded by a large number of tokens!
                ntokens = self._spkrate.ntokens(totime-fromtime)
                fromtoken = max(0, self._spkrate.ntokens( fromtime ) - ntokens)
                totoken   = min(len(toklist), self._spkrate.ntokens( totime ) + ntokens)

                logging.debug(" ... ... window: ")
                logging.debug("... ... ... - time  from %.4f to %.4f."%(fromtime,totime))
                logging.debug("... ... ... - token from %d to %d."%(fromtoken,totoken))
                logging.debug("... ... ... REF: %s"%(" ".join(  toklist[fromtoken:totoken] )))
                logging.debug("... ... ... HYP: ")

                # Fix anchors of this window
                anchors = self._fix_window_asr(fromtime, totime, fromtoken, totoken, aligner, channel, pronlist, toklist, diralign)

                # Add anchors in the anchor tier
                if len(anchors) > 0:
                    logging.debug('... ... ... Anchors:')
                    for (s,e,i) in anchors:
                        time  = TimeInterval(TimePoint(s),TimePoint(e))
                        label = Label( Text(i,data_type="int") )
                        anchortier.Add( Annotation(time,label) )
                        logging.debug(' ... ... ... ... %f %f - %s %s'%(s,e,toklist[i],pronlist[i]))
                else:
                    logging.debug("... ... ... No anchor.")

                # Prepare next window
                fromtime = anchors[-1][1]
                fails = 0

            except Exception as e:
                # try your luck in the next window...
                import traceback
                logging.info("%s"%str(traceback.format_exc()))
                fromtime = totime
                fails = fails + 1

        # Fill holes with -1 index value.

    # ------------------------------------------------------------------------

    def _append_anchors(self, toklist, pronlist, anchortier, channel, diralign):

        # Set the aligner: only julius can do that (for now)
        aligner = aligners.instantiate(self._aligntrack.get_model(),"julius")
        aligner.set_infersp(False)
        aligner.set_outext("walign")

        # Windowing on the audio to find anchors
        logging.debug(" ... Windowing the audio file:")
        fromtime  = 0.
        totime    = 0.
        fromtoken = 0
        fails     = 0
        maxtime   = channel.get_duration()

        while fromtime < maxtime and fromtoken < len(toklist):

            if fails > 3:
                raise Exception("The search of anchors failed too often. Stop process at time: %f"%fromtime)

            try:
                # Fix boundaries of this window...
                (fromtime,totime) = anchortier.fix_window(fromtime)
                if totime > maxtime:
                    totime = maxtime
                if fromtime >= totime:
                    break

                nbtokens = self._spkrate.ntokens( totime-fromtime )
                totoken = min( (fromtoken + nbtokens), len(toklist))

                logging.debug(" ... ... window: ")
                logging.debug("... ... ... - time  from %.4f to %.4f."%(fromtime,totime))
                logging.debug("... ... ... - token from %d to %d."%(fromtoken,totoken))
                logging.debug("... ... ... REF: %s"%(" ".join(  toklist[fromtoken:totoken] )))

                # Fix anchors of this window
                anchors = self._fix_window_anchors(fromtime, totime, fromtoken, totoken, aligner, channel, pronlist, toklist, diralign)

                # Add anchors in the anchor tier
                logging.debug('... ... ... Anchors:')
                for (s,e,i) in anchors:
                    time  = TimeInterval(TimePoint(s),TimePoint(e))
                    label = Label( Text(i,data_type="int") )
                    anchortier.Add( Annotation(time,label) )
                    logging.debug(' ... ... ... ... %f %f - %s %s'%(s,e,toklist[i],pronlist[i]))

                # Prepare next window
                fromtime  = anchors[-1][1]
                fromtoken = anchors[-1][2] + 1
                fails = 0

            except Exception as e:
                # try your luck in the next window...
                import traceback
                logging.info("%s"%str(traceback.format_exc()))
                fromtime = totime
                fails = fails + 1

    # ------------------------------------------------------------------------

    def _fix_window_asr(self, fromtime, totime, fromtoken, totoken, aligner, channel, pronlist, toklist, diralign):
        """
        Fix asr result in a window.

        """
        # create audio file
        fnw = self._tracknames.alignfilename(diralign,0)
        fna = self._tracknames.audiofilename(diralign,0)
        trackchannel = autils.extract_channel_fragment( channel, fromtime, totime, 0.2)
        autils.write_channel( fna, trackchannel )

        # call the ASR engine to recognize tokens of this track
        aligner.set_phones( " ".join( pronlist[fromtoken:totoken] ) )
        aligner.set_tokens( " ".join(  toklist[fromtoken:totoken] ) )
        aligner.run_alignment(fna, fnw)

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
        matchingslist = self._fix_matchings_list( tman,tasr )
        if len(matchingslist) == 0:
            raise Exception('No matching found between ASR result and manual transcription.')

        anchors = []
        for match in matchingslist:
            i  = match[0]   # ref
            hi = match[1]   # hyp
            s = wordalign[hi][0]
            e = wordalign[hi][1]
            anchors.append( (s,e,fromtoken+i) )

        return anchors

    # ------------------------------------------------------------------------

    def _fix_window_anchors(self, fromtime, totime, fromtoken, totoken, aligner, channel, pronlist, toklist, diralign):
        """
        Fix anchors in a window.

        """
        # create audio file
        fnw = self._tracknames.alignfilename(diralign,0)
        fna = self._tracknames.audiofilename(diralign,0)
        trackchannel = autils.extract_channel_fragment( channel, fromtime, totime, 0.2)
        autils.write_channel( fna, trackchannel )

        # call the ASR engine to recognize tokens of this track
        aligner.set_phones( " ".join( pronlist[fromtoken:totoken] ) )
        aligner.set_tokens( " ".join(  toklist[fromtoken:totoken] ) )
        aligner.run_alignment(fna, fnw)

        # get the tokens time-aligned by the ASR engine
        wordalign = self._alignerio.read_aligned(fnw)[1]  # (starttime,endtime,label,score)
        wordalign = self._adjust_asr_result(wordalign, fromtime, 0.2)
        logging.debug("... ... ... ASR hypothesis:")
        for (b,e,w,s) in wordalign:
            logging.debug("... ... ... ... %f %f, %s %f"%(b,e,w,s))

        # delete files

        # list of tokens the ASR automatically time-aligned
        tman = [token for token in toklist[fromtoken:totoken]]
        # list of tokens manually transcribed
        tasr = [(token,score) for (start,end,token,score) in wordalign]

        # Find matching tokens: the anchors
        matchingslist = self._fix_matchings_list( tman,tasr )
        if len(matchingslist) == 0:
            raise Exception('No matching found between ASR result and manual transcription.')

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

        # the first token was starting during to the silence we prepended.
        wordsalign[0][0] = max( 0. , wordsalign[0][0] )

        # shift all local time values to the real time values in the audioinput
        for i in range(len(wordsalign)):
            wordsalign[i][0] = wordsalign[i][0] + fromtime
            wordsalign[i][1] = wordsalign[i][1] + fromtime

        return wordsalign

    # ------------------------------------------------------------------------

    def _fix_matchings_list(self, ref, hyp ):
        """
        Create the list of match between ref and hyp.

        The default set of anchors is defined as:

            1. tokens in 3-grams sequences matching in a gap of 2 possible
               consecutive insertions or deletions;
            2. tokens matching in ref and hyp in a gap of 1 possible insertion
               or deletion, if the score of token is more than 0.9 in hyp.

        """
        pattern = Patterns()
        pattern.set_ngram(3)
        m3 = pattern.ngram_matchings( ref,hyp )
        pattern.set_ngram(1)
        pattern.set_score(0.9)
        m1 = pattern.ngram_matchings( ref,hyp )

        return sorted(list(set(m1+m3)))

    # ------------------------------------------------------------------------

    def _tier2raw( self,tier ):
        """
        Return all interval contents into a single string.
        """
        raw = ""
        for ann in tier:
            if ann.GetLabel().IsSilence() is False:
                besttext = ann.GetLabel().GetValue()
                if UNKSTAMP in besttext:
                    besttext = "sil"
                raw = raw + " " + besttext

        return ToStrip(raw)

    # ------------------------------------------------------------------------

    def _write_text_track(self, trackname, trackcontent):
        """
        Write a raw text in a file.
        """
        with codecs.open(trackname,"w", encoding) as fp:
            fp.write(trackcontent)


    # ------------------------------------------------------------------------
    # Deprecated
    # ------------------------------------------------------------------------

    def _fix_chunks_list(self, ref, pronref, hyp, match ):
        """
        Create the list of chunks from matching anchors.

        pronref = [p1, p2, p3 ... pn ... pN ]
        ref = [ w1, w2, w3 ... wn ... wN ]
        hyp = [ (b1,e1,t1,s1), (b2,e2,t2,s2), ... (bk,ek,tk,sk) ]
        match = [ (w1,t1), (w2,t2), ... , (wn,tg) ]

        with N < k, and the fact that match has holes, of course.

        """
        chunks = []
        tocontinue = True
        if match[0][0] > 0:
            re = match[0][0]-1
            he = match[0][1]-1
            textt = " ".join( ref[0:re+1] )
            textp = " ".join( pronref[0:re+1] )
            chunks.append( (hyp[0][0], hyp[he][1], textt, textp) )

        start = 0
        end   = 0

        if end+1 >= len(match):
            tocontinue = False

        while tocontinue:

            cur = match[end][0]
            nex = match[end+1][0]
            # we finished a sequence of anchors
            if cur+1 != nex:
                # append the chunk
                c = self.__fix_chunk(ref, pronref, hyp, match, start, end)
                chunks.append( c )
                # append the hole
                #if end+1 < len(match):
                #    h = self.__fix_chunk_from_hole(ref, pronref, hyp, match, end)
                #    chunks.append( h )
                start = end + 1

            end = end + 1

            if end+1 >= len(match):
                # the last chunk found
                if start < end:
                    c = self.__fix_chunk(ref, pronref, hyp, match, start, end)
                    chunks.append( c )

                tocontinue = False

        return chunks

    # ------------------------------------------------------------------------

    def __fix_chunk(self, ref, pronref, hyp, match, s, e):

        rs = match[s][0]
        re = match[e][0]
        texttok  = " ".join( ref[rs:re+1] )
        textpron = " ".join( pronref[rs:re+1] )

        hs = match[s][1]
        he = match[e][1]

        return (hyp[hs][0], hyp[he][1], texttok, textpron)

# --------------------------------------------------------------------------
# ------------------------------------------------------------------

class TracksReader( Transcription ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Read time-aligned segments, convert into Tier.

    """
    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new SegmentsIn instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)
        self.alignerio = AlignerIO()
        self._radius = 0.005
        self._tracknames = TrackNamesGenerator()

    # ------------------------------------------------------------------------

    def set_tracksnames( self, tracknames ):
        self._tracknames = tracknames

    # ------------------------------------------------------------------------

    def read(self, dirname, units):
        """
        Read a set of alignment files and set as tiers.

        @param dirname (str - IN) the input directory containing a set of unit
        @param units (list - IN) List of units with start/end times

        """
        # Verify if the directory exists
        if os.path.exists( dirname ) is False:
            raise IOError("Missing directory: " + dirname+".\n")

        # Create new tiers
        itemp = self.NewTier("PhonAlign")
        itemw = self.NewTier("TokensAlign")

        # Explore each unit to get alignments
        for track in range(len(units)):

            # Get real start and end time values of this unit.
            unitstart,unitend = units[track]

            basename = self._tracknames.alignfilename(dirname, track+1)
            (_phonannots,_wordannots) = self.alignerio.read_aligned(basename)

            # Append alignments in tiers
            self._append_tuples(itemp, _phonannots, unitstart, unitend)
            self._append_tuples(itemw, _wordannots, unitstart, unitend)

        # Adjust Radius
        if itemp.GetSize()>1:
            itemp[-1].GetLocation().SetEndRadius(0.)
        if itemw.GetSize()>1:
            itemw[-1].GetLocation().SetEndRadius(0.)
            try:
                self._hierarchy.addLink('TimeAlignment', itemp, itemw)
            except Exception as e:
                logging.info('Error while assigning hierarchy between phonemes and tokens: %s'%(str(e)))
                pass

    # ------------------------------------------------------------------------

    def _append_tuples(self, tier, tdata, delta, unitend):
        """
        Append a list of (start,end,text,score) into the tier.
        Shift start/end of a delta value and set the last end value.

        """
        try:

            for i,t in enumerate(tdata):
                (loc_s,loc_e,lab,scr) = t
                loc_s += delta
                loc_e += delta
                if i==(len(tdata)-1):
                    loc_e = unitend

                # prepare the code in case we'll find a solution with
                # alternatives phonetizations/tokenization....
                #lab = [lab]
                #scr = [scr]
                #label = Label()
                #for l,s in zip(lab,scr):
                #    label.AddValue(Text(l,s))
                label = Label( Text(lab,scr) )
                annotationw = Annotation(TimeInterval(TimePoint(loc_s,self._radius), TimePoint(loc_e,self._radius)), label)
                tier.Append(annotationw)

        except Exception:
            import traceback
            print(traceback.format_exc())
            logging.info('No alignment appended in tier from %f to %f.'%(delta,unitend))
            pass

    # ------------------------------------------------------------------------

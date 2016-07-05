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

from annotations.Align.aligners.alignerio import AlignerIO

from annotationdata.transcription  import Transcription
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point    import TimePoint
from annotationdata.annotation     import Annotation
from annotationdata.label.label    import Label
from annotationdata.label.text     import Text

import audiodata.io
from audiodata.audio         import AudioPCM
from audiodata.channel       import Channel
from audiodata.channelframes import ChannelFrames

from sp_glob import encoding

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
        self._aligntrack  = None

    # ------------------------------------------------------------------------

    def set_tracksnames( self, tracknames ):
        self._tracknames = tracknames

    # ------------------------------------------------------------------------

    def set_trackalign( self, ta ):
        self._aligntrack = ta

    # ------------------------------------------------------------------------

    def split(self, inputaudio, phontier, toktier, diralign):
        """
        Split all the data into tracks.

        @param phontier (Tier - IN) the tier with phonetization to split
        @param toktier  (Tier - IN) the tier with tokenization to split
        @param diralign (str - IN) the directory to put units.

        @return List of units with (start-time end-time)

        """
        if phontier.IsTimeInterval() is False:
            if self._aligntrack is None or self._aligntrack.get_aligner() != "julius":
                raise IOError("The phonetization tier is not of type TimeInterval and the aligner can't perform this segmentation.")
            else:
                self._create_tracks(inputaudio, phontier, toktier)

        units = self._write_text_tracks(phontier, toktier, diralign)
        self._write_audio_tracks(inputaudio, units, diralign)
        return units

    # ------------------------------------------------------------------------

    def _create_tracks(self, inputaudio, phontier, toktier):
        """
        """
        raise NotImplementedError("the aligner can't perform the units segmentation.")

    # ------------------------------------------------------------------------

    def _write_text_tracks(self, phontier, toktier, diralign):
        """
        Write tokenization and phonetization of tiers into separated track files.

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
            # we dont care about alternative text-labels
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

    def _write_text_track(self, trackname, trackcontent):
        with codecs.open(trackname,"w", encoding) as fp:
            fp.write(trackcontent)

    # ------------------------------------------------------------------------

    def _write_audio_tracks(self, inputaudio, units, diralign, silence=0.):
        """
        Write the first channel of an audio file into separated files.

        """
        # Get the audio channel we'll work on
        audio = audiodata.io.open(inputaudio)
        idx = audio.extract_channel(0)
        channel = audio.get_channel(idx)
        audio.close() # no more need of input audio data, can close it

        framerate = channel.get_framerate()
        sampwidth = channel.get_sampwidth()

        track = 1
        for (s,e) in units:

            # Extract the fragment of frames and convert to 16000 Hz, 16 bits.
            fragmentchannel = channel.extract_fragment(begin=int(s*framerate), end=int(e*framerate))
            cf = ChannelFrames( fragmentchannel.get_frames( fragmentchannel.get_nframes()) )
            cf.resample( sampwidth, framerate, 16000 )
            cf.change_sampwidth( sampwidth, 2)
            #cf.prepend_silence( silence*16000 )
            #cf.append_silence( silence*16000 )

            trackname    = self._tracknames.audiofilename(diralign, track)
            trackchannel = Channel( 16000, 2, frames=cf.get_frames() )
            self._write_audio_track(trackname, trackchannel)

            track = track + 1

    def _write_audio_track(self, trackname, channel):
        audio_out = AudioPCM()
        audio_out.append_channel( channel )
        audiodata.io.save( trackname, audio_out )


# ------------------------------------------------------------------
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


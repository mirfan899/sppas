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
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
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
# File: wavsil.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------

import sys
import getopt
import codecs
import os

import signals
import audio
from annotationdata.transcription import Transcription
import annotationdata.io
import audioutils


# ----------------------------------------------------------------------------


class WaveSil:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: This class implements the silence finding.

    """

    def __init__(self, audiospeech, m=0.3):
        """
        Create a WaveSil audio instance.

        @param audiospeech (Audio) the input object
        @param m (float) is the minimum track duration (in seconds)

        """
        self.audiospeech = audiospeech
        self.silence   = None
        self.minlenght = m

    # End __init__
    # ------------------------------------------------------------------


    def set_mintrack(self, m):
        """
        Set a new minimum track duration.

        @param m (float): duration (in seconds)

        """
        self.minlenght = float(m)

    # End set_minlength
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # Silence detection
    # ------------------------------------------------------------------


    def tracks(self):
        from_pos = 0
        if self.silence is None or len(self.silence)==0:
        # No silence: Only one track!
            yield 0,self.audiospeech.get_nframes()
            return
        # At least one silence
        for to_pos, next_from in self.silence:
            if (to_pos - from_pos) >= (self.minlenght * self.audiospeech.get_framerate()):
                # Track is long enough to be considered a track.
                yield int(from_pos), int(to_pos)
            from_pos = next_from

        # Last track after the last silence
        # (if the silence does not end at the end of the wav)
        to_pos = self.audiospeech.get_nframes()
        if (to_pos - from_pos) >= (self.minlenght * self.audiospeech.get_framerate()):
            yield int(from_pos), int(to_pos)

    # End tracks
    # ------------------------------------------------------------------


    def track_data(self, tracks):
        """
        Get the track data: a set of frames for each track.
        """
        nframes = self.audiospeech.get_nframes()
        for from_pos, to_pos in tracks:
            if nframes < from_pos:
                # Accept a "DELTA" of 10 frames, in case of corrupted data.
                if nframes < from_pos-10:
                    raise ValueError("Position %d not in range(%d)" % (from_pos, nframes))
                else:
                    from_pos = nframes
            # Go to the provided position
            self.audiospeech.set_pos(from_pos)
            # Keep in mind the related frames
            yield self.audiospeech.read_frames(to_pos - from_pos)

    # End track_data
    # ------------------------------------------------------------------


    def get_silence(self, p=0.250, v=150, s=0.0):
        """
        Get silences from an audio file.

        @return a set of frames corresponding to silences.

        """
        self.silence = []
        # Once silence has been found, continue searching in this interval
        afterloop_frames = int((self.audiospeech.get_frameduration()/2) * self.audiospeech.get_framerate())
        initpos = i = self.audiospeech.tell()
        self.silence = []
        # This scans the file in steps of frames whether a section's volume
        # is lower than silence_cap, if it is it is written to silence.
        while i < self.audiospeech.get_nframes():
            curframe  = self.audiospeech.read()
            volume   = audioutils.get_rms(curframe, self.audiospeech.get_sampwidth())
            if volume < v:
                # Continue searching in smaller steps whether the silence is
                # longer than readed frames but smaller than readed frames * 2.
                while volume < v and self.audiospeech.tell() < self.audiospeech.get_nframes():
                    curframe = self.audiospeech.read_frames(afterloop_frames)
                    volume   = audioutils.get_rms(curframe, self.audiospeech.get_sampwidth())
                # If the last sequence of silence ends where the new one starts
                # it's a continuous range.
                if self.silence and self.silence[-1][1] == i:
                    self.silence[-1][1] = self.audiospeech.tell()
                else:
                # append if silence is long enough
                    duree = self.audiospeech.tell() - i
                    nbmin = int( (p+s) * self.audiospeech.get_framerate())
                    if duree > nbmin:
                        # Adjust silence start-pos
                        __startpos = i + ( s * self.audiospeech.get_framerate() )
                        # Adjust silence end-pos
                        __endpos = self.audiospeech.tell() - ( s * self.audiospeech.get_framerate() )
                        self.silence.append([__startpos, __endpos])
            i = self.audiospeech.tell()

        # Return the position in the file to where it was when we got it.
        self.audiospeech.set_pos(initpos)

    # End get_silence
    # ------------------------------------------------------------------


    def set_silence(self, silence):
        self.silence = silence

    # End set_silence
    # ------------------------------------------------------------------


    def write_tracks(self, trstracks, output, ext="txt", trsunits=[], trsnames=[], logfile=None):
        """
        Write tracks in an output directory.

        Print only errors in a log file.

        @param trstracks   All tracks as an array of tuples (start,end)
        @param output      Directory name (String)
        @param ext         Tracks file names extension (String)
        @param trsunits    Tracks content (Array of string)
        @param trsnames    Expected tracks file's names (Array of string)
        @param logfile     Log file (sppasLog)

        """
        wavtraks = True
        if not os.path.exists( output ):
            os.mkdir( output )

        # Write text tracks

        for i in range(len(trsunits)):
            trackbasename = ""
            if len(trsnames) > 0:
                # Specific names are given
                trackbasename = os.path.join(output, trsnames[i])
            else:
                trackbasename = os.path.join(output, "track_%.06d" % (i+1))
            if len(trackbasename)>0:
                # Write the transcription track content (if any)
                if len(trsunits)>0:
                    tracktxtname = trackbasename+"."+ext
                    if isinstance(trsunits[0], Transcription):
                        annotationdata.io.write(tracktxtname, trsunits[i])
                    else:
                        encoding='utf-8'
                        with codecs.open(tracktxtname,"w", encoding) as fp:
                            fp.write(trsunits[i])
                elif logfile is not None:
                    logfile.print_message( "Writing track "+tracktxtname,indent=3,status=-1 )
                else:
                    print ( " ... ... ... Writing track "+tracktxtname+": [ERROR]" )

        # Write wav tracks

        if self.audiospeech is None:
            return False

        try:
            split_tracks = self.track_data( trstracks )
        except Exception:
            logfile.print_message('split tracks failed: wav corrupted',indent=2,status=-1)
            return False

        for i, split_track in enumerate(split_tracks):
            trackbasename = ""
            if len(trsnames) > 0:
                # Specific names are given
                trackbasename = os.path.join(output, trsnames[i])
            else:
                trackbasename = os.path.join(output, "track_%.06d" % (i+1))
            if len(trackbasename)>0:
                # Write the wav track content
                trackwavname = trackbasename+".wav"
                try:
                    signals.save_fragment(trackwavname, self.audiospeech, split_track)
                except Exception as e:
                    if logfile:
                        logfile.print_message('Writing track %s failed with error: %s'%(trackwavname,str(e)), status=-1)
                    else:
                        print 'Writing track %s failed with error: %s'%(trackwavname,str(e))
                    wavtraks = False

        return wavtraks

    # End write_tracks
    # ------------------------------------------------------------------

# ----------------------------------------------------------------------

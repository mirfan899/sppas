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
# File: aiff.py
# ----------------------------------------------------------------------------

import struct
import aifc

from audiodata.audio        import AudioPCM
from audiodata.audiodataexc import AudioDataError

# ---------------------------------------------------------------------------

class AiffIO( AudioPCM ):
    """
    @authors:      Nicolas Chazeau, Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      An AIFF/AIFC file open/save utility class.

    Audio Interchange File Format (AIFF) is an audio file format developed by
    Apple Inc. in 1988.

    """
    def __init__(self):
        """
        Constructor.

        """
        AudioPCM.__init__(self)

    # ------------------------------------------------------------------------

    def open(self, filename):
        """
        Get an audio from an Audio Interchange File Format file.

        @param filename: input file name.

        """
        #Passing a unicode filename to aifc.open() results in the argument
        #being treated like a filepointer instead of opening the file.
        fp = open( unicode(filename), "r" )

        # Use the standard aifc library to load the audio file
        # open method return an Aifc_read object
        self.audiofp = aifc.open( fp )

    # ----------------------------------------------------------------------
    # Read content, for audiofp
    # ----------------------------------------------------------------------

    def read_frames(self, nframes):
        """
        Specific frame reader for aiff files.
        AIFF data is in big endian and we need little endian.

        @param nframes (int) the the number of frames wanted
        @return the frames read

        """
        if not self.audiofp:
            raise AudioDataError

        data = self.audiofp.readframes(nframes)

        if self.get_sampwidth() == 4:
            data = struct.unpack(">%ul" % (len(data) / 4), data)
            return struct.pack("<%ul" % (len(data)), *data)

        elif self.get_sampwidth() == 2:
            data = struct.unpack(">%uh" % (len(data) / 2), data)
            return struct.pack("<%uh" % (len(data)), *data)

        return data

    # ----------------------------------------------------------------------

    def _write_frames(self, file, data):
        """
        Specific writer for aiff files.
        Data is in little endian and aiff files need big endian.

        @param file (AudioPCM) the audio file pointer to write in
        @param data (string) the frames to write

        """
        if file.getsampwidth() == 4 :
            data = struct.unpack("<%ul" % (len(data) / 4), data)
            file.writeframes(struct.pack(">%ul" % (len(data)), *data))
        elif file.getsampwidth() == 2 :
            data = struct.unpack("<%uh" % (len(data) / 2), data)
            file.writeframes(struct.pack(">%uh" % (len(data)), *data))
        else :
            file.writeframes(data)

    # ----------------------------------------------------------------------

    def save(self, filename):
        """
        Write an audio content as a Audio Interchange File Format file.

        @param filename (string) output filename.

        """
        if self.audiofp:
            self.save_fragment( filename, self.audiofp.readframes(self.audiofp.getnframes()) )
        elif len(self) == 1:
            channel = self.channels[0]
            fp = open( filename, 'w' )
            f = aifc.open( fp )
            f.setnchannels(1)
            f.setsampwidth(channel.get_sampwidth())
            f.setframerate(channel.get_framerate())
            f.setnframes(channel.get_nframes())
            try:
                self._write_frames( f, channel.frames )
            finally:
                f.close()

        else:
            self.verify_channels()

            frames = ""
            for i in xrange(0, self.channels[0].get_nframes()*self.channels[0].get_sampwidth(), self.channels[0].get_sampwidth()):
                for j in xrange(len(self.channels)):
                        frames += self.channels[j].frames[i:i+self.channels[0].get_sampwidth()]

            f = aifc.open( filename, 'w')
            f.setnchannels(len(self.channels))
            f.setsampwidth(self.channels[0].get_sampwidth())
            f.setframerate(self.channels[0].get_framerate())
            f.setnframes(self.channels[0].get_nframes())
            try:
                self._write_frames( f, frames )
            finally:
                f.close()

    # -----------------------------------------------------------------------

    def save_fragment(self, filename, frames):
        """
        Write an audio content as a Audio Interchange File Format file.

        @param filename (string) output filename.
        @param frames (string) the frames to write

        """
        fp = open( unicode(filename), "w")
        f = aifc.Aifc_write( fp )
        f.setnchannels(self.get_nchannels())
        f.setsampwidth(self.get_sampwidth())
        f.setframerate(self.get_framerate())
        f.setnframes(len(frames)/self.get_nchannels()/self.get_sampwidth())
        try:
            self._write_frames( f, frames )
        except Exception:
            raise
        finally:
            f.close()

# ----------------------------------------------------------------------------

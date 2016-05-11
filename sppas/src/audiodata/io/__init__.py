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
# audiodata.io package
# ----------------------------------------------------------------------------

"""
@author:       Brigitte Bigi, Jibril Saffi
@organization: Laboratoire Parole et Langage, Aix-en-Provence, France
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2011-2016  Brigitte Bigi
@summary:      Readers and writers of audio data.

"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

from os.path import splitext

from audiofactory import AudioFactory


# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

ext_wav  = ['.wav', '.wave', '.[wWaAvV]', '.[wWaAvVeE]']
ext_aiff = ['.aiff', '.[aAiIfF]']
ext_sunau = ['.au', '.[aAuU]']

extensions   = [ '.wav', '.wave', '.aiff', '.au' ]
extensionsul = ext_wav + ext_aiff + ext_sunau

# ----------------------------------------------------------------------------

def get_extension(filename):
    return splitext(filename)[1][1:]

# ----------------------------------------------------------------------------
# Functions for opening and saving audio files.
# ----------------------------------------------------------------------------

def open( filename ):
    """
    Open an audio file.

    @param filename (string) the file name (including path)
    @raise IOError, UnicodeError, Exception
    @return AudioPCM()

    >>> Open an audio file:
    >>> audio = audiodata.io.open(filename)

    """
    ext = get_extension(filename).lower()
    aud = AudioFactory.NewAudio( ext )

    try:
        aud.open( unicode(filename) )
    except UnicodeError as e:
        raise UnicodeError('Encoding error: the file %r contains non-UTF-8 characters: %s' % (filename,e))
    except IOError:
        raise
#    except Exception as e:
#        raise Exception('Invalid audio file: %s' % e)

    return aud


def save( filename, audio ):
    """
    Write an audio file.

    @param filename: (string) the file name (including path)
    @param audio: (AudioPCM) the Audio to write.
    @raise IOError

    """
    ext = get_extension(filename).lower()
    output = AudioFactory.NewAudio(ext)

    output.Set( audio  )
    output.save( unicode(filename) )


def save_fragment( filename, audio, frames ):
    """
    Write a fragment of frames of an audio file.

    @param filename: (string) the file name (including path)
    @param audio: (AudioPCM) the Audio to write.
    @param frames: (string)
    @raise IOError

    """
    ext = get_extension(filename).lower()
    output = AudioFactory.NewAudio(ext)

    output.Set( audio  )
    output.save_fragment( filename, frames )

# ----------------------------------------------------------------------------

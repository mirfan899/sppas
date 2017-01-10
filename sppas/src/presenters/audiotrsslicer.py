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
# File: wavslicer.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Tatsuya Watanabe, Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import os
import audiodata
from annotationdata.utils.trsutils import TrsUtils
import annotationdata.aio

# ----------------------------------------------------------------------------

class AudioSlicer(object):
    """
    @authors: Tatsuya Watanabe, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: This class implements the slicer of an audio file and its transcription.

    """

    def __init__(self):
        pass


    def run(self, audiofile, trsfile, output_dir, output_ext="TextGrid"):
        """
        Split an audio file into multiple small audio file.

        @param audiofile is the audio input file name
        @param trsfile is the transcription input file name
        @param output_dir is a directory name to save output tracks (one per unit)
        @param output_ext (default TextGrid)

        """
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        audiospeech = audiodata.aio.open(audiofile)

        transcription = annotationdata.aio.read(trsfile)

        tracks_tier = None
        for tier in transcription:
            if "name" in tier.GetName().lower():
                tracks_tier = tier

        if tracks_tier is None:
            raise Exception("Expected tier not found: a tier name must contain 'name'")

        list_transcription = TrsUtils.Split(transcription, tracks_tier)
        names = [a.GetLabel().GetValue() for a in tracks_tier if not a.GetLabel().IsEmpty()]

        trstracks = []
        for trs in list_transcription:
            begin = int(trs.GetBegin() * audiospeech.get_framerate())
            end = int(trs.GetEnd() * audiospeech.get_framerate())
            trstracks.append((begin, end))
            TrsUtils.Shift(trs, trs.GetBegin())

        chunks = []
        nframes = audiospeech.get_nframes()
        for from_pos, to_pos in trstracks:
            if nframes < from_pos:
                raise ValueError("Position %d not in range(%d)" % (from_pos, nframes))
            audiospeech.set_pos(from_pos)
            chunks.append(audiospeech.read_frames(to_pos - from_pos))

        for name, chunk, trs in zip(names, chunks, list_transcription):
            audiodata.aio.save(os.path.join(output_dir, name + ".wav"), chunk)
            annotationdata.aio.write(os.path.join(output_dir, name + "." + output_ext), trs)

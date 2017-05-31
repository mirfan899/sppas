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

"""
    This package includes the SPPAS implementation of the Alignment annotation.

    Alignment is the process of aligning speech with its corresponding
    transcription at the phone level.

    The phonetic segmentation problem consists in a time-matching between a
    given speech unit along with a phonetic representation of the unit.
    The goal is to generate an alignment between the speech signal and its
    phonetic representation.

    SPPAS is based on the Julius Speech Recognition Engine (SRE) for 3 reasons:
        1. it is  easy to install which is important for users;
        2. it is also easy to use then easy to integrate in SPPAS;
        3. its performances correspond to the state-of-the-art of HMM-based
    systems and are quite good.

    The Julius alignment task is a 2-step process:
    1/ the first step chooses the phonetization,
    2/ the second step performs the segmentation.

    To perform alignment, a finite state grammar that describes sentence
    patterns to be recognized and an acoustic model are needed. A grammar
    essentially defines constraints on what the SRE can expect as input.
    It is a list of words that the SRE listens to. Each word has a set of
    associated list of phonemes, extracted from the dictionary.
    When given a speech input, Julius searches for the most likely word
    sequence under constraint of the given grammar.

    Speech Alignment also requires  an Acoustic Model in order to align
    speech. An acoustic model is a file that contains statistical
    representations of each of the distinct sounds of one language.
    Each phoneme is represented by one of these statistical representations.
    SPPAS is based on the use of HTK-ASCII acoustic models.

    This package contains a set of classes dealing with the alignment problem.
    It is a 3-steps process:
        1. the transcription and related wav files are split into units;
        2. each unit is aligned; then
        3. unit alignments are merged in a transcription tier and saved.

    Step 2 is a little bit more complicated than it can look at first.
    We encountered 3 difficulties using Julius. Firstly, a unit is not aligned
    if a triphone is missing in the tiedlist. We implemented a ``TiedList''
    class that adds the unobserved triphone into the tiedlist.
    Secondly, we observed that the alignment failed for about 3-5% of units.
    In these cases, Julius performs its 1st step properly (it chooses the
    phonetization, depending on the grammar) but its 2nd step (the segmentation)
    fails. To deal with these errors (and to produce a result instead of nothing),
    we implemented a function that uses the same duration for each phone of the
    unit.
    Thirdly, Julius Grammar-based system skip short pauses! We do not
    implemented a solution to solve this problem.
"""
from .activity import Activity
from .alignio import AlignIO
from .aligntrack import AlignTrack
from .sppasalign import sppasAlign

__all__ = [
    'Activity',
    'AlignIO',
    'AlignTrack',
    'sppasAlign'
]

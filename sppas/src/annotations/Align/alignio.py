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
# File: segmentsio.py
# ----------------------------------------------------------------------------

import codecs
import os
import logging

from resources.rutils import ToStrip
from sp_glob import encoding
from alignerio import AlignerIO

import glob

from annotationdata.transcription  import Transcription
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point    import TimePoint
from annotationdata.annotation     import Annotation
from annotationdata.label.label    import Label
from annotationdata.label.text     import Text

# ------------------------------------------------------------------
# Main class
# ------------------------------------------------------------------

class AlignIO:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Read/Write segments from/to Tiers.

    """
    def __init__(self, mapping):
        """
        Creates a new AlignIO instance.

        @param mapping (Mapping) Phoneme mapping table

        """
        self._mapping = mapping
        self._listio  = ListIO()

    # ------------------------------------------------------------------------

    def read(self, dirname, listfilename):
        """
        Return a Transcription.

        """
        units = self._listio.read( listfilename )

        trsin = SegmentsIn()
        trsin.read(dirname, units)

        # map-back phonemes
        self._mapping.set_keepmiss( True )
        self._mapping.set_reverse( False )

        tier = trsin.Find("PhonAlign")
        for ann in tier:
            label = ann.GetLabel().GetLabel()
            text  = label.GetValue()
            score = label.GetScore()
            ann.GetLabel().SetValue( Text(self._mapping.map_entry(text),score) )

        return trsin

    # ------------------------------------------------------------------------

# ------------------------------------------------------------------

class SegmentsOut( Transcription ):
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
        self.alignerio = AlignerIO()
        self._radius = 0.005

    # ------------------------------------------------------------------------


# ------------------------------------------------------------------

class SegmentsIn( Transcription ):
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
        Creates a new SegmentsIO instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)
        self.alignerio = AlignerIO()
        self._radius = 0.005

    # ------------------------------------------------------------------------

    def read(self, dirname, units):
        """
        Read a set of alignment files and set as tiers.

        @param dirname (str - IN) the input directory containing a set of unit
        @param units (list - IN) List of units with start/end times

        """
        # Verify if the directory exists
        if not os.path.exists( dirname ):
            raise IOError("Missing directory: " + dirname+".\n")

        # Create new tiers
        itemp = self.NewTier("PhonAlign")
        itemw = self.NewTier("TokensAlign")

        # Get all unit alignment file names (default file names of write_tracks())
        dirlist  = glob.glob( os.path.join(dirname, "track_*palign") )
        dirlist += glob.glob( os.path.join(dirname, "track_*mlf") )
        ntracks = len(dirlist)
        if ntracks == 0:
            raise IOError('No tracks were time-aligned.')

        # The number of alignment files must correspond
        # to the number of units in the "list" file.
        if (len(units)-1) != ntracks:
            raise IOError('Inconsistency between expected nb of tracks '+str(len(units)-1)+' and nb track files '+str(ntracks))

        # Explore each unit to get alignments
        wavend,unitend = units[ntracks] # Get the audio duration (last line in list file)
        prevunitend = units[0][0]
        for track in range(ntracks):

            # Get real start and end time values of this unit.
            unitstart,unitend = units[track]

            # Silences were not time-aligned. We add back them now.
            if prevunitend < unitstart:
                # An empty interval between 2 units...
                time = TimeInterval(TimePoint(prevunitend,self._radius), TimePoint(unitstart,self._radius))
                annotation = Annotation(time, Label("#"))
                itemp.Append(annotation)
                #itemw.Append(annotation.Copy())

            basename = os.path.join(dirname, "track_%06d"%(track+1))
            (_phonannots,_wordannots) = self.alignerio.read_aligned(basename)

            # Append alignments in tiers
            self._append_tuples(itemp, _phonannots, unitstart, unitend)
            self._append_tuples(itemw, _wordannots, unitstart, unitend)

            prevunitend = unitend

        # A silence at the end?
        # ... Extend the transcription to the end of the wav.
        if (unitend+0.01) < wavend:
            try:
                if itemp.GetSize()>0: # we had phonemes
                    time = TimeInterval(TimePoint(unitend,self._radius), TimePoint(wavend,0.))
                    annotation = Annotation(time, Label("#"))
                    itemp.Append(annotation)
            except Exception as e:
                raise IOError('Error %s with the audio file duration, for track %d.'%(str(e),(track-1)))
            if itemw.GetSize()>0: # we had tokens
                try:
                    itemw.Append(annotation.Copy())
                except Exception as e:
                    raise IOError('Error %s with the audio file duration, for track %d.'%(str(e),(track-1)))

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
                (loc_s,loc_e,l,score) = t
                loc_s += delta
                loc_e += delta
                if i==(len(tdata)-1):
                    loc_e = unitend

                text = Text(l,score)
                annotationw = Annotation(TimeInterval(TimePoint(loc_s,self._radius), TimePoint(loc_e,self._radius)), Label(text))
                tier.Append(annotationw)

        except Exception:
            import traceback
            print(traceback.format_exc())
            logging.info('No alignment appended in tier from %f to %f.'%(delta,unitend))
            pass

# ----------------------------------------------------------------------

class ListIO():

    def __init__(self):
        pass

    # ------------------------------------------------------------------

    def read(self, filename):
        """
        Read a list file (start-time end-time track-filename).

        @param filename is the list file name.
        @raise IOError

        """
        with codecs.open(filename, 'r', encoding) as fp:
            lines = fp.readlines()

        _units = []
        # Each line corresponds to a track,
        # with a couple 'start end' of float values.
        for line in lines:
            line = ToStrip(line)
            _tab = line.split()
            if len(_tab) >= 2:
                _units.append( (float(_tab[0]),float(_tab[1])) )
            elif len(_tab) == 1:
                # last line indicates the duration of the audio file.
                _units.append( (float(_tab[0]), 0.) )

        return _units

    # ------------------------------------------------------------------

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

    src.anndata.aio.text.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Text reader and writer.

"""
import codecs
import re

from sppas import encoding

from ..anndataexc import AioLineFormatError
from ..annotation import sppasAnnotation
from ..media import sppasMedia
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag

from .basetrs import sppasBaseIO

# ----------------------------------------------------------------------------


class sppasXtrans(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS TDF reader and writer.

    https://www.ldc.upenn.edu/language-resources/tools/xtrans

    XTrans is a multi-platform, multilingual, multi-channel transcription tool
    that supports manual transcription and annotation of audio recordings.
    Last version of Xtrans was distributed in 2009.

    This class implements only a Xtrans reader, not a writer.

    Xtrans does not support alternatives labels nor locations. Only the ones
    with the best score are saved.
    Xtrans can save several tiers.
    Xtrans does not support controlled vocabularies.
    Xtrans does not support hierarchy.
    Xtrans does not support metadata.
    Xtrans supports media assignment.
    Xtrans supports intervals only.
    Xtrans does not support alternative tags.
    Xtrans does not support radius.

    """
    @staticmethod
    def detect(filename):
        with codecs.open(filename, 'r', 'utf-8') as fp:
            lines = fp.readlines()
            for line in lines:
                if line.startswith(";;"):
                    continue
                tab = line.split('\t')
                if len(tab) < 10:  # expected is 13
                    return False

        return True

    # -----------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        return sppasPoint(midpoint, radius=0.005)

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new Xtrans instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = True
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = True
        self._accept_gaps = True
        self._accept_overlaps = True

    # -----------------------------------------------------------------

    def read(self, filename):
        """ Read a tdf file and fill the Transcription.
        It creates a tier for each speaker-channel observed in the file.

        :param filename: (str)

        """
        with codecs.open(filename, 'r', 'utf-8') as fp:
            lines = fp.readlines()

            row_names = lines[0].split('\t')
            lines.pop(0)

            # Extract rows, create tiers and metadata.
            for i, line in enumerate(lines):

                # a comment
                if line.startswith(';;'):
                    continue

                # a tab-delimited line
                line = line.split('\t')
                if len(line) < 10:
                    raise AioLineFormatError(i+1, line)

                try:
                    # index raises a ValueError if the string is missing
                    channel = line[row_names.index('channel;int')]
                    speaker = line[row_names.index('speaker;unicode')]
                    speaker_type = line[row_names.index('speakerType;unicode')]
                    speaker_dialect = line[row_names.index('speakerDialect;unicode')]
                    tag_str = line[row_names.index('transcript;unicode')]
                    begin_str = line[row_names.index('start;float')]
                    end_str = line[row_names.index('end;float')]
                    media_url = line[row_names.index('file;unicode')].strip()
                except ValueError:
                    raise AioLineFormatError(i+1, line)

                # check for the tier (find it or create it)
                tier_name = speaker + '-' + channel
                tier = self.find(tier_name)
                if tier is None:

                    media = None
                    idt = media_url.strip()
                    for m in self._media:
                        if m.get_filename() == idt:
                            media = m
                    if media is None:
                        media = sppasMedia(media_url)

                    tier = self.create_tier(tier_name, media=media)
                    tier.metadata["mediaChannel"] = channel
                    tier.metadata["speakerName"] = speaker
                    tier.metadata["speakerType"] = speaker_type
                    tier.metadata["speakerDialect"] = speaker_dialect

                # Add the new annotation
                label = sppasLabel(sppasTag(tag_str))
                location = sppasLocation(sppasInterval(sppasXtrans.make_point(float(begin_str)),
                                                       sppasXtrans.make_point(float(end_str))))
                tier.create_annotation(location, label)

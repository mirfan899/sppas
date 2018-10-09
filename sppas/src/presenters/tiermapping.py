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

    src.presenters.tiermapping.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sppas.src.utils.makeunicode import u
from sppas.src.resources.mapping import sppasMapping
from sppas.src.resources.mapping import DEFAULT_SEP
from sppas.src.anndata import sppasLabel, sppasTag
from sppas.src.anndata import sppasAnnotation

# ---------------------------------------------------------------------------


class sppasMappingTier(sppasMapping):
    """Map content of annotations of a tier from a mapping table.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    A conversion table is used to map symbols of labels of a tier with new
    symbols. This class can convert either individual symbols or strings of
    symbols (syllables, words, ...) if a separator is given.

    Any symbols in the transcription tier which is not in the conversion
    table is replaced by a specific symbol (by default '*').

    """
    def __init__(self, dict_name=None):
        """Create a sppasMappingTier instance.

        :param dict_name: (str) The mapping dictionary.

        """
        super(sppasMappingTier, self).__init__(dict_name)
        self._delimiters = DEFAULT_SEP

    # -----------------------------------------------------------------------

    def set_delimiters(self, delimit_list):
        """Fix the list of characters used as symbol delimiters.

        If delimit_list is an empty list, the mapping system will map with a
        longest matching algorithm.

        :param delimit_list: List of characters, for example [" ", ".", "-"]

        """
        # Each element of the list must contain only one character
        for i, c in enumerate(delimit_list):
            delimit_list[i] = str(c)[0]

        # Set the delimiters as Iterable() and not as List()
        self._delimiters = tuple(delimit_list)

    # -----------------------------------------------------------------------

    def map_tier(self, tier):
        """Run the mapping process on an input tier.

        :param tier: (Tier) The tier instance to map label symbols.
        :returns: a new tier, with the same name as the given tier

        """
        # Create the output tier
        new_tier = tier.Copy()

        # if nothing to do
        if tier.GetSize() == 0 or self.is_empty() is True:
            return new_tier

        # map
        for ann in new_tier:
            for text in ann.GetLabel().GetLabels():
                if text.IsEmpty() is False and text.IsSilence() is False:
                    l = self.map(text.GetValue(), self._delimiters)
                    text.SetValue(l)

        return new_tier

    # -----------------------------------------------------------------------

    def map_annotation(self, annotation):
        """Run the mapping process on an annotation.

        :param annotation: (sppasAnnotation) annotation with symbols to map
        :returns: a new annotation, with the same 'id' as the given one

        """
        # Annotation without label
        if annotation.is_labelled() is False:
            a = annotation.copy()
            a.gen_id()
            return a

        # Map all tags of all labels, if tags are strings
        new_labels = list()
        for label in annotation.get_labels():
            new_label = sppasLabel()
            for tag, score in label:
                if tag.get_type() == 'str' and \
                        tag.is_empty() is False and \
                        tag.is_silence() is False:
                    new_content = self.map(tag.get_content(), self._delimiters)
                    new_label.append(sppasTag(new_content), score)
                else:
                    new_label.append(tag.copy())
            new_labels.append(new_label)

        # Create an annotation with the new version of labels
        a = sppasAnnotation(annotation.get_location().copy(), new_labels)
        for m in annotation.get_meta_keys():
            if m != 'id':
                a.set_meta(m, annotation.get_meta(m))

        return a

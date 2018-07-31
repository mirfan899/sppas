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
#                   Copyright (C) 2011-2018  Brigitte Bigi
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
# File: filterprocess.py
# ----------------------------------------------------------------------------

import wx
import logging

from sppas.src.anndata import sppasFilters
from sppas.src.ui.wxgui.views.processprogress import ProcessProgressDialog

# ----------------------------------------------------------------------------


class SingleFilterProcess:

    def __init__(self, data,
                       match_all,
                       tier_name,
                       file_manager,
                ):
        """Filter process for "tag", "loc" and "dur" filters.

        :param data: tuple(filter, function, patterns)
        :param match_all: (bool) match all predicates, instead of match any of them
        :param tier_name: (str) output tier name
        :param file_manager: (xFiles)

        """
        self.data = data
        self.match_all = match_all
        self.file_manager = file_manager
        self.tier_name = tier_name

    # -----------------------------------------------------------------------
    #
    # def __create_single_predicate(self):
    #     # Musn't occur, but we take care...
    #     if not len(self.sel_predicates):
    #         # create a predicate that will filter... nothing: everything is matching!
    #         return Sel(regexp='*')
    #     # Define operator:
    #     #    - AND if "Apply All"
    #     #    - OR  if "Apply any"
    #     if self.match_all:
    #         return functools.reduce(operator.and_, self.sel_predicates)
    #     return functools.reduce(operator.or_, self.sel_predicates)

    # -----------------------------------------------------------------------

    def run_on_tier(self, tier):
        """Apply filters on a tier.

        :param tier: (sppasTier)
        :param data: tuple(filter, function, patterns)
        :return: (sppasTier)

        TODO: can work with multiple values (only if tag)
        TODO: convert the type of the value (str is only if tag-str)

        """

        logging.info("Apply sppasFilter() on tier: {:s}".format(tier.get_name()))
        filter = sppasFilters(tier)
        ann_sets = list()

        for d in self.data:

            if len(d[2]) == 1:
                # a little bit of doc:
                #   - getattr() returns the value of the named attributed of object.
                #     it returns filter.tag if called like getattr(filter, "tag")
                #   - func(**{'x': '3'}) is equivalent to func(x='3')
                #
                logging.info(" >>> filter.{:s}({:s}={:s})".format(
                    d[0],
                    d[1],
                    d[2][0]))

                ann_sets.append(getattr(filter, d[0])(**{d[1]: d[2][0]}))

        if len(ann_sets) == 0:
            return None

        # Merge results (apply '&' or '|' on the resulting data sets)
        ann_set = ann_sets[0]
        if self.match_all:
            for i in range(1, len(ann_sets)):
                ann_set = ann_set & ann_sets[i]
                if len(ann_set) == 0:
                    return None
        else:
            for i in range(1, len(ann_sets)):
                ann_set = ann_set | ann_sets[i]

        # convert the annotations set into a tier
        filtered_tier = ann_set.to_tier(name=self.tier_name, annot_value=False)

        return filtered_tier

    # -----------------------------------------------------------------------

    def run(self):
        """Filter all the given tiers."""

        for i in range(self.file_manager.GetSize()):
            # obj is a TrsList instance
            obj = self.file_manager.GetObject(i)
            trs = obj.GetTranscription()

            for tier in trs:
                # tier is selected to be filtered
                if obj.IsSelected(tier.get_name()):
                    # so, we do the job!
                    new_tier = self.run_on_tier(tier)
                    if new_tier is not None:
                        # add the new tier both in Transcription and in the list
                        obj.AddTier(new_tier)

# ---------------------------------------------------------------------------

class RelationFilterProcess:

    def __init__(self, data, tier_name, file_manager):
        """Filter process for "rel".

        :param data: tuple(filter, function, patterns)
        :param tier_name: (str) output tier name
        :param file_manager: (xFiles)

        """
        self.data = data
        self.file_manager = file_manager
        self.tier_name = tier_name

    # -----------------------------------------------------------------------

    def _runRelationFilter(self, tiername, progress, annotformat):
        progress.set_header("Apply RelationFilter")
        progress.update(0, "")
        total = self.file_manager.GetSize()

        # Musn't occur, but we take care...
        if not self.rel_predicate:
            # create a predicate that will filter... nothing: everything is matching!
            predicate = Rel('after') | Rel('before')
        else:
            predicate = self.rel_predicate

        for i in range(total):

            # obj is a TrsList instance
            obj = self.file_manager.GetObject(i)
            trs = obj.GetTranscription()
            logging.debug(' ... Apply on transcription: %s (%s)'
                          '' % (self.file_manager.GetFilename(i), trs.get_name()))
            progress.set_header(self.file_manager.GetFilename(i))

            # find the Y-tier
            ytier = trs.find(tiername)
            if not ytier:
                logging.debug(' ... ... tier Y is missing.')
                continue
            yfilter = Filter(ytier)

            # apply to X-tier
            for tier in trs:

                # tier is selected to be filtered
                if obj.IsSelected(tier.get_name()):
                    logging.debug(' ... ... tier %s will be filtered' % tier.get_name())
                    progress.set_text("... %s" % tier.get_name())

                    # create an apply filter
                    xfilter = Filter(tier)
                    sf = RelationFilter(predicate, xfilter, yfilter)
                    new_tier = sf.Filter(annotformat)
                    new_tier.set_name(self.tier_name)
                    logging.debug(' ... ... ... new tier %s created ' % new_tier.get_name())

                    # append the new tier both in Transcription and in the list
                    obj.Append(new_tier)
                    logging.debug(' ... ... ... new tier %s appended ' % new_tier.get_name())

                else:
                    logging.debug(' ... ... tier %s WONT be filtered' % tier.get_name())

            logging.debug('filter is finished!')
            progress.set_fraction(float((i+1))/float(total))

        # Indicate completed!
        progress.update(1, "Completed.\n")
        progress.set_header("")

    # -----------------------------------------------------------------------

    def run(self, parent, tiername, annotformat):
        wx.BeginBusyCursor()
        # Create the progress bar
        p = ProcessProgressDialog(parent, parent._prefsIO, "Filtering progress...")
        self._runRelationFilter(tiername, p, annotformat)
        p.close()
        wx.EndBusyCursor()

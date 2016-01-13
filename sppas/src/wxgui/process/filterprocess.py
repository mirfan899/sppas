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
# ----------------------------------------------------------------------------
# File: filterprocess.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import operator
import wx
import logging

from annotationdata import Filter, SingleFilter, RelationFilter
from wxgui.views.processprogress import ProcessProgressDialog


# ----------------------------------------------------------------------------


class FilterProcess:

    def __init__(self, sel_predicates,
                       rel_predicate,
                       match_all,
                       tier_name,
                       file_manager,
                       ):
        """

        @param sel_predicates (list) list of SinglePredicate
        @param rel_predicates (RelationPredicate)
        @param match_all (bool) match all predicates, instead of match any of them
        @param output (str) output tier name
        @param file_manager (xFiles)

        """
        self.sel_predicates = sel_predicates
        self.rel_predicate  = rel_predicate
        self.match_all      = match_all
        self.file_manager   = file_manager
        self.tier_name      = tier_name


    def __create_single_predicate(self):
        # Musn't occur, but we take care...
        if not len(self.sel_predicates):
            # create a predicate that will filter... nothing: everything is matching!
            return Sel( regexp='*' )
        # Define operator:
        #    - AND if "Apply All"
        #    - OR  if "Apply any"
        if self.match_all:
            return reduce(operator.and_, self.sel_predicates)
        return reduce(operator.or_, self.sel_predicates)


    def RunSingleFilter(self):
        predicate = self.__create_single_predicate()

        for i in range(self.file_manager.GetSize()):
            # obj is a TrsList instance
            obj = self.file_manager.GetObject(i)
            trs = obj.GetTranscription()

            for tier in trs:
                # tier is selected to be filtered
                if obj.IsSelected(tier.GetName()):
                    # create an apply filter
                    tierfilter = Filter( tier )
                    sf = SingleFilter( predicate,tierfilter )
                    new_tier = sf.Filter()
                    new_tier.SetName( self.tier_name )
                    # append the new tier both in Transcription and in the list
                    obj.Append( new_tier )



    def _runRelationFilter(self, tiername, progress):
        progress.set_header("Apply RelationFilter")
        progress.update(0,"")
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
            logging.debug (' ... Apply on transcription: %s (%s)'%(self.file_manager.GetFilename(i),trs.GetName()))
            progress.set_header(self.file_manager.GetFilename(i))

            # find the Y-tier
            ytier = trs.Find( tiername )
            if not ytier:
                logging.debug(' ... ... tier Y is missing.')
                continue
            yfilter = Filter( ytier )

            # apply to X-tier
            for tier in trs:

                # tier is selected to be filtered
                if obj.IsSelected(tier.GetName()):
                    logging.debug(' ... ... tier %s will be filtered'%tier.GetName())
                    progress.set_text("... %s"%tier.GetName())

                    # create an apply filter
                    xfilter = Filter( tier )
                    sf = RelationFilter( predicate, xfilter, yfilter )
                    new_tier = sf.Filter()
                    new_tier.SetName( self.tier_name )
                    logging.debug(' ... ... ... new tier %s created '%new_tier.GetName())

                    # append the new tier both in Transcription and in the list
                    obj.Append( new_tier )
                    logging.debug(' ... ... ... new tier %s appended '%new_tier.GetName())

                else:
                    logging.debug(' ... ... tier %s WONT be filtered'%tier.GetName())

            logging.debug('filter is finished!')
            progress.set_fraction(float((i+1))/float(total))

        # Indicate completed!
        progress.update(1,"Completed.\n")
        progress.set_header("")


    def RunRelationFilter(self, parent, tiername):
        wx.BeginBusyCursor()

        # Create the progress bar
        p = ProcessProgressDialog(parent, parent._prefsIO)
        p.set_title("Filtering progress...")
        self._runRelationFilter(tiername,p)
        p.close()
        wx.EndBusyCursor()

# ----------------------------------------------------------------------------


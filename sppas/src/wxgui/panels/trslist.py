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
# File: trslist.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import os.path
import logging

import annotationdata.io
from annotationdata.transcription import Transcription

from wxgui.ui.CustomEvents import PanelSelectedEvent
from wxgui.structs.prefs   import Preferences
from wxgui.structs.themes  import BaseTheme
from wxgui.views.preview   import PreviewTierDialog
from wxgui.dialogs.choosers import RadiusChooser
from wxgui.dialogs.msgdialogs import ShowInformation
from wxgui.dialogs.msgdialogs import ShowYesNoQuestion

from wxgui.ui.CustomListCtrl import CheckListCtrl


# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

FG_FILE_COLOUR = wx.Colour(45,60,10)
FG_FILE_DIRTY_COLOUR = wx.Colour(45,60,170)

# -------------------------------------------------------------------------

class TrsList( wx.Panel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Show data about transcriptions, in a panel including a list of tiers.

    """

    def __init__(self, parent, filename, trs=None, multiple=False):
        wx.Panel.__init__(self, parent, -1, size=wx.DefaultSize)

        # initialize the GUI
        self._prefs     = Preferences( BaseTheme() )
        self._filename  = filename
        self._dirty     = False # the transcription was changed
        self._selected  = False # the transcription is selected
        self._protected = []    # list of the tiers that are protected (can't be modified)

        if len(filename) == 0:
            self._filename = "Empty"

        boxtitle = self._create_title()
        self.tier_list = self._create_list( multiple )

        # load the Transcription
        if trs is None and len(filename) != 0:
            self.LoadFile(filename)
        else:
            self._transcription = trs
        # add Transcription information in the list
        for i in range(self._transcription.GetSize()):
            self.SetTierProperties(i)
        self._checksize()

        # events
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected, self.tier_list)
        self.Bind(wx.EVT_LIST_COL_CLICK,     self.OnListItemSelected, self.tier_list)

        # layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(boxtitle,       0, wx.EXPAND|wx.ALL, border=4)
        sizer.Add(self.tier_list, 1, wx.EXPAND|wx.ALL, border=4)

        self.SetFont( self._prefs.GetValue( 'M_FONT') )
        self.SetForegroundColour( self._prefs.GetValue( 'M_FG_COLOUR') )
        self.SetBackgroundColour( self._prefs.GetValue( 'M_BG_COLOUR') )
        self._boxtitle.SetForegroundColour( FG_FILE_COLOUR )

        self.SetSizer(sizer)
        self.SetAutoLayout( True )
        self.Layout()

    # End __init__
    # ----------------------------------------------------------------------


    def _create_title(self):
        """ Create the title of the panel. """
        _sizer = wx.BoxSizer( wx.HORIZONTAL )

        self._static_tx = wx.TextCtrl(self, -1, "File: ", style=wx.TE_READONLY|wx.NO_BORDER)
        self._boxtitle  = wx.TextCtrl(self, -1, self._filename, style=wx.TE_READONLY|wx.NO_BORDER)

        _sizer.Add(self._static_tx, 0, wx.RIGHT, border=2)
        _sizer.Add(self._boxtitle,  1, wx.EXPAND)
        return _sizer


    def _create_list(self, multiple=False):
        """ Create the list to show information of a each tier of a transcription. """
        #tier_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.BORDER_NONE)
        if multiple:
            tier_list = CheckListCtrl(self, -1, style=wx.LC_REPORT|wx.BORDER_NONE)
        else:
            tier_list = CheckListCtrl(self, -1, style=wx.LC_REPORT|wx.BORDER_NONE|wx.LC_SINGLE_SEL)

        # Add all columns
        colnames = [" Nb ", " Name    ", " Begin   ", " End     ", " Type    ", " Size    "]
        for i,n in enumerate(colnames):
            tier_list.InsertColumn(i,n)

        # Fix column width
        for i in range(len(colnames)):
            tier_list.SetColumnWidth(i,wx.LIST_AUTOSIZE_USEHEADER)
        # Enlarge column with tier name
        tier_list.SetColumnWidth(1, 140)

        return tier_list

    # ----------------------------------------------------------------------

    def __display_text_in_statusbar(self, text):
        wx.GetTopLevelParent(self).SetStatusText(text,0)

    def __reset_text_in_statusbar(self):
        wx.GetTopLevelParent(self).SetStatusText('',0)

    # ----------------------------------------------------------------------


    #-------------------------------------------------------------------------

    def SetTierProperties(self, tier_idx):
        """ Display tier properties. """

        try:
            tier = self._transcription[tier_idx]

            if tier.IsPoint() is True:
                tier_type = "Point"
            elif tier.IsInterval():
                tier_type = "Interval"
            elif tier.IsDisjoint():
                tier_type = "Disjoint"
            else:
                tier_type = "Unknown"

            if tier.IsEmpty() is True:
                begin = " ... "
                end   = " ... "
            else:
                begin = str(tier.GetBeginValue())
                end   = str(tier.GetEndValue())

            self.tier_list.InsertStringItem(tier_idx, "Tier %d"%(tier_idx+1))
            self.tier_list.SetStringItem(tier_idx, 1, tier.GetName())
            self.tier_list.SetStringItem(tier_idx, 2, begin )
            self.tier_list.SetStringItem(tier_idx, 3, end )
            self.tier_list.SetStringItem(tier_idx, 4, tier_type)
            self.tier_list.SetStringItem(tier_idx, 5, str(tier.GetSize()))

        except Exception as e:
            self.tier_list.InsertStringItem(1, "Error: "+str(e))

    # End SetTierProperties
    # -----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Callbacks...
    # ----------------------------------------------------------------------


    def OnListItemSelected(self, event):
        """
        An item of this panel was clicked. Inform the parent.
        """
        evt = PanelSelectedEvent(panel=self)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # End OnListItemSelected
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # GUI
    # ----------------------------------------------------------------------


    def SetPreferences(self, prefs):
        """ Set new preferences. """

        self._prefs = prefs
        self.SetBackgroundColour( self._prefs.GetValue("M_BG_COLOUR") )
        self.SetForegroundColour( self._prefs.GetValue("M_FG_COLOUR") )
        self.SetFont( self._prefs.GetValue("M_FONT") )

    #-------------------------------------------------------------------------


    def SetFont(self, font):
        """ Set a new font. """

        wx.Window.SetFont( self,font )

        self.tier_list.SetFont( font )
        for i in range(self._transcription.GetSize()):
            self.tier_list.SetItemFont( i, font )
        self._static_tx.SetFont( font )
        self._boxtitle.SetFont( font )
        self.Layout() # bigger/smaller font can impact on the layout


    def SetBackgroundColour(self, color):
        """ Set background. """

        wx.Window.SetBackgroundColour( self,color )

        self.tier_list.SetBackgroundColour( color )
        for i in range(self._transcription.GetSize()):
            self.tier_list.SetItemBackgroundColour( i, color )
        self._static_tx.SetBackgroundColour( color )
        self._boxtitle.SetBackgroundColour( color )
        self.Refresh()


    def SetForegroundColour(self, color):
        """ Set foreground and items text color. """

        wx.Window.SetForegroundColour( self,color )

        self.tier_list.SetForegroundColour( color )
        for i in range(self._transcription.GetSize()):
            self.tier_list.SetItemTextColour( i, color )
        self._static_tx.SetForegroundColour( color )
        self.Refresh()


    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Functions...
    # ----------------------------------------------------------------------


    def Protect(self):
        """
        Fix the current list of tiers as protected: they won't be changed.
        """
        self._protected = []
        for i,t in enumerate(self._transcription):
            self._protected.append(t)
            self.tier_list.SetItemTextColour( i, wx.Colour(140,10,10) )


    def Unprotect(self):
        """
        Erase the list of protected tiers.
        """
        self._protected = []

    # ----------------------------------------------------------------------


    def IsSelected(self, tiername, case_sensitive=False):
        """
        Return True if the tier is selected.
        """
        i = self._transcription.GetIndex(tiername, case_sensitive)
        if i != -1:
            return self.tier_list.IsSelected(i)
        return False

    # End IsSelected
    # ----------------------------------------------------------------------


    def Select(self, tiername, case_sensitive=False):
        """
        Select tiers which name is exactly matching.
        """
        i = self._transcription.GetIndex(tiername, case_sensitive)
        if i != -1:
            self.tier_list.Select(i, on=True)
            return True
        return False

    # End Select
    # ----------------------------------------------------------------------


    def Deselect(self):
        #for i in range(self.tier_list.GetItemCount()):
        #    self.tier_list.Select( i, on=0 )
        self.tier_list.DeSelectAll()

    # End Deselect
    # ----------------------------------------------------------------------


    def Rename(self):
        """ Rename the selected tier. Dialog with the user to get the new name. """

        if self._transcription.GetSize() == 0:
            return

        # Get the selected tier in the list
        sellist = self.tier_list.GetFirstSelected()
        # Nothing selected
        if sellist == -1:
            return
        # Too many selected items
        if self.tier_list.GetSelectedItemCount()>1:
            ShowInformation(self, self._prefs, 'You must check only one tier to rename...', style=wx.ICON_INFORMATION)
            return

        tier = self._transcription[sellist]
        if tier in self._protected:
            ShowInformation(self, self._prefs, "You are attempting to rename a protected tier. It's forbidden!", style=wx.ICON_INFORMATION)
            return

        # Ask the user to enter a new name
        dlg = wx.TextEntryDialog(self, 'What is the new tier name?','Data Roamer', 'Rename a tier.')
        dlg.SetValue( self._transcription[sellist].GetName() )
        if dlg.ShowModal() == wx.ID_OK:
            self.__display_text_in_statusbar('New tier name: %s.' % dlg.GetValue())
            # Update tier name of the transcription
            tier.SetName( dlg.GetValue())
            # Update tier name of the list
            self.tier_list.SetStringItem(sellist, 1, dlg.GetValue())
            self._dirty = True
            self._boxtitle.SetForegroundColour( FG_FILE_DIRTY_COLOUR )
            self.Refresh()
        dlg.Destroy()

    # End Rename
    # ----------------------------------------------------------------------


    def Cut(self):
        """ Cut the selected tier. Return the clipboard. """

        if self._transcription.GetSize() == 0:
            return

        # Get the selected tier in the list
        sellist = self.tier_list.GetFirstSelected()
        # No tier selected
        if sellist == -1:
            return
        # Too many selected items
        if self.tier_list.GetSelectedItemCount()>1:
            ShowInformation( self, self._prefs, 'One tier must be checked.', style=wx.ICON_INFORMATION)
            return

        # Copy the tier to the clipboard
        tier = self._transcription[sellist]
        if tier in self._protected:
            ShowInformation( self, self._prefs, "You are attempting to cut a protected tier. It's forbidden!", style=wx.ICON_INFORMATION)
            return

        clipboard = tier.Copy()
        # Delete tier of the transcription
        self._transcription.Remove(sellist)
        # Delete tier of the list
        self.tier_list.DeleteItem(sellist)

        # Update tier numbers of next items in the list.
        for i in range(sellist,self.tier_list.GetItemCount()):
            self.tier_list.SetStringItem(i, 0, "Tier "+str(i+1))

        # give information
        self.__display_text_in_statusbar('Tier '+clipboard.GetName() +' cutted by the user.')

        self.Deselect()
        self._checksize()
        self._dirty = True
        self._boxtitle.SetForegroundColour( FG_FILE_DIRTY_COLOUR )
        self.Refresh()

        return clipboard

    # End Cut
    # ----------------------------------------------------------------------


    def Copy(self):
        """ Return the selected tier. """

        if self._transcription.GetSize() == 0:
            return

        # Get the selected tier in the list
        sellist = self.tier_list.GetFirstSelected()
        if sellist == -1:
            return
        # Too many selected items
        if self.tier_list.GetSelectedItemCount()>1:
            ShowInformation( self, self._prefs, "One tier must be checked", style=wx.ICON_INFORMATION)
            return

        # Copy the tier to the clipboard
        tier = self._transcription[sellist]

        # give information
        self.__display_text_in_statusbar('Tier '+tier.GetName()+' cutted by the user.')

        return tier.Copy()

    # End Copy
    # ----------------------------------------------------------------------


    def Paste(self, clipboard):
        """ Paste the clipboard tier to the current page. """

        # Get the clipboard tier
        if clipboard is None:
            return

        # Append clipboard to the transcription
        tier = clipboard #.Copy()

        self.Append(tier)

        # The tier comes from another Transcription... must update infos.
        if not (tier.GetTranscription() is self._transcription):
            # parent transcription
            tier.SetTranscription( self._transcription )
            # And if CtrlVocab...
            # TODO

        # give information
        self.__display_text_in_statusbar('Tier '+clipboard.GetName()+' added.')

        self._checksize()

    # End Paste
    # ----------------------------------------------------------------------


    def Delete(self):
        """ Delete the selected tier.
            Dialog with the user to confirm. """

        if self._transcription.GetSize() == 0:
            return 0

        # Get the selected tier in the list of this page
        sellist = self.tier_list.GetFirstSelected()
        if sellist == -1:
            return 0

        # Get Indexes of tiers to remove
        indexes = []
        while sellist != -1:
            indexes.append( sellist )
            sellist = self.tier_list.GetNextSelected(sellist)

        # Ask the user to confirm before deleting
        delete = 0
        message = 'Are you sure you want to definitively delete:\n%d tiers in %s?'%(len(indexes),self._filename)
        dlg = ShowYesNoQuestion(self, self._prefs, message)
        if dlg == wx.ID_YES:
            for sellist in reversed( sorted(indexes) ):

                item = self.tier_list.GetItem(sellist)
                self.__display_text_in_statusbar('Delete tier: %d.' % item.GetId())

                tier = self._transcription[sellist]
                if tier in self._protected:
                    self.__display_text_in_statusbar('Tier %d is protected. It cant be deleted.'% item.GetId())
                else:

                    # Delete tier of the transcription
                    self._transcription.Remove(sellist)
                    # Delete tier of the list
                    self.tier_list.DeleteItem(sellist)
                    self.__display_text_in_statusbar('Tier %d deleted by the user.'% item.GetId())
                    delete = delete + 1
                    # Update tier numbers of next items in the list.
                    for i in range(sellist,self.tier_list.GetItemCount()):
                        self.tier_list.SetStringItem(i, 0, str(i+1))

        self._dirty = True
        self._boxtitle.SetForegroundColour( FG_FILE_DIRTY_COLOUR )
        self.Refresh

        self._checksize()
        return delete

    # End Delete
    # ----------------------------------------------------------------------


    def Duplicate(self):
        """ Duplicate the selected tier. """

        if self._transcription.GetSize() == 0:
            return

        # Get the selected tier index in the list
        sellist = self.tier_list.GetFirstSelected()
        if sellist == -1:
            return
        # Too many selected items
        if self.tier_list.GetSelectedItemCount()>1:
            ShowInformation(self, self._prefs, "One tier must be checked", style=wx.ICON_INFORMATION)
            return

        tier = self._transcription[sellist]
        self.Append(tier.Copy())

        # give information
        self.__display_text_in_statusbar('Tier '+tier.GetName()+ ' successfully duplicated.')

    # End Duplicate
    # ----------------------------------------------------------------------


    def MoveUp(self):
        """ Move up the selected tier (except for the first one). """

        if self._transcription.GetSize() == 0:
            return

        # Get the selected tier in the list
        sellist = self.tier_list.GetFirstSelected()
        if sellist == -1:
            return
        # Too many selected items
        if self.tier_list.GetSelectedItemCount()>1:
            ShowInformation( self, self._prefs, "One tier must be checked", style=wx.ICON_INFORMATION)
            return

        #
        tier = self._transcription[sellist]
        if tier in self._protected:
            ShowInformation(self, self._prefs, "You are attempting to move a protected tier. It's forbidden!", style=wx.ICON_INFORMATION)
            return

        #Impossible to move up the first tier.
        if sellist == 0:
            return

        # Pop selected tier from transcription.
        try:
            self._transcription._hierarchy.removeTier(self._transcription[sellist]) # waiting a better way to work with hierarchy...
        except Exception:
            pass
        self._transcription.Pop(sellist)

        # Delete old tier of the list
        self.tier_list.DeleteItem(sellist)

        # Add tier to the transcription
        tierindex = self._transcription.Add(tier, sellist-1 )
        # Add tier to the list
        self.SetTierProperties(tierindex)
        # Update tier number
        self.tier_list.SetStringItem(sellist, 0, str(sellist+1))

        # Let the item selected
        self.tier_list.Select(sellist-1, on=True)
        self._dirty = True
        self._boxtitle.SetForegroundColour( FG_FILE_DIRTY_COLOUR )
        self.Refresh()

        # give information
        self.__display_text_in_statusbar('Tier successfully moved up.')

    # End MoveUp
    # ----------------------------------------------------------------------


    def MoveDown(self):
        """ Move down the selected tier (except for the last one). """

        if self._transcription.GetSize() == 0:
            return

        # Get the selected tier in the list
        sellist = self.tier_list.GetFirstSelected()
        if sellist == -1:
            return

        # Too many selected items
        if self.tier_list.GetSelectedItemCount()>1:
            ShowInformation(self, self._prefs, "One tier must be checked", style=wx.ICON_INFORMATION)
            return

        #
        tier = self._transcription[sellist]
        if tier in self._protected:
            ShowInformation(self, self._prefs, "You are attempting to move a protected tier. It's forbidden!", style=wx.ICON_INFORMATION)
            return

        # Impossible to move down the last tier.
        if (sellist+1) == self.tier_list.GetItemCount():
            return

        # Pop selected tier from transcription.
        try:
            self._transcription._hierarchy.removeTier(self._transcription[sellist]) # waiting a better way to work with hierarchy...
        except Exception:
            pass
        self._transcription.Pop(sellist)

        # Delete old tier of the list
        self.tier_list.DeleteItem(sellist)

        # Add tier to the transcription
        if (sellist+1) >= self.tier_list.GetItemCount():
            tierindex = self._transcription.Add( tier )
        else:
            tierindex = self._transcription.Add( tier, sellist+1 )
        # Add tier to the list
        self.SetTierProperties(tierindex)
        # Update tier number
        self.tier_list.SetStringItem(sellist,   0, "Tier "+str(sellist+1))
        self.tier_list.SetStringItem(sellist+1, 0, "Tier "+str(tierindex+1))

        # Let the item selected
        self.tier_list.Select(sellist+1, on=True)
        self._dirty = True
        self._boxtitle.SetForegroundColour( FG_FILE_DIRTY_COLOUR )
        self.Refresh()

        # give information
        self.__display_text_in_statusbar('Tier successfully moved down.')

    # End MoveDown
    # ----------------------------------------------------------------------


    def Radius(self):
        """ Fix a new radius value to all TimePoint instances of the selected tier. """

        if self._transcription.GetSize() == 0:
            return

        # Get the selected tier in the list
        sellist = self.tier_list.GetFirstSelected()
        if sellist == -1:
            return

        #
        tier = self._transcription[sellist]
        if tier in self._protected:
            ShowInformation(self, self._prefs, "You are attempting to modify a protected tier. It's forbidden!", style=wx.ICON_INFORMATION)
            return

        # Open a dialog to ask the new radius value
        radius = tier.GetBegin().GetRadius()
        dlg = RadiusChooser( self, radius )
        if dlg.ShowModal() == wx.ID_OK:
            # Get the value
            r = dlg.GetValue()
            try:
                r = float(r)
                if r > 1.0: raise
            except Exception:
                logging.info('Radius cancelled (can not be applied: %f).'%r)
                return

            # Set the value
            while sellist != -1:
                tier.SetRadius( r )
                logging.debug('Radius fixed to %f'%r)
                sellist = self.tier_list.GetNextSelected(sellist)

        dlg.Destroy()

    # End Radius
    # ----------------------------------------------------------------------


    def Preview(self):
        """ Open a grid frame with the selected tier content. """

        if self._transcription.GetSize() == 0:
            return

        # Get the selected tier in the list
        sellist = self.tier_list.GetFirstSelected()
        if sellist == -1:
            return

        # Too many selected items
        if self.tier_list.GetSelectedItemCount()>1:
            ShowInformation(self, self._prefs, "One tier only must be checked", style=wx.ICON_INFORMATION)
            return

        tier = self._transcription[sellist]

        dlg = PreviewTierDialog(self, self._prefs, tiers=[tier])
        dlg.Show()

    # End Preview
    # ----------------------------------------------------------------------


    def Append(self, newtier):
        """
        Append a tier in the transcription and in the list.

        """
        # Append tier to the transcription
        tierindex = self._transcription.Append( newtier )

        # Append tier to the list
        self.SetTierProperties(tierindex)

        # Display information
        self._dirty = True
        self._boxtitle.SetForegroundColour( FG_FILE_DIRTY_COLOUR )
        self.Refresh()
        self.__display_text_in_statusbar('Tier '+newtier.GetName()+ ' successfully added.')

    # End Append
    # ----------------------------------------------------------------------


    def LoadFile(self, filename):
        """
        Load a file in memory and show it.

        @param filename is an annotated file.

        """
        self._filename = filename
        if os.path.exists(filename) is False:
            self._transcription = Transcription("Empty")
            return
        try:
            self._transcription = annotationdata.io.read( filename )
            self._dirty = False
            self._boxtitle.SetForegroundColour( FG_FILE_COLOUR )
            self.Refresh()
        except Exception as e:
            logging.info('Error loading file %s: %s'%(filename,str(e)))
            self._transcription = Transcription("IO-Error")
            #raise

    # End LoadFile
    # ----------------------------------------------------------------------


    def Save(self):
        """ Save the current page content. """

        if self._dirty is False:
            self.__display_text_in_statusbar('File '+ self._filename + " not saved (not changed)!")
            return

        try:
            annotationdata.io.write(self._filename, self._transcription)
            self._dirty = False
            self._boxtitle.SetForegroundColour( FG_FILE_COLOUR )
            self.Refresh()
            self.__display_text_in_statusbar('File '+ self._filename + " saved.")
        except Exception as e:
            # give information
            ShowInformation(self, self._prefs, 'File not saved: %s'%str(e), style=wx.ICON_ERROR)

    # End Save
    # ----------------------------------------------------------------------


    def SaveAs(self, filename):
        """
        Save the current page content with another file name.
        Keep everything un-changed in self.
        """
        try:
            annotationdata.io.write(filename, self._transcription)
        except Exception as e:
            # give information
            ShowInformation(self, self._prefs, 'File not saved: %s'%str(e), style=wx.ICON_ERROR)

    # End SaveAs
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------

    def GetTranscription(self):
        """ Return the Transcription. """

        return self._transcription

    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------

    def _checksize(self):
        """
        Check the transcription size. Append an "empty line" if
        transcription is empty. Remove this empty line if transcription
        is not empty. Return True if something has changed.
        """

        # Append an "empty" line in the ListCtrl
        if self._transcription.GetSize() == 0 and self.tier_list.GetItemCount() == 0:
            self.tier_list.InsertStringItem(0, " ... ")
            if self._transcription.GetName() == "IO-Error":
                self.tier_list.SetStringItem(0, 1, " Error while reading this file " )
            else:
                self.tier_list.SetStringItem(0, 1, " Empty file: no tiers " )
            for i in range(2,5):
                self.tier_list.SetStringItem(0, i, " " )
            return True

        # Remove the "empty" line of the ListCtrl
        if self._transcription.GetSize() < self.tier_list.GetItemCount():
            self.tier_list.DeleteItem( self.tier_list.GetItemCount()-1 )
            return True

        return False

    # End _checksize
    # ----------------------------------------------------------------------

# --------------------------------------------------------------------------

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

    src.ui.phoenix.filespck.filesviewmodel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This model acts as a bridge between a DataViewCtrl and a FileData instance. 

"""

import unittest
import os
import logging
import wx
import wx.dataview

from sppas import sppasTypeError
from sppas.src.anndata import sppasRW
from sppas.src.files.filedata import FileName, FileRoot, FilePath, FileData

from sppas.src.ui.phoenix import sppasSwissKnife
from .basectrls import ColumnProperties

# -----------------------------------------------------------------------

   
class FileAnnotIcon(object):
    """Represents the link between a file extension and an icon name.
    
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Constructor of a FileAnnotIcon.

        Set the name of the icon for all known extensions of annotations.

        Create a dictionary linking a file extension to the name of the 
        software it comes from. It is supposed this name is matching an
        an icon in PNG format.

        """
        self.__exticon = dict()
        self.__exticon['.WAV'] = "Audio"
        self.__exticon['.WAVE'] = "Audio"

        for ext in sppasRW.TRANSCRIPTION_SOFTWARE:
            software = sppasRW.TRANSCRIPTION_SOFTWARE[ext]
            if ext.startswith(".") is False:
                ext = "." + ext
            self.__exticon[ext.upper()] = software

    # -----------------------------------------------------------------------

    def get_icon_name(self, ext):
        if ext.startswith(".") is False:
            ext = "." + ext
        return self.__exticon.get(ext.upper(), "")

# ---------------------------------------------------------------------------


class FileIconRenderer(wx.dataview.DataViewCustomRenderer):
    """Draw an icon matching a known file extension.
    
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """
    def __init__(self,
                 varianttype="wxBitmap",
                 mode=wx.dataview.DATAVIEW_CELL_INERT,
                 align=wx.dataview.DVR_DEFAULT_ALIGNMENT):
        super(FileIconRenderer, self).__init__(varianttype, mode, align)
        self.value = ""

    def SetValue(self, value):
        self.value = value
        return True

    def GetValue(self):
        return self.value

    def GetSize(self):
        """Return the size needed to display the value."""
        size = self.GetTextExtent('TT')
        return size[1]*2, size[1]*2

    def Render(self, rect, dc, state):
        """Draw the bitmap, adjusting its size. """
        if self.value == "":
            return False

        x, y, w, h = rect
        s = min(w, h)
        s = int(0.6 * s)

        bmp = sppasSwissKnife.get_bmp_icon(self.value, s)
        dc.DrawBitmap(bmp, x + (w-s)//2, y + (h-s)//2)
        
        return True

# ----------------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------------


class FilesTreeViewModel(wx.dataview.PyDataViewModel):
    """A class that is a DataViewModel combined with an object mapper.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This model mapper provides these data columns identifiers:

        0. icon:     wxBitmap
        1. file:     string
        2. check:    bool
        3. type:     string
        4. data:     string
        5. size:     string

    """

    def __init__(self):
        """Constructor of a fileTreeModel.

        :param data: (FileData) Workspace to be managed by the mapper

        """
        wx.dataview.PyDataViewModel.__init__(self)
        try:  # wx4 only
            self.UseWeakRefs(True)
        except AttributeError:
            pass

        # The icons to display depending on the file extension
        self.exticon = FileAnnotIcon()

        # The workspace to display
        self.__data = FileData()

        # Map between displayed columns and workspace
        self.__mapper = dict()
        self.__mapper[0] = FilesTreeViewModel.__create_col('icon')
        self.__mapper[1] = FilesTreeViewModel.__create_col('file')
        self.__mapper[2] = FilesTreeViewModel.__create_col('check')
        self.__mapper[3] = FilesTreeViewModel.__create_col('type')
        self.__mapper[4] = FilesTreeViewModel.__create_col('date')
        self.__mapper[5] = FilesTreeViewModel.__create_col('size')
        self.__mapper[6] = FilesTreeViewModel.__create_col('')

        # GUI information which can be managed by the mapper
        self._bgcolor = None
        self._fgcolor = None

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data displayed into the tree."""
        return self.__data

    # -----------------------------------------------------------------------

    def set_data(self, data):
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        self.__data = data
        self.Cleared()

    # -----------------------------------------------------------------------
    # Manage column properties
    # -----------------------------------------------------------------------

    def GetColumnCount(self):
        """Override. Report how many columns this model provides data for."""
        return len(self.__mapper)

    # -----------------------------------------------------------------------

    def GetExpanderColumn(self):
        """Returns column which have to contain the expanders."""
        return 1

    # -----------------------------------------------------------------------

    def GetColumnType(self, col):
        """Override. Map the data column number to the data type.

        :param col: (int)

        """
        return self.__mapper[col].stype

    # -----------------------------------------------------------------------

    def GetColumnName(self, col):
        """Map the data column number to the data name.
        
        :param col: (int)

        """
        return self.__mapper[col].name

    # -----------------------------------------------------------------------

    def GetColumnMode(self, col):
        """Map the data column number to the cell mode.

        :param col: (int)

        """
        return self.__mapper[col].mode

    # -----------------------------------------------------------------------

    def GetColumnWidth(self, col):
        """Map the data column number to the col width.
        
        :param col: (int)

        """
        return self.__mapper[col].width

    # -----------------------------------------------------------------------

    def GetColumnRenderer(self, col):
        """Map the data column numbers to the col renderer.
        
        :param col: (int)

        """
        return self.__mapper[col].renderer

    # -----------------------------------------------------------------------

    def GetColumnAlign(self, col):
        """Map the data column numbers to the col alignment.
        
        :param col: (int)

        """
        return self.__mapper[col].align

    # -----------------------------------------------------------------------
    # Manage the tree
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        self._bgcolor = color

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        self._fgcolor = color

    # -----------------------------------------------------------------------

    def GetChildren(self, parent, children):
        """The view calls this method to find the children of any node.
        
        There is an implicit hidden root node, and the top level
        item(s) should be reported as children of this node. 

        """
        if not parent:
            for fp in self.__data:
                children.append(self.ObjectToItem(fp))
            return len(self.__data)

        # Otherwise we'll fetch the python object associated with the parent
        # item and make DV items for each of its child objects.
        node = self.ItemToObject(parent)
        if isinstance(node, (FilePath, FileRoot)):
            for f in node:
                children.append(self.ObjectToItem(f))
            return len(node)

        return 0

    # -----------------------------------------------------------------------

    def IsContainer(self, item):
        """Return True if the item has children, False otherwise.
        
        :param item: (wx.dataview.DataViewItem)

        """
        # The hidden root is a container
        if not item:
            return True
        
        # In this model the path and root objects are containers
        node = self.ItemToObject(item)
        if isinstance(node, (FilePath, FileRoot)):
            return True
        
        # but everything else (the file objects) are not
        return False

    # -----------------------------------------------------------------------

    def GetParent(self, item):
        """Return the item which is this item's parent.
        
        :param item: (wx.dataview.DataViewItem)

        """
        # The hidden root does not have a parent
        if not item:
            return wx.dataview.NullDataViewItem

        node = self.ItemToObject(item)
        
        # A FilePath does not have a parent
        if isinstance(node, FilePath):
            return wx.dataview.NullDataViewItem
        
        # A FileRoot has a FilePath parent
        elif isinstance(node, FileRoot):
            for fp in self.__data:
                if node in fp:
                    #  if fp.id == node.folder():
                    return self.ObjectToItem(fp)

        # A FileName has a FileRoot parent
        elif isinstance(node, FileName):
            for fp in self.__data:
                for fr in fp:
                    #  if fp.get_id() == node.folder():
                    if node in fr:
                        return self.ObjectToItem(fr)
        
        return wx.dataview.NullDataViewItem

    # -----------------------------------------------------------------------
    # Manage the values to display
    # -----------------------------------------------------------------------

    def GetValue(self, item, col):
        """Return the value to be displayed for this item and column. 
        
        :param item: (wx.dataview.DataViewItem)
        :param col: (int)
        
        Pull the values from the data objects we associated with the items 
        in GetChildren.
        
        """
        # Fetch the data object for this item.
        node = self.ItemToObject(item)
        if isinstance(node, (FileName, FileRoot, FilePath)) is False:
            raise RuntimeError("Unknown node type {:s}".format(type(node)))

        if self.__mapper[col].id == "icon":
            if isinstance(node, FileName) is True:
                ext = node.get_extension()
                icon_name = self.exticon.get_icon_name(ext)
                return icon_name
            return ""

        return self.__mapper[col].get_value(node)

    # -----------------------------------------------------------------------
 
    def HasContainerColumns(self, item):
        """Override.
        
        :param item: (wx.dataview.DataViewItem)

        We override this method to indicate if a container item merely acts 
        as a headline (or for categorisation) or if it also acts a normal 
        item with entries for further columns.
        
        """
        node = self.ItemToObject(item)        
        if isinstance(node, FileRoot):
            return True
        if isinstance(node, FilePath):
            return True
        return False

    # -----------------------------------------------------------------------

    def HasValue(self, item, col):
        """Override.
        
        Return True if there is a value in the given column of this item.
        
        """
        return True

    # -----------------------------------------------------------------------

    def SetValue(self, value, item, col):
        """Override. 

        :param value:
        :param item: (wx.dataview.DataViewItem)
        :param col: (int)

        """
        logging.debug("SetValue: %s\n" % value)
        
        node = self.ItemToObject(item)
        if isinstance(node, (FileName, FileRoot, FilePath)) is False:
            raise RuntimeError("Unknown node type {:s}".format(type(node)))

        if self.__mapper[col].id == "check":
            node.check = value
            # Search for the parent. It has to verify if it's check value
            # is still correct.
            if isinstance(node, FileName):
                root_parent = self.GetParent(item)
                fr = self.ItemToObject(root_parent)
                # instead of simply updating the root, we set the check
                # value to all files of this root
                # fr.update_check() is replaced by
                fr.check = value
                path_parent = self.GetParent(root_parent)
                fp = self.ItemToObject(path_parent)
                fp.update_check()

            if isinstance(node, FileRoot):
                path_parent = self.GetParent(item)
                fp = self.ItemToObject(path_parent)
                fp.update_check()

        return True

    # -----------------------------------------------------------------------

    def GetAttr(self, item, col, attr):
        node = self.ItemToObject(item)

        # default colors for foreground and background
        if self._fgcolor is not None:
            attr.SetColour(self._fgcolor)
        if self._bgcolor is not None:
            attr.SetBackgroundColour(self._bgcolor)

        if isinstance(node, FilePath):
            attr.SetBold(True)
            return True

        if isinstance(node, FileRoot):
            attr.SetItalic(True)
            return True

        if isinstance(node, FileName):
            # parent_root = self.GetParent(item)
            # parent_path = self.GetParent(parent_root)
            # if node.lock:
            #    attr.SetColour(wx.Colour(128, 128, 128))
            return True
        
        return False

    # -----------------------------------------------------------------------
    # Manage the data
    # -----------------------------------------------------------------------

    def AddFile(self, filename):
        """Add a file in the data."""
        self.__data.add_file(filename)

    # -----------------------------------------------------------------------

    def UpdateFiles(self):
        """Update the data and refresh the tree."""
        self.__data.update()
        self.Cleared()

    # -----------------------------------------------------------------------

    def RemoveCheckedFiles(self):
        self.__data.remove(FileName.CHECKED)

    # -----------------------------------------------------------------------

    def GetCheckedFiles(self):
        return self.__data.get_state(FileName.CHECKED)

    # -----------------------------------------------------------------------

    def Check(self, value=True, entry=None):
        """Check or uncheck all or any file.

        :param value: (bool) Toggle value
        :param entry: (str) Absolute or relative name of a file or a file root
        
        """
        self.__data.check(value, entry)

    # -----------------------------------------------------------------------

    def Expand(self, value=True, item=None):
        """Expand or collapse an item or all items.

        :param value: (bool) Expanded (True) or Collapsed (False)
        :param item: (wx.dataview.DataViewItem)

        """
        if item is None:
            self.__data.expand_all(bool(value))
        else:
            obj = self.ItemToObject(item)
            if isinstance(obj, (FileRoot, FilePath)):
                obj.expand = bool(value)

    # -----------------------------------------------------------------------

    def GetExpandedItems(self, value=True):
        items = list()
        for obj in self.__data.get_expanded_objects(value):
            items.append(self.ObjectToItem(obj))

        return items

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def FileToItem(self, entry):
        """Return the item matching the given entry name.

        :param entry: (str) Absolute or relative name of a file or a file root or a file path

        """
        obj = self.__data.get_object(entry)
        if obj is None:
            return wx.dataview.NullDataViewItem
        return self.ObjectToItem(obj)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    @staticmethod
    def __create_col(name):
        if name == "icon":
            col = ColumnProperties("Soft", name, "wxBitmap")
            col.width = 36
            col.align = wx.ALIGN_CENTRE
            col.renderer = FileIconRenderer()
            return col

        if name == "file":
            col_file = ColumnProperties("File", name)
            col_file.add_fct_name(FilePath, "get_id")
            col_file.add_fct_name(FileRoot, "get_id")
            col_file.add_fct_name(FileName, "get_name")
            col_file.width = 320
            return col_file

        if name == "check":
            col = ColumnProperties("Check", name, "bool")
            col.mode = wx.dataview.DATAVIEW_CELL_ACTIVATABLE
            col.align = wx.ALIGN_CENTRE
            col.width = 36
            col.add_fct_name(FileName, "get_check")
            col.add_fct_name(FileRoot, "get_check")
            col.add_fct_name(FilePath, "get_check")
            return col

        if name == "type":
            col = ColumnProperties("Type", name)
            col.add_fct_name(FileName, "get_extension")
            col.width = 120
            return col

        if name == "date":
            col = ColumnProperties("Modified", name)
            col.add_fct_name(FileName, "get_date")
            col.width = 140
            col.align = wx.ALIGN_CENTRE
            return col

        if name == "size":
            col = ColumnProperties("Size", name)
            col.add_fct_name(FileName, "get_size")
            col.width = 80
            col.align = wx.ALIGN_RIGHT
            return col

        col = ColumnProperties("", name)
        col.width = 200
        return col

# ---------------------------------------------------------------------------


class TestFileAnnotIcon(unittest.TestCase):

    def test_init(self):
        f = FileAnnotIcon()
        self.assertEqual("SPPAS.png", f.get_icon_name(".xra"))
        self.assertEqual("praat.png", f.get_icon_name(".TextGrid"))

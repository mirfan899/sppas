# coding=UTF8
# Copyright (C) 2015  Brigitte Bigi

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os.path
sys.path.append( os.path.dirname(os.path.dirname(os.path.abspath(__file__) )))
sys.path.append( os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__) ))))

import wx
from test_utils import setup_logging
from ui.CustomListCtrl import LineListCtrl

# ----------------------------------------------------------------------------

class DemoFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1,
                          "A wx.ListCtrl customized to indicate line numbers in first column",
                          size=(700,500))
        self.MakeMenu()
        self.MakeListCtrl()


    def MakeListCtrl(self):

        # create the list control
        self.list = LineListCtrl(self, -1, style=wx.LC_REPORT)#|wx.LC_SINGLE_SEL)

        # Add some columns
        for col in range(3):
            self.list.InsertColumn(col, "col-%d"%col)

        # add the rows
        for row in range(10):
            self.list.InsertStringItem(row, "content-%d-%d"%(row,1))
            for col in range(1,3):
                self.list.SetStringItem(row, col, "content-%d-%d"%(row,(col+1)))

        self.list.InsertStringItem(5, "Row5")
        for col in range(1,3):
            self.list.SetStringItem(5, col, "ro5-%d"%(col+1))

        # set the width of the columns in various ways
        for col in range(3):
            self.list.SetColumnWidth(col, wx.LIST_AUTOSIZE)

        self.list.DeleteItem(5)

        # in case we are recreating the list tickle the frame a bit so
        # it will redo the layout
        self.SendSizeEvent()


    def MakeMenu(self):
        mbar = wx.MenuBar()

        menu = wx.Menu()
        item = menu.Append(-1, "E&xit\tAlt-X")
        self.Bind(wx.EVT_MENU, self.OnExit, item)
        mbar.Append(menu, "&File")

        menu = wx.Menu()
        item = menu.Append(-1, "Show selected")
        self.Bind(wx.EVT_MENU, self.OnShowSelected, item)
        item = menu.Append(-1, "Select all")
        self.Bind(wx.EVT_MENU, self.OnSelectAll, item)
        item = menu.Append(-1, "Select none")
        self.Bind(wx.EVT_MENU, self.OnSelectNone, item)
        menu.AppendSeparator()
        item = menu.Append(-1, "Set item text colour")
        self.Bind(wx.EVT_MENU, self.OnSetTextColour, item)
        item = menu.Append(-1, "Set item background colour")
        self.Bind(wx.EVT_MENU, self.OnSetBackgroundColour, item)

        mbar.Append(menu, "&Demo")
        self.SetMenuBar(mbar)



    def OnExit(self, evt):
        self.Close()


    def OnItemActivated(self, evt):
        item = evt.GetItem()
        print "Item activated:", item.GetText()


    def OnShowSelected(self, evt):
        print "These items are selected:"
        index = self.list.GetFirstSelected()
        if index == -1:
            print "\tNone"
            return
        while index != -1:
            item = self.list.GetItem(index)
            print "\t%d" % item.GetId()
            index = self.list.GetNextSelected(index)

    def OnSelectAll(self, evt):
        for index in range(self.list.GetItemCount()):
            self.list.Select(index, True)

    def OnSelectNone(self, evt):
        index = self.list.GetFirstSelected()
        while index != -1:
            self.list.Select(index, False)
            index = self.list.GetNextSelected(index)

    def OnSetTextColour(self, evt):
        dlg = wx.ColourDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            colour = dlg.GetColourData().GetColour()
            index = self.list.GetFirstSelected()
            while index != -1:
                self.list.SetItemTextColour(index, colour)
                index = self.list.GetNextSelected(index)
        dlg.Destroy()

    def OnSetBackgroundColour(self, evt):
        dlg = wx.ColourDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            colour = dlg.GetColourData().GetColour()
            index = self.list.GetFirstSelected()
            while index != -1:
                self.list.SetItemBackgroundColour(index, colour)
                index = self.list.GetNextSelected(index)
        dlg.Destroy()

# ----------------------------------------------------------------------------

class DemoApp(wx.App):
    def OnInit(self):
        frame = DemoFrame()
        self.SetTopWindow(frame)
        frame.Show()
        return True

# ----------------------------------------------------------------------------

app = DemoApp(redirect=True, filename="testlinelistctrl.log")
app.MainLoop()

# ----------------------------------------------------------------------------

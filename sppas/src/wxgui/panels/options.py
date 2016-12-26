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
#                   Copyright (C) 2011-2017  Brigitte Bigi
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
# File: options.py
# ----------------------------------------------------------------------------

import wx.lib.scrolledpanel

# ----------------------------------------------------------------------------


class sppasOptionsPanel(wx.lib.scrolledpanel.ScrolledPanel):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Create dynamically a panel depending on a list of options.

    """
    def __init__(self, parent, options):
        """
        Constructor.

        :param options: (list) List of "Option" instances.

        """
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, style=wx.NO_BORDER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # wx objects to fill option values
        self._items = []

        for opt in options:
            self.AppendOption(opt)

        self.SetMinSize((320, 240))
        self.Fit()
        self.SetupScrolling()

    # ------------------------------------------------------------------------

    def AppendOption(self, opt):
        """
        Append an option in the panel.

        :param opt: an "Option" to append to the bottom of the panel.

        """
        if opt.get_type() == "bool":
            self.__add_bool(opt.get_text(), value=opt.get_value())

        elif opt.get_type() == "int":
            self.__add_int(opt.get_text(), value=opt.get_value())

        elif opt.get_type() == "float":
            self.__add_float(opt.get_text(), value=opt.get_value())

        else:  # if opt.get_type() == "str":
            self.__add_text(opt.get_text(), value=opt.get_value())

    # ------------------------------------------------------------------------

    def GetItems(self):
        """
        Return the objects created from the given options.

        :return: wx objects

        """
        return self._items

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def __add_bool(self, label, value=True):
        """
        Add a checkbox to the panel.

        :param label: (string) the description of the value
        :param value: (boolean) the current value

        """
        cb = wx.CheckBox(self, -1, label)
        cb.SetValue(value)
        self.GetSizer().Add(cb, 0, wx.BOTTOM, 8)

        self._items.append(cb)

    # ------------------------------------------------------------------------

    def __add_int(self, label, smin=0, smax=2000, value=1, width=130):
        """
        Add a spinner to the panel.

        :param label: (string) the description of the value
        :param smin: (int) the minimum value
        :param smax: (int) the maximum value
        :param value: (int) the current value

        """
        st = wx.StaticText(self, -1, label)

        sc = wx.SpinCtrl(self, -1, label, (30, 20), (width, -1))
        sc.SetRange(smin, smax)
        sc.SetValue(value)

        self.GetSizer().Add(st, 0, wx.LEFT, 3)
        self.GetSizer().Add(sc, 0, wx.BOTTOM, 8)

        self._items.append(sc)

    # ------------------------------------------------------------------------

    def __add_float(self, label, smin=0, smax=2000, incr=0.01, value=1.0, width=130):
        """
        Add a float spinner to the panel.

        :param label: (string) the description of the value
        :param smin: (float) the minimum value
        :param smax: (float) the maximum value
        :param incr: (float) increment for every evt_floatspin events
        :param value: (float) the current value

        """
        st = wx.StaticText(self, -1, label)

        fsc = wx.lib.agw.floatspin.FloatSpin(self, -1, size=(width, -1), increment=incr, digits=3)
        fsc.SetRange(smin, smax)
        fsc.SetValue(value)
        self.GetSizer().Add(st, 0, wx.LEFT, 3)
        self.GetSizer().Add(fsc, 0, wx.BOTTOM, 8)

        self._items.append(fsc)

    # ------------------------------------------------------------------------

    def __add_text(self, label, value=""):
        """
        Add a TextCtrl to the panel.

        :param label: (string) the description of the value
        :param value: (string) the current value

        """
        st = wx.StaticText(self, -1, label)
        textctrl = wx.TextCtrl(self, -1, size=(300, -1))
        textctrl.SetValue(value)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(textctrl)

        self.GetSizer().Add(st, 0, wx.BOTTOM, 8)
        self.GetSizer().Add(sizer, 0, wx.BOTTOM, 8)

        self._items.append(textctrl)

    # ------------------------------------------------------------------------

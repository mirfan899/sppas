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

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import wx

try:
    from agw import floatspin as FS
except ImportError:
    import wx.lib.agw.floatspin as FS

import ultimatelistctrl as ULC

# ---------------------------------------------------------------------------


DISJOINT = ("before",
            "after",
            "meets",
            "metby")

CONVERGENT = ("starts",
              "startedby",
              "finishes",
              "finishedby",
              "overlaps",
              "overlappedby",
              "contains",
              "during")

EQUALS = ("equals",)

CUSTOM = ("equals",)

META_RELATIONS = (EQUALS, DISJOINT, CONVERGENT, CUSTOM)


ALLEN_RELATIONS = (
                   ('equals', 'Equals', '', ''),
                   ('before', 'Before', 'Max delay\nin seconds:', 3.0),
                   ('after', 'After', 'Max delay\nin seconds:', 3.0),
                   ('meets', 'Meets', '', ''),
                   ('metby', 'Met by', '', ''),
                   ('overlaps', 'Overlaps', 'Min overlap\n in seconds', 0.001),
                   ('overlappedby', 'Overlapped by', 'Min overlap\n in seconds', 0.001),
                   ('starts', 'Starts', '', ''),
                   ('startedby', 'Started by', '', ''),
                   ('finishes', 'Finishes', '', ''),
                   ('finishedby', 'Finished by', '', ''),
                   ('during', 'During', '', ''),
                   ('contains', 'Contains', '', '')
                   )

illustration = (
               # equals
               ('X |-----|\nY |-----|',
                'Non efficient',
                'Non efficient',
                'X |\nY |'),
               # before
               ('X |-----|\nY' + ' ' *15 + '|-----|',
                'X |-----|\nY' + ' ' *15 + '|',
                'X |\nY   |-----|',
                'X |\nY   |'),
               # after
               ('X' + ' ' *15 + '|-----|\nY |-----|',
                'X' + ' ' *15 + '|\nY |-----|',
                'X   |-----|\nY |',
                'X   |\nY |'),
               # meets
               ('X |-----|\nY'+ ' ' * 8 + '|-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # metby
               ('X'+ ' ' * 8 +'|-----|\nY |-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # overlaps
               ('X |-----|\nY '+ ' ' * 5 + '|-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # overlappedby
               ('X' + ' ' *5 + '|-----|\nY |-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # starts
               ('X |---|\nY |-----|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # startedby
               ('X |-----|\nY |---|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # finishes
               ('X |------|\nY    |---|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # finishedby
               ('X    |---|\nY |------|',
                'Non efficient',
                'Non efficient',
                'Non efficient'),
               # during
               ('X    |---|\nY |------|',
                'Non efficient',
                'X      |\nY |------|',
                'Non efficient'),
               # contains
               ('X |------|\nY    |---|',
                'X |-----|\nY     |',
                'Non efficient',
                'Non efficient'),
               )

ALLEN_RELATIONS = tuple(row + illustration[i] for i, row in enumerate(ALLEN_RELATIONS))


# ---------------------------------------------------------------------------


class AllensRelationsTable(ULC.UltimateListCtrl):

    def __init__(self, parent, *args, **kwargs):
        agwStyle= ULC.ULC_REPORT|ULC.ULC_VRULES|ULC.ULC_HRULES|\
                  ULC.ULC_HAS_VARIABLE_ROW_HEIGHT|ULC.ULC_NO_HEADER
        ULC.UltimateListCtrl.__init__(self, parent, agwStyle=agwStyle, *args, **kwargs)
        self._optionCtrlList = []
        self.InitUI()

    def InitUI(self):
        headers = ('Name',
                   'Option',
                   'X: Interval \nY: Interval',
                   'X: Interval \nY: Point',
                   'X: Point \nY: Interval',
                   'X: Point \nY: Point'
                   )
        # Create columns
        for i, col in enumerate(headers):
            self.InsertColumn(col=i, heading=col)

        self.SetColumnWidth(col=0, width=150)
        self.SetColumnWidth(col=1, width=180)
        self.SetColumnWidth(col=2, width=150)
        self.SetColumnWidth(col=3, width=100)
        self.SetColumnWidth(col=4, width=100)
        self.SetColumnWidth(col=5, width=100)

        # Create first row
        index = self.InsertStringItem(0, headers[0])
        for i, col in enumerate(headers[1:], 1):
            self.SetStringItem(index, i, col)

        # Add rows
        for i, row in enumerate(ALLEN_RELATIONS,1):
            func, name, opt_label, opt_value, desc1, desc2, desc3, desc4 = row

            opt_panel = wx.Panel(self)
            opt_sizer= wx.BoxSizer(wx.HORIZONTAL)

            if isinstance(opt_value, float):
                opt_ctrl = FS.FloatSpin(opt_panel,
                                        min_val=0.001,
                                        increment=0.001,
                                        value=opt_value,
                                        digits=3)
            elif isinstance(opt_value, int):
                opt_ctrl = wx.SpinCtrl(opt_panel, min=1, value=str(opt_value))
            else:
                opt_ctrl = wx.StaticText(opt_panel, label="")

            self._optionCtrlList.append(opt_ctrl)
            opt_text = wx.StaticText(opt_panel, label=opt_label)
            opt_sizer.Add(opt_text)
            opt_sizer.Add(opt_ctrl)
            opt_panel.SetSizer(opt_sizer)

            index = self.InsertStringItem(i, name, 1)
            self.SetItemWindow(index, 1, opt_panel, expand=True)
            self.SetStringItem(index, 2, desc1)
            self.SetStringItem(index, 3, desc2)
            self.SetStringItem(index, 4, desc3)
            self.SetStringItem(index, 5, desc4)

        item  = self.GetItem(1)
        self._mainWin.CheckItem(item)


    def GetData(self):
        data = {}
        data['name'] = []
        data['function'] = []
        data['value'] = []
        data['type'] = "Relation"
        data['reverse'] = False
        for i, option in enumerate(self._optionCtrlList, 1):
            if self.IsItemChecked(i, col=0):
                func_name = ALLEN_RELATIONS[i-1][0]
                try:
                    option_value = option.GetValue()
                except:
                    option_value = None
                data['name'].append(func_name)
                data['function'].append(func_name)
                data['value'].append(option_value)
        return data


    def SetData(self, relations, value=True):
        for i, relation in enumerate(ALLEN_RELATIONS, 1):
            item = self.GetItem(i)
            if relation[0] in relations:
                self._mainWin.CheckItem(item, checked=True)
            else:
                self._mainWin.CheckItem(item, checked=False)

# ---------------------------------------------------------------------------

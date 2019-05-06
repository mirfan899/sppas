import wx.lib.newevent

# ---------------------------------------------------------------------------
# Event to be used when the data have changed.

DataChangedEvent, EVT_DATA_CHANGED = wx.lib.newevent.NewEvent()
DataChangedCommandEvent, EVT_DATA_CHANGED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------
# Event to be used when the state of any data of FileData() has changed.

StateChangedEvent, EVT_STATE_CHANGED = wx.lib.newevent.NewEvent()
StateChangedCommandEvent, EVT_STATE_CHANGED_COMMAND = wx.lib.newevent.NewCommandEvent()



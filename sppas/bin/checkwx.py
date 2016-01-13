import wx

version = int(wx.version().split('.')[0])
if version >= 3:
    exit(0)
exit(1)


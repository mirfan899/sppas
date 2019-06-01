import wx
import logging
from sppas.src.files import sppasAttribute

# ----------------------------------------------------------------------------


class IdentifierTextValidator(wx.Validator):
    """Check if the TextCtrl is valid for an identifier.

    If the TextCtrl is not valid, the background becomes pinky.

    """

    def __init__(self):
        super(IdentifierTextValidator, self).__init__()

    def Clone(self):
        # Required method for validator
        return IdentifierTextValidator()

    def TransferToWindow(self):
        # Prevent wxDialog from complaining.
        return True

    def TransferFromWindow(self):
        # Prevent wxDialog from complaining.
        return True

    def Validate(self, win=None):
        text_ctrl = self.GetWindow()
        text = text_ctrl.GetValue().strip()
        if sppasAttribute.validate(text) is False:
            text_ctrl.SetBackgroundColour("pink")
            text_ctrl.SetFocus()
            text_ctrl.Refresh()
            return False

        try:
            text_ctrl.SetBackgroundColour(wx.GetApp().settings.bg_color)
        except:
            logging.debug('Error: Application settings not defined.')
            text_ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        text_ctrl.Refresh()
        return True


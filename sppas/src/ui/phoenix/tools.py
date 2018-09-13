import os
import wx

# -----------------------------------------------------------------------


class sppasSwissKnife:

    @staticmethod
    def get_bitmap(name, height=24):
        """Return the bitmap corresponding to the name of an icon.

        :param name: (str) Name of an icon.
        :param height: (int) Height/Width of the bitmap.
        :return: (wx.Bitmap)

        """
        # fix the image file name
        icon_name = os.path.join(wx.GetApp().cfg.icons_path,
                                 wx.GetApp().settings.icons_theme,
                                 name + ".png")
        if os.path.exists(icon_name) is False:
            icon_name = os.path.join(wx.GetApp().cfg.icons_path,
                                     "Refine",
                                     "default.png")

        # create an image with the appropriate size
        img = wx.Image(icon_name, wx.BITMAP_TYPE_ANY)
        img.Rescale(height, height, wx.IMAGE_QUALITY_HIGH)
        img.Replace(0, 0, 0, 128, 128, 128)

        return wx.Bitmap(img)

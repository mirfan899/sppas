import os
import wx

from sppas.src.config import paths

# -----------------------------------------------------------------------


class sppasSwissKnife:

    @staticmethod
    def get_bmp_icon(name, height=24):
        """Return the bitmap corresponding to the name of an icon.

        :param name: (str) Name of an icon.
        :param height: (int) Height/Width of the bitmap.
        :return: (wx.Bitmap)

        """
        # fix the image file name
        icon_name = os.path.join(paths.etc, "icons",
                                 wx.GetApp().settings.icons_theme,
                                 name + ".png")
        if os.path.exists(icon_name) is False:
            icon_name = os.path.join(paths.etc, "icons", "Refine", "default.png")

        # create an image with the appropriate size
        img = wx.Image(icon_name, wx.BITMAP_TYPE_ANY)
        img.Rescale(height, height, wx.IMAGE_QUALITY_HIGH)
        button_color = wx.GetApp().settings.button_fg_color
        img.Replace(0, 0, 0,
                    button_color.Red(),
                    button_color.Green(),
                    button_color.Blue())

        return wx.Bitmap(img)

    @staticmethod
    def get_bmp_image(name, height=None):
        """Return the bitmap corresponding to the name of an image.

        :param name: (str) Name of an icon.
        :param height: (int) Height of the bitmap, Width is proportional.
        :return: (wx.Bitmap)

        """
        # fix the image file name
        img_name = os.path.join(paths.etc, "images", name + ".png")
        if os.path.exists(img_name) is False:
            img_name = os.path.join(paths.etc, "images", "sppas.png")

        if height is not None:
            img = wx.Image(img_name, wx.BITMAP_TYPE_ANY)
            proportion = height / img.GetHeight()
            w = int(img.GetWidth() * proportion)
            img.Rescale(w, height, wx.IMAGE_QUALITY_HIGH)
            return wx.Bitmap(img)

        return wx.Bitmap(img_name, wx.BITMAP_TYPE_PNG)

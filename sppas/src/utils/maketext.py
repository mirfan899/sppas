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

    src.utils.maketext
    ~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    maketext is useful for the internationalization of texts for both
    Python 2 and Python 3.
    The locale is used to set the language and English is the default.

    Example:

        from sppas.src.utils.maketext import translate
        t = translate("domain")
        my_string = t.gettext("Some string in the domain.")

"""
import os.path
import gettext
import locale

from sppas import BASE_PATH
from .makeunicode import u

# ---------------------------------------------------------------------------


class T(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Utility class used to return an unicode message.

    """
    @staticmethod
    def gettext(msg):
        return u(msg)

# ---------------------------------------------------------------------------


def translate(domain):
    """ Fix the domain to translate messages and activate the gettext method.

    :param domain: (str) Name of the domain.
    A domain corresponds to a ".po" file of the language. The language is
    automatically fixed with the default locale. English is used by default.

    """
    try:
        lc, encoding = locale.getdefaultlocale()
        if lc is not None:
            lang = [lc, "en_US"]
    except:
        lang = ["en_US"]

    try:
        t = gettext.translation(domain, os.path.join(BASE_PATH, "po"), lang)
        t.install()
        return t
    except:
        try:
            t = gettext.translation(domain, os.path.join(BASE_PATH, "po"), ["en_US"])
            t.install()
            return t
        except IOError:
            pass

    return T()

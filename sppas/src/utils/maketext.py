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

    >>> from sppas.src.utils.maketext import translate
    >>> t = translate("domain")
    >>> my_string = t.gettext("Some string in the domain.")

"""
import gettext
import locale

from sppas.src.config import paths
from .makeunicode import u

# ---------------------------------------------------------------------------


class T(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Utility class to simulate the GNUTranslations class.

    """
    @staticmethod
    def gettext(msg):
        return u(msg)

    @staticmethod
    def ugettext(msg):
        return u(msg)

# ---------------------------------------------------------------------------


def get_lang_list():
    """ Return the list of languages depending on the default locale.

    At a first stage, the language is fixed with the default locale.
    English is then either appended to the list or used by default.

    """
    try:
        lc, encoding = locale.getdefaultlocale()
        if lc is not None:
            return [lc, "en_US"]
    except:
        pass

    return ["en_US"]

# ---------------------------------------------------------------------------


def translate(domain, language=None):
    """ Fix the domain to translate messages and to activate the gettext method.

    :param domain: (str) Name of the domain.
    A domain corresponds to a ".po" file of the language in the 'po' folder
    of the SPPAS package.
    :param language: (list) Preferred language for the translation system.
    :returns: (GNUTranslations)

    """
    if language is None:
        # Get the list of languages to be installed.
        lang = get_lang_list()
    else:
        lang = [language]
        if "en_US" not in lang:
            lang.append('en_US')

    try:
        # Install translation for the local language and English
        t = gettext.translation(domain, paths.po, lang)
        t.install()
        return t

    except:
        try:
            # Install translation for English only
            t = gettext.translation(domain, paths.po, ["en_US"])
            t.install()
            return t

        except IOError:
            pass

    # No language installed. The messages won't be translated;
    # at least they are converted to unicode.
    return T()

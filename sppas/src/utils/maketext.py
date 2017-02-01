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

    src.utils.makeunicode
    ~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    maketext is useful for the internationalization of texts.

"""
import os.path
import gettext
import locale

from sppas.src.sp_glob import BASE_PATH
from .makeunicode import u


class T(object):
    @staticmethod
    def gettext(msg):
        return u(msg)


def translate(domain):
    lang = []
    try:
        locale.setlocale(locale.LC_ALL, '')
        lc, encoding = locale.getdefaultlocale()
        lang.append(lc)
    except:
        pass
    lang.append("en_US")

    try:
        t = gettext.translation(domain, os.path.join(BASE_PATH, "po"), lang)
        t.install()
        return t
    except IOError:
        pass

    return T()

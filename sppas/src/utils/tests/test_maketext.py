# -*- coding:utf-8 -*-
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

    src.utils.tests.test_maketest.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Test internationalization text maker.

"""
import unittest

from ..makeunicode import u
from ..maketext import get_lang_list, translate, T

# ---------------------------------------------------------------------------


class TestMakeText(unittest.TestCase):

    def test_T(self):
        t = T()
        self.assertEqual("abc", t.gettext("abc"))
        self.assertEqual(u("éàù"), t.gettext("éàù"))

    def test_get_lang_list(self):
        lang = get_lang_list()
        self.assertEqual(lang, ["fr_FR", "en_US"])

    def test_translate_invalid_domain(self):
        t = translate('invalid')
        self.assertEqual(t.gettext(":INFO 1000: "), ":INFO 1000: ")

    def test_translate_valid_domain(self):
        # Translate in English
        t = translate('annotations', 'en_EN')
        self.assertEqual(t.gettext(":INFO 1000: "), "Valid. ")

        # Translate in French
        t = translate('annotations', 'fr_FR')
        self.assertEqual(t.gettext(":INFO 1000: "), "Valide. ")

        # Translate in an unknown language (then... English)
        t = translate('annotations', 'de_DE')
        self.assertEqual(t.gettext(":INFO 1000: "), "Valid. ")

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

    src.annotations.tests.test_phonetize.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the SPPAS Phonetization.

"""
import unittest
import os.path

from sppas import RESOURCES_PATH, SAMPLES_PATH
from sppas import unk_stamp
from sppas import PHONE_SYMBOLS, ORTHO_SYMBOLS

from sppas.src.resources.dictpron import sppasDictPron
from sppas.src.resources.mapping import sppasMapping
from sppas.src.anndata import sppasRW

from .. import ERROR_ID, WARNING_ID, OK_ID
from ..Phon.phonetize import sppasDictPhonetizer
from ..Phon.dagphon import sppasDAGPhonetizer
from ..Phon.phonunk import sppasPhonUnk
from ..Phon.sppasphon import sppasPhon

# ---------------------------------------------------------------------------

SIL = list(PHONE_SYMBOLS.keys())[list(PHONE_SYMBOLS.values()).index("silence")]
SP = list(PHONE_SYMBOLS.keys())[list(PHONE_SYMBOLS.values()).index("pause")]
SP_ORTHO = list(ORTHO_SYMBOLS.keys())[list(ORTHO_SYMBOLS.values()).index("pause")]

# ---------------------------------------------------------------------------


class TestDictPhon(unittest.TestCase):
    """ Test sppasDictPhonetizer: a dictionary-based phonetization. """

    def setUp(self):
        self.dd = sppasDictPron()
        self.grph = sppasDictPhonetizer(self.dd)
        self.dd.add_pron("a", "a")
        self.dd.add_pron("b", "b")
        self.dd.add_pron("c", "c")
        self.dd.add_pron(SP_ORTHO, SP)

    # -----------------------------------------------------------------------

    def test_get_phon_silence(self):
        """ Test the phonetization of a silence. """

        self.assertEqual(SIL, self.grph.get_phon_entry("gpf_1"))
        self.assertEqual(SIL, self.grph.get_phon_entry("gpf_1 "))
        self.assertEqual(SIL, self.grph.get_phon_entry(" gpf_13 "))

    # -----------------------------------------------------------------------

    def test_get_phon_unk(self):
        """ Test the phonetization of an unknown entry. """

        self.assertEqual(self.grph.get_phon_entry("ipu"), unk_stamp)
        self.assertEqual(self.grph.get_phon_entry("gpd"), unk_stamp)
        self.assertEqual(self.grph.get_phon_entry("gpf"), unk_stamp)
        self.assertEqual(self.grph.get_phon_entry("aa"), unk_stamp)
        self.assertEqual(self.grph.get_phon_entry("a-a"), unk_stamp)

    # -----------------------------------------------------------------------

    def test_get_phon_entry(self):
        """ Test the phonetization of an entry. """

        self.assertEqual("a", self.grph.get_phon_entry("a"))
        self.assertEqual("", self.grph.get_phon_entry("<>"))
        self.assertEqual("a", self.grph.get_phon_entry("<a>"))
        self.assertEqual("", self.grph.get_phon_entry("gpd_1"))
        self.assertEqual("", self.grph.get_phon_entry("ipu_1"))

    # -----------------------------------------------------------------------

    def test_get_phon_tokens(self):
        """ Test the phonetization of a list of tokens,
        with the status returned.

        """
        self.assertEqual([], self.grph.get_phon_tokens([' \n \t']))

        self.assertEqual([('a', 'a', OK_ID)],
                         self.grph.get_phon_tokens(['a']))

        self.assertEqual([('gpf_1', SIL, OK_ID)],
                         self.grph.get_phon_tokens(['gpf_1']))

        self.assertEqual([], self.grph.get_phon_tokens(['gpd_1']))

        self.assertEqual([('a', 'a', OK_ID), ('b', 'b', OK_ID)],
                         self.grph.get_phon_tokens(['a', 'b']))

        self.assertEqual([('a-a', 'a-a', WARNING_ID), ('b', 'b', OK_ID)],
                         self.grph.get_phon_tokens(['a-a', 'b']))

        self.assertEqual([('a-', 'a', WARNING_ID)],
                         self.grph.get_phon_tokens(['a-']))

        self.assertEqual([('A', 'a', OK_ID), ('B', 'b', OK_ID)],
                         self.grph.get_phon_tokens(['A', 'B']))

        self.assertEqual([('a', 'a', OK_ID), ('aa', 'a-a', WARNING_ID)],
                         self.grph.get_phon_tokens(['a', 'aa']))

        self.assertEqual([('a', 'a', OK_ID), ('aa', unk_stamp, ERROR_ID)],
                         self.grph.get_phon_tokens(['a', 'aa'], phonunk=False))

        self.assertEqual([('a', 'a', OK_ID), ('d', unk_stamp, ERROR_ID)],
                         self.grph.get_phon_tokens(['a', 'd']))

        self.assertEqual([('/a/', 'a', OK_ID), ('d', unk_stamp, ERROR_ID)],
                         self.grph.get_phon_tokens(['/a/', 'd']))

        self.assertEqual([('/A-a/', 'A-a', OK_ID), ('d', unk_stamp, ERROR_ID)],
                         self.grph.get_phon_tokens(['/A-a/', 'd']))

    # -----------------------------------------------------------------------

    def test_phonetize(self):
        """ Test the phonetization of an utterance. """

        with self.assertRaises(TypeError):
            self.grph.phonetize('A', delimiter="_-")

        self.assertEqual("", self.grph.phonetize(' \n \t'))
        self.assertEqual("a", self.grph.phonetize('a'))
        self.assertEqual("a b a c", self.grph.phonetize('a b a c'))
        self.assertEqual("a b a c "+unk_stamp, self.grph.phonetize('a b a c d'))
        self.assertEqual("a sp a", self.grph.phonetize('a + a'))
        self.assertEqual("a b c", self.grph.phonetize('A B C'))
        self.assertEqual("a_b_c", self.grph.phonetize('A_B_C', delimiter="_"))
        self.assertEqual("a-b-a c", self.grph.phonetize("a'b-a c"))
        self.assertEqual("a-b-a c", self.grph.phonetize("ipu_4 a'b-a c"))
        self.assertEqual("a-b-a sp c", self.grph.phonetize("gpd_4 a'b-a + c"))
        self.assertEqual("a-a-b-a", self.grph.phonetize("gpd_4 aa'b-a"))
        self.assertEqual(SIL, self.grph.phonetize("gpf_4 "))

    # -----------------------------------------------------------------------

    def test_phonetize_with_map_table(self):
        """ Test the phonetization of an utterance if a sppasMapping() is fixed. """

        mapt = sppasMapping()
        mapt.add('a', 'A')
        mapt.add('b', 'B')
        mapt.add('b', 'v')
        mapt.add('a-c', 'a-C')
        self.grph.set_maptable(mapt)

        self.assertEqual("c", self.grph._map_phonentry("c"))

        self.assertEqual(set("a|A".split('|')),
                         set(self.grph._map_phonentry("a").split('|')))

        self.assertEqual(set("B|b|v".split('|')),
                         set(self.grph._map_phonentry("b").split('|')))

        self.assertEqual('c.c', self.grph._map_phonentry("c.c"))

        self.assertEqual(set('a-b|a-B|A-b|A-B|A-v|a-v'.split("|")),
                         set(self.grph._map_phonentry("a-b").split("|")))

        self.assertEqual(set("a-c|a-C".split("|")),
                         set(self.grph._map_phonentry("a-c").split("|")))

        self.assertEqual(set("a-c-A|a-c-a|a-C-A|a-C-a".split("|")),
                         set(self.grph._map_phonentry("a-c-a").split("|")))

        self.assertEqual(set("c-a-c|c-a-C".split("|")),
                         set(self.grph._map_phonentry("c-a-c").split("|")))

        mapt.add('a', 'a')
        mapt.add('b', 'b')
        mapt.add('c', 'c')
        self.assertEqual("c", self.grph._map_phonentry("c"))

        self.assertEqual(set("a|A".split('|')),
                         set(self.grph._map_phonentry("a").split('|')))

        self.assertEqual(set("B|b|v".split('|')),
                         set(self.grph._map_phonentry("b").split('|')))

        # reset the mapping table for the next tests...
        self.grph.set_maptable(None)

    # -----------------------------------------------------------------------

    def test_phon_from_loaded_data(self):
        """ Test phonetize with real resource data. """

        dict_file = os.path.join(RESOURCES_PATH, "dict", "eng.dict")
        map_table = os.path.join(RESOURCES_PATH, "dict", "eng-fra.map")
        mapt = sppasMapping(map_table)
        dd = sppasDictPron(dict_file)
        grph = sppasDictPhonetizer(dd)

        self.assertEqual(set("D-@|D-V|D-i:".split('|')),
                         set(grph.get_phon_entry("THE").split('|')))

        self.assertEqual(set("3:r|U-r\\".split('|')),
                         set(grph.get_phon_entry("UR").split('|')))

        self.assertEqual(set("A-r\\|3:r".split('|')),
                         set(grph.get_phon_entry("ARE").split('|')))

        self.assertEqual(set("b-{-N-k".split('|')),
                         set(grph.get_phon_entry("BANC").split('|')))

        grph.set_maptable(mapt)
        grph.set_unk_variants(0)
        # DICT:   the [] D @   /    the(2) [] D V    /    the(3) [] D i:
        # MAP:    D z   /   i: i    /    V 9    /   V @
        self.assertEqual(set("D-@|D-V|D-i:|z-@|z-V|z-i:|D-i|z-i|D-9|z-9|z-@".split("|")),
                         set(grph.get_phon_entry("THE").split("|")))

        # DICT:  ur [] 3:r   /   ur(2) [] U r\
        # MAP:   3:r 9-R   /  U u   /    r\ R   /   r\ w
        self.assertEqual(set("3:r|U-r\\|9-R|u-r\\|U-R|U-w|u-R|u-w".split("|")),
                         set(grph.get_phon_entry("UR").split("|")))

        # DICT =   are [] A r\    /    are(2) [] 3:r
        # MAP:  r\ R   /   r\ w    /   3:r 9-R    / A a
        self.assertEqual(set("A-r\\|3:r|a-r\\|9-R|A-R|A-w|a-R|a-w".split("|")),
                         set(grph.get_phon_entry("ARE").split("|")))

# ---------------------------------------------------------------------------


class TestDAGPhon(unittest.TestCase):
    """ Test phonetization of unknown entries with a DAG. """

    def setUp(self):
        self.dd = sppasDAGPhonetizer()

    # -----------------------------------------------------------------------

    def test_decompose(self):
        """ Create a decomposed phonetization from a string as follow:

            >>> dag_phon.decompose("p1 p2|x2 p3|x3")
            >>> p1-p2-p3|p1-p2-x3|p1-x2-p3|p1-x2-x3

        The input string is converted into a DAG, then output corresponds
        to all paths.

        """
        self.assertEqual(set("a|b".split('|')),
                         set(self.dd.decompose("a", "b").split('|')))

        self.assertEqual(set("a-b|A-b".split('|')),
                         set(self.dd.decompose("a|A b").split('|')))

        self.assertEqual(set("a|A|B|b".split('|')),
                         set(self.dd.decompose("a|A", "b|B").split('|')))

        result = "p1-p2-x3|p1-x2-x3|p1-p2-p3|p1-x2-p3"
        self.assertEqual(set(result.split("|")),
                         set(self.dd.decompose("p1 p2|x2 p3|x3").split("|")))

        result = 'p1-p2-p3|x1-x2-x3'
        self.assertEqual(set(result.split("|")),
                         set(self.dd.decompose("p1 p2 p3", "x1 x2 x3").split("|")))

        result = 'p1-p2-p3|p1-x2-p3|x1-x2-x3'
        self.assertEqual(set(result.split("|")),
                         set(self.dd.decompose("p1 p2|x2 p3", "x1 x2 x3").split("|")))

# ---------------------------------------------------------------------------


class TestPhonUnk(unittest.TestCase):
    """ Unknown words phonetization. """

    def setUp(self):
        d = {'a': 'a|aa',
             'b': 'b',
             'c': 'c|cc',
             'abb': 'abb',
             'bac': 'bac'
             }
        self.p = sppasPhonUnk(d)

    # -----------------------------------------------------------------------

    def test_phon(self):
        """ Text the phonetization of an unknown entry. """

        self.assertEqual(set("abb-a|abb-aa".split('|')),
                         set(self.p.get_phon('abba').split('|')))

        self.assertEqual(set("abb-a|abb-aa".split('|')),
                         set(self.p.get_phon('abba-').split('|')))

        self.assertEqual(set("abb-a|abb-aa".split('|')),
                         set(self.p.get_phon("abba'").split('|')))

        self.assertEqual(set("abb-a|abb-aa".split('|')),
                         set(self.p.get_phon("<abba>").split('|')))

        self.assertEqual("",
                         self.p.get_phon("<>"), "")

        self.assertEqual(set("abb-a|abb-aa".split('|')),
                         set(self.p.get_phon("abb-a").split('|')))

        self.assertEqual(set('a-b-c|a-b-cc|aa-b-c|aa-b-cc'.split('|')),
                         set(self.p.get_phon('abc').split('|')))

        self.assertEqual(set('a-b|aa-b'.split('|')),
                         set(self.p.get_phon('abd').split('|')))


# ---------------------------------------------------------------------------


class TestPhonetization(unittest.TestCase):
    """ Test the SPPAS integration of the Phonetization. """

    def setUp(self):
        dict_file = os.path.join(RESOURCES_PATH, "dict", "eng.dict")
        map_file = os.path.join(RESOURCES_PATH, "dict", "eng-fra.map")
        self.sp = sppasPhon(dict_file)
        self.spl = sppasPhon(dict_file, map_file)

    # -----------------------------------------------------------------------

    def test_phonetize(self):
        """ Test phonetization of an utterance. """

        self.sp.set_unk(True)
        self.assertEqual(unk_stamp, self.sp.phonetize("é à"))

        self.assertEqual(set("D-@|D-V|D-i:".split('|')),
                         set(self.sp.phonetize("THE")[0].split('|')))

        self.assertEqual("h-i:",
                         self.sp.phonetize("HE")[0])

        self.sp.set_unk(False)  # do not try to phonetize if missing of the dict
        self.assertEqual(unk_stamp, self.sp.phonetize("THE BANCI THE"))

        self.sp.set_unk(True)

    # -----------------------------------------------------------------------

    def test_phonetize_silence(self):
        """ Test phonetization of an utterance made only of a silence. """

        self.assertEqual([SIL], self.sp.phonetize("#"))
        self.assertEqual([SIL], self.sp.phonetize("+"))
        self.assertEqual([SIL], self.sp.phonetize("  gpf_12  "))
        self.assertEqual([SIL], self.sp.phonetize("   gpd_1   +  "))

    # -----------------------------------------------------------------------

    def test_phonetize_learners(self):
        """ Test phonetization of an utterance with a map table defined. """

        self.assertEqual(set("D-@|D-V|D-i:|z-@|z-V|z-i:|D-i|z-i|D-9|z-9|z-@".split('|')),
                         set(self.spl.phonetize("THE")[0].split('|')))

        self.assertEqual(set("i|h-i:|h-i|i:".split("|")),
                         set(self.spl.phonetize("HE")[0].split('|')))

    # -----------------------------------------------------------------------

    def test_samples(self):
        """ Test if the current result is the same as the existing one. """

        # the place where are the samples to be tested.
        samples_path = os.path.join(SAMPLES_PATH, "annotation-results")

        # each samples folder is tested
        for samples_folder in os.listdir(samples_path):
            if samples_folder.startswith("samples-") is False:
                continue

            # Create a Phonetizer for the given set of samples of the given language
            lang = samples_folder[-3:]
            pron_dict = os.path.join(RESOURCES_PATH, "dict", lang+".dict")
            tn = sppasPhon(pron_dict)

            # Apply Phonetization on each sample
            for filename in os.listdir(os.path.join(samples_path, samples_folder)):
                if filename.endswith("-token.xra") is False:
                    continue

                # Get the expected result
                expected_result_filename = os.path.join(samples_path, samples_folder,
                                                        filename[:-10] + "-phon.xra")
                if os.path.exists(expected_result_filename) is False:
                    print("no match token/phon for:", filename)
                    continue
                parser = sppasRW(expected_result_filename)
                expected_result = parser.read()

                # Estimate the result and check if it's like expected.
                result = tn.run(os.path.join(samples_path, samples_folder, filename))

                # expected_tier_phones = expected_result.find('Phones')
                # if expected_tier_phones is not None:
                #     self.compare_tiers(expected_tier_tokens, result.find('Tokens'))

    # -----------------------------------------------------------------------

    def compare_tiers(self, expected, result):
        self.assertEqual(len(expected), len(result))
        for a1, a2 in zip(expected, result):
            self.assertEqual(a1, a2)
            for key in a1.get_meta_keys():
                if key != 'id':
                    self.assertEqual(a1.get_meta(key), a2.get_meta(key))
        for key in expected.get_meta_keys():
            if key != 'id':
                self.assertEqual(expected.get_meta(key), result.get_meta(key))

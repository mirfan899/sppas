#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas import RESOURCES_PATH
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from ..Syll.syllabify import Syllabifier
from ..Syll.sppassyll import sppasSyll


# -------------------------------------------------------------------------

POL_SYLL = os.path.join(RESOURCES_PATH, "syll", "syllConfig-pol.txt")
FRA_SYLL = os.path.join(RESOURCES_PATH, "syll", "syllConfig-fra.txt")

# -------------------------------------------------------------------------


class TestSyllabifier(unittest.TestCase):
    """ Syllabification of a list of phonemes. """

    def setUp(self):
        self.syll_pol = Syllabifier(POL_SYLL)
        self.syll_fra = Syllabifier(FRA_SYLL)

    # -----------------------------------------------------------------------

    def test_find_next_vowel(self):
        """ Test the search of the next vowel in classes. """

        c = ['L', 'V', 'P', 'P', 'V', 'F', 'V', 'L']
        self.assertEqual(1, Syllabifier._find_next_vowel(c, 0))
        self.assertEqual(1, Syllabifier._find_next_vowel(c, 1))
        self.assertEqual(4, Syllabifier._find_next_vowel(c, 2))
        self.assertEqual(4, Syllabifier._find_next_vowel(c, 3))
        self.assertEqual(4, Syllabifier._find_next_vowel(c, 4))
        self.assertEqual(6, Syllabifier._find_next_vowel(c, 5))
        self.assertEqual(6, Syllabifier._find_next_vowel(c, 6))
        self.assertEqual(-1, Syllabifier._find_next_vowel(c, 7))
        self.assertEqual(-1, Syllabifier._find_next_vowel(c, 8))

    # -----------------------------------------------------------------------

    def test_find_next_break(self):
        """ Test the search of the next break in classes. """

        c = ['L', 'V', 'P', 'P', 'V', 'F', 'V', 'L']
        self.assertEqual(-1, Syllabifier._find_next_break(c, 0))
        self.assertEqual(-1, Syllabifier._find_next_break(c, 6))

        c = ['L', 'V', 'P', 'P', 'V', '#', 'F', 'V', 'L']
        self.assertEqual(5, Syllabifier._find_next_break(c, 0))

    # -----------------------------------------------------------------------

    def test_fix_nucleus(self):
        """ Search for the next nucleus of a syllable. """

        self.assertEqual(-1, Syllabifier._fix_nucleus([], 0))
        self.assertEqual(-1, Syllabifier._fix_nucleus(['#'], 0))
        self.assertEqual(0, Syllabifier._fix_nucleus(['V'], 0))
        self.assertEqual(1, Syllabifier._fix_nucleus(['#', 'V'], 0))
        self.assertEqual(1, Syllabifier._fix_nucleus(['#', 'V'], 1))

        c = ['L', 'V', 'P', 'P', 'V', '#', 'F', 'V', 'L']
        self.assertEqual(1, Syllabifier._fix_nucleus(c, 0))
        self.assertEqual(1, Syllabifier._fix_nucleus(c, 1))
        self.assertEqual(4, Syllabifier._fix_nucleus(c, 2))
        self.assertEqual(4, Syllabifier._fix_nucleus(c, 3))
        self.assertEqual(4, Syllabifier._fix_nucleus(c, 4))
        self.assertEqual(7, Syllabifier._fix_nucleus(c, 5))

        c = ['L', 'V', 'P', '#', 'V', '#', 'P', 'V', '#', '#', 'F', 'V', 'V', 'L']
        self.assertEqual(1, Syllabifier._fix_nucleus(c, 0))
        self.assertEqual(1, Syllabifier._fix_nucleus(c, 1))
        self.assertEqual(4, Syllabifier._fix_nucleus(c, 2))
        self.assertEqual(7, Syllabifier._fix_nucleus(c, 5))

    # -----------------------------------------------------------------------

    def test_fix_start_syll(self):
        """ Search for the index of the first phoneme of the syllable. """

        c = ['L', 'V', 'P', '#', 'V', '#', 'P', 'V', '#', '#', 'F', 'V', 'V', 'L']

        self.assertEqual(0, Syllabifier._fix_start_syll(c, -1, 1))
        self.assertEqual(4, Syllabifier._fix_start_syll(c, 2, 4))
        self.assertEqual(6, Syllabifier._fix_start_syll(c, 4, 7))
        self.assertEqual(10, Syllabifier._fix_start_syll(c, 7, 11))
        self.assertEqual(12, Syllabifier._fix_start_syll(c, 11, 12))

        c = ['V', 'N', 'P', 'V']
        self.assertEqual(2, Syllabifier._fix_start_syll(c, 1, 3))

    # -----------------------------------------------------------------------

    def test_apply_class_rules(self):
        """ Apply the syllabification rules between v1 and v2. """

        c = ['L', 'V', 'P', 'P', 'V', 'F', 'V', 'L']
        self.assertEqual(2, self.syll_fra._apply_class_rules(c, 1, 4))
        self.assertEqual(4, self.syll_fra._apply_class_rules(c, 4, 6))

    # -----------------------------------------------------------------------

    def test_apply_phon_rules(self):
        """ Apply the syllabification rules between v1 and v2. """

        p = ['l', '@', 'p', 't', 'i', 'S', 'A/', 'l']
        self.assertEqual(1, self.syll_fra._apply_phon_rules(p, 2, 1, 4))
        self.assertEqual(4, self.syll_fra._apply_phon_rules(p, 4, 4, 6))

    # -----------------------------------------------------------------------

    def test_annotate(self):
        """ Test the limits of annotate method. """

        self.assertEqual([(0, 3)], self.syll_fra.annotate(['g', 'j', 'i', 't']))
        self.assertEqual([(0, 4)], self.syll_fra.annotate(['g', 'j', 'i', 't', 'p']))
        self.assertEqual([(0, 4)], self.syll_fra.annotate(['g', 'j', 'i', 't', 'p', '#']))

    # -----------------------------------------------------------------------


    def test_no_syll(self):
        """ Test situations when no syllables are returned. """

        self.assertEqual([], self.syll_pol.annotate([]))
        self.assertEqual([], self.syll_pol.annotate(['#']))
        self.assertEqual([], self.syll_pol.annotate(['#', "#"]))
        self.assertEqual([], self.syll_pol.annotate(['m']))
        self.assertEqual([], self.syll_pol.annotate(['m', 'm']))
        self.assertEqual([], self.syll_pol.annotate(["#", 'm', 'm']))
        self.assertEqual([], self.syll_pol.annotate(["#", 'm', 'm', '#']))

    # -----------------------------------------------------------------------

    def test_V(self):
        """ Test situations when 1 syllable is returned. """

        self.assertEqual([(0, 0)], self.syll_fra.annotate(['a']))
        self.assertEqual([(0, 0)], self.syll_fra.annotate(['a', '#']))
        self.assertEqual([(1, 1)], self.syll_fra.annotate(['#', 'a']))
        self.assertEqual([(1, 1)], self.syll_fra.annotate(['UNK', 'a']))
        self.assertEqual([(1, 1)], self.syll_fra.annotate(['UNK', 'a', '#']))

    # -----------------------------------------------------------------------

    def test_VV(self):
        phonemes = (['a', 'a'])
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 0), (1, 1)], syllables)

        phonemes = (['a', '#', 'a'])
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 0), (2, 2)], syllables)

    # -----------------------------------------------------------------------

    def test_VCV(self):
        phonemes = (['a', 'b', 'a'])
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 0), (1, 2)], syllables)  # a.ba

    # -----------------------------------------------------------------------

    def test_VCCV(self):
        # general rule
        phonemes = ['a', 'n', 'c', 'a']
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 1), (2, 3)], syllables)  # an.ca

        # exception rule
        phonemes = ['a', 'g', 'j', 'a']
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 0), (1, 3)], syllables)  # a.gja

        # specific (shift to left)
        phonemes = ['a', 'd', 'g', 'a']
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 0), (1, 3)], syllables)  # a.dga

        # do not apply the previous specific rule if not VdgV
        phonemes = ['a', 'x', 'd', 'g', 'a']
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 1), (2, 4)], syllables)  # ax.dga

        # specific (shift to right)
        phonemes = ['a', 'z', 'Z', 'a']
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 1), (2, 3)], syllables)  # az.Za

    # -----------------------------------------------------------------------

    def test_VCCCV(self):
        # general rule
        phonemes = ['a', 'm', 'm', 'n', 'a']
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 1), (2, 4)], syllables)  # am.mna
        #
        phonemes = ['g', 'j', 'i', 't', "@"]
        syllables = self.syll_fra.annotate(phonemes)
        self.assertEqual([(0, 2), (3, 4)], syllables)  # gji.t@
        #
        phonemes = ['g', 'j', 'i', 't']
        syllables = self.syll_fra.annotate(phonemes)
        self.assertEqual([(0, 3)], syllables)  # gjit

        # exception rule
        phonemes = ['a', 'dz', 'v', 'j', 'a']
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 0), (1, 4)], syllables)  # a.dzvja

        # specific (shift to left)
        phonemes = ['a', 'b', 'z', 'n', 'a']
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 0), (1, 4)], syllables)  # a.bzna

        # specific (shift to right)
        phonemes = ['a', 'r', 'w', 'S', 'a']
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 2), (3, 4)], syllables)  # arw.Sa

    # -----------------------------------------------------------------------

    def test_VCCCCV(self):
        phonemes = ['a', 'b', 'r', 'v', 'j', 'a']
        syllables = self.syll_pol.annotate(phonemes)
        self.assertEqual([(0, 0), (1, 5)], syllables)  # a.brvja

    # -----------------------------------------------------------------------

    def test_VCCCCCV(self):
        """ French sentence: à parce que moi. """
        phonemes = ['a', 'p', 's', 'k', 'm', 'w', 'a']
        syllables = self.syll_fra.annotate(phonemes)
        self.assertEqual([(0, 3), (4, 6)], syllables)  # apsk.mwa

    # -----------------------------------------------------------------------

    def test_phonetize_syllables(self):
        phonemes = ['a', 'p', 's', 'k', 'm', 'w', 'a']
        syllables = self.syll_fra.annotate(phonemes)
        self.assertEqual("a-p-s-k.m-w-a", Syllabifier.phonetize_syllables(phonemes, syllables))

# -------------------------------------------------------------------------


class TestsppasSyll(unittest.TestCase):
    """ Syllabification of a tier with time-aligned phonemes. """

    def setUp(self):
        self.syll = sppasSyll(FRA_SYLL)
        tier = sppasTier('PhonAlign')
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2))),
                               sppasLabel(sppasTag('l')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2), sppasPoint(3))),
                               sppasLabel(sppasTag('@')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(4))),
                               sppasLabel(sppasTag('#')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(4), sppasPoint(5))),
                               sppasLabel(sppasTag('S')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(5), sppasPoint(6))),
                               sppasLabel(sppasTag('A/')))
        # hole [6,7]
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(7), sppasPoint(8))),
                               sppasLabel(sppasTag('#')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(8), sppasPoint(9))),
                               sppasLabel(sppasTag('e')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(9), sppasPoint(10))),
                               sppasLabel(sppasTag('#')))
        # hole [10,11]
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(11), sppasPoint(12))),
                               sppasLabel(sppasTag('k')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(12), sppasPoint(13))),
                               sppasLabel(sppasTag('2')))
        # hole [13,14]
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(14), sppasPoint(15))),
                               sppasLabel(sppasTag('p')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(15), sppasPoint(16))),
                               sppasLabel(sppasTag('U~/')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(16), sppasPoint(17))),
                               sppasLabel(sppasTag('#')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(17), sppasPoint(18))),
                               sppasLabel(sppasTag('E')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(18), sppasPoint(19))),
                               sppasLabel(sppasTag('o')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(19), sppasPoint(20))),
                               sppasLabel(sppasTag('#')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(20), sppasPoint(21))),
                               sppasLabel(sppasTag('g')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(21), sppasPoint(22))),
                               sppasLabel(sppasTag('j')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(22), sppasPoint(23))),
                               sppasLabel(sppasTag('i')))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(23), sppasPoint(24))),
                               sppasLabel(sppasTag('t')))

        self.tier = tier

    # -----------------------------------------------------------------------

    def test_phon_to_intervals(self):
        """ Create the intervals to be syllabified. """

        test_tier = self.tier.copy()

        expected = sppasTier('Expected')
        expected.create_annotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        expected.create_annotation(sppasLocation(sppasInterval(sppasPoint(4), sppasPoint(6))))
        expected.create_annotation(sppasLocation(sppasInterval(sppasPoint(8), sppasPoint(9))))
        expected.create_annotation(sppasLocation(sppasInterval(sppasPoint(11), sppasPoint(13))))
        expected.create_annotation(sppasLocation(sppasInterval(sppasPoint(14), sppasPoint(16))))
        expected.create_annotation(sppasLocation(sppasInterval(sppasPoint(17), sppasPoint(19))))
        expected.create_annotation(sppasLocation(sppasInterval(sppasPoint(20), sppasPoint(24))))

        intervals = sppasSyll._phon_to_intervals(test_tier)
        self.assertEqual(len(expected), len(intervals))
        for a1, a2 in zip(expected, intervals):
            self.assertEqual(a1, a2)

        # add en empty interval at start
        test_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(0), sppasPoint(1))))
        intervals = sppasSyll._phon_to_intervals(test_tier)
        self.assertEqual(len(expected), len(intervals))
        for a1, a2 in zip(expected, intervals):
            self.assertEqual(a1, a2)

        # add en empty interval at end
        test_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(24), sppasPoint(25))))
        intervals = sppasSyll._phon_to_intervals(test_tier)
        self.assertEqual(len(expected), len(intervals))
        for a1, a2 in zip(expected, intervals):
            self.assertEqual(a1, a2)

        # silence at start
        test_tier[0].append_label(sppasLabel(sppasTag('#')))
        intervals = sppasSyll._phon_to_intervals(test_tier)
        self.assertEqual(len(expected), len(intervals))
        for a1, a2 in zip(expected, intervals):
            self.assertEqual(a1, a2)

        # silence at end
        test_tier[-1].append_label(sppasLabel(sppasTag('#')))
        intervals = sppasSyll._phon_to_intervals(test_tier)
        self.assertEqual(len(expected), len(intervals))
        for a1, a2 in zip(expected, intervals):
            self.assertEqual(a1, a2)

    # -----------------------------------------------------------------------

    def test_syllabify_interval(self):
        """ Perform the syllabification of one interval. """

        expected = sppasTier('Expected')
        expected.create_annotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))),
                                   sppasLabel(sppasTag('l-@')))

        syllables = sppasTier('SyllAlign')
        self.syll.syllabify_interval(self.tier, 0, 1, syllables)
        self.assertEqual(len(expected), len(syllables))
        for a1, a2 in zip(expected, syllables):
            self.assertEqual(a1, a2)

        expected.create_annotation(sppasLocation(sppasInterval(sppasPoint(17), sppasPoint(18))),
                                   sppasLabel(sppasTag('E')))
        expected.create_annotation(sppasLocation(sppasInterval(sppasPoint(18), sppasPoint(19))),
                                   sppasLabel(sppasTag('o')))
        self.syll.syllabify_interval(self.tier, 13, 15, syllables)
        self.assertEqual(len(expected), len(syllables))
        for a1, a2 in zip(expected, syllables):
            self.assertEqual(a1, a2)

    # -----------------------------------------------------------------------

    def test_convert(self):
        """ Syllabify labels of a time-aligned phones tier. """

        s = self.syll.convert(self.tier)

    # -----------------------------------------------------------------------

    def test_run(self):
        """ Test on real-life data. """

        pass

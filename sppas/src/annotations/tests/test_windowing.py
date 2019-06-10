import unittest

from sppas import sppasTier, sppasLabel, sppasTag, sppasTypeError
from sppas import sppasLocation, sppasPoint
from sppas import sppasInterval
from sppas.src.annotations.Occurrences.windowing import sppasTierWindow


class WindowingTest(unittest.TestCase):
    """Test of the windowing system on a sppasTier.

    """
    def setUp(self):

        # A sentence with 119 entries.
        self.sent = "#" \
               " David Lightman est plus intéressé par son ordinateur que par ses études +" \
               " ce qui ne l' inquiète pas puisqu' il se sait capable de modifier lui-même +" \
               " ses notes en agissant sur l' ordinateur de l'école" \
               " # " \
               " Un jour + " \
               " en cherchant à percer le code d' accès d' un nouveau jeu vidéo +" \
               " il se branche accidentellement +" \
               " sur l'ordinateur du département de la Défense +" \
               " qui prend au sérieux ce qui n' était au départ qu' un jeu" \
               " #" \
               " Pour les besoins d' une scène +" \
               " Matthew Broderick s'est entraîné pendant deux mois +" \
               " sur les jeux Galaxian et Galaga grâce à des bornes d' arcade +" \
               " livrées directement chez lui par le studio" \
               " #"   # (WarGames, 1983)

    # -----------------------------------------------------------------------

    def test_time_split_int_points(self):
        tier = sppasTier()
        for i, entry in enumerate(self.sent.split()):
            tier.create_annotation(
                sppasLocation(sppasPoint(i)),
                sppasLabel(sppasTag(entry)))
        wp = sppasTierWindow(tier)

        # does not work as expected (11 words in each window)
        sp10 = wp.time_split(10, 10)
        self.assertEqual(12, len(sp10))
        for i in range(11):
            self.assertEqual(10, len(sp10[i]))
        self.assertEqual(9, len(sp10[11]))

    # -----------------------------------------------------------------------

    def test_time_split_int_intervals(self):
        tier = sppasTier()
        for i, entry in enumerate(self.sent.split()):
            tier.create_annotation(
                sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))),
                sppasLabel(sppasTag(entry)))
        wi = sppasTierWindow(tier)

        #with self.assertRaises(sppasTypeError):
        #    w.time_split(2.1)

        # Continuous windows

        si10 = wi.time_split(10, 10)
        self.assertEqual(12, len(si10))
        for i in range(11):
            self.assertEqual(10, len(si10[i]))
        self.assertEqual(9, len(si10[-1]))

        # Overlapping windows

        si5 = wi.time_split(10, 5)
        self.assertEqual(24, len(si5))
        for i in range(22):
            self.assertEqual(10, len(si5[i]))
        self.assertEqual(9, len(si5[-2]))
        self.assertEqual(4, len(si5[-1]))

    # -----------------------------------------------------------------------

    def test_time_split_float_intervals(self):
        tier = sppasTier()
        for i, entry in enumerate(self.sent.split()):
            tier.create_annotation(
                sppasLocation(sppasInterval(sppasPoint(float(i)), sppasPoint(float(i)+1.))),
                sppasLabel(sppasTag(entry)))
        wi = sppasTierWindow(tier)

        # Continuous windows

        si10 = wi.time_split(10., 10.)
        self.assertEqual(12, len(si10))
        for i in range(11):
            self.assertEqual(10, len(si10[i]))
        self.assertEqual(9, len(si10[-1]))

        # Overlapping windows (no need of delta)

        si5 = wi.time_split(10., 5.)
        self.assertEqual(24, len(si5))
        for i in range(22):
            self.assertEqual(10, len(si5[i]))
        self.assertEqual(9, len(si5[-2]))
        self.assertEqual(4, len(si5[-1]))

        # Need of delta

        si10d = wi.time_split(10.5, 5., 0.1)
        self.assertEqual(24, len(si10d))
        for i in range(22):
            self.assertEqual(11, len(si10d[i]))
        self.assertEqual(9, len(si10d[-2]))
        self.assertEqual(4, len(si10d[-1]))

        si10d = wi.time_split(10.5, 5.)
        self.assertEqual(24, len(si10d))
        for i in range(22):
            self.assertEqual(10, len(si10d[i]))
        self.assertEqual(9, len(si10d[-2]))
        self.assertEqual(4, len(si10d[-1]))

        si10d = wi.time_split(10.5, 5., 0.9)
        self.assertEqual(24, len(si10d))
        for i in range(22):
            self.assertEqual(10, len(si10d[i]))
        self.assertEqual(9, len(si10d[-2]))
        self.assertEqual(4, len(si10d[-1]))

    # -----------------------------------------------------------------------

    def test_continuous_anchor_split_int_intervals(self):
        tier = sppasTier()
        for i, entry in enumerate(self.sent.split()):
            tier.create_annotation(
                sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i + 1))),
                sppasLabel(sppasTag(entry)))
        wi = sppasTierWindow(tier)

        intervals = wi.continuous_anchor_split(["#"])
        self.assertEqual(3, len(intervals))
        self.assertEqual(1, intervals[0][0])
        self.assertEqual(38, intervals[0][1])
        self.assertEqual(39, intervals[1][0])
        self.assertEqual(82, intervals[1][1])
        self.assertEqual(83, intervals[2][0])
        self.assertEqual(118, intervals[2][1])

        #todo: Test if holes in the tier

    # -----------------------------------------------------------------------

    def test_continuous_anchor_split_int_points(self):
        tier = sppasTier()
        for i, entry in enumerate(self.sent.split()):
            tier.create_annotation(
                sppasLocation(sppasPoint(i+1)),
                sppasLabel(sppasTag(entry)))
        wp = sppasTierWindow(tier)

        intervals = wp.continuous_anchor_split(["#"])
        self.assertEqual(3, len(intervals))
        self.assertEqual(1, intervals[0][0])
        self.assertEqual(38, intervals[0][1])
        self.assertEqual(39, intervals[1][0])
        self.assertEqual(82, intervals[1][1])
        self.assertEqual(83, intervals[2][0])
        self.assertEqual(118, intervals[2][1])

    # -----------------------------------------------------------------------

    def test_anchor_split_int_intervals(self):
        tier = sppasTier()
        for i, entry in enumerate(self.sent.split()):
            tier.create_annotation(
                sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))),
                sppasLabel(sppasTag(entry)))
        wi = sppasTierWindow(tier)

        si = wi.anchor_split(1, 1, ["#"])

        self.assertEqual(3, len(si))
        self.assertEqual(37, len(si[0]))
        self.assertEqual(43, len(si[1]))
        self.assertEqual(35, len(si[2]))

        si = wi.anchor_split(2, 1, ["#"])
        self.assertEqual(2, len(si))
        self.assertEqual(80, len(si[0]))
        self.assertEqual(78, len(si[1]))

        si = wi.anchor_split(1, 1, ["#", "+"])
        self.assertEqual(12, len(si))

        si = wi.anchor_split(3, 1, ["#", "+"])
        self.assertEqual(10, len(si))

    # -----------------------------------------------------------------------

    def test_anchor_split_int_tags(self):
        tier = sppasTier()
        for i, entry in enumerate(self.sent.split()):
            if entry in ("+", "#"):
                tier.create_annotation(
                    sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i + 1))),
                    sppasLabel(sppasTag(0, "int")))
            else:
                tier.create_annotation(
                    sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))),
                    sppasLabel(sppasTag(i+1, "int")))

        wi = sppasTierWindow(tier)

        si = wi.anchor_split(1, 1, [0])
        self.assertEqual(12, len(si))

        si = wi.anchor_split(3, 1, [0])
        self.assertEqual(10, len(si))

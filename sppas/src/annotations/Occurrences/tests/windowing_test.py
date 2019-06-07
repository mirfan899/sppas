import unittest

from sppas import sppasTier, sppasAnnotation, sppasLabel, sppasTag, sppasTypeError
from sppas import sppasLocation, sppasPoint
from sppas import sppasInterval
from ..windowing import sppasWindow


class WindowingTest(unittest.TestCase):
    def setUp(self):
        self.tiers = sppasTier()
        sentence = ['le', 'petit', 'chat', 'chat', 'tout', 'beau']
        labels1 = list()
        labels2 = list()
        for word in sentence[:2]:
            labels1.append(sppasLabel(sppasTag(word, 'str')))
        for word in sentence[2:]:
            labels2.append(sppasLabel(sppasTag(word, 'str')))

        ann1 = sppasAnnotation(sppasLocation
                               (sppasInterval
                                (sppasPoint(0.0), sppasPoint(1.2))), labels1)
        ann2 = sppasAnnotation(sppasLocation
                               (sppasInterval
                                (sppasPoint(1.4), sppasPoint(2.2))), labels2)
        self.tiers.append(ann1)
        self.tiers.append(ann2)

    def test_time_split(self):
        my_window1 = sppasWindow(self.tiers)
        my_split1 = my_window1.time_split(0.0, 0.9, 0.4, 0.9)
        my_window2 = sppasWindow(self.tiers)
        my_split2 = my_window2.time_split(1.4, 2.2, 0.4)

        self.assertNotEqual(my_split1, my_split2)
        self.assertEqual(1, len(my_split1))
        self.assertEqual(1, len(my_split2))

        class Hello(object):
            def __init__(self):
                pass

        with self.assertRaises(sppasTypeError) as error:
            my_window3 = sppasWindow(Hello())

            self.assertTrue(isinstance(error.exception, sppasTypeError))

        with self.assertRaises(sppasTypeError) as error:
            my_split3 = my_window2.time_split('a', Hello(), 12)

            self.assertTrue(isinstance(error.exception, sppasTypeError))

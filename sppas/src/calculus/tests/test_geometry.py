# -*- coding:utf-8 -*-

import unittest

from ..geometry.distances import squared_euclidian
from ..calculusexc import VectorsError

# ---------------------------------------------------------------------------


class TestGeometry(unittest.TestCase):

    def test_distances(self):
        x = (1.0, 0.0)
        y = (0.0, 1.0)
        self.assertEqual(squared_euclidian(x, y), 2.)
        with self.assertRaises(VectorsError):
            z = (1.0, 0.0, 1.0)
            self.assertEqual(squared_euclidian(x, z), 2.)


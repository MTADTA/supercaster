"""Regression checks for the physical direction of the floor and cutter reach."""
import unittest

import numpy as np
from scipy import ndimage

import air
import geom


class ChamberGeometry(unittest.TestCase):
    def test_floor_and_volume(self):
        floor = np.array([-1.1, -1.0])
        np.testing.assert_array_equal(geom.chamber_floor(floor, 7), floor)
        np.testing.assert_allclose(geom.chamber_floor(floor, 6), floor - 1/25.4)
        self.assertTrue(np.all(geom.chamber_floor(floor, 8) > floor))

    def test_connected_tool_pocket(self):
        opening = np.zeros((26, 26), dtype=bool)
        opening[3:17, 3:17] = True
        opening[18:23, 18:23] = True
        raster = dict(m=opening, din=ndimage.distance_transform_edt(opening), r=1)
        np.testing.assert_array_equal(air.throat_mask(raster, 0), opening)
        pocket = air.throat_mask(raster, 0, 2*25.4)
        self.assertEqual(ndimage.label(pocket)[1], 1)
        self.assertFalse(np.any(pocket & ~opening))
        self.assertTrue(pocket[10,10])
        self.assertFalse(pocket[20,20])

"""Run with python3 -m unittest discover -s body/optimize/carve-v2-acoustics."""
import unittest
from strength_sizing import thickness_for_strength


class StrengthSizingTests(unittest.TestCase):
    def setUp(self):
        # Analytic bending law: stress = 16/t^2 MPa.
        self.samples = [{'t': t, 'worst_MPa': 16 / t**2} for t in (2, 4, 8)]

    def test_known_solution_and_strength_direction(self):
        for strength in (1e6, 2e6, 4e6):
            expected = (16 / (0.5 * strength / 1e6))**0.5
            self.assertAlmostEqual(thickness_for_strength(self.samples, 0.5, strength), expected)

    def test_out_of_range_is_not_a_boundary_solution(self):
        self.assertIsNone(thickness_for_strength(self.samples, 0.5, 0.1e6))
        self.assertIsNone(thickness_for_strength(self.samples, 0.5, 20e6))

    def test_nonmonotone_requires_review(self):
        with self.assertRaises(ValueError):
            thickness_for_strength(self.samples + [{'t': 10, 'worst_MPa': 1}], 0.5, 2e6)


if __name__ == '__main__':
    unittest.main()

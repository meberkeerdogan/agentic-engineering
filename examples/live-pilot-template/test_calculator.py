import unittest

from calculator import median


class MedianTests(unittest.TestCase):
    def test_odd_length(self) -> None:
        self.assertEqual(median([9, 1, 5]), 5)

    def test_even_length(self) -> None:
        self.assertEqual(median([1, 10, 2, 6]), 4)

    def test_input_is_not_mutated(self) -> None:
        values = [3, 1, 2]
        median(values)
        self.assertEqual(values, [3, 1, 2])

    def test_empty_input(self) -> None:
        with self.assertRaises(ValueError):
            median([])


if __name__ == "__main__":
    unittest.main()

import unittest

from Generator import Generator
from common import FaultBoundary, FrameSize


class TestGenerator(unittest.TestCase):
    frames_sets = [
        [
            [
                [15, 54, 24, 185, 134],
                [75, 42, 53, 64, 21],
                [42, 52, 75, 43, 23],
                [92, 42, 64, 75, 12],
                [94, 0, 32, 255, 34],
            ],
            [
                [64, 42, 34, 111, 121],
                [75, 42, 53, 64, 21],
                [42, 52, 75, 43, 23],
                [92, 42, 64, 75, 12],
                [94, 0, 32, 255, 34],
            ],
        ],
    ]

    def test_init_parameters(self):
        generator = Generator(fault_boundary=FaultBoundary(2, 253), expected_no_bits=25)

        self.assertEqual(2, generator.fault_boundary.lower)
        self.assertEqual(253, generator.fault_boundary.upper)
        self.assertEqual(25, generator.expected_no_bits)
        self.assertEqual(3, generator.extra_frames)
        self.assertEqual(5, generator.cols)
        self.assertEqual(5, generator.rows)
        self.assertEqual(5, len(generator.matrix))
        self.assertEqual(25, generator.matrix_length)
        self.assertEqual(0, generator.current_length)
        self.assertEqual(0, generator.row)
        self.assertEqual(0, generator.col)

    def test_fill_matrix(self):
        generator = Generator(fault_boundary=FaultBoundary(2, 253), expected_no_bits=25)

        generator.fill_matrix(self.frames_sets[0])
        self.assertEqual(25, generator.current_length)
        self.assertListEqual([
            [1, 0, 0, 1, 0],
            [1, 0, 1, 0, 1],
            [0, 0, 1, 1, 1],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 1, 1]
        ], generator.matrix)

    def test_get_hashed_matrix(self):
        generator = Generator(fault_boundary=FaultBoundary(2, 253), expected_no_bits=25)

        generator.fill_matrix(self.frames_sets[0])
        hashed_matrix = list(generator.get_hashed_matrix())
        self.assertEqual(25, len(hashed_matrix))
        self.assertListEqual([
            1, 1, 0, 0, 0,
            0, 0, 0, 0, 0,
            0, 1, 1, 0, 0,
            1, 0, 1, 1, 1,
            0, 1, 1, 0, 1
        ], hashed_matrix)

    def test_needed_no_frames(self):
        generator = Generator(fault_boundary=FaultBoundary(2, 253), expected_no_bits=25)

        self.assertEqual(4, generator.needed_no_frames(FrameSize(width=1280, height=720)))

    def test_is_matrix_filled(self):
        generator = Generator(fault_boundary=FaultBoundary(2, 253), expected_no_bits=25)
        generator.fill_matrix(self.frames_sets[0])

        self.assertTrue(generator.is_matrix_filled())


if __name__ == '__main__':
    unittest.main()

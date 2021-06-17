import argparse
import math
import timeit

import numpy as np
import pandas as pd
from tabulate import tabulate

from common import FaultBoundary, FrameSize


class Generator:
    def __init__(self, fault_boundary: FaultBoundary, expected_no_bits: int, extra_frames: int = 3) -> None:
        self.fault_boundary: FaultBoundary = fault_boundary
        self.expected_no_bits: int = expected_no_bits
        self.extra_frames: int = extra_frames

        expected_no_bits_sqrt: int = math.ceil(math.sqrt(expected_no_bits))
        self.cols: int = expected_no_bits_sqrt
        self.rows: int = expected_no_bits_sqrt

        self.matrix: list[list[int]] = [[0 for j in range(self.cols)] for i in range(self.rows)]
        self.matrix_length: int = self.cols * self.rows

        self.current_length: int = 0

        self.row: int = 0
        self.col: int = 0

    def fill_matrix(self, frames) -> None:
        if self.current_length == self.matrix_length:
            raise Exception('Matrix is already filled')

        for i, frame in enumerate(frames):
            frame = np.ravel(frame)
            filtered_frame = filter(
                lambda x: self.fault_boundary.lower <= x <= self.fault_boundary.upper,
                frame
            )

            for val in filtered_frame:
                if self.col == self.cols:
                    self.col = 0
                    self.row += 1
                if self.row >= self.rows:
                    break

                self.matrix[self.row][self.col] = (val + 1) & 1 if i & 1 else val & 1

                self.current_length += 1
                self.col += 1

    def get_hashed_matrix(self) -> list[int]:
        if self.current_length < self.matrix_length:
            raise Exception('Matrix shall be filled')

        hashed_result = np.ravel(self.matrix, 'F')
        return hashed_result[:self.expected_no_bits]

    def needed_no_frames(self, frame_size: FrameSize) -> int:
        no_frames: int = math.ceil(self.matrix_length / (frame_size.width * frame_size.height))
        no_frames += self.extra_frames  # extra frames for more data (boundary values)
        return no_frames

    def is_matrix_filled(self) -> bool:
        return self.current_length > self.matrix_length


if __name__ == '__main__':
    def gen_8bit_nums(expected_no_nums: int, of_path: str):
        from Camera import Camera
        from common import bit_list_to_bit_string, split_bit_string_to_n_bit_nums

        start_time_total = timeit.default_timer()

        frame_size = FrameSize(width=1280, height=720)
        fault_boundary = FaultBoundary(lower=2, upper=253)
        camera = Camera(src=0, frame_size=frame_size, fps=30, no_frames_auto_settings=120)
        expected_no_bits = expected_no_nums * 8
        generator = Generator(fault_boundary=fault_boundary, expected_no_bits=expected_no_bits)
        needed_no_frames = generator.needed_no_frames(frame_size)

        start_time_take_frames = timeit.default_timer()
        frames = camera.take_frames(needed_no_frames)
        end_time_take_frames = timeit.default_timer()

        camera.release_cap()

        start_time_fill_matrix = timeit.default_timer()
        generator.fill_matrix(frames)
        end_time_fill_matrix = timeit.default_timer()

        start_time_hash_matrix = timeit.default_timer()
        random_bits = generator.get_hashed_matrix()  # [1, 0, 1, 1, 0, 1, ...]
        end_time_hash_matrix = timeit.default_timer()

        start_time_bl2bs = timeit.default_timer()
        random_bits_string = bit_list_to_bit_string(random_bits)
        end_time_bl2bs = timeit.default_timer()

        start_time_bs2nums = timeit.default_timer()
        nums_8bit = split_bit_string_to_n_bit_nums(8, random_bits_string)
        end_time_bs2nums = timeit.default_timer()

        start_time_w2f = timeit.default_timer()
        with open(of_path, 'w') as f:
            for num in nums_8bit:
                f.write(f'{num}\n')
        end_time_w2f = timeit.default_timer()

        end_time_total = timeit.default_timer()

        df = pd.DataFrame({
            'Name': [
                'Time of taking frames',
                'Time of filling matrix',
                'Time of hashing matrix',
                'Time of converting bit list to bit string',
                'Time of converting bit string to list of 8-bit nums',
                'Time of writing 8-bit nums to file',
                'Total time',
                'Matrix length',
                'No. pushed bits to matrix',
                'Expected no. bits',
                'No. bits',
                'No. needed frames',
                'No. took frames',
                'No. 8-bit nums',
            ],
            'Value': [
                end_time_take_frames - start_time_take_frames,
                end_time_fill_matrix - start_time_fill_matrix,
                end_time_hash_matrix - start_time_hash_matrix,
                end_time_bl2bs - start_time_bl2bs,
                end_time_bs2nums - start_time_bs2nums,
                end_time_w2f - start_time_w2f,
                end_time_total - start_time_total,
                generator.matrix_length,
                generator.current_length,
                expected_no_bits,
                len(random_bits),
                needed_no_frames,
                len(frames),
                len(nums_8bit),
            ]
        })

        print(tabulate(df, headers='keys', tablefmt='psql', numalign='right', showindex=False))


    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-n', '--no-nums', action='store', type=int, help='No. 8-bit nums to generate')
    arg_parser.add_argument('-o', '--output', action='store', type=str, help='Output file path')
    args = arg_parser.parse_args()

    if not args.no_nums:
        print('No. 8-bit nums must be specified')
        exit(1)
    if not args.output:
        print('Output file path must be specified')
        exit(1)

    try:
        gen_8bit_nums(expected_no_nums=args.no_nums, of_path=args.output)
        exit(0)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
        exit(1)

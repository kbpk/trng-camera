from collections import namedtuple

import numpy as np
from scipy.stats import entropy

FrameSize = namedtuple('FrameSize', ['width', 'height'])
FaultBoundary = namedtuple('FaultBoundary', ['lower', 'upper'])


def bit_list_to_bit_string(bit_list: list[int]) -> str:
    bit_string = ''.join([str(x & 1) for x in bit_list])
    return bit_string


def split_bit_string_to_n_bit_nums(n: int, bit_string: str) -> list[int]:
    n_bit_nums = [int(bit_string[i:i + n], 2) for i in range(0, len(bit_string), n)]
    return n_bit_nums


def calc_entropy(nums: list[int]) -> float:
    p, _ = np.histogram(nums, bins=256, range=(0, 255), density=True)
    entropy_val = entropy(p, base=2)
    return entropy_val

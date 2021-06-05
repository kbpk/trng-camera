from collections import namedtuple
from typing import List

FrameSize = namedtuple('FrameSize', ['width', 'height'])
FaultBoundary = namedtuple('FaultBoundary', ['lower', 'upper'])


def bit_list_to_bit_string(bit_list: List[int]) -> str:
    bit_string = ''.join([str(x & 1) for x in bit_list])
    return bit_string


def split_bit_string_to_n_bit_nums(n: int, bit_string: str) -> List[int]:
    n_bit_nums = [int(bit_string[i:i + n], 2) for i in range(0, len(bit_string), n)]
    return n_bit_nums

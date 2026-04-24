# src/domain/value_objects.py
from enum import Enum

"""
Enum을 사용하여 추후 사용시에 오타를 줄이고, 에러를 줄이고, 유지보수성도 좋다!
"""

class MismatchType(str, Enum):
    ORIGINAL     = "original"
    SHUFFLE     = "shuffle"
    OBJECT_SWAP = "object_swap"
    ACTION_SWAP = "action_swap"
    PLACE_SWAP  = "place_swap"

class Label(int, Enum):
    MATCH       = 1
    MISMATCH    = 0

class PromptType(str, Enum):
    A = "A"
    B = "B"
    C = "C"
# src/domain/entities.py
from dataclasses import dataclass
from .value_objects import MismatchType, Label

'''
@dataclass 의 역할 : __init__과 __repr__을 자동으로 만들어준다.
__init__ : Sample.image_id 같은 초기화하는 기능
__repr__ : print(Sample(image_id),...) 등으로 예쁜 문자열로 출력하는 기능
'''

@dataclass
class Sample:
    image_id: str
    image_path: str
    caption: str
    label: Label
    mismatch_type: MismatchType

@dataclass
class Prediction:
    image_id: str
    caption: str
    label: Label
    pred_match: int
    confidence: float
    reason: str
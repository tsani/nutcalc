from __future__ import annotations
from dataclasses import dataclass, fields
from typing import NewType

Row = NewType('Row', int)
Col = NewType('Col', int)

@dataclass
class SourceSpan:
    start: (Row, Col)
    end: (Row, Col)
    filename: str | None = None

    def as_prefix(self):
        return ''.join([
            '' if self.filename is None else self.filename + ":",
            f'{self.start[0]}:{self.start[1]}:',
        ])

@dataclass
class Located:
    @property
    def filename(self):
        if self.location is None:
            return None
        else:
            return self.location.filename

    @filename.setter
    def filename(self, x):
        if self.location is not None:
            self.location.filename = x

        for field in fields(self):
            attr = getattr(self, field.name)
            if isinstance(attr, Located):
                attr.filename = x
            elif isinstance(attr, list) and len(attr):
                for elem in attr:
                    if isinstance(elem, Located):
                        elem.filename = x

def located(cls):
    @dataclass
    class ClsWithLocation(cls, Located):
        location: SourceSpan | None = None
    ClsWithLocation.__name__ = cls.__name__ + 'WithLocation'
    return ClsWithLocation

@located
@dataclass
class FoodStmt:
    lhs: QuantifiedFood
    weight: Quantity | None
    body: Expr


@located
@dataclass
class WeightStmt:
    lhs: QuantifiedFood
    rhs: QuantifiedFood

@located
@dataclass
class PrintStmt:
    body: Expr

@located
@dataclass
class ImportStmt:
    path: str

Stmt = FoodStmt | WeightStmt | PrintStmt

@located
@dataclass
class Quantity:
    count: float
    unit: str

@located
@dataclass
class QuantifiedFood:
    quantity: Quantity
    food: str

@located
@dataclass
class Expr:
    items: list[QuantifiedFood]

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]

@located
@dataclass
class Module:
    imports: list[ImportStmt]
    body: list[Stmt]

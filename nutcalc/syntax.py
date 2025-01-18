from __future__ import annotations
from dataclasses import dataclass
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
class FoodStmt:
    lhs: QuantifiedFood
    weight: Quantity | None
    body: Expr

    location: SourceSpan | None = None

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
        self.lhs.filename = x
        if self.weight is not None:
            self.weight.filename = x
        self.body.filename = x

@dataclass
class WeightStmt:
    lhs: QuantifiedFood
    rhs: QuantifiedFood

    location: SourceSpan | None = None

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
        self.lhs.filename = x
        self.rhs.filename = x

@dataclass
class PrintStmt:
    body: Expr

    location: SourceSpan | None = None

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
        self.lhs.filename = x
        self.rhs.filename = x

@dataclass
class ImportStmt:
    path: str

    location: SourceSpan | None = None

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

# @dataclass
# class EatStmt:
#     body: Expr
#
# @dataclass
# class SleepStmt:
#     pass

Stmt = FoodStmt | WeightStmt | PrintStmt

@dataclass
class Quantity:
    count: float
    unit: str

    location: SourceSpan | None = None

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

@dataclass
class QuantifiedFood:
    quantity: Quantity
    food: str

    location: SourceSpan | None = None

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
        self.quantity.filename = x

@dataclass
class Expr:
    items: list[QuantifiedFood]

    location: SourceSpan | None = None

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]

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
        for item in self.items:
            item.filename = x

@dataclass
class Module:
    imports: list[ImportStmt]
    body: list[Stmt]

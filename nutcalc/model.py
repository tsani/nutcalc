from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

UnitName = NewType('UnitName', str)

@dataclass
class Unit:
    """A unit represents an amount of a particular food."""
    name: UnitName
    gram_equivalent: float

    @staticmethod
    def is_weight(x: Unit | str):
        return (x in WEIGHTS) or (getattr(x, 'name', '') in WEIGHTS)

FoodName = NewType('FoodName', str)

@dataclass
class Nutrient:
    name: FoodName
    energy: float
    natural_unit: UnitName

    def unit_weight(self, name: UnitName) -> float:
        if name != self.natural_unit:
            raise ValueError(
                f"Cannot retrieve weight of {self.name} in {name}; it's "
                f"natural unit is {self.natural_unit}.",
            )
        unit = WEIGHTS.get(name)
        if unit is None:
            raise ValueError(f"Nutrient natural unit must be a weight")
        return unit.gram_equivalent

    @property
    def units(self):
        return [WEIGHTS[self.natural_unit]]

    @property
    def reference_quantity(self):
        return Quantity(count=1, unit=self.natural_unit)

    @property
    def nutrition_facts(self):
        return NutritionFacts(
            data={ self.name: self.reference_quantity },
        )

@dataclass
class CompoundFood:
    """A food consisting of several constituent foods, and possessing several
    units. The constituent amounts are for a normalized quantity of 100 g of
    this compound food."""
    units: list[Unit] # TODO use a dict keyed on names
    name: FoodName
    constituents: list[QuantifiedFood]

    @staticmethod
    def from_reference_quantity(
        name: str,
        units: list[Unit],
        constituents: list[QuantifiedFood],
        reference: Quantity,
    ):
        """Constructs a compound food from the constituents of a given
        reference quantity, normalizing to the standard 100g reference."""
        reference_unit = next(
            (u for u in units if u.name == reference.unit),
            None,
        )
        if reference_unit is None:
            raise ValueError(
                f'Unit of reference quantity `{reference}` is not among '
                f'units `{units}` of food to construct, `{name}`',
            )
        scale_factor = 100 / (reference.count * reference_unit.gram_equivalent)
        food = CompoundFood(
            name=name,
            units=list(units),
            constituents=[food*scale_factor for food in constituents],
        )
        return food

    @staticmethod
    def from_constituent_sum(
        name: str,
        units: list[Unit],
        constituents: list[QuantifiedFood],
        quantity: Quantity,
    ):
        """Constructs a compound food together with a new unit for it whose
        gram equivalent is computed from the sum of the weights of the
        constituent foods."""
        total_weight = sum(c.weight for c in constituents)
        unit = Unit(
            name=UnitName(quantity.unit),
            gram_equivalent=total_weight / quantity.count,
        )
        return CompoundFood.from_reference_quantity(
            name,
            units=units + [unit],
            constituents=constituents,
            reference=quantity,
        )

    # def actually_weighs(self, qty: Quantity, grams: float):
    #     ratio = grams / qty.weigh(self)

    def unit_weight(self, name: UnitName) -> float:
        """Retrieves the weight in grams of the given unit for this food."""
        unit = next(
            (u for u in self.units if u.name == name),
            None,
        )
        if unit is None:
            raise ValueError(
                f'No such unit {name} for CompoundFood {self.name}',
            )
        return unit.gram_equivalent

    @property
    def reference_quantity(self):
        return Quantity(count=100, unit=G.name)

    @property
    def nutrition_facts(self):
        nut = NutritionFacts.empty()
        for constituent in self.constituents:
            nut += constituent.nutrition_facts
        return nut

    def define_unit(self, qty: Quantity, reference: Quantity):
        """Defines a new unit, expressed as a quantity, as a computed ratio
        with a reference quantity using an existing unit."""
        w = reference.weigh(self)
        self.units.append(Unit(name=qty.unit, gram_equivalent=w / qty.count))

Food = Nutrient | CompoundFood

@dataclass
class Quantity:
    """A quantity can only be interpreted relative to some food, into which we
    can look up the name of the unit and determine its gram equivalent.
    A quantity can be multiplied by a scalar."""
    count: float
    unit: UnitName

    @staticmethod
    def zero(unit: UnitName):
        return Quantity(count=0, unit=unit)

    def __mul__(self, k):
        match k:
            case float:
                return Quantity(count=self.count*k, unit=self.unit)
        raise ValueError(f"Quantity cannot be multiplied by {type(k)}")

    def __add__(self, other):
        """Adds two quantities, provided they have the exact same unit."""
        if self.unit != other.unit:
            raise ValueError(
                f'Quantity of {self.unit} cannot be added to quantity of '
                f'{other.unit}',
            )
        return Quantity(self.count + other.count, self.unit)

    def __str__(self):
        return f'{self.count:.2f} {self.unit}'

    def weigh(self, food: Food) -> float:
        """Computes the weight in grams of this quantity of the given food."""
        return self.count * food.unit_weight(self.unit)

@dataclass
class QuantifiedFood:
    """A Quantity together with a Food.
    The unit name contained in the Quantity is valid for the Food.
    For a Nutrient, that means it's the same as the Nutrient's natural unit.
    For a CompoundFood, that means it's among the units of that food.
    A QuantifiedFood can be multiplied by a scalar."""
    quantity: Quantity
    food: Food

    def __mul__(self, k):
        return QuantifiedFood(quantity=self.quantity * k, food=self.food)

    @property
    def weight(self):
        """The weight of this quantity of food, in grams."""
        return self.quantity.weigh(self.food)

    @property
    def nutrition_facts(self):
        nut = self.food.nutrition_facts
        reference_weight = self.food.reference_quantity.weigh(self.food)
        scale_factor = self.weight / reference_weight
        return nut * scale_factor

@dataclass
class NutritionFacts:
    """Wraps a map of nutrients -> quantities with some arithmetic
    operations."""
    data: dict[FoodName, Quantity]

    @staticmethod
    def empty():
        return NutritionFacts(data={})

    def __add__(self, other: NutritionFacts) -> NutritionFacts:
        nut = NutritionFacts(data=dict(self.data))
        for name, qty in other.data.items():
            nut.data[name] = nut.data.get(name, Quantity.zero(qty.unit)) + qty
        return nut

    def __mul__(self, k) -> NutritionFacts:
        match k:
            case float:
                return NutritionFacts(
                    { name: qty*k for name, qty in self.data.items() },
                )
        raise ValueError(
            f'NutritionFacts cannot be multiplied by {type(k)}, only `float`.',
        )

    @property
    def energy(self):
        """The energy content in kcal of these nutrition facts."""
        return sum(
            NUTRIENTS[name].energy * qty.count
            for name, qty in
            self.data.items()
        )

    @property
    def pretty(self):
        rows = []
        rows.append(f'energy: {Quantity(self.energy, "kcal")}')
        for k in (n.name for n in ALL_NUTRIENTS):
            if k in self.data:
                rows.append(f'{k}: {self.data[k]}')
        return '\n'.join(rows)

def nutrition_facts(q: Quantity, food: Food):
    return QuantifiedFood(quantity=q, food=food).nutrition_facts

### GLOBAL CONSTANTS: ###

# The weights are special units, in that they are independent of any food.
# This is expressed by making every food have these units as a basis, plus any
# extra units that might be defined for that food.
G = Unit(name=UnitName('g'), gram_equivalent=1)
KG = Unit(name=UnitName('kg'), gram_equivalent=1000)
MG = Unit(name=UnitName('mg'), gram_equivalent=0.001)
MCG = Unit(name=UnitName('mcg'), gram_equivalent=0.000001)
OZ = Unit(name=UnitName('oz'), gram_equivalent=28)
LB = Unit(name=UnitName('lb'), gram_equivalent=454)
IU = Unit(name=UnitName('IU'), gram_equivalent=0)

ALL_WEIGHTS = [G, KG, MG, OZ, LB]
WEIGHTS = { w.name: w for w in ALL_WEIGHTS }

PROTEIN = Nutrient(name=FoodName('protein'), energy=4, natural_unit=G.name)
CARBS = Nutrient(name=FoodName('carbs'), energy=4, natural_unit=G.name)
FAT = Nutrient(name=FoodName('fat'), energy=9, natural_unit=G.name)

MILLI_MINERALS = [
    Nutrient(FoodName(name), 0, MG.name)
    for name in
    [ 'calcium', 'iron', 'magnesium', 'phosphorus', 'potassium', 'sodium'
    , 'zinc', 'copper', 'flouride', 'manganese', 'VitC', 'VitE', 'riboflavin'
    , 'niacin', 'cholesterol'
    ]
]

MICRO_MINERALS = [
    Nutrient(FoodName(name), 0, MCG.name)
    for name in
    [ 'selenium', 'carotene', 'folate' ]
]

VITAMINS = [
    Nutrient(FoodName(name), 0, IU.name)
    for name in
    [ 'VitA', 'VitD', 'VitB6', 'VitB12', 'VitK' ]
]

MACRONUTRIENTS = [PROTEIN, FAT, CARBS]
ALL_NUTRIENTS = MACRONUTRIENTS + [Nutrient(FoodName('water'), 0, G.name)] + \
    MILLI_MINERALS + MICRO_MINERALS + VITAMINS

NUTRIENTS = { nut.name: nut for nut in ALL_NUTRIENTS }

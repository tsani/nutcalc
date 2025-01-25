from . import syntax
from . import model
from . import config
from .log import log

from dataclasses import dataclass
from typing import NewType
import os.path as ospath

class InterpretationError(RuntimeError):
    def __init__(self, msg, location=None, **kwargs):
        self.location = location
        self.msg = msg
        super().__init__(self, **kwargs)

    def __str__(self):
        if self.location is None:
            return self.msg
        else:
            return self.location.as_prefix() + self.msg

###############################################################################

FoodMap = NewType('FoodMap', dict[model.FoodName, model.Food])

NUTRIENT_DB = {
    nut.name: nut
    for nut in
    model.ALL_NUTRIENTS
}

class FoodDB:
    data: FoodMap = {}

    def __init__(self, data: FoodMap | None = None):
        if data is None:
            data = dict(NUTRIENT_DB)
        self.data = data

    def register(self, food: model.Food, location=None):
        if food.name in self.data:
            raise InterpretationError(
                f'food {food.name} already defined',
                location=location,
            )
        self.data[food.name] = food

    def get(self, name: model.FoodName, location = None):
        if name not in self.data:
            raise InterpretationError(
                f'food {name} is not defined',
                location=location,
            )
        return self.data[name]

    def has(self, name: model.FoodName):
        return name in self.data

###############################################################################

class Interpreter:
    def __init__(self, foodDB: FoodDB | None = None, verbose=False):
        self.verbose = verbose
        if foodDB is None:
            self.foodDB = FoodDB()
        self.modules = set()

    def load_module(self, path: str, module: syntax.Module):
        if path in self.modules: return # already loaded
        normalize = lambda p: ospath.join(ospath.dirname(path), p + '.nut')
        if any(normalize(m.path) not in self.modules for m in module.imports):
            raise InterpretationError(
                f'Module {path} cannot be loaded; at least one of its imports '
                'is not loaded yet.',
            )
        for stmt in module.body:
            self.execute(stmt)
        self.modules.add(path)

    def execute(self, stmt: syntax.Stmt) -> None:
        """Execute a statement in this interpreter."""
        match stmt:
            case syntax.FoodStmt():
                self._food_stmt(stmt)
            case syntax.WeightStmt():
                self._weight_stmt(stmt)
            case syntax.PrintStmt():
                self._print_stmt(stmt)
            case _:
                assert False, f'statement {stmt} is handled'

    ##########################################################################

    def _print_stmt(self, stmt: syntax.PrintStmt):
        qfs = [self._quantified_food(part) for part in stmt.body]
        print(sum(
            (qf.nutrition_facts for qf in qfs),
            start=model.NutritionFacts.empty(),
        ).pretty)

    def _food_stmt(self, stmt: syntax.FoodStmt):
        lhs_qty = self._quantity(stmt.lhs.quantity)
        rhs = [self._quantified_food(part) for part in stmt.body]

        if model.Unit.is_weight(lhs_qty.unit):
            if stmt.weight is None:
                # e.g. `20 g foo = ...`
                food = model.CompoundFood.from_reference_quantity(
                    name=stmt.lhs.food,
                    units=model.ALL_WEIGHTS,
                    constituents=rhs,
                    reference=lhs_qty,
                )
                self.foodDB.register(food, location=stmt.lhs.location)
                log(f'defined food {stmt.lhs.food}, ref qty {lhs_qty}')
            else:
                # forbid stuff like `20 g foo weighs 25 g = ...`
                raise InterpretationError(
                    f'unit {lhs_qty.unit} already defined for food ' \
                    '{stmt.lhs.food}',
                    location=stmt.location,
                )
        else:
            if stmt.weight is None:
                # e.g. `1 x foo = ...`
                self.foodDB.register(
                    model.CompoundFood.from_constituent_sum(
                        name=stmt.lhs.food,
                        units=model.ALL_WEIGHTS,
                        constituents=rhs,
                        quantity=lhs_qty,
                    ),
                    location=stmt.location,
                )
                log(f'defined food {stmt.lhs.food} from constituent sum')
            else:
                # e.g. `1 x foo weighs 20 g = ...`
                weight = self._quantity(stmt.weight)
                food = model.CompoundFood.from_reference_quantity(
                    name=stmt.lhs.food,
                    units=model.ALL_WEIGHTS,
                    constituents=rhs,
                    reference=weight,
                )
                self._define_unit(food, lhs_qty, weight)
                self.foodDB.register(food, location=stmt.location)
                log(
                    f'defined food {stmt.lhs.food} @ qty {lhs_qty} '
                    f'weight {weight}'
                )

    def _weight_stmt(self, stmt: syntax.WeightStmt):
        lhs_food = self.foodDB.get(stmt.lhs.food)
        lhs_qty = self._quantity(stmt.lhs.quantity)
        if model.Unit.is_weight(lhs_qty.unit):
            raise InterpretationError(
                f'unit {lhs_qty.unit} already exists for food {lhs_food.name}',
                location=stmt.location,
            )
        self._define_unit(
            lhs_food,
            lhs_qty,
            model.Quantity(
                self._quantified_food(stmt.rhs).weight,
                model.G.name,
            ),
        )

    ##########################################################################

    def _quantity(self, qty: syntax.Quantity, food: model.Food | None = None):
        """Interprets a syntax quantity into a model quantity, optionally
        validating its unit against a supplied food."""
        if food is not None and qty.unit not in (u.name for u in food.units):
            raise InterpretationError(
                f'unit {qty.unit} does not exit for food {food.name}',
                location=qty.location,
            )
        return model.Quantity(qty.count, qty.unit)

    def _quantified_food(self, syn: syntax.QuantifiedFood) -> model.QuantifiedFood:
        food = self.foodDB.get(syn.food)
        qty = self._quantity(syn.quantity, food)
        return model.QuantifiedFood(qty, food)

    def _is_new_food(self, syn: syntax.QuantifiedFood) -> bool:
        return not self.foodDB.has(syn.food)

    def _define_unit(self,
                     food: model.Food,
                     qty: model.Quantity,
                     reference: model.Quantity,
                     location=None):
        match food:
            case model.Nutrient:
                raise InterpretationError(
                    'new units cannot be defined for nutrients',
                    location=location,
                )
        if qty.unit in (u.name for u in food.units):
            raise InterpretationError(
                f'unit {qty.unit} already defined for food {food.name}',
                location=location,
            )
        food.define_unit(qty, reference)

###############################################################################

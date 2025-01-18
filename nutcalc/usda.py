from collections import defaultdict
from dataclasses import dataclass
from typing import NewType

import csv

NutrientName = NewType('NutrientName', str)
UnitName = NewType('UnitName', str)

@dataclass
class Food:
    id: int
    description: str
    nutrients: dict[NutrientName, [float, UnitName]]

# MODEL_NUTRIENTS = {
#     'Carbohydrate, by difference

@dataclass
class USDA:
    foods: dict[id, Food]

    @staticmethod
    def load(food_path, foot_nutrient_path, nutrient_path):
        with open(food_path) as food_file, \
            open(food_nutrient_path) as food_nutrient_file, \
            open(nutrient_path) as nutrient_file:

            foods = csv.reader(food_file)
            food_nutrients = csv.reader(food_nutrient_file)
            nutrients = csv.reader(nutrient_file)

            # skip headers
            next(foods)
            next(food_nutrients)
            next(nutrients)

            # load nutrients into dictionary
            nutrients_map : dict[int, [str, UnitName]] = {}
            for id, name, unit_name, *_ in nutrients:
                nutrients_map[id] = (name, unit_name)

            food_nutrients_map = defaultdict(lambda: {})
            for _, fdc_id, nut_id, amount, *_ in food_nutrients:
                (nutrient_name, unit_name) = nutrients_map[nut_id]
                food_nutrients_map[fdc_id][nutrient_name] = \
                    (amount, unit_name.lower())

            return USDA(
                foods={
                    fdc_id: Food(
                        fdc_id,
                        desc,
                        food_nutrients_map[fdc_id],
                    )
                    for fdc_id, _, desc, *__ in foods
                },
            )

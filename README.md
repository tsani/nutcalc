# Nutcalc: nutrition calculator

Nutcalc is:
- a calculator for nutrition facts
- a declarative programming language for computing nutritional information of foods, meals,
  recipes
- a simple way to journal your meals and track your macros
- designed to integrate best into a text editing, terminal-based workflow.

Try the online demo [here](https://nutcalc.jerrington.me/).

## Examples

This section defines a number of `.nut` files to first build up what foods you have on hand, then
to illustrate two use-cases: a meal plan and a food journal

### What foods do you have?

Create a file `pantry.nut` to define the foods you have on hand simply by reading off their
Nutrition Facts labels.

```nutcalc
# pantry.nut

2 slice 'factory white bread' weighs 71 g:
- 2 g fat + 6 g protein + 33 g carbs
- 320 mg sodium + 50 mg potassium + 2.25 mg iron

# ^ Defines 2 slices to weigh 71 g and having the given nutrition facts
# Uses the colon & bullet syntax to make vertical layout nicer

60 ml 'maple syrup' weighs 1.37*60 g = 54 g carbs + 0.15 mg copper
1 large egg weighs 50 g = 4.8 g fat + 6.3 g protein + 0.4 g carbs + 71 mg sodium

# ^ For simpler foods, you can use single-line layout with =
# Those lines define units `ml` and `large` for the foods `maple syrup` and `egg` respectively
# Anywhere a number is expected, you can do simple arithmetic consisting of addition,
# multiplication, and division.

# Define new units for foods based on existing units for those foods:
1 loaf 'factory white bread' = 20 slice
1 tbsp 'maple syrup' = 15 ml
```

### Define recipes

We could do everything in one file, but nutcalc has a simple `import` statement that makes it easy
to meaningfully break up our definitions to be more organized.

```nutcalc
# recipes.nut

import pantry

# Define recipes made up of various foods
2 portion 'french toast bake' weighs 1.2 kg:
- 1/2 loaf 'factory white bread'
- 8 large egg

1 portion 'pasta with meat sauce':
- 140 g 'dry pasta'
- 200 g 'meat sauce'

# etc.
```

### Create a meal plan

From our recipes, we can create a meal plan and easily tweak it to satisfy our energy and
macronutrient requirements.

```nutcalc
# mealplan-jan25.nut

import recipes

1 x 'breakfast 1':
- 2 x bagel + 4 tbsp 'cream cheese'
- 125 g yogurt

# Define two more breakfasts...

# Then make a meal plan:

1 x Monday:
- 1 x 'breakfast 1'
- 1 portion 'pasta with meat sauce'
- 1 x 'protein shake'
- 1 x 'steak dinner'
- 1 x 'mass gainer shake'

# 1 x Tuesday:
# ...
#
# and so on
```

Query nutrition facts computed from the above:

```bash
$ nutcalc example.nut
nutcalc> print 1 x '2025-01-18'
energy: 931.00 kcal
protein: 40.20 g
fat: 24.20 g
carbs: 138.10 g
iron: 5.62 mg
potassium: 125.00 mg
sodium: 1084.00 mg
copper: 0.15 mg
nutcalc> print 0.75 x '2025-01-18'
energy: 698.25 kcal
protein: 30.15 g
fat: 18.15 g
carbs: 103.58 g
iron: 4.22 mg
potassium: 93.75 mg
sodium: 813.00 mg
copper: 0.11 mg
nutcalc>
```

### Compute a shopping list

Since August 2025, Nutcalc supports a system of arbitrary tags that can be attached to entries when
making a definition. These tags are in general used to guide different traversals of a Food tree.
For now, the only meaningful tags are `buy` and `use`, related to the new ShoppingList feature.

Suppose I'm preparing to batch cook a lot of chili.
I can write out the shopping list for it by marking the constitutents of the `'chili batch aug
2025'` with the `buy` tag. (In practice I won't know ahead of time the weight of the finished
product, so at this point I would leave off the `weighs` clause. After cooking the chili and
weighing the finished product I would go and add the weighs clause.)

```nutcalc
1/2 cup 'KS diced tomatoes' weighs 126 g:
- 1 g protein + 6 g carbs
- 140 mg sodium + 261 mg potassium
250 ml 'KS diced tomatoes' = 1 cup
1 'big can' 'KS diced tomatoes' = 800 ml

224 g 'bottom blade roast':
- 48 g fat + 38.4 g protein
- 605 mg potassium + 160 mg cholesterol

1 cup 'dry white beans' weighs 202 g:
- 1.7 g fat + 122 g carbs + 47 g protein
- 21 mg iron

1 x 'chili batch aug 2025' weighs 8*1.2 + 1.5 + 0.6 kg:
- buy 4 kg 'bottom blade roast'
- buy 1.5 kg 'dry white beans'
- buy 3 'big can' 'KS diced tomatoes'
```

Now that I've cooked the chili, I want to prepare a meal plan for the upcoming week. The goal is
that after writing the meal plan, we can extract both its nutrition facts and the shopping list.
In this meal plan, for simplicity and ease of demonstration, I'll assume I'll eat the same thing
every day: `375 g 'KS greek yogurt'` and `450 g 'chili batch aug 2025'`.

```
3/4 cup 'KS greek yogurt' weighs 175 g:
- 17 g protein + 6 g carbs + 200 mg calcium

1 cup 'dry white rice' weighs 200 g:
- 1 g fat + 158 g carbs + 13 g protein
- 2 mg sodium + 1.6 mg iron

1 day 'meal plan':
- buy 375 g 'KS greek yogurt'
- use 450 g 'chili batch aug 2025'
- buy 1 cup 'dry white rice'
```

After loading this nut file into the nutcalc repl, I can now compute the shopping list for five
days of this meal plan easily.

```
nutcalc> shop 5 day 'meal plan'
1875.00 g KS greek yogurt
5.00 cup dry white rice
nutcalc> facts 1 day 'meal plan'
energy: 1510.46 kcal
protein: 89.96 g
fat: 34.45 g
carbs: 210.13 g
calcium: 428.57 mg
iron: 7.60 mg
potassium: 608.26 mg
sodium: 105.38 mg
cholesterol: 109.89 mg
```

The shopping list is computed by recursively traversing the items of the given expression, `5 day
'meal plan'`, multiplying by the quantity at each stage. Items marked with `buy` are collected into
the shopping list. Items marked with `use`, on the other hand, block traversal. This allows a meal
plan to refer to something previously cooked (with its own shopping list).

## How it works -- technical and mathematical details

Nutcalc uses the _inductive model of food._ I designed this model to enable arbitrary layering of
foods upon foods to uniformly represent recipes, meals, meal plans, etc.
I wrote a [blog post](https://jerrington.me/posts/2025-02-20-induction-on-food.html) about the
inductive model. I explain the gist of it here below.

A _Food_ is defined as either:

- Base case: nutrient -- a raw nutrient such as one of the macronutrients `protein`, `fat`,
  `carbs`, or a mineral such as `calcium`, `iron`, etc.
- Step case: compound food -- a list of _Quantified Foods_

- A _Quantified Food_ is just a _Quantity_ together with a _Food._
- A _Quantity_ is a _count_ of some _unit._

Units are specific to foods, since `1 cup` of flour doesn't have the same weight as `1 cup` of
maple syrup. Internally, each custom (essentially volumetric) unit is associated with its
equivalent in grams for its corresponding food.

- Units are only defined on compound foods, which come equipped by default with all the weight
  units such as `g`, `kg`, `mg`, `lb`, `oz`, etc.
- Nutrients, which are built-in, are associated to exactly one 'natural unit' in which quantities
  of that that nutrient must be expressed, e.g. `g` for the macronutrients and typically `mg` for
  most minerals.

Calculation of nutrition facts is defined for a Quantified Food according to the type of Food:
- For a nutrient, nutrition facts are simply the nutrient itself.
- For a compound food, i.e. itself list of Quantified Foods, compute the nutrition facts for a
  reference quantity of each constituent Food, multiply by its corresponding Quantity, and sum
  everything.

Mathematically, a Food is modelled as a finitely-branching weighted tree where the leaves are
nutrients and the internal nodes are compound foods.

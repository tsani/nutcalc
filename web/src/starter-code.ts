const EDITOR_STARTER_CODE = `# Define foods, meals, and journal what you eat in a .nut file like this.
# Add comments to your files using hashes.

# Define some simple foods:
1 cup '3.25% milk' weighs 257 g = 8 g fat + 12 g carbs + 9 g protein

# We needed to give a 'weighs' clause above as otherwise Nutcalc infers the
# weight of a food based on its constituents; a cup of milk weighs way more
# than just its macronutrients though!

# Alternative syntax for defining a food allows nice layout on multiple lines.
1 cup 'steel cut oats' weighs 160 g:
- 10 g fat + 21 g protein + 108 g carbs
- 6.8 mg iron + 579 mg potassium

# That form is more useful if you want to also track micronutrients, since you
# can put those on their own line separate from macros.

# Define a more complex food.
1 serving oatmeal = 2.5 cup '3.25% milk' + 3/4 cup 'steel cut oats'

# Nutcalc infers the weight of the custom unit 'serving' based on the sum of the weight of the constituent foods.
# This is not accurate for oatmeal since some water evaporates during cooking.
# Doesn't really matter though so long as you work with the 'serving' unit
# and don't log the oatmeal that you eat by weight. Otherwise, you can
# weigh the cooked product and add a 'weighs' clause to the definition.

# I eat my oatmeal with a number of garnishes. Let's define those.

# The nutrition facts label I found only lists per 100 g
100 g 'chia seeds' = 31 g fat + 42 g carbs + 17 g protein
1 tbsp 'chia seeds' = 14 g # but I work in tbsp for the chia seeds
# ^ This is a convenient syntax for defining new units. The right-hand side
# can directly be a weight, or more generally any unit that is already defined
# for the food mentioned on the left-hand side.

100 g walnuts:
- 65 g fat + 14 g carbs + 15 g protein
- 441 mg potassium

# I looked up that maple syrup is 1/3 sugar 2/3 water
1 tbsp 'maple syrup' weighs 14 g = 14*2/3 g carbs
# Anywhere you need to write a number in Nutcalc, you can instead use a math
# expression. Let Nutcalc do the math for you.

# Now let's journal our food intake.
# Just define a 'food' whose name is a date and list off the meals you eat
# as if they were constituents.
1 x '2025-02-11':
- 1 serving oatmeal + 40 g walnuts + 1 tbsp 'chia seeds' + 1 tbsp 'maple syrup'

# Of course, if you eat your oatmeal the same way every day, you can
# bake the garnishes directly into the definition of '1 serving oatmeal'.

# Now load this module using Ctrl+Enter and see what the macros are!
# Try "facts 1 serving oatmeal" or "facts 1 x '2025-02-11'"
# In general, "facts" can take any food expression on its right and computes
# the aggregate nutrition facts of that food.
`;

export default EDITOR_STARTER_CODE;
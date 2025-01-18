# example.nut

# Define foods by easily reading off a Nutrition Facts label
2 slice 'factory white bread' weighs 71 g:
- 2 g fat + 6 g protein + 33 g carbs
- 320 mg sodium + 50 mg potassium + 2.25 mg iron

60 ml 'maple syrup' = 54 g carbs + 0.15 mg copper

1 large egg weighs 50 g = 4.8 g fat + 6.3 g protein + 0.4 g carbs + 71 mg sodium

# Conveniently define new units for foods
1 loaf 'factory white bread' = 20 slice
1 tbsp 'maple syrup' = 15 ml

# Define recipes made up of various foods
1 x 'french toast bake' weighs 1.2 kg:
- 1/2 loaf 'factory white bread'
- 8 large egg

# Log what you eat
1 x '2025-01-18':
- 1/2 x 'french toast bake' + 4 tbsp 'maple syrup'

print 1 x '2025-01-18'

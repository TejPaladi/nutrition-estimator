# References and Method Notes

## FSA

The FSA-style score is based on traffic-light thresholds for:

- sugar
- salt, or sodium converted to salt
- fat
- saturated fat

Each nutrient receives:

- `1`: green / healthier range
- `2`: amber / medium range
- `3`: red / less healthy range

The item score is:

```text
FSA = sugar_score + salt_score + fat_score + saturated_fat_score
```

Range:

```text
4 to 12
```

Direction:

```text
lower is healthier
```

Sodium conversion:

```text
salt_g = sodium_mg * 2.5 / 1000
```

## WHO

The WHO-style score checks seven nutrients:

- protein
- carbohydrates
- sugar
- sodium
- fat
- saturated fat
- fiber

Each satisfied condition receives one point:

```text
WHO = protein_ok + carbs_ok + sugar_ok + sodium_ok
    + fat_ok + saturated_fat_ok + fiber_ok
```

Range:

```text
0 to 7
```

Direction:

```text
higher is healthier
```

## Meal Aggregation

MealRec+ computes healthiness at the course/item level first. Meal-level
healthiness is then the mean score of the courses/items in the meal:

```text
meal_fsa = mean(item_fsa scores)
meal_who = mean(item_who scores)
```

This package follows that structure.

## Missing Data Policy

The default policy is:

```text
default = "no-guess"
```

If a required nutrient is missing, the estimator returns:

```text
status = "insufficient_data"
estimated_value = None
missing_fields = [...]
```


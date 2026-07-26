# References and Method Notes

This package is designed for transparent recommendation experiments. It does
not hide missing nutrition data or call a black-box scoring service. The score
formulas and thresholds are documented here so another project can reproduce or
replace them.

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

Threshold source notes:

- NHS food-label guidance lists high/low thresholds for total fat, saturated
  fat, sugars, and salt: https://www.nhs.uk/live-well/eat-well/food-guidelines-and-food-labels/how-to-read-food-labels/
- GOV.UK explains front-of-pack traffic-light labeling for fat, saturates,
  sugar, salt, and energy: https://www.gov.uk/government/publications/check-the-label/check-the-label

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

Method note:

The WHO score here is a transparent WHO-style nutrient-range score for
recommendation experiments. WHO publishes healthy-diet guidance for nutrients
such as sugars, sodium/salt, fats, saturated fats, carbohydrates, protein, and
fiber. This package converts those nutrient dimensions into explicit binary
checks so the output is reproducible. If a project needs a different WHO or
regional nutrient profile model, it should be added as a separate method.

Relevant WHO sources:

- WHO healthy diet fact sheet: https://www.who.int/news-room/fact-sheets/detail/healthy-diet
- WHO technical report, *Diet, Nutrition and the Prevention of Chronic
  Diseases*: https://www.who.int/publications/i/item/924120916X

## Meal Aggregation

MealRec+ computes healthiness at the course/item level first. Meal-level
healthiness is then the mean score of the courses/items in the meal:

```text
meal_fsa = mean(item_fsa scores)
meal_who = mean(item_who scores)
```

This package follows that structure.

MealRec+ sources:

- Paper: Ming Li, Lin Li, Xiaohui Tao, and Jimmy Xiangji Huang. 2024.
  *MealRec+: A Meal Recommendation Dataset with Meal-Course Affiliation for
  Personalization and Healthiness.* SIGIR 2024. https://arxiv.org/abs/2404.05386
- Dataset repository: https://github.com/WUT-IDEA/MealRecPlus

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

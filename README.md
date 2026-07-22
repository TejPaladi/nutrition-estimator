# Nutrition Estimator

A small Python package for reproducible food and meal healthiness scoring.

The package currently supports:

- `fsa`: traffic-light style score using sugar, sodium/salt, fat, and saturated fat.
- `who`: nutrient-range score using protein, carbohydrates, sugar, sodium, fat, saturated fat, fiber, and calories.
- `all`: compute both FSA and WHO.

The default missing-data behavior is `no-guess`: if required nutrients are missing,
the package returns an insufficient-data result instead of inventing values.

## Local Setup

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Then run:

```bash
python examples/dunkin_example.py
python -m unittest discover -s tests -v
```

For VS Code notebooks, select the Python interpreter from:

```text
.venv/bin/python
```

## Quick Example

```python
from nutrition_estimator import estimate_food, estimate_meal

item = {
    "name": "Dunkin Omelet Bites",
    "nutrition": {
        "calories": 180,
        "protein_g": 13,
        "carbs_g": 7,
        "sugar_g": 2,
        "sodium_mg": 460,
        "fat_g": 11,
        "saturated_fat_g": 5,
        "fiber_g": 1,
    },
}

print(estimate_food(item, estimation_method="fsa"))
print(estimate_food(item, estimation_method="who"))
```

Meal-level scoring follows the MealRec+ style: score each item/course first,
then average the available item/course scores.

```python
meal = estimate_meal([item_1, item_2, item_3], estimation_method="all")
```

## Score Ranges

| Method | Range | Direction |
|---|---:|---|
| FSA | 4 to 12 | lower is healthier |
| WHO | 0 to 7 | higher is healthier |

## Notes

FSA traffic-light thresholds are commonly defined per 100g or 100ml. Many
restaurant and recipe datasets, including the data we use in the Beacon app,
provide nutrition per serving. This package therefore labels the score basis in
the output and supports the values exactly as provided by default.

For stricter FSA-style normalization, pass `basis="per_100g"` and include
`serving_size_g` in the item.

## References

- MealRec+: A Meal Recommendation Dataset with Meal-Course Affiliation for Personalization and Healthiness. SIGIR 2024.
- UK traffic-light nutrition labeling guidance for fat, saturated fat, sugars, and salt.
- World Health Organization nutrition guidance for sugar, sodium, fats, saturated fats, protein, carbohydrates, and fiber.

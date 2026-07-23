# Nutrition Estimator

A small Python package for reproducible food and meal healthiness scoring.

The package currently supports:

- `fsa`: traffic-light style score using sugar, sodium/salt, fat, and saturated fat.
- `who`: nutrient-range score using protein, carbohydrates, sugar, sodium, fat, saturated fat, fiber, and calories.
- `all`: compute both FSA and WHO.

The default missing-data behavior is `no-guess`: if required nutrients are missing,
the package returns an insufficient-data result instead of inventing values.

## Repository Structure

```text
nutrition-estimator/
  README.md
  pyproject.toml
  src/
    nutrition_estimator/
      __init__.py
      estimator.py
      fsa.py
      who.py
      nutrients.py
  examples/
    dunkin_example.py
  notebooks/
    01_fsa_who_examples.ipynb
    README.md
  references/
    README.md
  tests/
    test_estimator.py
```

| Path | Purpose |
|---|---|
| `src/nutrition_estimator/estimator.py` | Main public API: `estimate_food(...)` and `estimate_meal(...)`. |
| `src/nutrition_estimator/fsa.py` | FSA traffic-light scoring logic and component breakdown. |
| `src/nutrition_estimator/who.py` | WHO-style nutrient-range scoring logic and component breakdown. |
| `src/nutrition_estimator/nutrients.py` | Nutrient parsing helpers, aliases, sodium-to-salt conversion, and optional basis normalization. |
| `examples/dunkin_example.py` | Small runnable example using restaurant-style nutrition fields. |
| `notebooks/` | Presentation-friendly examples for explaining FSA, WHO, and meal aggregation. |
| `references/README.md` | Method notes, formulas, score ranges, and missing-data policy. |
| `tests/test_estimator.py` | Unit tests for food scoring, meal aggregation, and missing-field behavior. |
| `pyproject.toml` | Python packaging configuration. |

## How The Code Is Written

The package is intentionally split into small modules:

1. `nutrients.py` reads nutrient values from flexible item dictionaries.
   It supports common aliases such as `sugar_g`, `Sugar`, `sodium_mg`, and
   `Sodium`.
2. `fsa.py` calculates the FSA score from sugar, sodium/salt, fat, and
   saturated fat.
3. `who.py` calculates a WHO-style score from seven nutrient checks.
4. `estimator.py` combines these methods into user-facing functions for food
   items and full meals.

The main design rule is:

```text
no required nutrient -> no guessed score
```

By default, missing fields return:

```python
{
    "estimated_value": None,
    "status": "insufficient_data",
    "missing_fields": [...]
}
```

This makes the package safer for research use because incomplete nutrition data
does not silently become a fake healthiness score.

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

## Input Format

Each food item should be a dictionary with a `name` and a `nutrition` block:

```python
item = {
    "name": "Example Food",
    "nutrition": {
        "calories": 250,
        "protein_g": 10,
        "carbs_g": 35,
        "sugar_g": 8,
        "sodium_mg": 420,
        "fat_g": 9,
        "saturated_fat_g": 3,
        "fiber_g": 2,
    },
}
```

The package also accepts several common aliases, including `Sugar`, `Sodium`,
`Fat`, `Saturated Fat`, `Protein`, `Carbohydrates`, and `Fiber`.

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

## Adapting This To Another Project

There are two simple ways to use this package.

### Option 1: Install From GitHub

```bash
python -m pip install git+https://github.com/TejPaladi/nutrition-estimator.git
```

Then import it:

```python
from nutrition_estimator import estimate_food, estimate_meal
```

### Option 2: Install Locally In Editable Mode

Clone the repo and install:

```bash
git clone https://github.com/TejPaladi/nutrition-estimator.git
cd nutrition-estimator
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Editable mode is useful during research because changes to the package code are
immediately available without reinstalling.

## Example Integration

For a recommendation system, the typical flow is:

```text
recommended items -> estimate item scores -> estimate meal score -> show FSA/WHO
```

Example:

```python
from nutrition_estimator import estimate_meal

recommended_meal = [
    {
        "name": "Omelet Bites",
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
    },
    {
        "name": "Iced Coffee",
        "nutrition": {
            "calories": 158,
            "protein_g": 1,
            "carbs_g": 29,
            "sugar_g": 33,
            "sodium_mg": 98,
            "fat_g": 3,
            "saturated_fat_g": 2,
            "fiber_g": 0,
        },
    },
]

result = estimate_meal(recommended_meal, estimation_method="all")
print(result["total"])
```

Output shape:

```python
{
    "fsa": {
        "meal_score": 7.0,
        "aggregation": "mean_of_item_scores",
        "range": "4-12",
        "direction": "lower_is_healthier",
    },
    "who": {
        "meal_score": 3.5,
        "aggregation": "mean_of_item_scores",
        "range": "0-7",
        "direction": "higher_is_healthier",
    },
}
```

## How To Extend

To add a new method such as `nutriscore`:

1. Create a new file such as `src/nutrition_estimator/nutriscore.py`.
2. Implement a function that returns the same result shape:

```python
{
    "estimated_value": ...,
    "status": "estimated",
    "estimation_method": "nutriscore",
    "range": "...",
    "direction": "...",
    "components": {...},
    "missing_fields": [],
}
```

3. Add the method routing in `estimator.py`.
4. Add unit tests in `tests/test_estimator.py`.
5. Add an example in `examples/` or `notebooks/`.

Keeping the result shape consistent makes it easy for another app to display
different nutrition scores in the same UI.

## References

- MealRec+: A Meal Recommendation Dataset with Meal-Course Affiliation for Personalization and Healthiness. SIGIR 2024.
- UK traffic-light nutrition labeling guidance for fat, saturated fat, sugars, and salt.
- World Health Organization nutrition guidance for sugar, sodium, fats, saturated fats, protein, carbohydrates, and fiber.

"""Helpers for reading nutrition values from flexible food dictionaries.

The package accepts a compact project-friendly schema such as
`nutrition["sugar_g"]`, but it also handles common labels like `"Sugar"` or
`"Saturated Fat"` from scraped restaurant/menu data.
"""

from __future__ import annotations

import re
from typing import Any


NUTRIENT_ALIASES: dict[str, list[str]] = {
    "calories": ["calories", "Calories", "energy_kcal", "kcal"],
    "protein_g": ["protein_g", "protein", "Protein"],
    "carbs_g": ["carbs_g", "carbohydrates_g", "carbs", "Carbohydrates"],
    "sugar_g": ["sugar_g", "sugars_g", "sugar", "Sugar", "Sugars"],
    "sodium_mg": ["sodium_mg", "sodium", "Sodium"],
    "salt_g": ["salt_g", "salt", "Salt"],
    "fat_g": ["fat_g", "total_fat_g", "fat", "Fat", "Total Fat"],
    "saturated_fat_g": [
        "saturated_fat_g",
        "saturated_fat",
        "Saturated Fat",
        "Saturates",
    ],
    "fiber_g": ["fiber_g", "dietary_fiber_g", "fiber", "Fiber", "Dietary Fiber"],
    "serving_size_g": ["serving_size_g", "serving_g", "Serving Size"],
}


def item_name(item: dict[str, Any]) -> str | None:
    """Return a readable item identifier when one is provided."""
    value = item.get("name") or item.get("recipe_name") or item.get("id")
    return str(value) if value not in (None, "") else None


def nutrition_block(item_or_nutrition: dict[str, Any] | None) -> dict[str, Any]:
    """Return the nested nutrition/macronutrient block, or the input itself."""
    if not isinstance(item_or_nutrition, dict):
        return {}
    if "nutrition" in item_or_nutrition and isinstance(
        item_or_nutrition["nutrition"], dict
    ):
        return item_or_nutrition["nutrition"]
    if "macronutrients" in item_or_nutrition and isinstance(
        item_or_nutrition["macronutrients"], dict
    ):
        return item_or_nutrition["macronutrients"]
    return item_or_nutrition


def nutrient_number(nutrition: dict[str, Any] | None, canonical_key: str) -> float | None:
    """Extract a nutrient as a float using the known aliases for that nutrient."""
    nutrition = nutrition_block(nutrition)
    for key in NUTRIENT_ALIASES.get(canonical_key, [canonical_key]):
        if key not in nutrition:
            continue
        value = nutrition[key]
        if isinstance(value, dict):
            value = value.get("measure")
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r"-?\d+(?:\.\d+)?", str(value))
        return float(match.group(0)) if match else None
    return None


def sodium_to_salt_g(sodium_mg: float) -> float:
    """Convert sodium in milligrams to salt in grams."""
    return sodium_mg * 2.5 / 1000


def value_for_basis(
    value: float | None,
    serving_size_g: float | None,
    basis: str,
) -> float | None:
    """Use a nutrient as provided or normalize it to a per-100g basis."""
    if value is None:
        return None
    if basis == "provided":
        return value
    if basis == "per_100g":
        if not serving_size_g or serving_size_g <= 0:
            return None
        return value * 100 / serving_size_g
    raise ValueError("basis must be 'provided' or 'per_100g'")

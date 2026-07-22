from __future__ import annotations

from typing import Any

from .nutrients import nutrient_number


WHO_METHOD = (
    "WHO-style nutrient-range score from protein, carbohydrates, sugar, sodium, "
    "fat, saturated fat, and fiber"
)
WHO_RANGE = "0-7"
WHO_DIRECTION = "higher_is_healthier"


def calculate_who(
    item_or_nutrition: dict[str, Any] | None,
    *,
    default: str = "no-guess",
    basis: str = "provided",
) -> dict[str, Any]:
    """Calculate a WHO-style 0-7 nutrient-range score.

    The current implementation is designed for transparent recommendation
    experiments. It checks seven nutrient conditions and returns one point for
    each satisfied condition.
    """
    if default != "no-guess":
        raise ValueError("Only default='no-guess' is supported in v0.1.")
    if basis != "provided":
        raise ValueError("WHO scoring currently supports basis='provided'.")

    calories = nutrient_number(item_or_nutrition, "calories")
    protein = nutrient_number(item_or_nutrition, "protein_g")
    carbs = nutrient_number(item_or_nutrition, "carbs_g")
    sugar = nutrient_number(item_or_nutrition, "sugar_g")
    sodium = nutrient_number(item_or_nutrition, "sodium_mg")
    fat = nutrient_number(item_or_nutrition, "fat_g")
    saturated_fat = nutrient_number(item_or_nutrition, "saturated_fat_g")
    fiber = nutrient_number(item_or_nutrition, "fiber_g")

    required = {
        "calories": calories,
        "protein_g": protein,
        "carbs_g": carbs,
        "sugar_g": sugar,
        "sodium_mg": sodium,
        "fat_g": fat,
        "saturated_fat_g": saturated_fat,
        "fiber_g": fiber,
    }
    missing_fields = [field for field, value in required.items() if value is None]
    if missing_fields:
        return {
            "estimated_value": None,
            "total": None,
            "status": "insufficient_data",
            "estimation_method": "who",
            "method": WHO_METHOD,
            "range": WHO_RANGE,
            "direction": WHO_DIRECTION,
            "basis": basis,
            "missing_fields": missing_fields,
            "components": {},
        }

    fat_energy_share = fat * 9 / calories if calories > 0 else 1
    saturated_fat_energy_share = saturated_fat * 9 / calories if calories > 0 else 1

    components = {
        "protein": int(protein >= 5),
        "carbohydrates": int(0 <= carbs <= 75),
        "sugar": int(sugar <= 25),
        "sodium": int(sodium <= 600),
        "fat": int(fat_energy_share < 0.30),
        "saturated_fat": int(saturated_fat_energy_share < 0.10),
        "fiber": int(fiber >= 3),
    }
    total = sum(components.values())
    return {
        "estimated_value": total,
        "total": total,
        "status": "estimated",
        "estimation_method": "who",
        "method": WHO_METHOD,
        "range": WHO_RANGE,
        "direction": WHO_DIRECTION,
        "basis": basis,
        "missing_fields": [],
        "components": components,
        "normalized_inputs": {
            "calories": round(calories, 3),
            "protein_g": round(protein, 3),
            "carbs_g": round(carbs, 3),
            "sugar_g": round(sugar, 3),
            "sodium_mg": round(sodium, 3),
            "fat_g": round(fat, 3),
            "saturated_fat_g": round(saturated_fat, 3),
            "fiber_g": round(fiber, 3),
            "fat_energy_share": round(fat_energy_share, 3),
            "saturated_fat_energy_share": round(saturated_fat_energy_share, 3),
        },
    }


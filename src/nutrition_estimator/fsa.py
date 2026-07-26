"""FSA-style traffic-light scoring.

The FSA-style score uses four nutrition components: sugar, salt, fat, and
saturated fat. Each component is mapped to a traffic-light value:

- green = 1
- amber = 2
- red = 3

The final range is 4-12, where lower is healthier.
"""

from __future__ import annotations

from typing import Any

from .nutrients import nutrient_number, sodium_to_salt_g, value_for_basis


FSA_METHOD = "FSA traffic-light score from sugar, sodium/salt, fat, and saturated fat"
FSA_RANGE = "4-12"
FSA_DIRECTION = "lower_is_healthier"


def _traffic_light_score(value: float, low: float, high: float) -> int:
    """Map a nutrient amount to green/amber/red numeric traffic-light score."""
    if value <= low:
        return 1
    if value > high:
        return 3
    return 2


def calculate_fsa(
    item_or_nutrition: dict[str, Any] | None,
    *,
    default: str = "no-guess",
    basis: str = "provided",
) -> dict[str, Any]:
    """Calculate an FSA-style traffic-light score.

    `basis="provided"` uses nutrients exactly as supplied. `basis="per_100g"`
    normalizes gram and milligram nutrient values using `serving_size_g`.

    Required fields are sugar, fat, saturated fat, and either sodium or salt.
    Sodium is converted to salt using `salt_g = sodium_mg * 2.5 / 1000`.
    Missing data returns `status="insufficient_data"` and no guessed score.
    """
    if default != "no-guess":
        raise ValueError("Only default='no-guess' is supported in v0.1.")

    serving_size_g = nutrient_number(item_or_nutrition, "serving_size_g")
    sugar = value_for_basis(
        nutrient_number(item_or_nutrition, "sugar_g"), serving_size_g, basis
    )
    sodium = value_for_basis(
        nutrient_number(item_or_nutrition, "sodium_mg"), serving_size_g, basis
    )
    salt = value_for_basis(
        nutrient_number(item_or_nutrition, "salt_g"), serving_size_g, basis
    )
    fat = value_for_basis(
        nutrient_number(item_or_nutrition, "fat_g"), serving_size_g, basis
    )
    saturated_fat = value_for_basis(
        nutrient_number(item_or_nutrition, "saturated_fat_g"), serving_size_g, basis
    )

    salt_g = salt
    if salt_g is None and sodium is not None:
        salt_g = sodium_to_salt_g(sodium)

    required = {
        "sugar_g": sugar,
        "sodium_mg_or_salt_g": salt_g,
        "fat_g": fat,
        "saturated_fat_g": saturated_fat,
    }
    missing_fields = [field for field, value in required.items() if value is None]
    if basis == "per_100g" and not serving_size_g:
        missing_fields.append("serving_size_g")

    if missing_fields:
        return {
            "estimated_value": None,
            "total": None,
            "status": "insufficient_data",
            "estimation_method": "fsa",
            "method": FSA_METHOD,
            "range": FSA_RANGE,
            "direction": FSA_DIRECTION,
            "basis": basis,
            "missing_fields": sorted(set(missing_fields)),
            "components": {},
        }

    components = {
        "sugar": _traffic_light_score(sugar, 5, 22.5),
        "salt": _traffic_light_score(salt_g, 0.3, 1.5),
        "fat": _traffic_light_score(fat, 3, 17.5),
        "saturated_fat": _traffic_light_score(saturated_fat, 1.5, 5),
    }
    total = sum(components.values())
    return {
        "estimated_value": total,
        "total": total,
        "status": "estimated",
        "estimation_method": "fsa",
        "method": FSA_METHOD,
        "range": FSA_RANGE,
        "direction": FSA_DIRECTION,
        "basis": basis,
        "missing_fields": [],
        "components": components,
        "normalized_inputs": {
            "sugar_g": round(sugar, 3),
            "salt_g": round(salt_g, 3),
            "fat_g": round(fat, 3),
            "saturated_fat_g": round(saturated_fat, 3),
        },
    }

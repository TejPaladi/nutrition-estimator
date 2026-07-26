"""Public estimation API for food-item and meal-level nutrition scores.

Most users should start here instead of calling `calculate_fsa` or
`calculate_who` directly. The estimator functions return compact output by
default and expose detailed formula traces only when `verbose=True`.
"""

from __future__ import annotations

from typing import Any, Iterable

from .fsa import calculate_fsa
from .nutrients import item_name
from .who import calculate_who


def estimate_food(
    item: dict[str, Any],
    *,
    estimation_method: str = "fsa",
    default: str = "no-guess",
    basis: str = "provided",
    verbose: bool = False,
) -> dict[str, Any]:
    """Estimate healthiness for a single food item.

    Parameters
    ----------
    item:
        Food item dictionary. `nutrition` is required; `name` is optional.
    estimation_method:
        `"fsa"`, `"who"`, or `"all"`.
    default:
        Missing-data policy. Currently only `"no-guess"` is supported.
    basis:
        `"provided"` uses nutrient values as supplied. `"per_100g"` is
        supported for FSA when `serving_size_g` is available.
    verbose:
        When false, return compact output for apps and simple notebooks. When
        true, include method text, component scores, normalized inputs, and
        missing-field details.
    """
    method = estimation_method.lower()
    if method == "fsa":
        result = calculate_fsa(item, default=default, basis=basis)
    elif method == "who":
        result = calculate_who(item, default=default, basis=basis)
    elif method == "all":
        return {
            "item": item_name(item),
            "estimation_method": "all",
            "status": "estimated",
            "scores": {
                "fsa": _format_food_result(
                    calculate_fsa(item, default=default, basis=basis),
                    verbose=verbose,
                ),
                "who": _format_food_result(
                    calculate_who(item, default=default, basis="provided"),
                    verbose=verbose,
                ),
            },
        }
    else:
        raise ValueError("estimation_method must be 'fsa', 'who', or 'all'")

    return {
        "item": item_name(item),
        **_format_food_result(result, verbose=verbose),
    }


def estimate_meal(
    items: Iterable[dict[str, Any]],
    *,
    estimation_method: str = "fsa",
    default: str = "no-guess",
    basis: str = "provided",
    verbose: bool = False,
) -> dict[str, Any]:
    """Estimate healthiness for a meal by averaging item-level scores.

    This mirrors the MealRec+ aggregation idea: calculate healthiness at the
    item/course level first, then average item scores into a meal score.
    """
    item_list = list(items)
    method = estimation_method.lower()
    if method == "all":
        return {
            "estimation_method": "all",
            "items": [
                estimate_food(
                    item,
                    estimation_method="all",
                    default=default,
                    basis=basis,
                    verbose=verbose,
                )
                for item in item_list
            ],
            "total": {
                "fsa": _aggregate_method(item_list, "fsa", default, basis),
                "who": _aggregate_method(item_list, "who", default, "provided"),
            },
        }
    if method not in {"fsa", "who"}:
        raise ValueError("estimation_method must be 'fsa', 'who', or 'all'")

    item_results = [
        estimate_food(
            item,
            estimation_method=method,
            default=default,
            basis=basis,
            verbose=verbose,
        )
        for item in item_list
    ]
    return {
        "estimation_method": method,
        "items": item_results,
        "total": _aggregate_results(item_results, method),
    }


def _aggregate_method(
    items: list[dict[str, Any]],
    method: str,
    default: str,
    basis: str,
) -> dict[str, Any]:
    """Run one method across meal items and aggregate the resulting scores."""
    item_results = [
        estimate_food(item, estimation_method=method, default=default, basis=basis)
        for item in items
    ]
    return _aggregate_results(item_results, method)


def _format_food_result(result: dict[str, Any], *, verbose: bool) -> dict[str, Any]:
    """Return either compact public output or a full explanatory result."""
    required_keys = [
        "estimation_method",
        "estimated_value",
        "range",
        "direction",
        "status",
    ]
    compact = {key: result.get(key) for key in required_keys}
    if result.get("status") != "estimated":
        compact["missing_fields"] = result.get("missing_fields", [])
    if verbose:
        for key, value in result.items():
            compact.setdefault(key, value)
    return compact


def _aggregate_results(item_results: list[dict[str, Any]], method: str) -> dict[str, Any]:
    """Average available item scores and preserve missing-item information."""
    values = [
        float(result["estimated_value"])
        for result in item_results
        if isinstance(result.get("estimated_value"), (int, float))
    ]
    missing_items = [
        {
            "item": result.get("item"),
            "missing_fields": result.get("missing_fields", []),
        }
        for result in item_results
        if not isinstance(result.get("estimated_value"), (int, float))
    ]
    if not values:
        return {
            "meal_score": None,
            "status": "insufficient_data",
            "aggregation": "mean_of_item_scores",
            "item_scores_used": 0,
            "missing_items": missing_items,
            "range": "4-12" if method == "fsa" else "0-7",
            "direction": "lower_is_healthier" if method == "fsa" else "higher_is_healthier",
        }
    return {
        "meal_score": round(sum(values) / len(values), 3),
        "status": "estimated" if not missing_items else "partial",
        "aggregation": "mean_of_item_scores",
        "item_scores_used": len(values),
        "missing_items": missing_items,
        "range": "4-12" if method == "fsa" else "0-7",
        "direction": "lower_is_healthier" if method == "fsa" else "higher_is_healthier",
    }

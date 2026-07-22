from nutrition_estimator import estimate_food, estimate_meal


OMELET_BITES = {
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

SNACKIN_BACON = {
    "name": "Dunkin Snackin Bacon",
    "nutrition": {
        "calories": 272,
        "protein_g": 7,
        "carbs_g": 10,
        "sugar_g": 10.4,
        "sodium_mg": 378,
        "fat_g": 23,
        "saturated_fat_g": 8,
        "fiber_g": 0.1,
    },
}

ICED_COFFEE = {
    "name": "Dunkin Iced Coffee",
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
}


if __name__ == "__main__":
    print("Single item FSA:")
    print(estimate_food(OMELET_BITES, estimation_method="fsa"))
    print()

    print("Single item WHO:")
    print(estimate_food(OMELET_BITES, estimation_method="who"))
    print()

    print("Meal FSA and WHO:")
    print(
        estimate_meal(
            [OMELET_BITES, SNACKIN_BACON, ICED_COFFEE],
            estimation_method="all",
        )
    )


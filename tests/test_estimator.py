import unittest

from nutrition_estimator import calculate_fsa, calculate_who, estimate_food, estimate_meal


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


class NutritionEstimatorTests(unittest.TestCase):
    def test_fsa_scores_components_and_total(self):
        result = calculate_fsa(OMELET_BITES)

        self.assertEqual(result["estimated_value"], 7)
        self.assertEqual(result["range"], "4-12")
        self.assertEqual(result["direction"], "lower_is_healthier")
        self.assertEqual(
            result["components"],
            {"sugar": 1, "salt": 2, "fat": 2, "saturated_fat": 2},
        )

    def test_who_scores_components_and_total(self):
        result = calculate_who(OMELET_BITES)

        self.assertEqual(result["estimated_value"], 4)
        self.assertEqual(result["range"], "0-7")
        self.assertEqual(result["direction"], "higher_is_healthier")
        self.assertEqual(
            result["components"],
            {
                "protein": 1,
                "carbohydrates": 1,
                "sugar": 1,
                "sodium": 1,
                "fat": 0,
                "saturated_fat": 0,
                "fiber": 0,
            },
        )

    def test_no_guess_reports_missing_fields(self):
        result = estimate_food(
            {"name": "Incomplete Item", "nutrition": {"sugar_g": 3}},
            estimation_method="fsa",
        )

        self.assertIsNone(result["estimated_value"])
        self.assertEqual(result["status"], "insufficient_data")
        self.assertIn("fat_g", result["missing_fields"])
        self.assertIn("saturated_fat_g", result["missing_fields"])

    def test_meal_averages_item_scores(self):
        meal = estimate_meal(
            [
                OMELET_BITES,
                {
                    "name": "Snackin Bacon",
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
                },
            ],
            estimation_method="fsa",
        )

        self.assertEqual(meal["total"]["meal_score"], 8.5)
        self.assertEqual(meal["total"]["aggregation"], "mean_of_item_scores")
        self.assertEqual(meal["total"]["item_scores_used"], 2)


if __name__ == "__main__":
    unittest.main()


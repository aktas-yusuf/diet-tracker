# recommendations/services.py
"""
Yemek önerisi ve API işlemlerini yöneten servis fonksiyonları.
"""
from .utils import (
    calculate_daily_calorie_need,
    get_meal_recommendations,
    calculate_bmi,
    get_nutrition_advice,
    calculate_macro_ratios,
)


def build_meal_plan_for_user(user):
    """Kullanıcı için yemek planı ve özet bilgileri döndürür."""
    if not all([user.age, user.weight, user.height, user.gender, user.activity_level]):
        return None, None, None, None, None
    daily_calories = calculate_daily_calorie_need(
        user.age, user.weight, user.height, user.gender, user.activity_level
    )
    meals = get_meal_recommendations(daily_calories, user)
    total_calories = sum(m.get('calories', 0) if isinstance(m, dict) else m.calories for m in meals)
    bmi, bmi_category = calculate_bmi(user.weight, user.height)
    macro_ratios = calculate_macro_ratios(meals)
    nutrition_advice = get_nutrition_advice(user, daily_calories)
    return meals, total_calories, daily_calories, bmi, {
        'bmi_category': bmi_category,
        'macro_ratios': macro_ratios,
        'nutrition_advice': nutrition_advice
    }

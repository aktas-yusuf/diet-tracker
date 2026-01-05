from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Recommendation
from .services import build_meal_plan_for_user
from .constants import ERR_PROFILE_INCOMPLETE, ERR_SYSTEM

@login_required
def get_recommendation(request):
    user = request.user
   
    

    # Profil kontrolü
    if not all([user.age, user.weight, user.height, user.gender, user.activity_level]):
        messages.warning(request, ERR_PROFILE_INCOMPLETE)
        return render(request, "recommendations/recommendation.html", {
            "meals": [], "total_calories": 0, "target": 0,
            "error": ERR_PROFILE_INCOMPLETE,
            "macro_ratios": {}, "nutrition_advice": []
        })
    
    try:
        # Yemek planı ve özet bilgileri servis katmanından al
        meals, total_calories, daily_need, bmi, extra = build_meal_plan_for_user(user)
        if not meals:
            # Senaryo tabanlı hata mesajı oluştur
            scenario_msgs = []
            if user.weight and user.weight > 130:
                scenario_msgs.append("Kilonuz çok yüksek olduğu için API'den uygun yemek önerisi bulunamadı. Daha düşük kalori hedefi veya daha fazla öğün eklemeyi deneyin.")
            if user.age and user.age > 65:
                scenario_msgs.append("Yaşınız yüksek olduğu için önerilerde kısıtlılık olabilir. Daha fazla sebze ve protein eklemeyi düşünebilirsiniz.")
            if user.activity_level == 'high':
                scenario_msgs.append("Yüksek aktivite seviyesi için API'den yeterli kaloriye sahip yemek bulunamadı. Aktivite seviyenizi 'Orta' olarak güncelleyip tekrar deneyin.")
            if not scenario_msgs:
                scenario_msgs.append("API'den uygun yemek önerisi alınamadı. Profil bilgilerinizi gözden geçirin veya daha farklı bir kombinasyon deneyin.")
            error_message = "<br>".join(scenario_msgs)
            messages.warning(request, error_message)
            return render(request, "recommendations/recommendation.html", {
                "meals": [], "total_calories": 0, "target": round(daily_need or 0, 0),
                "error": error_message,
                "macro_ratios": {}, "nutrition_advice": []
            })
        # Öneriyi kaydet
        recommendation = Recommendation.objects.create(user=user, total_calories=total_calories)
        for meal in meals:
            if isinstance(meal, dict):
                from .models import RecommendedMeal
                meal_obj, _ = RecommendedMeal.objects.get_or_create(
                    name=meal['name'],
                    defaults={
                        'calories': meal['calories'],
                        'protein': meal['protein'],
                        'carbs': meal['carbs'],
                        'fat': meal['fat']
                    }
                )
                recommendation.recommended_meals.add(meal_obj)
        return render(request, "recommendations/recommendation.html", {
            "meals": meals,
            "total_calories": total_calories,
            "target": round(daily_need, 0),
            "user_info": {
                "age": user.age,
                "weight": user.weight,
                "height": user.height,
                "gender": user.get_gender_display() if user.gender else "Belirtilmemiş",
                "activity_level": user.get_activity_level_display() if user.activity_level else "Belirtilmemiş",
                "bmi": bmi,
                "bmi_category": extra['bmi_category'] if extra else ""
            },
            "macro_ratios": extra['macro_ratios'] if extra else {},
            "nutrition_advice": extra['nutrition_advice'] if extra else [],
            "calorie_difference": round((daily_need or 0) - (total_calories or 0), 0)
        })
    except Exception as e:
        messages.error(request, ERR_SYSTEM)
        return render(request, "recommendations/recommendation.html", {
            "meals": [], "total_calories": 0, "target": 0,
            "error": ERR_SYSTEM,
            "macro_ratios": {}, "nutrition_advice": []
        })

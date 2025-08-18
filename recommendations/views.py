from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Recommendation
from .utils import generate_meal_plan, calculate_daily_calorie_need, get_nutrition_advice, calculate_macro_ratios

@login_required
def get_recommendation(request):
    
    user = request.user
    
    try:
       
        if not all([user.age, user.weight, user.height, user.gender, user.activity_level]):
            messages.warning(request, "Profil bilgilerinizi tamamlayın (yaş, kilo, boy, cinsiyet, aktivite seviyesi)")
            return render(request, "recommendations/recommendation.html", {
                "meals": [],
                "total_calories": 0,
                "target": 0,
                "error": "Profil bilgileri eksik",
                "macro_ratios": {}, 
                "nutrition_advice": []
            })
        
        
        meals, total_calories, daily_need = generate_meal_plan(user)
        
        
        if not meals:
            messages.warning(request, "API'den yemek önerileri alınamadı. Lütfen daha sonra tekrar deneyin.")
            return render(request, "recommendations/recommendation.html", {
                "meals": [],
                "total_calories": 0,
                "target": 0,
                "error": "API'den yemek önerileri alınamadı",
                "macro_ratios": {},
                "nutrition_advice": []
            })
        
        
        macro_ratios = calculate_macro_ratios(meals)
        
        
        nutrition_advice = get_nutrition_advice(user, daily_need)
        
        recommendation = Recommendation.objects.create(
            user=user,
            total_calories=total_calories
        )

        
        bmi = user.weight / ((user.height / 100) ** 2)
        bmi_category = "Normal"
        if bmi < 18.5:
            bmi_category = "Zayıf"
        elif bmi < 25:
            bmi_category = "Normal"
        elif bmi < 30:
            bmi_category = "Fazla Kilolu"
        else:
            bmi_category = "Obez"

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
                "bmi": round(bmi, 1),
                "bmi_category": bmi_category
            },
            "macro_ratios": macro_ratios,
            "nutrition_advice": nutrition_advice,
            "calorie_difference": round(daily_need - total_calories, 0)
        })
        
    except Exception as e:
        messages.error(request, f"Öneri oluşturulurken hata oluştu: {str(e)}")
        return render(request, "recommendations/recommendation.html", {
            "meals": [],
            "total_calories": 0,
            "target": 0,
            "error": "Sistem hatası",
            "macro_ratios": {},
            "nutrition_advice": []
        })

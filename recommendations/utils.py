import requests
import json
import re
from django.conf import settings
from django.core.cache import cache

def calculate_daily_calorie_need(age, weight, height, gender, activity_level):
    gender_normalized = None
    if isinstance(gender, str):
        g = gender.strip().lower()
        if g in ['m', 'male', 'erkek']:
            gender_normalized = 'male'
        elif g in ['f', 'female', 'kadın', 'kadin']:
            gender_normalized = 'female'
        else:
            gender_normalized = 'other'
    else:
        gender_normalized = 'other'

    # Mifflin-St Jeor formülü (BMR hesaplama)
    if gender_normalized == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Aktivite seviyesi çarpanları
    activity_multipliers = {
        'low': 1.2,      
        'medium': 1.55,  
        'high': 1.9      
    }

    multiplier = activity_multipliers.get(activity_level, 1.2)
    daily_calories = bmr * multiplier
    
    return round(daily_calories, 0)


def clean_cache_key(key):
    
    key = re.sub(r'[^a-zA-Z0-9_]', '_', key)
    key = re.sub(r'_+', '_', key)
    return key


def save_api_meal_to_db(meal_data):
    from .models import RecommendedMeal
    
    try:
        
        existing_meal = RecommendedMeal.objects.filter(name=meal_data['name']).first()
        if existing_meal:
            return existing_meal
        
        
        new_meal = RecommendedMeal.objects.create(
            name=meal_data['name'],
            calories=meal_data['calories'],
            protein=meal_data['protein'],
            carbs=meal_data['carbs'],
            fat=meal_data['fat']
        )
        return new_meal
    except Exception as e:
        print(f"Yemek kaydetme hatası: {e}")
        return None


def search_food_api(query, min_calories=None, max_calories=None):
    """Edamam Food Database API'den yemek arama"""
    from django.conf import settings
    
    
    APP_ID = getattr(settings, 'EDAMAM_APP_ID', '')
    APP_KEY = getattr(settings, 'EDAMAM_APP_KEY', '')
    
    
    if not APP_ID or not APP_KEY or APP_ID == 'your_app_id_here':
        return []
    
    
    cache_key = clean_cache_key(f"food_search_{query}_{min_calories}_{max_calories}")
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return cached_result
    
    try:
        
        url = "https://api.edamam.com/api/food-database/v2/parser"
        
        params = {
            'app_id': APP_ID,
            'app_key': APP_KEY,
            'ingr': query,
            'lang': 'en'  # İngilizce sonuçlar daha iyi
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 401:
            return []
        elif response.status_code != 200:
            return []
        
        data = response.json()
        foods = []
        
        if 'hints' in data:
            for hint in data['hints']:
                food = hint.get('food', {})
                nutrients = food.get('nutrients', {})
                
                # Kalori kontrolü
                calories = nutrients.get('ENERC_KCAL', 0)
                if min_calories and calories < min_calories:
                    continue
                if max_calories and calories > max_calories:
                    continue
                
                food_data = {
                    'name': food.get('label', 'Bilinmeyen'),
                    'calories': calories,
                    'protein': nutrients.get('PROCNT', 0),
                    'carbs': nutrients.get('CHOCDF', 0),
                    'fat': nutrients.get('FAT', 0),
                    'fiber': nutrients.get('FIBTG', 0),
                    'source': 'API'
                }
                
                
                db_meal = save_api_meal_to_db(food_data)
                if db_meal:
                    food_data['db_id'] = db_meal.id
                
                foods.append(food_data)
        
        
        cache.set(cache_key, foods, 3600)
        return foods
        
    except requests.RequestException as e:
        return []
    except Exception as e:
        return []


def get_turkish_food_suggestions(meal_type, target_calories):
    """Türk yemekleri için API arama terimleri (İngilizce öncelikli)"""
    turkish_foods = {
        'breakfast': [
            
            'omelet', 'cheese', 'olive', 'honey', 'jam', 'butter', 'milk', 'tea', 'bread', 'yogurt',
            
            'menemen', 'omlet', 'beyaz peynir', 'zeytin', 'bal', 'reçel', 'tereyağı', 'süt', 'çay', 'simit'
        ],
        'lunch': [
            
            'chicken', 'beef', 'rice', 'bulgur', 'lentil soup', 'tomato soup', 'salad', 'yogurt', 'pasta',
            
            'tavuk sote', 'kıyma', 'pirinç pilavı', 'bulgur pilavı', 'mercimek çorbası', 'domates çorbası', 'cacık'
        ],
        'dinner': [
            
            'grilled meatball', 'grilled fish', 'chicken kebab', 'eggplant', 'beans', 'chickpeas', 'pasta', 'spinach', 'zucchini',
            
            'ızgara köfte', 'balık ızgara', 'tavuk şiş', 'karnıyarık', 'imambayıldı', 'fasulye', 'nohut', 'ıspanak', 'kabak'
        ],
        'snack': [
           
            'apple', 'banana', 'orange', 'pear', 'strawberry', 'grape', 'cherry', 'almond', 'walnut', 'hazelnut',
            
            'elma', 'muz', 'portakal', 'armut', 'çilek', 'üzüm', 'kiraz', 'badem', 'ceviz', 'fındık'
        ]
    }
    
    return turkish_foods.get(meal_type, [])


def get_meal_recommendations(daily_calories, user=None, meal_type=None):
    """Günlük kalori ihtiyacına göre yemek önerileri getirir (Sadece API)"""
    
    api_foods = get_meal_recommendations_api(daily_calories, user, meal_type)
    
    
    if api_foods:
        return api_foods
    
    
    return []


def get_meal_recommendations_api(daily_calories, user=None, meal_type=None):
    """API'den yemek önerileri getirir (Sadece API)"""
    import random
    
    
    if meal_type == 'breakfast':
        meal_calories = daily_calories * 0.25
    elif meal_type == 'lunch':
        meal_calories = daily_calories * 0.35
    elif meal_type == 'dinner':
        meal_calories = daily_calories * 0.30
    elif meal_type == 'snack':
        meal_calories = daily_calories * 0.10
    else:
        meal_calories = daily_calories / 4
    
    
    min_calories = meal_calories * 0.8  # %20 tolerans
    max_calories = meal_calories * 1.2
    
    
    food_suggestions = get_turkish_food_suggestions(meal_type, meal_calories)
    
    all_foods = []
    
    
    for food_query in food_suggestions[:6]:
        foods = search_food_api(food_query, min_calories, max_calories)
        all_foods.extend(foods)
        
       
        if len(all_foods) >= 2:
            break
    
    
    if len(all_foods) > 2:
        if user and user.age:
            random.seed(user.age + user.weight + user.height)
        random.shuffle(all_foods)
        all_foods = all_foods[:2]
    
    return all_foods


def get_meal_recommendations_with_limit(daily_calories, user=None, meal_type=None, max_meal_calories=None):
    """Kalori sınırı ile yemek önerileri getirir (Sadece API)"""
    
    api_foods = get_meal_recommendations_api_with_limit(daily_calories, user, meal_type, max_meal_calories)
    
    
    if api_foods:
        return api_foods
    
    
    return []


def get_meal_recommendations_api_with_limit(daily_calories, user=None, meal_type=None, max_meal_calories=None):
    """API'den yemek önerileri getirir (Kalori Sınırlı, Sadece API)"""
    import random
    
    
    if meal_type == 'breakfast':
        meal_calories = daily_calories * 0.25
    elif meal_type == 'lunch':
        meal_calories = daily_calories * 0.35
    elif meal_type == 'dinner':
        meal_calories = daily_calories * 0.30
    elif meal_type == 'snack':
        meal_calories = daily_calories * 0.10
    else:
        meal_calories = daily_calories / 4
    
    
    if max_meal_calories:
        meal_calories = min(meal_calories, max_meal_calories)
    
    
    min_calories = meal_calories * 0.9  # %10 tolerans
    max_calories = meal_calories * 1.1
    
    
    food_suggestions = get_turkish_food_suggestions(meal_type, meal_calories)
    
    all_foods = []
    
    
    for food_query in food_suggestions[:8]:
        foods = search_food_api(food_query, min_calories, max_calories)
        all_foods.extend(foods)
        
        
        if len(all_foods) >= 2:
            break
    
    
    if len(all_foods) > 2:
        if user and user.age:
            random.seed(user.age + user.weight + user.height)
        random.shuffle(all_foods)
        all_foods = all_foods[:2]
    
    return all_foods


def generate_meal_plan(user):
    """Kullanıcı için günlük yemek planı oluşturur (Sadece API)"""
    
    
    if not all([user.age, user.weight, user.height, user.gender, user.activity_level]):
        return [], 0, 0
    
    
    daily_calories = calculate_daily_calorie_need(
        user.age, user.weight, user.height, user.gender, user.activity_level
    )
    
    print(f"Günlük kalori hedefi: {daily_calories} kcal")
    
    
    breakfast_target = daily_calories * 0.25  # %25
    lunch_target = daily_calories * 0.35      # %35  
    dinner_target = daily_calories * 0.30     # %30
    snack_target = daily_calories * 0.10      # %10
    
    print(f"Öğün hedefleri - Kahvaltı: {breakfast_target:.0f}, Öğle: {lunch_target:.0f}, Akşam: {dinner_target:.0f}, Atıştırmalık: {snack_target:.0f}")
    
    
    breakfast_meals = get_meal_recommendations(daily_calories, user, 'breakfast')
    lunch_meals = get_meal_recommendations(daily_calories, user, 'lunch')
    dinner_meals = get_meal_recommendations(daily_calories, user, 'dinner')
    snack_meals = get_meal_recommendations(daily_calories, user, 'snack')
    
    
    all_meals = breakfast_meals + lunch_meals + dinner_meals + snack_meals
    
    
    total_calories = sum(meal['calories'] if isinstance(meal, dict) else meal.calories for meal in all_meals)
    
    print(f"Kahvaltı: {len(breakfast_meals)} yemek, {sum(m['calories'] if isinstance(m, dict) else m.calories for m in breakfast_meals):.0f} kcal")
    print(f"Öğle: {len(lunch_meals)} yemek, {sum(m['calories'] if isinstance(m, dict) else m.calories for m in lunch_meals):.0f} kcal")
    print(f"Akşam: {len(dinner_meals)} yemek, {sum(m['calories'] if isinstance(m, dict) else m.calories for m in dinner_meals):.0f} kcal")
    print(f"Atıştırmalık: {len(snack_meals)} yemek, {sum(m['calories'] if isinstance(m, dict) else m.calories for m in snack_meals):.0f} kcal")
    print(f"Toplam önerilen: {total_calories:.0f} kcal")
    print(f"Kalori farkı: {daily_calories - total_calories:.0f} kcal")

    return all_meals, total_calories, daily_calories


def get_nutrition_advice(user, daily_calories):
    """Kullanıcıya beslenme tavsiyesi verir"""
    advice = []
    
    
    if user.age and user.age > 50:
        advice.append("50 yaş üstü için kalsiyum ve D vitamini açısından zengin besinler tüketin.")
    
    
    if user.weight and user.height:
        bmi = user.weight / ((user.height / 100) ** 2)
        if bmi > 25:
            advice.append("Kilo vermek için kalori açığı oluşturun ve düzenli egzersiz yapın.")
        elif bmi < 18.5:
            advice.append("Kilo almak için kalori fazlası oluşturun ve protein açısından zengin besinler tüketin.")
    
    
    if user.activity_level == 'low':
        advice.append("Hareketsiz yaşam tarzı için günlük 30 dakika yürüyüş yapmayı hedefleyin.")
    elif user.activity_level == 'high':
        advice.append("Yoğun aktivite için yeterli protein ve karbonhidrat alımına dikkat edin.")
    
    
    advice.append("Günde en az 2-2.5 litre su için.")
    advice.append("Meyve ve sebze tüketimini artırın.")
    advice.append("İşlenmiş gıdalardan kaçının.")
    
    return advice


def calculate_macro_ratios(meals):
    """Yemeklerin makro besin oranlarını hesaplar"""
    total_calories = sum(meal['calories'] if isinstance(meal, dict) else meal.calories for meal in meals)
    total_protein = sum(meal['protein'] if isinstance(meal, dict) else meal.protein for meal in meals)
    total_carbs = sum(meal['carbs'] if isinstance(meal, dict) else meal.carbs for meal in meals)
    total_fat = sum(meal['fat'] if isinstance(meal, dict) else meal.fat for meal in meals)
    
    if total_calories > 0:
        protein_ratio = (total_protein * 4 / total_calories) * 100
        carbs_ratio = (total_carbs * 4 / total_calories) * 100
        fat_ratio = (total_fat * 9 / total_calories) * 100
    else:
        protein_ratio = carbs_ratio = fat_ratio = 0
    
    return {
        'protein_ratio': round(protein_ratio, 1),
        'carbs_ratio': round(carbs_ratio, 1),
        'fat_ratio': round(fat_ratio, 1),
        'total_protein': round(total_protein, 1),
        'total_carbs': round(total_carbs, 1),
        'total_fat': round(total_fat, 1)
    }

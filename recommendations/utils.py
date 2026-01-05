import requests
import re
import random
from django.conf import settings
from django.core.cache import cache

# Kalori hesaplama
def calculate_daily_calorie_need(age, weight, height, gender, activity_level):
    """Mifflin-St Jeor formülü ile günlük kalori ihtiyacını hesaplar"""
    # Cinsiyet kontrolü
    gender_str = str(gender).strip().upper()
    is_male = gender_str in ['M', 'MALE', 'ERKEK']
    is_female = gender_str in ['F', 'FEMALE', 'KADIN', 'KADIN']
    
    # BMR hesaplama
    if is_male:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Aktivite çarpanları
    multipliers = {'low': 1.2, 'medium': 1.55, 'high': 1.9}
    multiplier = multipliers.get(activity_level, 1.2)
    
    return round(bmr * multiplier, 0)


# Cache yardımcı fonksiyonu
def clean_cache_key(key):
    key = re.sub(r'[^a-zA-Z0-9_]', '_', key)
    return re.sub(r'_+', '_', key)


# Veritabanı kaydetme
def save_api_meal_to_db(meal_data):
    """API'den gelen yemeği veritabanına kaydeder"""
    from .models import RecommendedMeal
    
    try:
        meal, created = RecommendedMeal.objects.get_or_create(
            name=meal_data['name'],
            defaults={
                'calories': meal_data['calories'],
                'protein': meal_data['protein'],
                'carbs': meal_data['carbs'],
                'fat': meal_data['fat']
            }
        )
        return meal
    except Exception as e:
        print(f"Yemek kaydetme hatası: {e}")
        return None


# API'den yemek bilgisi çekme
def _parse_food_from_api(food_data):
    """API'den gelen yemek verisini parse eder"""
    food = food_data.get('food', {})
    nutrients = food.get('nutrients', {})
    
    # API 100g başına kalori veriyor, porsiyon için 250g varsayıyoruz
    calories_per_100g = nutrients.get('ENERC_KCAL', 0)
    portion_multiplier = 2.5
    
    return {
        'name': food.get('label', 'Bilinmeyen'),
        'calories': round(calories_per_100g * portion_multiplier, 1),
        'protein': round(nutrients.get('PROCNT', 0) * portion_multiplier, 1),
        'carbs': round(nutrients.get('CHOCDF', 0) * portion_multiplier, 1),
        'fat': round(nutrients.get('FAT', 0) * portion_multiplier, 1),
        'fiber': round(nutrients.get('FIBTG', 0) * portion_multiplier, 1),
        'source': 'API'
    }


def search_food_api(query, min_calories=None, max_calories=None):
    """Edamam API'den yemek arama"""
    APP_ID = getattr(settings, 'EDAMAM_APP_ID', '')
    APP_KEY = getattr(settings, 'EDAMAM_APP_KEY', '')
    
    if not APP_ID or not APP_KEY:
        print(f"[LOG] Edamam API anahtarı eksik. APP_ID: {APP_ID}, APP_KEY: {APP_KEY}")
        return []
    
    # Cache kontrolü
    cache_key = clean_cache_key(f"food_{query}_{min_calories}_{max_calories}")
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        url = "https://api.edamam.com/api/food-database/v2/parser"
        params = {'app_id': APP_ID, 'app_key': APP_KEY, 'ingr': query, 'lang': 'en'}
        print(f"[LOG] API çağrısı başlatılıyor: {url} params={params}")
        response = requests.get(url, params=params, timeout=10)
        print(f"[LOG] API yanıt kodu: {response.status_code}")
        if response.status_code != 200:
            print(f"[LOG] API başarısız yanıt: {response.text}")
            return []
        data = response.json()
        foods = []
        for hint in data.get('hints', []):
            food_data = _parse_food_from_api(hint)
            calories = food_data['calories']
            # Kalori filtresi
            if min_calories and calories < min_calories * 0.5:
                continue
            if max_calories and calories > max_calories * 1.5:
                continue
            save_api_meal_to_db(food_data)
            foods.append(food_data)
        cache.set(cache_key, foods, 3600)
        print(f"[LOG] API'den {len(foods)} yemek döndü.")
        return foods
    except requests.Timeout as e:
        print(f"[LOG] API timeout hatası ({query}): {str(e)}")
        return []
    except Exception as e:
        print(f"[LOG] API genel hatası ({query}): {str(e)}")
        return []


def get_meal_recommendations(daily_calories, user=None, meal_type=None):
    """Öğün için yemek önerileri getirir"""
    # Öğün kalori hedefi
    meal_percentages = {
        'breakfast': 0.25,
        'lunch': 0.35,
        'dinner': 0.30,
        'snack': 0.10
    }
    meal_calories = daily_calories * meal_percentages.get(meal_type, 0.25)
    # Yüksek aktivite seviyesinde öğün başına kalori üst limiti koy
    MAX_MEAL_CAL = 1000  # API'nin döndürebileceği makul üst limit
    if meal_calories > MAX_MEAL_CAL:
        meal_calories = MAX_MEAL_CAL
    # Kalori aralığı (%50 tolerans)
    min_cal = meal_calories * 0.5
    max_cal = meal_calories * 1.5
    if max_cal > 1200:
        max_cal = 1200
    
    # Genel arama terimleri
    search_queries = ['food', 'meal', 'dish', 'chicken', 'rice', 'bread']
    if meal_type == 'snack':
        search_queries = ['fruit', 'snack', 'nut', 'apple', 'banana']
    
    # Yemek arama
    all_foods = []
    for query in search_queries[:6]:
        foods = search_food_api(query, min_cal, max_cal)
        all_foods.extend(foods)
        if len(all_foods) >= 2:
            break
    
    # Filtre olmadan tekrar dene
    if len(all_foods) < 2:
        for query in search_queries[:6]:
            foods = search_food_api(query, None, None)
            all_foods.extend(foods)
            if len(all_foods) >= 4:
                break
    
    # Kalori aralığına uygun olanları seç
    if len(all_foods) > 0:
        filtered = [f for f in all_foods if min_cal <= f.get('calories', 0) <= max_cal]
        if len(filtered) >= 2:
            all_foods = filtered
        else:
            # En yakın kalorili olanları seç
            all_foods.sort(key=lambda x: abs(x.get('calories', 0) - meal_calories))
    
    # Rastgele 2 yemek seç
    if len(all_foods) > 2:
        if user and user.age:
            meal_type_hash = {'breakfast': 1, 'lunch': 2, 'dinner': 3, 'snack': 4}.get(meal_type, 0)
            random.seed(user.age + int(user.weight or 0) + int(user.height or 0) + meal_type_hash)
        random.shuffle(all_foods)
        all_foods = all_foods[:2]
    
    return all_foods




# BMI hesaplama
def calculate_bmi(weight, height):
    """BMI (Body Mass Index) hesaplar ve kategori döndürür"""
    if not weight or not height or height <= 0:
        return 0, "Hesaplanamadı"
    
    bmi = weight / ((height / 100) ** 2)
    
    if bmi < 18.5:
        category = "Zayıf"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Fazla Kilolu"
    else:
        category = "Obez"
    
    return round(bmi, 1), category


# Beslenme tavsiyeleri
def get_nutrition_advice(user, daily_calories):
    """Kullanıcıya beslenme tavsiyesi verir"""
    advice = []
    
    if user.age and user.age > 50:
        advice.append("50 yaş üstü için kalsiyum ve D vitamini açısından zengin besinler tüketin.")
    
    if user.weight and user.height and user.height > 0:
        bmi, _ = calculate_bmi(user.weight, user.height)
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


# Makro besin oranları
def calculate_macro_ratios(meals):
    """Yemeklerin makro besin oranlarını hesaplar"""
    total_cal = sum(m.get('calories', 0) if isinstance(m, dict) else m.calories for m in meals)
    total_protein = sum(m.get('protein', 0) if isinstance(m, dict) else m.protein for m in meals)
    total_carbs = sum(m.get('carbs', 0) if isinstance(m, dict) else m.carbs for m in meals)
    total_fat = sum(m.get('fat', 0) if isinstance(m, dict) else m.fat for m in meals)
    
    if total_cal > 0:
        return {
            'protein_ratio': round((total_protein * 4 / total_cal) * 100, 1),
            'carbs_ratio': round((total_carbs * 4 / total_cal) * 100, 1),
            'fat_ratio': round((total_fat * 9 / total_cal) * 100, 1),
            'total_protein': round(total_protein, 1),
            'total_carbs': round(total_carbs, 1),
            'total_fat': round(total_fat, 1)
        }
    
    return {
        'protein_ratio': 0, 'carbs_ratio': 0, 'fat_ratio': 0,
        'total_protein': 0, 'total_carbs': 0, 'total_fat': 0
    }

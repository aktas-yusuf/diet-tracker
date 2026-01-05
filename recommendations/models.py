from django.db import models
from django.conf import settings

class RecommendedMeal(models.Model):
    name = models.CharField(max_length=100)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()

    def __str__(self):
        return self.name

class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    recommended_meals = models.ManyToManyField(RecommendedMeal)
    total_calories = models.FloatField(default=0)

    def __str__(self):
        return f"Recommendation for {self.user.username} on {self.date}"

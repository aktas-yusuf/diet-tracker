from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser 

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'age', 'height', 'weight', 'gender', 'activity_level', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('age', 'height', 'weight', 'gender', 'activity_level')}),
        ('Yetkiler', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
# Register your models here.

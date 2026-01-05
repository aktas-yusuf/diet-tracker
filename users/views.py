from django.shortcuts import render , redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from recommendations.constants import MSG_PROFILE_UPDATED, MSG_INVALID_VALUE, MSG_SYSTEM_ERROR

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    
    if request.method == "POST":
        # Form verilerini al ve parse et
        age_str = request.POST.get('age', '').strip()
        user.age = int(age_str) if age_str and age_str.isdigit() else None

        weight_str = request.POST.get('weight', '').strip()
        user.weight = float(weight_str) if weight_str and weight_str.replace('.', '', 1).isdigit() else None

        height_str = request.POST.get('height', '').strip()
        user.height = float(height_str) if height_str and height_str.replace('.', '', 1).isdigit() else None

        user.gender = request.POST.get('gender') or None
        user.activity_level = request.POST.get('activity_level') or None

        try:
            user.save()
            user.refresh_from_db()
            messages.success(request, MSG_PROFILE_UPDATED)
            return redirect('profile')
        except (ValueError, TypeError):
            messages.error(request, MSG_INVALID_VALUE)
        except Exception:
            messages.error(request, MSG_SYSTEM_ERROR)

    return render(request, 'users/profile.html', {'user': user})


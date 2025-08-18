from django.shortcuts import render , redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm

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
    """Kullanıcı profil sayfası"""
    user = request.user
    
    if request.method == "POST":
    
        user.age = request.POST.get('age') or None
        user.weight = request.POST.get('weight') or None
        user.height = request.POST.get('height') or None
        user.gender = request.POST.get('gender') or None
        user.activity_level = request.POST.get('activity_level') or None
        
        try:
            user.save()
            messages.success(request, "Profil bilgileriniz güncellendi!")
            return redirect('profile')
        except Exception as e:
            messages.error(request, f"Güncelleme sırasında hata oluştu: {str(e)}")
    
    return render(request, 'users/profile.html', {'user': user})


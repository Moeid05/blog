from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm
from home.models import Blog

from django.contrib.auth import get_user_model
User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('profile', request.user.username ) 
        else :
            form.add_error('username', 'Invalid input')
    else:
        form = SignUpForm()
    return render(request, 'users/pages/signin.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('profile',request.user.username) 
            else :
                form.add_error(None , 'username/password is wrong')
    else:
        form = LoginForm()
    return render(request, 'users/pages/login.html', {'form': form})
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request, username=None):
    user = get_object_or_404(User, username=username if username else request.user.username)

    published_blogs = Blog.objects.filter(author=user)

    voted_up_blogs = Blog.objects.filter(voteUps=user)

    viewed_blogs = Blog.objects.filter(view=user)

    context = {
        'user': user,
        'published_blogs': published_blogs,
        'voted_up_blogs': voted_up_blogs,
        'viewed_blogs': viewed_blogs,
    }

    return render(request, "users/pages/profile.html", context)
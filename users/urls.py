from . import views
from django.urls import path


urlpatterns = [
    path('profile/<str:username>' , views.profile , name='profile'),
    path('login/' , views.login_view , name='login'),
    path('logout/' , views.logout_view , name='logout'),
    path('register/' , views.register , name='register'),
]
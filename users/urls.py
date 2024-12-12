from . import views
from django.urls import path


urlpatterns = [
    path('login/' , views.login_view , name='login'),
    path('logout/' , views.logout_view , name='logout'),
    path('register/' , views.register , name='register'),
    path('profile/' , views.profile , name='profile'),
    path('profile/<str:username>/' , views.profile , name='profile'),
]
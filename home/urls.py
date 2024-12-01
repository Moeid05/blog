from . import views
from django.urls import path


urlpatterns = [
#guest view
    path('' , views.index , name='home'),
    path('blog/' , views.blogs , name='blogs'),
    path('blog/new/' , views.new_blogs , name='new_blogs'),
    path('blog/top/' , views.top_blogs , name='top_blogs'),
    path('blog/hot/' , views.hot_blogs , name='hot_blogs'),
    path('blog/<int:id>/<str:name>/' , views.blog , name='blog'),
    path('blog/<int:id>/<str:name>/voteup/' , views.blog , name='voteup'),
    path('blog/<int:id>/<str:name>/votedown/' , views.blog , name='votedown'),
#author view
    path('blog/add/' , views.add_blog , name='add_blogs'),
    path('blog/edit/' , views.edit_blog , name='edit_blogs'),
    path('blog/delete/<int:blog_id>/' , views.delete_blog , name='delete_blogs'),
]
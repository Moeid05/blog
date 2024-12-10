from . import views
from django.urls import path


urlpatterns = [
#guest view
    path('' , views.index , name='home'),
    path('blog/' , views.blogs , name='blogs'),
    path('blog/new/' , views.new_blogs , name='new_blogs'),
    path('blog/top/' , views.top_blogs , name='top_blogs'),
    path('blog/hot/' , views.hot_blogs , name='hot_blogs'),
    path('blog/<int:id>/<str:name>/' , views.BlogView.as_view() , name='blog'),
#author view
    path('blog/add/' , views.AddBlog.as_view() , name='add_blog'),
    path('blog/edit/<int:blog_id>/' , views.UpdateBlog.as_view() , name='edit_blog'),
    path('blog/delete/<int:blog_id>/' , views.delete_blog , name='delete_blog'),
]
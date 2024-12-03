from django.shortcuts import render ,get_object_or_404
from .models import Blog
from django.utils import timezone
from datetime import timedelta
from django.db.models import F, ExpressionWrapper, FloatField
from django.http import JsonResponse
from django.core.paginator import Paginator
import json
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model
User = get_user_model()

def index (request) :
    user = request.user
    return render(request , "home/pages/home.html",context={"user" : user})

def blogs (request) :
    user = request.user
    return render(request , "home/pages/blogs" , context={"user":user})

def new_blogs(request):
    try:
        data = json.loads(request.body)
        page_number = int(data.get('page', 1))
    except (json.JSONDecodeError, TypeError):
        page_number = 1
    new_blogs = Blog.objects.all()
    paginator = Paginator(new_blogs, 10)
    try:
        blogs = paginator.page(page_number)
    except :
        blogs = []
    blog_data = [{'id': blog.id, 'title': blog.title, 'content': blog.content} for blog in blogs]
    return JsonResponse(blog_data, safe=False)

    
def top_blogs (request) :
    try:
        data = json.loads(request.body)
        page_number = int(data.get('page', 1))
    except (json.JSONDecodeError, TypeError):
        page_number = 1
    top_blogs = Blog.objects.order_by('-vote')
    paginator = Paginator(top_blogs, 10)
    try:
        blogs = paginator.page(page_number)
    except :
        blogs = []
    blog_data = [{'id': blog.id, 'title': blog.title, 'content': blog.content} for blog in blogs]
    return JsonResponse(blog_data, safe=False)

def hot_blogs (request) :
    try:
        data = json.loads(request.body)
        page_number = int(data.get('page', 1))
    except (json.JSONDecodeError, TypeError):
        page_number = 1
        time_frame = timezone.now() - timedelta(days=7)
    hot_blogs = Blog.objects.filter(publish_date__gte=time_frame).annotate(
        # Create a score based on votes, views, and comments
        score=ExpressionWrapper(
            F('vote') * 2 +
            F('views') * 1 +
            F('comment_count') * 3 +
            (timezone.now() - F('publish_date')).total_seconds() / 3600 * -1,
            output_field=FloatField()
        )
    ).order_by('-score')[:10]
    paginator = Paginator(hot_blogs, 10)
    try:
        blogs = paginator.page(page_number)
    except :
        blogs = []
    blog_data = [{'id': blog.id, 'title': blog.title, 'content': blog.content} for blog in blogs]
    return JsonResponse(blog_data, safe=False)
def show_blog (request,id=None,name=None) :
    user = request.user
    blog = Blog.objects.get(pk=id)
    return render(request , "home/pages/blogs" , context={"user":user,"blog":blog})

class voteup_blog(LoginRequiredMixin, View) :
    def  post(self, request, *args, **kwargs):
        try:
            data = json.decoder(request.body)
            like = data.get('like')
            blog = Blog.objects.get(pk=id)
            blog.vote = blog.vote + (1 if  else -1 )
            blog.save()
            return JsonResponse({'success': True, 'votes': blog.vote})
        except :
            return JsonResponse({'success': False, 'error': 'Blog not found.'}, status=404)
        
class votedown_blog(LoginRequiredMixin, View) :
    def  post(self, request, *args, **kwargs):
        try:
            blog = Blog.objects.get(pk=id)
            blog.vote -= 1
            blog.save()
            return JsonResponse({'success': True, 'votes': blog.vote})
        except :
            return JsonResponse({'success': False, 'error': 'Blog not found.'}, status=404)
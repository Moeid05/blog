from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse,HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .forms import BlogForm
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
import json
from .models import Blog
from django.db.models import F, ExpressionWrapper, FloatField
from django.db.models import Count

from django.contrib.auth import get_user_model
User  = get_user_model()

def index (request) :
    user = request.user
    return render(request , "home/pages/home.html",context={"user" : user})

def blogs (request) :
    user = request.user
    return render(request , "home/pages/blogs.html" , context={"user":user})

def get_paginated_blogs(queryset, page_number):
    paginator = Paginator(queryset, 10)
    try:
        blogs = paginator.page(page_number)
    except:
        blogs = []
    return [{'id': blog.id, 'title': blog.title, 'content': blog.content} for blog in blogs]

def new_blogs(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            page_number = int(data.get('page', 1))
        except (json.JSONDecodeError, TypeError):
            page_number = 1
        new_blogs = Blog.objects.all()
        blog_data = get_paginated_blogs(new_blogs, page_number)
        return JsonResponse(blog_data, safe=False)
    return HttpResponseNotAllowed(['POST'])

def top_blogs(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            page_number = int(data.get('page', 1))
        except (json.JSONDecodeError, TypeError):
            page_number = 1
        top_blogs = Blog.objects.annotate(
            votes=Count('voteUps') - Count('voteDowns')
        ).order_by('-votes')
        blog_data = get_paginated_blogs(top_blogs, page_number)
        return JsonResponse(blog_data, safe=False)
    return HttpResponseNotAllowed(['POST'])

def hot_blogs(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            page_number = int(data.get('page', 1))
        except (json.JSONDecodeError, TypeError):
            page_number = 1

        time_frame = timezone.now() - timedelta(days=7)
        hot_blogs = Blog.objects.filter(publish_date__gte=time_frame).annotate(
            score=ExpressionWrapper(
                F('voteUps') * 2 +
                F('view') * 1 +
                F('voteDowns') * -1,
                output_field=FloatField()
            )
        ).order_by('-score')

        blog_data = get_paginated_blogs(hot_blogs, page_number)
        return JsonResponse(blog_data, safe=False)
    return HttpResponseNotAllowed(['POST'])

class BlogView(LoginRequiredMixin, View):
    def get(self, request, id, name):
        blog = get_object_or_404(Blog, pk=id)
        return render(request, "home/pages/blog.html", context={"user": request.user, "blog": blog})
    # post always is voting
    def post(self, request, id, name):
        action = request.POST.get('action')
        blog = get_object_or_404(Blog, pk=id)

        if action == 'voteup':
            if request.user in blog.voteDowns.all():
                blog.voteDowns.remove(request.user)
                blog.voteUps.add(request.user)
            elif request.user not in blog.voteUps.all():
                blog.voteUps.add(request.user)
            else :
                blog.voteUps.remove(request.user)
            return JsonResponse({'success': True, 'votes': blog.vote})

        elif action == 'votedown':            
            if request.user in blog.voteUps.all():
                blog.voteUps.remove(request.user)
                blog.voteDowns.add(request.user)
            elif request.user not in blog.voteDowns.all():
                blog.voteDowns.add(request.user)
            else :
                blog.voteDowns.remove(request.user)
            return JsonResponse({'success': True, 'votes': blog.vote})
        return JsonResponse({'success': False, 'error': 'Invalid action.'}, status=400)

class AddBlog(LoginRequiredMixin, View) :
    def get(self, request):
        form = BlogForm()
        return render(request, "home/pages/create_blog.html", {'form': form})
    def post(self, request):
            form = BlogForm(request.POST)
            if form.is_valid():
                blog = form.save(commit=False)
                blog.author = request.user
                blog.save()
                redirect_url = reverse('blog', args=[blog.id, blog.title])
                print(redirect_url)
                return JsonResponse({'success': True, 'redirect_to': redirect_url})
            else:
                return JsonResponse({'success': False, 'error': form.errors}, status=400)

class UpdateBlog(LoginRequiredMixin, View):
    def get(self, request, blog_id):
        blog = get_object_or_404(Blog, pk=blog_id)
        if blog.author != request.user:
            return JsonResponse({'success': False, 'error': 'You are not authorized to edit this blog.'}, status=403)
        
        form = BlogForm(instance=blog)
        return render(request, "home/pages/create_blog.html", context={"form": form, "is_update": True, "blog": blog})

    def post(self, request, blog_id):
        blog = get_object_or_404(Blog, pk=blog_id)
        if blog.author != request.user:
            return JsonResponse({'success': False, 'error': 'You are not authorized to edit this blog.'}, status=403)

        form = BlogForm(request.POST, instance=blog)  # Bind the form to the existing blog instance
        if form.is_valid():
            form.save()  # Save the updated blog
            redirect_url = reverse('blog', args=[blog.id, blog.title])
            return JsonResponse({'success': True, 'redirect_to': redirect_url})
        else:
            return JsonResponse({'success': False, 'error': form.errors}, status=400)

@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    if blog.author != request.user:
        return JsonResponse({'success': False, 'error': 'You are not authorized to delete this blog.'}, status=403)
    blog.delete()
    return redirect('blogs')
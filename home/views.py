from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse,HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
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
            if request.user not in blog.voteUps.all():
                try :
                    blog.voteUps.add(request.user)
                    blog.voteDowns.remove(request.user)
                except :
                    blog.voteUps.add(request.user)
                blog.save()
                return JsonResponse({'success': True, 'votes': blog.vote})
            else:
                return JsonResponse({'success': False, 'error': 'You have already voted up.'}, status=400)

        elif action == 'votedown':
            if request.user in blog.voteDowns.all():
                return JsonResponse({'success': False, 'error': 'You already voted down.'}, status=400)
            else:
                try :
                    blog.voteDowns.add(request.user)
                    blog.voteUps.remove(request.user)
                except :
                    blog.voteDowns.add(request.user)
                blog.save()
                return JsonResponse({'success': True, 'votes': blog.vote})
        return JsonResponse({'success': False, 'error': 'Invalid action.'}, status=400)

class AddBlog(LoginRequiredMixin, View) :
    def get(self,request) :
        return render (request , "home/pages/create_blog.html")
    def post(self,request) :
        try :
            data = json.loads(request.body)
            blog = Blog.objects.create(
                title = data.get('title'),
                content = data.get('content'),
                author = request.user,
            )
            return redirect('blog', id=blog.id, name=blog.title.replace(" ", "-").lower())
        except KeyError as e:
            return JsonResponse({'success': False, 'error': f'Missing field: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
class UpdateBlog(LoginRequiredMixin, View) :
    def get(self, request, blog_id):
        blog = get_object_or_404(Blog, pk=blog_id)
        if blog.author != request.user:
            return JsonResponse({'success': False, 'error': 'You are not authorized to edit this blog.'}, status=403)
        return render(request, "home/pages/create_blog.html", context={"blog": blog})
    
    def post(self,request,blog_id) :
        try :
            data = json.loads(request.body)
            blog = get_object_or_404(Blog, pk=blog_id)
            if blog.author != request.user:
                return JsonResponse({'success': False, 'error': 'You are not authorized to edit this blog.'}, status=403)
            blog.update(
                title=data.get('title'),
                content=data.get('content')
            )
            return redirect('blog', id=blog.id, name=blog.title.replace(" ", "-").lower())
        except KeyError as e:
            return JsonResponse({'success': False, 'error': f'Missing field: {str(e)}'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    if blog.author != request.user:
        return JsonResponse({'success': False, 'error': 'You are not authorized to delete this blog.'}, status=403)
    blog.delete()
    return redirect('blogs')
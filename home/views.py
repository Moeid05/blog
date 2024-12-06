from django.shortcuts import render, get_object_or_404, redirect
from .models import Blog
from django.utils import timezone
from datetime import timedelta
from django.db.models import F, ExpressionWrapper, FloatField
from django.http import JsonResponse
from django.core.paginator import Paginator
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from django.contrib.auth import get_user_model
User  = get_user_model()

def index (request) :
    user = request.user
    return render(request , "home/pages/home.html",context={"user" : user})

def blogs (request) :
    user = request.user
    return render(request , "home/pages/blogs" , context={"user":user})

def get_paginated_blogs(queryset, page_number):
    paginator = Paginator(queryset, 10)
    try:
        blogs = paginator.page(page_number)
    except:
        blogs = []
    return [{'id': blog.id, 'title': blog.title, 'content': blog.content} for blog in blogs]

def new_blogs(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        page_number = int(data.get('page', 1))
    except (json.JSONDecodeError, TypeError):
        page_number = 1
    new_blogs = Blog.objects.all()
    blog_data = get_paginated_blogs(new_blogs, page_number)
    return JsonResponse(blog_data, safe=False)

def top_blogs(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        page_number = int(data.get('page', 1))
    except (json.JSONDecodeError, TypeError):
        page_number = 1
    top_blogs = Blog.objects.order_by('-vote')
    blog_data = get_paginated_blogs(top_blogs, page_number)
    return JsonResponse(blog_data, safe=False)

def hot_blogs(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        page_number = int(data.get('page', 1))
    except (json.JSONDecodeError, TypeError):
        page_number = 1

    time_frame = timezone.now() - timedelta(days=7)
    hot_blogs = Blog.objects.filter(publish_date__gte=time_frame).annotate(
        score=ExpressionWrapper(
            F('vote') * 2 +
            F('views') * 1 +
            F('comment_count') * 3 +
            (timezone.now() - F('publish_date')).total_seconds() / 3600 * -1,
            output_field=FloatField()
        )
    ).order_by('-score')

    blog_data = get_paginated_blogs(hot_blogs, page_number)
    return JsonResponse(blog_data, safe=False)

class BlogView(LoginRequiredMixin, View):
    def get(self, request, id, name):
        # Display the blog
        blog = get_object_or_404(Blog, pk=id)
        return render(request, "home/pages/blogs", context={"user": request.user, "blog": blog})

    def post(self, request, id, name):
        # Handle voting
        action = request.POST.get('action')
        blog = get_object_or_404(Blog, pk=id)

        if action == 'voteup':
            if request.user not in blog.votes.all():
                blog.votes.add(request.user)
                blog.vote_count += 1  
                blog.save()
                return JsonResponse({'success': True, 'votes': blog.vote_count})
            else:
                return JsonResponse({'success': False, 'error': 'You have already voted up.'}, status=400)

        elif action == 'votedown':
            if request.user in blog.votes.all():
                blog.votes.remove(request.user)
                blog.vote_count -= 1
                blog.save()
                return JsonResponse({'success': True, 'votes': blog.vote_count})
            else:
                return JsonResponse({'success': False, 'error': 'You have not voted up yet.'}, status=400)

        return JsonResponse({'success': False, 'error': 'Invalid action.'}, status=400)

class AddBlog(LoginRequiredMixin, View) :
    def get(self,request) :
        return render (request , "home/pages/create_blog.html")
    def post(self,request) :
        try :
            data = json.load(request.body)
            blog = Blog.objects.create(
                title = data.title,
                content = data.content,
                author = request.user,
            )
            return redirect('blog', id=blog.id, name=blog.title.replace(" ", "-").lower())
        except KeyError as e:
            return JsonResponse({'success': False, 'error': f'Missing field: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
class UpdateBlog(LoginRequiredMixin, View) :
    def get(self, request, id):
        blog = get_object_or_404(Blog, pk=id)
        if blog.author != request.user:
            return JsonResponse({'success': False, 'error': 'You are not authorized to edit this blog.'}, status=403)
        return render(request, "home/pages/edit_blog.html", context={"blog": blog})
    def post(self,request) :
        try :
            blog = get_object_or_404(Blog, pk=id)
            if blog.author != request.user:
                return JsonResponse({'success': False, 'error': 'You are not authorized to edit this blog.'}, status=403)
            data = json.load(request.body)
            blog.update(
                title=data['title'],
                content=data['content']
            )
            return redirect('blog', id=blog.id, name=blog.title.replace(" ", "-").lower())
        except KeyError as e:
            return JsonResponse({'success': False, 'error': f'Missing field: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    if blog.author != request.user:
        return JsonResponse({'success': False, 'error': 'You are not authorized to delete this blog.'}, status=403)
    blog.delete()
    return redirect('blog_list')
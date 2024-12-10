from django.test import TestCase
from django.urls import reverse
from .models import Blog
import json

from django.contrib.auth import get_user_model
User  = get_user_model()

class BlogTests(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser',email= 'test@email.com' , password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        # Create a blog for testing
        self.blog = Blog.objects.create(
            title='Test Blog',
            content='This is a test blog content.',
            author=self.user
        )

    def test_index_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/pages/home.html')

    def test_blogs_view(self):
        response = self.client.get(reverse('blogs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/pages/blogs.html')

    def test_create_blog(self):
        response = self.client.post(reverse('add_blog'), data=json.dumps({
            'title': 'New Blog',
            'content': 'This is a new blog content.'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Blog.objects.filter(title='New Blog').exists())

    def test_update_blog(self):
        response = self.client.post(reverse('edit_blog', args=[self.blog.id]), data=json.dumps({
            'title': 'Updated Blog',
            'content': 'This is updated content.'
        }), content_type='application/json')
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, 'Updated Blog')
        self.assertEqual(self.blog.content, 'This is updated content.')
        self.assertEqual(response.status_code, 302)

    def test_delete_blog(self):
        response = self.client.post(reverse('delete_blog', args=[self.blog.id]))
        self.assertEqual(response.status_code, 302) 
        self.assertFalse(Blog.objects.filter(id=self.blog.id).exists())

    def test_vote_up_blog(self):
        response = self.client.post(reverse('blog', args=[self.blog.id, self.blog.title.replace(" ", "-").lower()]), data={'action': 'voteup'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['votes'], 1)

    def test_vote_down_blog(self):
        self.client.post(reverse('blog', args=[self.blog.id, self.blog.title.replace(" ", "-").lower()]), data={'action': 'voteup'})
        response = self.client.post(reverse('blog', args=[self.blog.id, self.blog.title.replace(" ", "-").lower()]), data={'action': 'votedown'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['votes'], -1)

    def test_get_paginated_blogs(self):
        response = self.client.post(reverse('new_blogs'), data=json.dumps({'page': 1}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json()[0])

    def test_hot_blogs(self):
        response = self.client.post(reverse('hot_blogs'), data=json.dumps({'page': 1}), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_top_blogs(self):
        response = self.client.post(reverse('top_blogs'), data=json.dumps({'page': 1}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
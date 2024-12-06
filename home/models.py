from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Blog(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    publish_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True)
    voteUps = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    voteDowns = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    vote_count = models.IntegerField(default=0)
    view = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-publish_date']

    def update(self,title,content) :
        self.title = title
        self.content = content
        self.updated_at = timezone.now()  # Update the timestamp
        self.save() 

    def __str__(self):
        return self.title
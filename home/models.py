from django.db import models
from django.utils import timezone

from django.contrib.auth import get_user_model
User  = get_user_model()

class Blog(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    publish_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True,null=True)
    voteUps = models.ManyToManyField(User, related_name='upvotes', blank=True)
    voteDowns = models.ManyToManyField(User, related_name='downvotes', blank=True)
    view = models.ManyToManyField(User, related_name='viewed', blank=True)

    @property
    def vote(self) :
        return (self.voteUps.count() - self.voteDowns.count())
    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-publish_date']

    def update(self,title,content) :
        self.title = title
        self.content = content
        self.updated_at = timezone.now()
        self.save() 

    def __str__(self):
        return self.title
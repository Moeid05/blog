# Generated by Django 5.1.3 on 2024-12-08 15:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('publish_date', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True)),
                ('vote_count', models.IntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('view', models.ManyToManyField(blank=True, related_name='viewed', to=settings.AUTH_USER_MODEL)),
                ('voteDowns', models.ManyToManyField(blank=True, related_name='downvotes', to=settings.AUTH_USER_MODEL)),
                ('voteUps', models.ManyToManyField(blank=True, related_name='upvotes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Blog Post',
                'verbose_name_plural': 'Blog Posts',
                'ordering': ['-publish_date'],
            },
        ),
    ]

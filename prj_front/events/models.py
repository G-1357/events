from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    name = models.CharField(max_length=150)
    surname = models.CharField(max_length=150)
    group_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)

class Event(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    annotation = models.TextField()
    description = models.TextField()
    event_date = models.DateField()
    location = models.CharField(max_length=200)
    participant_limit = models.PositiveIntegerField()
    request_moderation = models.BooleanField(default=False)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    image_description = models.CharField(max_length=255, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    published_on = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=50, default='DRAFT')
    views = models.PositiveIntegerField(default=0)

class Request(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='PENDING')

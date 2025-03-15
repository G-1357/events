from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateTimeField()
    description = models.TextField()
    photo_url = models.URLField(blank=True)

    def __str__(self):
        return self.name
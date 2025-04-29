from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Event

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=150)
    surname = forms.CharField(max_length=150)
    group_name = forms.CharField(max_length=150)

    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'surname', 'group_name', 'password1', 'password2')

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'annotation', 'description', 'event_date', 'location', 'participant_limit', 'request_moderation', 'image', 'image_description']

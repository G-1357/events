from django.urls import path
from . import views
from .views import add_event

app_name = 'events'

urlpatterns = [
    path('add/', views.start, name='start'),
    path('api/events/', add_event, name='add_event'),
]
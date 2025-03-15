from django.shortcuts import render
from .models import Event
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EventSerializer


def start(request):
    if request.method == 'POST':
        name = request.POST['name']
        date = request.POST['date']
        description = request.POST['description']
        photo_url = request.POST['photo_url']

        event = Event(name=name, date=date, description=description, photo_url=photo_url)
        event.save()

        return HttpResponseRedirect(reverse('events:start'))
    return render(request, 'events/start.html')

@api_view(['POST'])
def add_event(request):
    if request.method == 'POST':
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
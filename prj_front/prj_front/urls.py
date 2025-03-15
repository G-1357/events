from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('web/', include('web.urls')),
    path('accounts/', include('allauth.urls')),
]
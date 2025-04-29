from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Event

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        (('Additional Info'), {'fields': ('phone',)}),  # Убрал avatar
    )

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'creator', 'request_moderation')
    list_filter = ('request_moderation', 'event_date')
    search_fields = ('title', 'description')

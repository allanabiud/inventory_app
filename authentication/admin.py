from django.contrib import admin

from .models import InvitedUser, UserProfile

admin.site.register(InvitedUser)
admin.site.register(UserProfile)

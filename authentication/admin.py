from django.contrib import admin

from .models import InvitedUser, UserProfile


@admin.register(InvitedUser)
class InvitedUserAdmin(admin.ModelAdmin):
    list_display = ("email", "invited_at", "accepted")
    search_fields = ("email",)


admin.site.register(UserProfile)

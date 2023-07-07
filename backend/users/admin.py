from django.contrib import admin

from .models import User


class PostAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')


admin.site.register(User, PostAdmin)

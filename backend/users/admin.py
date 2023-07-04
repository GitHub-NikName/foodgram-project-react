from django.contrib import admin

# Register your models here.
from .models import User


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'password')
    empty_value_display = '-пусто-'


admin.site.register(User, PostAdmin)
# admin.site.register(User)

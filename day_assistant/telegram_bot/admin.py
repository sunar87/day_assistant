from django.contrib import admin

from .models import User as Um


@admin.register(Um)
class UserAdmin(admin.ModelAdmin):
    pass

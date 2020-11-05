from django.contrib import admin
from .models import User

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    exclude = ('password', 'id')
    list_display = ('username', 'last_login', 'is_superuser', 'displayName', 'is_staff', 'is_active', 'date_joined', 'jobTitle', 'mobilePhone')

admin.site.register(User, UserAdmin)

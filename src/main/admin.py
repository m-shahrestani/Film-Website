from .models import Film, Comment
from django.contrib import admin

# Register your models here.
admin.site.register([Film, Comment])
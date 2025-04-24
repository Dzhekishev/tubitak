from django.contrib import admin

# Register your models here.
from myapp .models import*
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

admin.site.register(Camera)


admin.site.register(Page)



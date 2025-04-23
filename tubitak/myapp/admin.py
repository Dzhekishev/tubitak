from django.contrib import admin

# Register your models here.
from myapp .models import*
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

admin.site.register(Camera)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'free', 'full', 'rezervation')


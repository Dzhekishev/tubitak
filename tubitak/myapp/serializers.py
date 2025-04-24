from rest_framework import serializers
from .models import*


class Camera_Serializers(serializers.ModelSerializer):
    class Meta:
        model=Camera
        fields=['id','title','video','time']


class Page_Serializers(serializers.ModelSerializer):
    class Meta:
        model=Page
        fields=['id','camera','free','full','rezervation']


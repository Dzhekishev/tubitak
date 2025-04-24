from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Camera(models.Model):
    title = models.CharField(max_length=255, verbose_name="Isim")
    video = models.ImageField(upload_to='videos/', verbose_name="Video")
    time = models.DateTimeField(auto_now_add=True, verbose_name="Ekleme zamani")
    updated = models.DateTimeField(auto_now=True, verbose_name="Son güncelleme")
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Камера"
        verbose_name_plural = "Камеры"

class Page(models.Model):
    camera = models.ManyToManyField(Camera)
    free = models.PositiveIntegerField(verbose_name="Свободные места")
    full = models.PositiveIntegerField(verbose_name="Занятые места")
    rezervation = models.PositiveIntegerField(verbose_name="Забронированные места")

    def __str__(self):
        return ", ".join([camera.title for camera in self.camera.all()])

    class Meta:
        verbose_name = "Парковка"
        verbose_name_plural = "Парковки"
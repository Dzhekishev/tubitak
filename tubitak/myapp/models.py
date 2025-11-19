from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User


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




class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} – {self.camera.title} ({self.start_time} to {self.end_time})"

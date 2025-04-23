from django.db import models
from django.core.exceptions import ValidationError

class Camera(models.Model):
    title = models.CharField(max_length=255, verbose_name="Isim")
    video = models.FileField(upload_to='videos/', verbose_name="Video")
    time = models.DateTimeField(auto_now_add=True, verbose_name="Ekleme zamani")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Камера"
        verbose_name_plural = "Камеры"gi

class Page(models.Model):
    camera = models.ManyToManyField(Camera)
    free = models.PositiveIntegerField(verbose_name="Свободные места")
    full = models.PositiveIntegerField(verbose_name="Занятые места")
    rezervation = models.PositiveIntegerField(verbose_name="Забронированные места")

    def reserve_spot(self):
            if self.free > 0:
                self.free -= 1
                self.rezervation += 1
                self.save()
                return True
            return False

    def __str__(self):
        return f"Свободные: {self.free}, Занятые: {self.full}, Забронированные: {self.rezervation}"

    class Meta:
        verbose_name = "Парковка"
        verbose_name_plural = "Парковки"
from django.db import models


# Create your models here.

class Film(models.Model):
    name = models.CharField(max_length=50)
    poster = models.CharField(max_length=200)
    director = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} from {self.director}"


class Comment(models.Model):
    text = models.TextField()
    film = models.ForeignKey(Film, on_delete=models.CASCADE)

    def __str__(self):
        return f"comment on {self.film}"

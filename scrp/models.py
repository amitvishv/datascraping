from django.db import models

# Create your models here.
class ScrapData(models.Model):
    objects = None
    scrapped_url = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    empolyername = models.CharField(max_length=100)
    empolyeremail = models.CharField(max_length=100)
    html = models.TextField()

    def __str__(self):
        return self.empolyeremail

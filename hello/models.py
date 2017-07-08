from django.db import models

# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)

class UserTrips(models.Model):
    fbid = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    start = models.DateTimeField('Start Date', auto_now_add=False)
    end = models.DateTimeField('End Date', auto_now_add=False)
    status = models.IntegerField()

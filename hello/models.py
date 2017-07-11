from django.db import models

# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)

class Trips(models.Model):
    fbid = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    start = models.DateTimeField()
    end = models.DateTimeField()
    status = models.IntegerField()

class Locations(models.Model):
    city = models.CharField(max_length=100)
    activity = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    price = models.IntegerField()
    acttype = models.CharField(max_length=100)
    hours = models.CharField(max_length=300)
    time = models.IntegerField()
    book = models.CharField(max_length=50)


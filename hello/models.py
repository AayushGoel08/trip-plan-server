from django.db import models

# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)

class Trips(models.Model):
    fbid = models.CharField(max_length=100)
    tripid = models.IntegerField()
    city = models.CharField(max_length=100)
    start = models.DateTimeField()
    end = models.DateTimeField()
    status = models.IntegerField()
    possibles = models.CharField(max_length=500, blank=True)
    actuals = models.CharField(max_length=500, blank=True)
    actualstime = models.CharField(max_length=500, blank=True)
    homename = models.CharField(max_length=200,blank=True)
    homecoordinates = models.CharField(max_length=200,blank=True)
    homedistances = models.CharField(max_length=500,blank=True)
    group = models.IntegerField()
    

class Locations(models.Model):
    city = models.CharField(max_length=100)
    locid = models.IntegerField()
    activity = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    price = models.IntegerField()
    acttype = models.CharField(max_length=100)
    hours = models.CharField(max_length=300)
    time = models.IntegerField()
    book = models.CharField(max_length=50)
    coordinates = models.CharField(max_length=200)

class Bookings(models.Model):
    fbid = models.CharField(max_length=100)
    tripid = models.IntegerField()
    city = models.CharField(max_length=100)
    locid = models.IntegerField()


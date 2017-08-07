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
    selections = models.CharField(max_length=500, blank=True)
    traversions = models.CharField(max_length=500, blank=True)
    

class Locations(models.Model):
    city = models.CharField(max_length=100)
    locid = models.IntegerField()
    activity = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    price = models.CharField(max_length=500)
    acttype = models.CharField(max_length=100)
    hours = models.CharField(max_length=300)
    time = models.IntegerField()
    book = models.CharField(max_length=50)
    coordinates = models.CharField(max_length=200)
    hashtag = models.CharField(max_length=200)
    deposit = models.CharField(max_length=500)

class Bookings(models.Model):
    fbid = models.CharField(max_length=100)
    tripid = models.IntegerField()
    city = models.CharField(max_length=100)
    locid = models.IntegerField()

class LocStore(models.Model):
    city = models.CharField(max_length=100)
    locid = models.IntegerField()
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    hashtag = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    imagelink = models.CharField(max_length=500)
    time = models.CharField(max_length=500)
    rating = models.CharField(max_length=50)
    price = models.CharField(max_length=500)
    book = models.CharField(max_length=50)
    deposit = models.CharField(max_length=500)
    acttype = models.CharField(max_length=100)
    hours = models.CharField(max_length=300)
    provider = models.CharField(max_length=300)
    website = models.CharField(max_length=300)
    address = models.CharField(max_length=200)
    coordinates = models.CharField(max_length=200)

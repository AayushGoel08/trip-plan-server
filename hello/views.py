from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings

from .models import Greeting
from .models import Trips
from .models import Locations


import json
import datetime
from ilp import *

# Create your views here.
def index(request):
    #string = ilp()
    #return JsonResponse({"data": string})
    if(request.method=='POST'):
        jsonData = request.body.decode("utf-8")
        postData = json.loads(jsonData)
        if(postData["type"]=="ILP"):
            locs = Locations.objects.filter(locid__in = postData["places"], city = "Prague")
            start = datetime.datetime(2017,7,17,9,0)
            end = datetime.datetime(2017,7,18,16,0)
            sleepstart = int((((start+datetime.timedelta(days=1)).replace(hour=1, minute=0)-start).total_seconds()/60))
            timeplaces = []
            staytimeplaces = []
            responses = []
            numduration = triplimit(start,end)
            for loc in locs:
                timeplaces.append(dateconversion(start,end,loc.acttype,loc.hours))
                staytimeplaces.append(loc.time)
                responses.append(loc.locid+"-"+loc.activity+"-"+loc.time)
            response = ilp(sleepstart, postData["home0"], postData["places"],timeplaces,staytimeplaces, numduration[0], numduration[1])
            return JsonResponse({"data": response[0], "found": response[1], "data": responses})
        elif(postData["type"]=="Count"):
            return JsonResponse({"data": Trips.objects.count()})
        elif(postData["type"]=="Insert"):
            insertRecord(postData)
            return JsonResponse({"data": Trips.objects.count()})
        elif(postData["type"]=="DeleteAll"):
            Trips.objects.all().delete()
            return JsonResponse({"data": Trips.objects.count()})
        elif(postData["type"]=="GetData"):
            usertrips = Trips.objects.filter(fbid = postData["fbid"])
            userentries = {"records": [[entry.city,entry.start,entry.end] for entry in usertrips]}
            return JsonResponse({"data": userentries})
        
def db(request):
    if(request.method=='POST'):
        jsonData = request.body.decode("utf-8")
        postData = json.loads(jsonData)
        if(postData["type"]=="Count"):
            return JsonResponse({"data": Locations.objects.count()})
        elif(postData["type"]=="Insert"):
            insertLocationRecord(postData)
            return JsonResponse({"data": Locations.objects.count()})
        elif(postData["type"]=="DeleteAll"):
            Locations.objects.all().delete()
            return JsonResponse({"data": Locations.objects.count()})
    else:
        locations = Locations.objects.all()
        return render(request, 'db.html', {'locations': locations})

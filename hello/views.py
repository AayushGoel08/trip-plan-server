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


def insertTripRecord(postData):
    tripid = Trips.objects.filter(fbid = postData["fbid"],city = postData["city"]).count()+1
    start = datetime.datetime.strptime(postData["start"], "%Y-%m-%d %H:%M")
    end = datetime.datetime.strptime(postData["end"], "%Y-%m-%d %H:%M")
    possibles = ""
    locsdata = []    
    for loc in Locations.objects.filter(city = postData["city"]):
        timepoint = dateconversion(start,end,loc.acttype,loc.hours)
        if(timepoint!=[]):
            possibles = possibles+str(loc.locid)+","
            locsdata.append([loc.locid,loc.activity,loc.price,loc.time])
    possibles = possibles[:-1]
    userTrip = Trips(None,postData["fbid"],int(tripid),postData["city"],postData["start"],postData["end"],1,possibles,"")
    userTrip.save()
    return [locsdata,tripid]
    
    
def insertLocationRecord(postData):
    loc = Locations(None,postData["city"],postData["locid"],postData["activity"],postData["address"],postData["price"],postData["acttype"],postData["hours"],postData["time"],postData["book"])
    loc.save()
    
def index(request):
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
            locids = []
            numduration = triplimit(start,end)
            for loc in locs:
                timeplaces.append(dateconversion(start,end,loc.acttype,loc.hours))
                staytimeplaces.append(loc.time)
                locids.append(loc.locid)
            response = ilp(sleepstart, postData["home0"], locids,timeplaces,staytimeplaces, numduration[0], numduration[1])
            return JsonResponse({"data": response[0], "found": response[1], "ids": locids, "routes": response[2]})

        elif(postData["type"]=="Count"):
            return JsonResponse({"data": Trips.objects.count()})

        elif(postData["type"]=="Insert"):
            locsdata = insertTripRecord(postData)
            return JsonResponse({"locsdata": locsdata[0], "tripid": locsdata[1]})

        elif(postData["type"]=="DeleteAll"):
            Trips.objects.all().delete()
            return JsonResponse({"data": Trips.objects.count()})

        elif(postData["type"]=="GetData"):
            usertrips = Trips.objects.filter(fbid = postData["fbid"])
            userentries = {"records": [[entry.city,entry.start,entry.end, entry.possibles, entry.tripid] for entry in usertrips]}
            return JsonResponse({"data": userentries})

        elif(postData["type"]=="GetAllData"):
            usertrips = Trips.objects.all()
            userentries = {"records": [[entry.fbid, entry.city,entry.start,entry.end, entry.possibles, entry.tripid] for entry in usertrips]}
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

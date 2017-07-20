from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings

from .models import Greeting
from .models import Trips
from .models import Locations
from .models import Bookings

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
    userTrip = Trips(None,postData["fbid"],int(tripid),postData["city"],postData["start"],postData["end"],1,possibles,"","")
    userTrip.save()
    return [locsdata,tripid]
    
    
def insertLocationRecord(postData):
    loc = Locations(None,postData["city"],postData["locid"],postData["activity"],postData["address"],postData["price"],postData["acttype"],postData["hours"],postData["time"],postData["book"], postData["coordinates"])
    loc.save()

def insertBookingRecord(postData):
    booking = Bookings(None,postData["fbid"],postData["tripid"],postData["city"],postData["locid"],0)
    booking.save()
    
def index(request):
    if(request.method=='POST'):
        jsonData = request.body.decode("utf-8")
        postData = json.loads(jsonData)
        if(postData["type"]=="ILP"):
            locs = Locations.objects.filter(locid__in = postData["places"], city = postData["city"])
            userTrip = Trips.objects.get(tripid = postData["tripid"], city = postData["city"], fbid = postData["fbid"])
            start = userTrip.start
            end = userTrip.end
            start = start.replace(tzinfo=None)
            end = end.replace(tzinfo=None)
            sleepstart = int((((start+datetime.timedelta(days=1)).replace(hour=1, minute=0)-start).total_seconds()/60))
            timeplaces = []
            staytimeplaces = []
            locids = []
            locdata = {}
            numduration = triplimit(start,end)
            for loc in locs:
                timeplaces.append(dateconversion(start,end,loc.acttype,loc.hours))
                staytimeplaces.append(loc.time)
                locids.append(loc.locid)
                locdata[loc.locid] = [loc.activity,loc.book,loc.coordinates]
            homeLoc = Locations.objects.get(locid = postData["home0"], city = postData["city"])
            locdata["Home"] = [homeLoc.coordinates]
            response = ilp(sleepstart, postData["home0"], locids,timeplaces,staytimeplaces, numduration[0], numduration[1])
            routeSaveString = ""
            routeSaveTimes = ""
            for i in range(0,len(response[2])-1):
                routeSaveString = routeSaveString + response[2][i]+";"
                routeSaveTimes = routeSaveTimes + response[3][i]+";"
            routeSaveString = routeSaveString + response[2][len(response[2])-1]
            routeSaveTimes = routeSaveTimes + response[3][len(response[3])-1]
            userTrip.actuals = routeSaveString
            userTrip.actualstime = routeSaveTimes
            userTrip.save()
            return JsonResponse({"data": response[0], "found": response[1], "locsdata": locdata, "routes": response[2], "dates": [start, end]})

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
            userentries = {"records": [[entry.fbid, entry.city,entry.start,entry.end, entry.possibles, entry.actuals, entry.actualstime, entry.tripid] for entry in usertrips]}
            return JsonResponse({"data": userentries})
    else:
        trips = Trips.objects.all()
        return render(request, 'index.html', {'trips': trips})
    
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

def bookings(request):
    if(request.method=='POST'):
        jsonData = request.body.decode("utf-8")
        postData = json.loads(jsonData)
        if(postData["type"]=="Count"):
            return JsonResponse({"data": Bookings.objects.count()})

        elif(postData["type"]=="Insert"):
            insertBookingRecord(postData)
            return JsonResponse({"data": Bookings.objects.count()})

        elif(postData["type"]=="DeleteAll"):
            Bookings.objects.all().delete()
            return JsonResponse({"data": Locations.objects.count()})
           
    else:
        bookings = Bookings.objects.all()
        objs = []
        for x in bookings:
            userTrip = Trips.objects.get(tripid = x.tripid, city = x.city, fbid = x.fbid)
            routeArr = userTrip.actuals.split(";")
            routeTimes = userTrip.actualstime.split(";")
            for i in range(0,len(routeArr)):
                routeDay = routeArr[i].split("-")
                routeDayTimes = routeTimes[i].split("-")
                if str(x.locid) in routeDay:
                    ind = routeDay.index(str(x.locid))
                    newdate = userTrip.start + datetime.timedelta(minutes=float(routeDayTimes[ind]))
                    objs.append({"fbid": userTrip.fbid, "city": userTrip.city, "tripid": userTrip.tripid, "locid": x.locid, "date": newdate.strftime("%d-%M-%Y %H:%M")})
        return render(request, 'bookings.html', {'bookings': objs})

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
import requests
from ilp import *

def getPlaces(routeArr):
    places = []
    for route in routeArr:
        routenums = route.split("-")
        for x in routenums:
            if(x!="Home"):
                places.append(int(x))
    return places

def gethomename(postData):
    data = requests.get(postData["url"])
    temp = data.text.split('<th class="hotel_name" colspan="2">')[1].split('<span class="nowrap pb-conf-rating">')[0].strip()
    return temp

def sendhomename(postData):
    userTrip = Trips.objects.get(fbid = postData["fbid"], tripid = postData["tripid"], city = postData["city"])
    userTrip.homename = postData["name"]

    key = "AIzaSyDEt4Ok7w7mo_zOZlT9Y8CI3v6-j9lU8xQ"
    url = "https://maps.googleapis.com/maps/api/geocode/json?address="
    url = url + postData["name"] +"&key=" +key

    data = requests.get(url).json()
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']
    userTrip.status = 1
    userTrip.homecoordinates = str(lat)+ " - " + str(lng)
    userTrip.save()
    return "Home location booked and saved"

def gethomedata(postData):
    key = "AIzaSyDEt4Ok7w7mo_zOZlT9Y8CI3v6-j9lU8xQ"
    url = "https://maps.googleapis.com/maps/api/geocode/json?address="
    url = url + postData["loctext"] + " "+ postData["city"] + "&key=" +key

    data = requests.get(url).json()
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']
    temp = data['results'][0]['formatted_address'].split(", ")
    n = len(temp)-2
    s = []
    s.append(', '.join(temp[:n]))
    s.append(', '.join(temp[n:]))
    return [s[0],s[1],lat,lng]

    
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
    userTrip = Trips(None,postData["fbid"],int(tripid),postData["city"],postData["start"],postData["end"],0,possibles,"","","","","")
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
            userTrip.status = 2
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
            userentries = {"records": [[entry.fbid, entry.city,entry.start,entry.end, entry.status, entry.possibles, entry.actuals, entry.actualstime, entry.tripid] for entry in usertrips]}
            return JsonResponse({"data": userentries})

        elif(postData["type"]=="GetHomeData"):
            return JsonResponse({"data": gethomedata(postData)})

        elif(postData["type"]=="GetHomeName"):
            return JsonResponse({"data": gethomename(postData)})

        elif(postData["type"]=="SendHomeName"):
            return JsonResponse({"data": sendhomename(postData)})

        elif(postData["type"]=="GetTripData"):
            userTrip = Trips.objects.get(fbid = postData["fbid"], tripid = postData["tripid"], city = postData["city"])
            if(userTrip.status==1 or userTrip.status==0):
                locdata = []
                possibles = userTrip.possibles.split(",")
                for i in range(0,len(possibles)):
                    possibles[i] = int(possibles[i])
                for loc in Locations.objects.filter(locid__in = possibles, city = postData["city"]):
                    locdata.append([loc.locid,loc.activity,loc.price,loc.time])
                return JsonResponse({"status": userTrip.status, "locsdata": locdata})
            elif(userTrip.status==2):
                start = userTrip.start
                end = userTrip.end
                start = start.replace(tzinfo=None)
                end = end.replace(tzinfo=None)
                routeArr =  userTrip.actuals.split(";")
                places = getPlaces(routeArr)
                
                locs = Locations.objects.filter(locid__in = places, city = postData["city"])
                locids = []
                locdata = {}
                for loc in locs:
                    locids.append(loc.locid)
                    locdata[loc.locid] = [loc.activity,loc.book,loc.coordinates]
                homeLoc = Locations.objects.get(locid = postData["home0"], city = postData["city"])
                locdata["Home"] = [homeLoc.coordinates]
                return JsonResponse({"status": 2, "locsdata": locdata, "routes": routeArr, "dates": [start, end]})
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
        
        try:    
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

            elif(postData["type"]=="GetAllData"):
                userbooks = Bookings.objects.all()
                userentries = {"records": [[entry.fbid, entry.city,entry.tripid,entry.locid, entry.booked] for entry in userbooks]}
                return JsonResponse({"data": userentries})
        except:
            bookfbid = request.POST.get("fbid", "")
            booktripid = int(request.POST.get("tripid",""))
            bookcity =  request.POST.get("city","")
            booklocids = request.POST.get("locids","").split("-")
            for i in range(0,len(booklocids)):
                booklocids[i] = int(booklocids[i])
            newdates = []
            for i in range(0,int(request.POST.get("count",""))):
                newdates.append(request.POST.get("newdate"+str(i+1),""))
            userTrip = Trips.objects.get(tripid = booktripid, city = bookcity, fbid = bookfbid)
            places = []
            timebooked = []
            oldroutes = userTrip.actuals.split(";")
            for route in oldroutes:
                routenums = route.split("-")
                for x in routenums:
                    if(x!="Home"):
                        places.append(int(x))

            timebooked = []
            for i in range(0,len(places)):
                timebooked.append("N/A")

            for i in range(0,len(booklocids)):
                ind = places.index(booklocids[i])
                timebooked[ind] = newdates[i]
                
            locs = Locations.objects.filter(locid__in = places, city = bookcity)
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
                if(timebooked[places.index(loc.locid)]=="N/A"):
                    timeplaces.append(dateconversion(start,end,loc.acttype,loc.hours))
                else:
                    timeplaces.append([dateconversionsimple(start,timebooked[places.index(loc.locid)])])
                staytimeplaces.append(loc.time)
                locids.append(loc.locid)
                locdata[loc.locid] = [loc.activity,loc.book,loc.coordinates]
            #To change home0 and homeLoc when adding homes facility
            home0 = 9
            homeLoc = Locations.objects.get(locid = home0, city = bookcity)
            locdata["Home"] = [homeLoc.coordinates]
            #To change home0 and homeLoc when adding homes facility 
            response = ilp(sleepstart, home0, locids,timeplaces,staytimeplaces, numduration[0], numduration[1])
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
            return JsonResponse({"data": "New trip booked"})
           
    else:
        bookings = Bookings.objects.all()
        objs = []
        num = 0
        for x in bookings:
            ind = -1
            userTrip = Trips.objects.get(tripid = x.tripid, city = x.city, fbid = x.fbid)
            startdate = userTrip.start.strftime("%d-%b-%Y %H:%M")
            enddate = userTrip.end.strftime("%d-%b-%Y %H:%M")
            activity = Locations.objects.get(city = x.city, locid = x.locid)
            routeArr = userTrip.actuals.split(";")
            routeTimes = userTrip.actualstime.split(";")
            for obj in objs:
                if(obj.fbid==userTrip.fbid and obj.city==userTrip.city and obj.tripid==userTrip.tripid):
                    ind = objs.index(obj)
            if(ind==-1):
                objs.append({"start": startdate, "end": enddate, "fbid": userTrip.fbid, "city": userTrip.city, "tripid": userTrip.tripid, "locidarr": [], "locidstr": "", "activityarr": [], "datearr": [], "newdatenames": [], "bookcount": 0})
                ind = num
                num = num + 1
            
            for i in range(0,len(routeArr)):
                routeDay = routeArr[i].split("-")
                routeDayTimes = routeTimes[i].split("-")
                if str(x.locid) in routeDay:
                    objs[ind]["bookcount"] = objs[ind]["bookcount"] + 1
                    locindex = routeDay.index(str(x.locid))
                    newdate = userTrip.start + datetime.timedelta(minutes=float(routeDayTimes[locindex]))
                    objs[ind]["locidarr"].append(x.locid)
                    objs[ind]["activityarr"].append(activity.activity)
                    objs[ind]["datearr"].append(newdate.strftime("%d-%b-%Y %H:%M"))
                    objs[ind]["newdatenames"].append("newdate"+str(objs[ind]["bookcount"]))

        for obj in objs:
            obj["locidstr"] = '-'.join(str(x) for x in obj["locidarr"])
            return render(request, 'bookings.html', {'bookings': objs})

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings

from .models import Greeting
from .models import Trips
from .models import Locations
from .models import Bookings
from .models import LocStore

import json
import datetime
import requests
from ilp2 import *

def getPlaces(routeArr):
    places = []
    for route in routeArr:
        routenums = route.split("-")
        for x in routenums:
            if(x!="Home"):
                places.append(int(x))
    return places

def gethomedistances(userTrip, lat, lng):
    distances = []
    locs = Locations.objects.filter(city = userTrip.city)
    key = "AIzaSyDEt4Ok7w7mo_zOZlT9Y8CI3v6-j9lU8xQ"
    for i in range(0,len(locs)):
        coordinates = locs[i].coordinates.split(" - ")
        latdest = coordinates[0]
        lngdest = coordinates[1]

        
        string = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="+str(lat)+","+str(lng)+"&destinations="+latdest+","+lngdest+"&mode=walking&key="+key
        data = requests.get(string).json()
        time = data['rows'][0]['elements'][0]['duration']['text'].split(" ")
        timenum = 0
        #Below code assumes x hours y minutes data format
        if(len(time)==2):
            timenum = int(time[0])
        else:
            timenum = (int(time[0])*60) + (int(time[2]))
        distances.append(str(locs[i].locid)+"-"+str(timenum))

    distancestring = ";".join(distances)
    userTrip.homedistances = distancestring
    userTrip.save()
    
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
    gethomedistances(userTrip, lat, lng)
    return "Home location booked and saved"

def savehomename(postData):
    userTrip = Trips.objects.get(fbid = postData["fbid"], tripid = postData["tripid"], city = postData["city"])
    userTrip.homename = postData["name"]
    userTrip.homecoordinates = str(postData["lat"])+ " - " + str(postData["lng"])
    userTrip.status = 1
    userTrip.save()
    gethomedistances(userTrip, postData["lat"], postData["lng"])
    return "Home location saved"

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
    userTrip = Trips(None,postData["fbid"],int(tripid),postData["city"],postData["start"],postData["end"],0,possibles,"","","","","", int(postData["group"]))
    userTrip.save()
    return [locsdata,tripid]
    
    
def insertLocationRecord(postData):
    loc = Locations(None,postData["city"],postData["locid"],postData["activity"],postData["address"],postData["price"],postData["acttype"],postData["hours"],postData["time"],postData["book"], postData["coordinates"])
    loc.save()

def insertBookingRecord(postData):
    booking = Bookings(None,postData["fbid"],postData["tripid"],postData["city"],postData["locid"])
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
            #homeLoc = Locations.objects.get(locid = postData["home0"], city = postData["city"])
            locdata["Home"] = [userTrip.homecoordinates]
            homedurations = {}
            hometemp = userTrip.homedistances.split(";")
            for x in hometemp:
                temp = x.split("-")
                homedurations[temp[0]] = int(temp[1])
            response = ilp(sleepstart, locids,timeplaces,staytimeplaces, numduration[0], numduration[1], homedurations)
            routeSaveString = ""
            routeSaveTimes = ""
            routeDispTimes = []
            for i in range(0,len(response[3])):
                routeDispTimes.append("Home-")
                tempStr = response[3][i].split("-")
                for x in tempStr:
                    if(x!="Home"):
                        dispDate = start+datetime.timedelta(minutes=float(x))
                        dispTime = dispDate.time().strftime("%I:%M %p")
                        routeDispTimes[i] = routeDispTimes[i]+dispTime+"-"
                routeDispTimes[i] = routeDispTimes[i]+"Home"
            for i in range(0,len(response[2])-1):
                routeSaveString = routeSaveString + response[2][i]+";"
                routeSaveTimes = routeSaveTimes + response[3][i]+";"
            routeSaveString = routeSaveString + response[2][len(response[2])-1]
            routeSaveTimes = routeSaveTimes + response[3][len(response[3])-1]
            userTrip.actuals = routeSaveString
            userTrip.actualstime = routeSaveTimes
            userTrip.status = 2
            userTrip.save()
            return JsonResponse({"data": response[0], "found": response[1], "locsdata": locdata, "routes": response[2], "dates": [start, end], "disptimes": routeDispTimes})

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
            userentries = {"records": [[entry.fbid, entry.city,entry.start,entry.end, entry.status, entry.possibles, entry.actuals, entry.actualstime, entry.tripid, entry.homename, entry.homecoordinates, entry.homedistances, entry.group] for entry in usertrips]}
            return JsonResponse({"data": userentries})

        elif(postData["type"]=="GetHomeData"):
            return JsonResponse({"data": gethomedata(postData)})

        elif(postData["type"]=="GetHomeName"):
            return JsonResponse({"data": gethomename(postData)})

        elif(postData["type"]=="SendHomeName"):
            return JsonResponse({"data": sendhomename(postData)})

        elif(postData["type"]=="SaveHomeName"):
            return JsonResponse({"data": savehomename(postData)})

        elif(postData["type"]=="RevertBookings"):
            userTrips = Trips.objects.all()
            for userTrip in userTrips:
                userTrip.status = 2
                userTrip.save()
            return JsonResponse({"data": Trips.objects.count()})
        
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
            elif(userTrip.status>=2):
                start = userTrip.start
                end = userTrip.end
                start = start.replace(tzinfo=None)
                end = end.replace(tzinfo=None)
                routeArr =  userTrip.actuals.split(";")
                routeTimes = userTrip.actualstime.split(";")
                places = getPlaces(routeArr)
                routeDispTimes = []
                for i in range(0,len(routeTimes)):
                    routeDispTimes.append("Home-")
                    tempStr = routeTimes[i].split("-")
                    for x in tempStr:
                        if(x!="Home"):
                            dispDate = start+datetime.timedelta(minutes=float(x))
                            dispTime = dispDate.time().strftime("%I:%M %p")
                            routeDispTimes[i] = routeDispTimes[i]+dispTime+"-"
                    routeDispTimes[i] = routeDispTimes[i]+"Home"
                locs = Locations.objects.filter(locid__in = places, city = postData["city"])
                locids = []
                locdata = {}
                for loc in locs:
                    locids.append(loc.locid)
                    locdata[loc.locid] = [loc.activity,loc.book,loc.coordinates]
                #homeLoc = Locations.objects.get(locid = postData["home0"], city = postData["city"])
                locdata["Home"] = [userTrip.homecoordinates]
                return JsonResponse({"status": 2, "locsdata": locdata, "routes": routeArr, "dates": [start, end], "disptimes": routeDispTimes})
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
                return JsonResponse({"data": Bookings.objects.count()})

            elif(postData["type"]=="GetAllData"):
                userbooks = Bookings.objects.all()
                userentries = {"records": [[entry.fbid, entry.city,entry.tripid,entry.locid] for entry in userbooks]}
                return JsonResponse({"data": userentries})

            elif(postData["type"]=="BookingRequest"):
                userTrip = Trips.objects.get(tripid = int(postData["tripid"]), city = postData["city"], fbid = postData["fbid"])
                if(userTrip.status==3):
                    return JsonResponse({"status": 3, "message": "Already booked"})
                elif(userTrip.status==2):
                    for x in postData["locs"]:
                        datasend = {}
                        datasend["fbid"] = postData["fbid"]
                        datasend["tripid"] = int(postData["tripid"])
                        datasend["city"] = postData["city"]
                        datasend["locid"] = int(x)
                        insertBookingRecord(datasend)
                    userTrip.status = 3
                    userTrip.save()
                    return JsonResponse({"status": 3, "message": "Booking request confirmed"})
            
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
            locdata["Home"] = [userTrip.homecoordinates]
            homedurations = {}
            hometemp = userTrip.homedistances.split(";")
            for x in hometemp:
                temp = x.split("-")
                homedurations[temp[0]] = int(temp[1])

            response = ilp(sleepstart, locids,timeplaces,staytimeplaces, numduration[0], numduration[1], homedurations)
            routeSaveString = ""
            routeSaveTimes = ""
            for i in range(0,len(response[2])-1):
                routeSaveString = routeSaveString + response[2][i]+";"
                routeSaveTimes = routeSaveTimes + response[3][i]+";"
            routeSaveString = routeSaveString + response[2][len(response[2])-1]
            routeSaveTimes = routeSaveTimes + response[3][len(response[3])-1]
            userTrip.actuals = routeSaveString
            userTrip.actualstime = routeSaveTimes
            userTrip.status = 4
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
                if(obj["fbid"]==userTrip.fbid and obj["city"]==userTrip.city and obj["tripid"]==userTrip.tripid):
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

        for i in range(0, len(objs)):
            objs[i]["locidstr"] = '-'.join(str(x) for x in objs[i]["locidarr"])
        return render(request, 'bookings.html', {'bookings': objs})


def entries(request):
    if(request.method=='POST'):
        try:
            jsonData = request.body.decode("utf-8")
            postData = json.loads(jsonData)
            if(postData["type"]=="Count"):
                return JsonResponse({"count": LocStore.objects.count()})

            elif(postData["type"]=="DeleteAll"):
                LocStore.objects.all().delete()
                return JsonResponse({"message": "All objects deleted"})

            elif(postData["type"]=="GetAllData"):
                locs = LocStore.objects.all()
                userentries = {"records": [[loc.city,loc.locid,loc.name,loc.title,loc.hashtag,loc.description,loc.imagelink,loc.time,loc.rating,loc.price,loc.prebook,loc.deposit,loc.acttype,loc.hours,loc.provider,loc.website,loc.address,loc.coordinates] for loc in locs]}
                return JsonResponse({"data": userentries})
        except:
            city = request.POST.get("city", "")
            locid = LocStore.objects.filter(city = request.POST.get("city","")).count()+1
            name = request.POST.get("name", "")
            title = request.POST.get("title", "")
            hashtag = request.POST.get("hashtag", "")
            description = request.POST.get("description", "")
            imagelink = request.POST.get("image", "")
            time = int(request.POST.get("time", ""))
            rating = request.POST.get("rating", "")
            price = int(request.POST.get("price", ""))
            prebook = request.POST.get("prebook", "")
            deposit = 0
            if(request.POST.get("deposit","")!=""):
                deposit = int(request.POST.get("deposit",""))
            acttype = request.POST.get("type", "")
            hours = "-"
            if(acttype!="Unrestricted"):
                hours = request.POST.get("timings", "")
            provider = "-"
            if(request.POST.get("provider","")!=""):
                provider = request.POST.get("provider","")
            website = "-"
            if(request.POST.get("provider","")!=""):
                website = request.POST.get("website","")
            address = "-"
            coordinates = "-"
            loc = LocStore(city,locid,name,title,hashtag,description,imagelink,time,rating,price,prebook,deposit,acttype,hours,provider,website,address,coordinates)
            loc.save()
            return render(request, 'entries.html')
    else:
        return render(request, 'entries.html')

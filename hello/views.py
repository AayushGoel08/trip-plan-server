from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings

from .models import Trips
from .models import Locations
from .models import Bookings
from .models import LocStore
from .models import Distances

import json
import datetime
import hashlib
import random
import requests
from ilp2 import *


def getpaymentlink(postData):
    url = "https://secure.payu.in/_payment"

    amount = postData["amount"]
    randomnum = random.randint(1,10000000)

    txnid = "A-"+str(randomnum)
    productinfo = "Trial Payment"
    firstname = "Aayush"
    key = "V4FnEbRu"
    email = "axgoel8@gmail.com"
    phone = "9910513133"
    surl = "https://trip-plan-router.herokuapp.com"
    furl = "https://trip-plan-router.herokuapp.com/bookings"    
    service_provider = "payu_paisa"
    salt = "LZsDglQTXL"
    string = key+"|"+txnid+"|"+amount+"|"+productinfo+"|"+firstname+"|"+email+"|||||||||||"+salt
    string = string.encode("UTF-8")
    hashstring = hashlib.sha512(bytes(string)).hexdigest()
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = requests.post(url, headers= headers, data={"amount": amount, "txnid": txnid, "productinfo": productinfo, "firstname": firstname, "key": key, "email": email, "phone": phone, "surl": surl, "furl": furl, "service_provider": service_provider, "hash": hashstring})
    return data.url

def getPlaces(routeArr):
    places = []
    for route in routeArr:
        routenums = route.split("-")
        for x in routenums:
            if(x!="Home"):
                places.append(int(x))
    return places

def gethomedistances(userTrip, name):
    distances = []
    locs = LocStore.objects.filter(city = userTrip.city)
    key = "AIzaSyDEt4Ok7w7mo_zOZlT9Y8CI3v6-j9lU8xQ"
    for i in range(0,len(locs)):
        string = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="+name+"&destinations="+locs[i].address+"&mode=walking&key="+key
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

def gethomeforedit(postData):
    userTrip = Trips.objects.get(fbid = postData["fbid"], tripid = postData["tripid"], city = postData["city"])

    key = "AIzaSyDEt4Ok7w7mo_zOZlT9Y8CI3v6-j9lU8xQ"
    url = "https://maps.googleapis.com/maps/api/geocode/json?address="
    url = url + userTrip.homename + "&key=" +key

    data = requests.get(url).json()
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']
    temp = data['results'][0]['formatted_address'].split(", ")
    n = len(temp)-2
    s = []
    s.append(', '.join(temp[:n]))
    s.append(', '.join(temp[n:]))

    homename = userTrip.homename.replace(" "+userTrip.city,"")
    
    locdata = []
    possibles = userTrip.possibles.split(",")
    for i in range(0,len(possibles)):
        possibles[i] = int(possibles[i])
    for loc in LocStore.objects.filter(locid__in = possibles, city = postData["city"]):
        if(loc.acttype=="Occurence"):
            tempprice = str(loc.price).split(", ")
            if(len(tempprice)==1):
                locdata.append([loc.locid,loc.title,int(loc.price),int(loc.time),loc.hashtag,int(loc.deposit),loc.description,loc.imagelink,loc.address,loc.book])
            else:
                minprice = 10000
                pos = 0
                temptime = str(loc.time).split(", ")
                tempdates = loc.hours.split(", ")
                for i in range(0,len(tempprice)):
                    if(datetime.datetime.strptime(x, "%d %B %Y - %H:%M")<userTrip.end):
                        if(int(tempprice[i])<minprice):
                            minprice = tempprice[i]
                            pos = i
                locdata.append([loc.locid,loc.title,int(tempprice[pos]),int(temptime[pos]),loc.hashtag,int(loc.deposit),loc.description,loc.imagelink,loc.address,loc.book])
        else:
            locdata.append([loc.locid,loc.title,int(loc.price),int(loc.time),loc.hashtag,int(loc.deposit),loc.description,loc.imagelink,loc.address,loc.book])
    return {"status": userTrip.status, "locsdata": locdata, "swiperstate": [userTrip.selections, userTrip.traversions], "homedata": [s[0],s[1],lat,lng,homename]}
    

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
    gethomedistances(userTrip, postData["name"])
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
    for loc in LocStore.objects.filter(city = postData["city"]):
        timepoint = dateconversion(start,end,loc.acttype,loc.hours)
        if(timepoint!=[]):
            possibles = possibles+str(loc.locid)+","
            if(loc.acttype=="Occurence"):
                tempprice = str(loc.price).split(", ")
                if(len(tempprice)==1):
                    locsdata.append([loc.locid,loc.title,int(loc.price),int(loc.time),loc.hashtag,int(loc.deposit),loc.description,loc.imagelink,loc.address,loc.book])
                else:
                    minprice = 10000
                    pos = 0
                    temptime = str(loc.time).split(", ")
                    tempdates = loc.hours.split(", ")
                    for i in range(0,len(tempprice)):
                        if(datetime.datetime.strptime(x, "%d %B %Y - %H:%M")<userTrip.end):
                            if(int(tempprice[i])<minprice):
                                minprice = tempprice[i]
                                pos = i
                    locsdata.append([loc.locid,loc.title,int(tempprice[pos]),int(temptime[pos]),loc.hashtag,int(loc.deposit),loc.description,loc.imagelink,loc.address,loc.book])
            else:
                locsdata.append([loc.locid,loc.title,int(loc.price),int(loc.time),loc.hashtag,int(loc.deposit),loc.description,loc.imagelink,loc.address,loc.book])
                
    possibles = possibles[:-1]
    userTrip = Trips(None,postData["fbid"],int(tripid),postData["city"],postData["start"],postData["end"],0,possibles,"","","","","", int(postData["group"]),"","",postData["email"],"")
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
            locs = LocStore.objects.filter(locid__in = postData["places"], city = postData["city"])
            userTrip = Trips.objects.get(tripid = postData["tripid"], city = postData["city"], fbid = postData["fbid"])
            userTrip.paysum = postData["deposit"]
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
                if(loc.acttype=="Occurence"):
                    tempprice = str(loc.price).split(", ")
                    if(len(tempprice)==1):
                        timeplaces.append(dateconversion(start,end,loc.acttype,loc.hours))
                    else:
                        minprice = 10000
                        pos = 0
                        temptime = str(loc.time).split(", ")
                        tempdates = loc.hours.split(", ")
                        for i in range(0,len(tempprice)):
                            if(datetime.datetime.strptime(x, "%d %B %Y - %H:%M")<userTrip.end):
                                if(int(tempprice[i])<minprice):
                                    minprice = tempprice[i]
                                    pos = i
                        timeplaces.append(dateconversion(start,end,loc.acttype,tempdates[pos]))
                else:
                    timeplaces.append(dateconversion(start,end,loc.acttype,loc.hours))
                staytimeplaces.append(int(loc.time))
                locids.append(loc.locid)
                locdata[loc.locid] = [loc.title,loc.book,loc.coordinates,loc.address]
            #homeLoc = Locations.objects.get(locid = postData["home0"], city = postData["city"])
            locdata["Home"] = [userTrip.homecoordinates]
            homedurations = {}
            hometemp = userTrip.homedistances.split(";")
            for x in hometemp:
                temp = x.split("-")
                homedurations[temp[0]] = int(temp[1])
            response = ilp(postData["city"],sleepstart, locids,timeplaces,staytimeplaces, numduration[0], numduration[1], homedurations)
            routeSaveString = ""
            routeSaveTimes = ""
            routeDispTimes = []
            routeCloseTimes = []
            for i in range(0,len(response[3])):
                routeDispTimes.append("Home-")
                routeCloseTimes.append("Home-")
                tempLocs = response[2][i].split("-")
                tempStr = response[3][i].split("-")
                for y in tempLocs:
                    if(y!="Home"):
                        loc = LocStore.objects.get(locid = int(y), city = postData["city"])
                        if(loc.acttype=="Regular"):
                            hour = loc.hours.split(" - ")[1].split(" to ")[1].split(":")
                            closetime = ""
                            if(len(hour)==2):
                                closetime = datetime.time(int(hour[0]),int(hour[1])).strftime("%I:%M %p")
                            else:
                                closetime = datetime.time(int(hour[0]),0).strftime("%I:%M %p")
                            routeCloseTimes[i] = routeCloseTimes[i]+closetime+"-"
                        else:
                            routeCloseTimes[i] = routeCloseTimes[i]+"N/A"+"-"
                    routeCloseTimes[i] = routeCloseTimes[i]+closetime+"Home"
                        
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
            timedata = []
            for i in range(0,len(response[0])):
                timedata.append(str(response[0][i])+"-"+str(response[4][i]))
            return JsonResponse({"data": response[0], "found": response[1], "locsdata": locdata, "routes": response[2], "dates": [start, end], "disptimes": routeDispTimes, "closetime": routeCloseTimes, "intervals": timedata})

        elif(postData["type"]=="Count"):
            return JsonResponse({"data": Trips.objects.count()})

        elif(postData["type"]=="DeleteTrip"):
            userTrip = Trips.objects.get(fbid = postData["fbid"], tripid = postData["tripid"], city = postData["city"])
            userTrip.delete()
            return JsonResponse({"message": "Trip Deleted"})

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
            userentries = {"records": [[entry.fbid, entry.city,entry.start,entry.end, entry.status, entry.possibles, entry.actuals, entry.actualstime, entry.tripid, entry.homename, entry.homecoordinates, entry.homedistances, entry.group, entry.selections, entry.traversions, entry.email, entry.paysum] for entry in usertrips]}
            return JsonResponse({"data": userentries})

        elif(postData["type"]=="GetHomeForEdit"):
            data = gethomeforedit(postData)
            return JsonResponse({"status": data["status"], "locsdata": data["locsdata"], "swiperstate": data["swiperstate"], "homedata": data["homedata"]})

        elif(postData["type"]=="GetHomeData"):
            return JsonResponse({"data": gethomedata(postData)})

        elif(postData["type"]=="GetHomeName"):
            return JsonResponse({"data": gethomename(postData)})

        elif(postData["type"]=="SendHomeName"):
            return JsonResponse({"data": sendhomename(postData)})

        elif(postData["type"]=="SaveHomeName"):
            return JsonResponse({"data": savehomename(postData)})

        elif(postData["type"]=="GetPaymentLink"):
            return JsonResponse({"url": getpaymentlink(postData)})

        elif(postData["type"]=="UpdatePaidStatus"):
            userTrip = Trips.objects.get(fbid = postData["fbid"], tripid = postData["tripid"], city = postData["city"])
            userTrip.status = 5
            userTrip.save()
            return JsonResponse({"data": "Updates performed"})

        elif(postData["type"]=="UpdateSelections"):
            userTrip = Trips.objects.get(fbid = postData["fbid"], tripid = postData["tripid"], city = postData["city"])
            userTrip.selections = "-".join(str(x) for x in postData["selections"])
            userTrip.traversions = "-".join(str(x) for x in postData["traversions"])
            userTrip.save()
            return JsonResponse({"data": "Updates performed"})

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
                for loc in LocStore.objects.filter(locid__in = possibles, city = postData["city"]):
                    if(loc.acttype=="Occurence"):
                        tempprice = str(loc.price).split(", ")
                        if(len(tempprice)==1):
                            locdata.append([loc.locid,loc.title,int(loc.price),int(loc.time),loc.hashtag,int(loc.deposit),loc.description,loc.imagelink,loc.address,loc.book])
                        else:
                            minprice = 10000
                            pos = 0
                            temptime = str(loc.time).split(", ")
                            tempdates = loc.hours.split(", ")
                            for i in range(0,len(tempprice)):
                                if(datetime.datetime.strptime(x, "%d %B %Y - %H:%M")<userTrip.end):
                                    if(int(tempprice[i])<minprice):
                                        minprice = tempprice[i]
                                        pos = i
                            locdata.append([loc.locid,loc.title,int(tempprice[pos]),int(temptime[pos]),loc.hashtag,int(loc.deposit),loc.description,loc.imagelink,loc.address,loc.book])
                    else:
                        locdata.append([loc.locid,loc.title,int(loc.price),int(loc.time),loc.hashtag,int(loc.deposit),loc.description,loc.imagelink,loc.address,loc.book])
                return JsonResponse({"status": userTrip.status, "locsdata": locdata, "swiperstate": [userTrip.selections, userTrip.traversions]})
            elif(userTrip.status>=2):
                start = userTrip.start
                end = userTrip.end
                start = start.replace(tzinfo=None)
                end = end.replace(tzinfo=None)
                routeArr =  userTrip.actuals.split(";")
                routeTimes = userTrip.actualstime.split(";")
                places = getPlaces(routeArr)
                routeDispTimes = []
                routeCloseTimes = []

                for i in range(0,len(routeArr)):
                    routeCloseTimes.append("Home-")
                    tempLocs = routeArr[i].split("-")
                    for y in tempLocs:
                        if(y!="Home"):
                            loc = LocStore.objects.get(locid = int(y), city = postData["city"])
                            if(loc.acttype=="Regular"):
                                hour = loc.hours.split(" - ")[1].split(" to ")[1].split(":")
                                closetime = ""
                                if(len(hour)==2):
                                    closetime = datetime.time(int(hour[0]),int(hour[1])).strftime("%I:%M %p")
                                else:
                                    closetime = datetime.time(int(hour[0]),0).strftime("%I:%M %p")
                                routeCloseTimes[i] = routeCloseTimes[i]+closetime+"-"
                            else:
                                routeCloseTimes[i] = routeCloseTimes[i]+"N/A"+"-"
                        routeCloseTimes[i] = routeCloseTimes[i]+closetime+"Home"
                
                for i in range(0,len(routeTimes)):
                    routeDispTimes.append("Home-")
                    tempStr = routeTimes[i].split("-")
                    for x in tempStr:
                        if(x!="Home"):
                            dispDate = start+datetime.timedelta(minutes=float(x))
                            dispTime = dispDate.time().strftime("%I:%M %p")
                            routeDispTimes[i] = routeDispTimes[i]+dispTime+"-"
                    routeDispTimes[i] = routeDispTimes[i]+"Home"
                locs = LocStore.objects.filter(locid__in = places, city = postData["city"])
                locids = []
                locdata = {}
                for loc in locs:
                    locids.append(loc.locid)
                    locdata[loc.locid] = [loc.title,loc.book,loc.coordinates,loc.address]
                #homeLoc = Locations.objects.get(locid = postData["home0"], city = postData["city"])
                locdata["Home"] = [userTrip.homecoordinates]
                return JsonResponse({"status": userTrip.status, "locsdata": locdata, "routes": routeArr, "dates": [start, end], "disptimes": routeDispTimes, "closetime": routeCloseTimes, "deposit": userTrip.paysum})
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

        elif(postData["type"]=="InsertHashtags"):
            userlocs = Locations.objects.all()
            deposit = ["0","1","2"]
            for entry in userlocs:
                entry.deposit = deposit[(entry.locid%3)]
                entry.save()
            return JsonResponse({"message": "Done"})

        elif(postData["type"]=="GetAllData"):
                userlocs = Locations.objects.all()
                userentries = {"records": [[entry.locid, entry.activity, entry.price, entry.hashtag, entry.deposit] for entry in userlocs]}
                return JsonResponse({"data": userentries})
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
                
            locs = LocStore.objects.filter(locid__in = places, city = bookcity)
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
                    for loc in locs:
                        if(loc.acttype=="Occurence"):
                            tempprice = str(loc.price).split(", ")
                            if(len(tempprice)==1):
                                timeplaces.append(dateconversion(start,end,loc.acttype,loc.hours))
                            else:
                                minprice = 10000
                                pos = 0
                                temptime = str(loc.time).split(", ")
                                tempdates = loc.hours.split(", ")
                                for i in range(0,len(tempprice)):
                                    if(datetime.datetime.strptime(x, "%d %B %Y - %H:%M")<userTrip.end):
                                        if(int(tempprice[i])<minprice):
                                            minprice = tempprice[i]
                                            pos = i
                                timeplaces.append(dateconversion(start,end,loc.acttype,tempdates[pos]))
                        else:
                            timeplaces.append(dateconversion(start,end,loc.acttype,loc.hours))
                else:
                    timeplaces.append([dateconversionsimple(start,timebooked[places.index(loc.locid)])])
                staytimeplaces.append(loc.time)
                locids.append(loc.locid)
                locdata[loc.locid] = [loc.title,loc.book,loc.coordinates,loc.address] 
            locdata["Home"] = [userTrip.homecoordinates]
            homedurations = {}
            hometemp = userTrip.homedistances.split(";")
            for x in hometemp:
                temp = x.split("-")
                homedurations[temp[0]] = int(temp[1])

            response = ilp(userTrip.city, sleepstart, locids,timeplaces,staytimeplaces, numduration[0], numduration[1], homedurations)
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
            activity = LocStore.objects.get(city = x.city, locid = x.locid)
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
                    objs[ind]["activityarr"].append(activity.title)
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

            elif(postData["type"]=="DeleteLoc"):
                userloc = LocStore.objects.get(city=postData["city"],locid=postData["locid"])
                userloc.delete()
                return JsonResponse({"message": "Deleted"})

            elif(postData["type"]=="DeleteTemp"):
                userloc = LocStore.objects.get(city="Amsterd",locid=1)
                userloc.delete()
                return JsonResponse({"message": "Wrong object deleted"})

            elif(postData["type"]=="DeleteAll"):
                LocStore.objects.all().delete()
                return JsonResponse({"message": "All objects deleted"})

            elif(postData["type"]=="GetAllData"):
                locs = LocStore.objects.all()
                userentries = {"records": [[loc.city,loc.locid,loc.name,loc.title,loc.hashtag,loc.description,loc.imagelink,loc.time,loc.rating,loc.price,loc.book,loc.deposit,loc.acttype,loc.hours,loc.provider,loc.website,loc.address,loc.coordinates] for loc in locs]}
                return JsonResponse({"data": userentries})

            elif(postData["type"]=="GetLocData"):
                locs = LocStore.objects.filter(city = postData["city"],locid = postData["locid"])
                userentries = {"records": [[loc.city,loc.locid,loc.name,loc.title,loc.hashtag,loc.description,loc.imagelink,loc.time,loc.rating,loc.price,loc.book,loc.deposit,loc.acttype,loc.hours,loc.provider,loc.website,loc.address,loc.coordinates] for loc in locs]}
                return JsonResponse({"data": userentries})

            elif(postData["type"]=="GetAllCityData"):
                locs = LocStore.objects.filter(city = postData["city"])
                userentries = {"records": [[loc.city,loc.locid,loc.name,loc.title,loc.hashtag,loc.description,loc.imagelink,loc.time,loc.rating,loc.price,loc.book,loc.deposit,loc.acttype,loc.hours,loc.provider,loc.website,loc.address,loc.coordinates] for loc in locs]}
                return JsonResponse({"data": userentries})

            elif(postData["type"]=="GetAllCityTypeData"):
                locs = LocStore.objects.filter(city = postData["city"], acttype=postData["acttype"])
                userentries = {"records": [[loc.city,loc.locid,loc.acttype,loc.hours] for loc in locs]}
                return JsonResponse({"data": userentries})

            elif(postData["type"]=="GetAllDistances"):
                dists = Distances.objects.all()
                userentries = {"records": [[dist.city,dist.originid,dist.destid,dist.distance] for dist in dists]}
                return JsonResponse({"data": userentries})

            elif(postData["type"]=="GetAddresses"):
                locs = LocStore.objects.filter(city = postData["city"])
                key = "AIzaSyDEt4Ok7w7mo_zOZlT9Y8CI3v6-j9lU8xQ"
                url = "https://maps.googleapis.com/maps/api/geocode/json?address="
                for loc in locs:     
                    string = url + loc.name + " "+ postData["city"] + "&key=" +key
                    data = requests.get(string).json()
                    lat = data['results'][0]['geometry']['location']['lat']
                    lng = data['results'][0]['geometry']['location']['lng']
                    address = data['results'][0]['formatted_address']
                    loc.address = address
                    loc.coordinates = str(lat) + " - " + str(lng)
                    loc.save()
                return JsonResponse({"message": "Done"})

            elif(postData["type"]=="GetDistances"):
                key = "AIzaSyDEt4Ok7w7mo_zOZlT9Y8CI3v6-j9lU8xQ"
                locs = LocStore.objects.filter(city = postData["city"])
                for x in locs:
                    for y in locs:
                        string = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="+x.address+"&destinations="+y.address+"&mode=walking&key="+key
                        data = requests.get(string).json()
                        time = data['rows'][0]['elements'][0]['duration']['text'].split(" ")
                        timenum = 0
                        #Below code assumes x hours y minutes data format
                        if(len(time)==2):
                            timenum = int(time[0])
                        else:
                            timenum = (int(time[0])*60) + (int(time[2]))
                        if Distances.objects.filter(city=postData["city"],originid=x.locid, destid=y.locid).exists():
                            dist = Distances.objects.get(city=postData["city"],originid=x.locid, destid=y.locid)
                            dist.distance = timenum
                            dist.save()
                        else:
                            dist = Distances(None,postData["city"],x.locid, y.locid,timenum)
                            dist.save()
                return JsonResponse({"message": "Done"})
                                
        except:
            city = request.POST.get("city", "")
            locid = LocStore.objects.filter(city = request.POST.get("city","")).count()+1
            name = request.POST.get("name", "")
            title = request.POST.get("title", "")
            hashtag = request.POST.get("hashtag", "")
            description = request.POST.get("description", "")
            imagelink = request.POST.get("image", "")
            time = request.POST.get("time", "")
            rating = request.POST.get("rating", "")
            price = request.POST.get("price", "")
            prebook = request.POST.get("prebook", "")
            deposit = "0"
            if(request.POST.get("deposit","")!=""):
                deposit = request.POST.get("deposit","")
            acttype = request.POST.get("type", "")
            hours = "-"
            if(acttype!="Unrestricted"):
                hours = request.POST.get("timings", "")
            provider = "-"
            if(request.POST.get("provider","")!=""):
                provider = request.POST.get("provider","")
            website = "-"
            if(request.POST.get("website","")!=""):
                website = request.POST.get("website","")
            address = "-"
            coordinates = "-"
            loc = LocStore(None,city,locid,name,title,hashtag,description,imagelink,time,rating,price,prebook,deposit,acttype,hours,provider,website,address,coordinates)
            loc.save()
            return render(request, 'entries.html')
    else:
        return render(request, 'entries.html')

def edit(request):
    if(request.method=='POST'):
            userLoc = LocStore.objects.get(locid = int(request.POST.get("locid", "")), city = request.POST.get("city", ""))
            city = request.POST.get("city", "")
            userLoc.name = request.POST.get("name", "")
            userLoc.title = request.POST.get("title", "")
            userLoc.hashtag = request.POST.get("hashtag", "")
            userLoc.description = request.POST.get("description", "")
            userLoc.imagelink = request.POST.get("image", "")
            userLoc.time = request.POST.get("time", "")
            userLoc.rating = request.POST.get("rating", "")
            userLoc.price = request.POST.get("price", "")
            userLoc.prebook = request.POST.get("prebook", "")
            userLoc.deposit = "0"
            if(request.POST.get("deposit","")!=""):
                userLoc.deposit = request.POST.get("deposit","")
            userLoc.acttype = request.POST.get("type", "")
            userLoc.hours = "-"
            if(userLoc.acttype!="Unrestricted"):
                userLoc.hours = request.POST.get("timings", "")
            userLoc.provider = "-"
            if(request.POST.get("provider","")!=""):
                userLoc.provider = request.POST.get("provider","")
            userLoc.website = "-"
            if(request.POST.get("website","")!=""):
                userLoc.website = request.POST.get("website","")
            userLoc.address = "-"
            userLoc.coordinates = "-"
            userLoc.save()
            return render(request, 'edit.html')
    else:
        return render(request, 'edit.html')

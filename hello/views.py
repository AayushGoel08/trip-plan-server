from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings

from .models import Greeting
from .models import UserTrips

from pulp import *
import math
import json
import datetime

def ilp():
    distances = []

    with open("praguedistances.txt") as f:
        distances = f.readlines()
    distances = [x.strip() for x in distances]

    numcount = int(math.sqrt(len(distances)))

    distancemat = []
    for i in range(0,numcount):
        distancemat.append([])
        for j in range(0, numcount):
            distancemat[i].append(0)

    for x in distances:
        content = x.split(",")
        distancemat[int(content[0])-1][int(content[1])-1] = int(content[2])
        
    home0 = 1
    places = [19,24,13,15]
    starttimeplaces = [60,1500,60,1500]
    endtimeplaces = [1980,1980,540,1980]
    staytimeplaces = [229,300,200,60]
    numdays = 2

    locs = []
    locs.append(["home0",home0])
    for x in places:
        locs.append(["place",x])
    for i in range(0,numdays-1):
        locs.append(["homeint",home0])

    timevars = []
    for i in range(0,len(places)+numdays):
        timevars.append(LpVariable("Time"+str(i),0,None))

    binvars = []
    numbins = int((len(places)+numdays-1)*(len(places)+numdays-2)/2)
    for i in range(0,numbins):
        binvars.append(LpVariable("Bin"+str(i),0,1, LpInteger))


    objvar = timevars[len(timevars)-1]

    traveltime = []
    stayhomes = []
    for i in range(0,numdays-1):
        stayhomes.append(LpVariable("Stay home"+str(i),0,None))
						 


    starttimehomes = []
    endtimehomes = []

    for i in range(0,numdays-1):
        starttimehomes.append(720+(1440*i))
        endtimehomes.append(1200+(1440*i))

    M = 10000
    excessdist = 100000

    traveltime = []
    totaltime = []
    for i in range(0,len(locs)):
        traveltime.append([])
        totaltime.append([])
        for j in range(0,len(locs)):
            if(i==j):
                traveltime[i].append(excessdist)
            else:
                traveltime[i].append(distancemat[locs[i][1]-1][locs[j][1]-1])
            if(locs[j][0]=="place"):
                totaltime[i].append(traveltime[i][j]+staytimeplaces[j-1])
            elif(locs[j][0]=="homeint"):
                totaltime[i].append(traveltime[i][j]+stayhomes[j-1-len(places)])
            else:
                totaltime[i].append(traveltime[i][j])

    prob = LpProblem("Travel Time",LpMinimize)
    prob += objvar, "Minimize travel time"
    for i in range(0,len(timevars)-1):
    	prob += timevars[i] >= totaltime[0][i+1], "Visit one city from home "+str(i)
    	prob += timevars[len(timevars)-1] - timevars[i] >= totaltime[i+1][0], "Visit home from one city "+str(i)

    num = 0

    for i in range(1,len(locs)-1):
        for j in range(i+1,len(locs)):
                prob += timevars[j-1]-timevars[i-1]+(M*binvars[num]) <= M - totaltime[i][j], "Prevent sub-tour part A "+str(i)+str(j)
                prob += timevars[i-1]-timevars[j-1]-(M*binvars[num]) <= 0 - totaltime[i][j], "Prevent sub-tour part B "+str(i)+str(j)
                num = num + 1

    for i in range(0,len(starttimeplaces)):
        prob += timevars[i] - staytimeplaces[i] >= starttimeplaces[i], "Start Time for Places "+str(i)
        prob += timevars[i] <= endtimeplaces[i], "End Time for Places "+str(i)

    for i in range(0,numdays-1):
        prob += timevars[len(places)+i] - stayhomes[i] <= starttimehomes[i], "Start Time for Homes "+str(i)
        prob += timevars[len(places)+i] >= endtimehomes[i], "End Time for Homes "+str(i)

	#prob.writeLP("RoutingModel.lp")
    prob.solve()
    if(LpStatus[prob.status]=="Optimal"):
        print("Time = ", value(prob.objective))
        for i in range(0,len(timevars)):
                print(value(timevars[i]))
        return "Solution Found"
    else:
        return "Solution not found"

def insertRecord(postData):
    userTrip = UserTrips(postData["fbid"],postData["city"],postData["start"],postData["end"],1)
    userTrip.save()

# Create your views here.
def index(request):
    #string = ilp()
    #return JsonResponse({"data": string})
    if(request.method=='POST'):
        jsonData = request.body.decode("utf-8")
        postData = json.loads(jsonData)
        if(postData["type"]=="Count"):
            return JsonResponse({"data": UserTrips.objects.count()})
        elif(postData["type"]=="Insert"):
            insertRecord(postData)
            return JsonResponse({"data": "Record Inserted"})

def db(request):
    trips = UserTrips.objects.all()

    return render(request, 'db.html', {'trips': trips})

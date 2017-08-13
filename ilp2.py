from pulp import *
import math
import datetime
import time
import calendar
from operator import itemgetter

def makeroute(numdays,places,times,staytimeplaces):
    routeString = []
    routeTimes = []
    coll = []
    for i in range(0,numdays):
        routeString.append("Home-")
        routeTimes.append("Home-")
    for i in range(0, len(places)):
        coll.append((places[i], times[i], staytimeplaces[i]))
    coll = sorted(coll,key=itemgetter(1))
    for i in range(0, len(coll)):
        ind = int(coll[i][1]//1440)
        routeString[ind] = routeString[ind]+str(coll[i][0])+"-"
        routeTimes[ind] = routeTimes[ind]+str(coll[i][1])+"-"
    for i in range(0,len(routeString)):
        routeString[i] = routeString[i]+ "Home"
        routeTimes[i] = routeTimes[i]+ "Home"
    return [routeString,routeTimes]


def triplimit(start,end):
    durationmin = int((end - start).total_seconds()/60)
    durationdays = int(math.ceil(durationmin/1440))

    return [durationmin,durationdays]

def dateconversionsimple(start,time):
    timeact = datetime.datetime.strptime(time,"%d-%b-%Y %H:%M")
    duration = int((timeact - start).total_seconds()/60)

    return [duration]
    
def dateconversion(start, end, acttype,hours):
    
    durationmin = int((end - start).total_seconds()/60)
    durationdays = int(math.ceil(durationmin/1440))

    timepoints = []
    
    if(acttype=="Slots"):
        data = hours.split(" - ")
        times = []
        days = []
        if(data[0]=="Daily"):
            if(len(data)==2):
                temp = data[1].split(", ")
                for x in temp:
                        x = x.split(":")
                        if(len(x)==2):
                            times.append([int(x[0]),int(x[1])])
                        else:
                            times.append([int(x[0]),0])
                initday = start.date()                
                while(initday<=end.date()):
                        for x in times:
                                initdate = datetime.datetime(initday.year,initday.month,initday.day,x[0],x[1])
                                if(initdate>=start and initdate<end):
                                    timepoints.append([int((initdate - start).total_seconds()/60)])
                                initday = initday + datetime.timedelta(days=1)
            else:
                interval = int(data[2].split(" ")[1])
                temp = data[1].split(" to ")
                starthr = temp[0].split(":")
                endhr = temp[0].split(":")
                initday = start.date()
                while(initday<=end.date()):
                        endtime = ""
                        initdate = ""
                        if(len(starthr)==2):
                                initdate = datetime.datetime(initday.year,initday.month,initday.day,int(starthr[0]),int(starthr[1]))
                        else:
                                initdate = datetime.datetime(initday.year,initday.month,initday.day,int(starthr[0]),0)
                        if(len(endhr)==2):
                                endtime = datetime.datetime(initday.year,initday.month,initday.day,int(endhr[0]),int(endhr[1]))
                        else:
                                endtime = datetime.datetime(initday.year,initday.month,initday.day,int(endhr[0]),0)
                        if(endtime<initdate):
                                endtime = endtime + datetime.timedelta(days=1)
                        while(initdate<endtime):
                                if(initdate>=start and initdate<end):
                                        timepoints.append([int((initdate - start).total_seconds()/60)])
                                initdate = initdate + datetime.timedelta(minutes=interval)
                        initday = initday + datetime.timedelta(days=1)
		
        else:
            daystruct = list(calendar.day_name)
            days = data[0].split(", ")
            for i in range(0, len(days)):
                days[i] = daystruct.index(days[i])
            if(len(data)==2):
                temp = data[1].split(", ")
                for x in temp:
                	x = x.split(":")
                	if(len(x)==2):
                    		times.append([int(x[0]),int(x[1])])
                	else:
                    		times.append([int(x[0]),0])
                initday = start.date()
                while(initday<=end.date()):
                        for x in times:
                                initdate = datetime.datetime(initday.year,initday.month,initday.day,x[0],x[1])
                                if(initdate>=start and initdate<end and initday.weekday() in days):
                                        timepoints.append([int((initdate - start).total_seconds()/60)])
                        initday = initday + datetime.timedelta(days=1)
            else:
                interval = int(data[2].split(" ")[1])
                temp = data[1].split(" to ")
                starthr = temp[0].split(":")
                endhr = temp[0].split(":")
                initday = start.date()
                while(initday<=end.date()):
                        endtime = ""
                        initdate = ""
                        if(len(starthr)==2):
                                initdate = datetime.datetime(initday.year,initday.month,initday.day,int(starthr[0]),int(starthr[1]))
                        else:
                                initdate = datetime.datetime(initday.year,initday.month,initday.day,int(starthr[0]),0)
                        if(len(endhr)==2):
                                endtime = datetime.datetime(initday.year,initday.month,initday.day,int(endhr[0]),int(endhr[1]))
                        else:
                                endtime = datetime.datetime(initday.year,initday.month,initday.day,int(endhr[0]),0)
                        if(endtime<initdate):
                                endtime = endtime + datetime.timedelta(days=1)
                        while(initdate<endtime):
                                if(initdate>=start and initdate<end and initday.weekday() in days):
                                        timepoints.append([int((initdate - start).total_seconds()/60)])
                                initdate = initdate + datetime.timedelta(minutes=interval)
                        initday = initday + datetime.timedelta(days=1)
    elif(acttype=="Regular"):
        data = hours.split(" - ")
        times = []
        days = []
        if(data[0]=="Daily"):
            times = data[1].split(" to ")
            times[0] = times[0].split(":")
            times[1] = times[1].split(":")
            if(len(times[0])==1):
                times[0].append("00")
            if(len(times[1])==1):
                times[1].append("00")
                    
            initday = start.date()
            while(initday<=end.date()):
                    initdate1 = datetime.datetime(initday.year,initday.month,initday.day,int(times[0][0]),int(times[0][1]))
                    initdate2 = datetime.datetime(initday.year,initday.month,initday.day,int(times[1][0]),int(times[1][1]))
                    if(initdate2<initdate1):
                        initdate2 = initdate2 + datetime.timedelta(days=1)
                    if(initdate1>=start and initdate1<end):
                        if(initdate2<end):    
                            timepoints.append([int((initdate1 - start).total_seconds()/60),int((initdate2 - start).total_seconds()/60)])
                        else:
                            timepoints.append([int((initdate1 - start).total_seconds()/60),durationmin])
                    initday = initday + datetime.timedelta(days=1)
        else:
            daystruct = list(calendar.day_name)
            days = data[0].split(", ")
            for i in range(0, len(days)):
                days[i] = daystruct.index(days[i])
            times = data[1].split(" to ")
            times[0] = times[0].split(":")
            times[1] = times[1].split(":")
            if(len(times[0])==1):
                times[0].append("00")
            if(len(times[1])==1):
                times[1].append("00")
                    
            initday = start.date()
            while(initday<=end.date()):
                    initdate1 = datetime.datetime(initday.year,initday.month,initday.day,int(times[0][0]),int(times[0][1]))
                    initdate2 = datetime.datetime(initday.year,initday.month,initday.day,int(times[1][0]),int(times[1][1]))
                    if(initdate2<initdate1):
                        initdate2 = initdate2 + datetime.timedelta(days=1)
                    if(initdate1>=start and initdate1<end and initday.weekday() in days):
                        if(initdate2<end):    
                            timepoints.append([int((initdate1 - start).total_seconds()/60),int((initdate2 - start).total_seconds()/60)])
                        else:
                            timepoints.append([int((initdate1 - start).total_seconds()/60),durationmin])
                    initday = initday + datetime.timedelta(days=1)
    elif(acttype=="Occurence"):
        datatemp = hours.split(", ")
        data = []
        for y in datatemp:
                temp = y.split(" - ")
                entrytime = temp[1]

                if(len(entrytime.split(":"))==1):
                        entrytime = entrytime + ":00"
                datesplit = temp[0].split(" ")
                entrydays = datesplit[0].split("+")
                for z in entrydays:
                        data.append(z+" "+datesplit[1]+" "+datesplit[2]+" - "+entrytime)
        for x in data:
            initdate = datetime.datetime.strptime(x, "%d %B %Y - %H:%M")
            if(initdate>=start and initdate <end):
                timepoints.append([int((initdate - start).total_seconds()/60)])
    elif(acttype=="Unrestricted"):
        timepoints.append([0,durationmin])
    elif(acttype=="Duration"):
        data = hours.split(" - ")
        times = []
        days = []
        times = data[1].split(" to ")
        times[0] = times[0].split(":")
        times[1] = times[1].split(":")
        if(len(times[0])==1):
            times[0].append("00")
        if(len(times[1])==1):
            times[1].append("00")

        days = data[0].split(" to ")
        initday = datetime.datetime.strptime(days[0], "%d %B %Y").date()
        lastday = datetime.datetime.strptime(days[1], "%d %B %Y").date()
        while(initday<=end.date()and initday<=lastday):
            initdate1 = datetime.datetime(initday.year,initday.month,initday.day,int(times[0][0]),int(times[0][1]))
            initdate2 = datetime.datetime(initday.year,initday.month,initday.day,int(times[1][0]),int(times[1][1]))
            if(initdate2<initdate1):
                initdate2 = initdate2 + datetime.timedelta(days=1)
            if(initdate1>=start and initdate1<end):
                if(initdate2<end):    
                    timepoints.append([int((initdate1 - start).total_seconds()/60),int((initdate2 - start).total_seconds()/60)])
                else:
                    timepoints.append([int((initdate1 - start).total_seconds()/60),durationmin])
            initday = initday + datetime.timedelta(days=1)
    return timepoints

                
def ilp(city,sleepstart, places, timeplaces, staytimeplaces, duration, numdays, homedurations):
    distances = []

    with open(city+"distances.txt") as f:
        distances = f.readlines()
    distances = [x.strip() for x in distances]

    numcount = int(math.sqrt(len(distances)))
    indextracker = {}
    for i in range(0,numcount):
        content = distances[i].split(",")
        indextracker[content[1]] = i+1

    distancemat = []
    for i in range(0,numcount):
        distancemat.append([])
        for j in range(0, numcount):
            distancemat[i].append(0)

    for x in distances:
        content = x.split(",")
        distancemat[indextracker[content[0]]-1][indextracker[content[1]]-1] = int(content[2])
        
    locs = []
    locs.append(["home0",0])
    for x in places:
        locs.append(["place",x])
    for i in range(0,numdays-1):
        locs.append(["homeint",0])

    starttimevars = []
    endtimevars = []
    for i in range(0,len(places)+numdays):
       starttimevars.append(LpVariable("StartTime"+str(i),0,None))
    for i in range(0,len(places)+numdays):
       endtimevars.append(LpVariable("EndTime"+str(i),0,None))

    binvars = []
    numbins = int((len(places)+numdays-1)*(len(places)+numdays-2)/2)
    for i in range(0,numbins):
        binvars.append(LpVariable("Bin"+str(i),0,1, LpInteger))


    objvar = endtimevars[len(endtimevars)-1]

    traveltime = []    

    starttimehomes = []
    endtimehomes = []

    for i in range(0,numdays-1):
        starttimehomes.append(sleepstart+(1440*i))
        endtimehomes.append(sleepstart+360+(1440*i))

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
            elif(locs[i][0]=="home0"):
                if(locs[j][0]=="homeint"):
                    traveltime[i].append(1)
                else:
                    traveltime[i].append(homedurations[str(locs[j][1])])
            elif(locs[i][0]=="homeint"):
                if(locs[j][0]=="home0"):
                    traveltime[i].append(1)
                else:
                    traveltime[i].append(homedurations[str(locs[j][1])])
            else:
                if(locs[j][0]=="home0"):
                    traveltime[i].append(homedurations[str(locs[i][1])])
                elif(locs[j][0]=="homeint"):
                    traveltime[i].append(homedurations[str(locs[i][1])])
                else:
                    traveltime[i].append(distancemat[indextracker[str(locs[i][1])]-1][indextracker[str(locs[j][1])]-1])
            #if(locs[j][0]=="place"):
            #    totaltime[i].append(traveltime[i][j]+staytimeplaces[j-1])
            #elif(locs[j][0]=="homeint"):
            #    totaltime[i].append(traveltime[i][j]+stayhomes[j-1-len(places)])
            #else:
            #    totaltime[i].append(traveltime[i][j])
    #print(traveltime)
    prob = LpProblem("Travel Time",LpMinimize)
    prob += objvar, "Minimize travel time"

    prob += endtimevars[len(endtimevars)-1] <= duration, "Time limit constraint"
    for i in range(0,len(endtimevars)):
        if(i in range(0, len(places))):
           prob += endtimevars[i] - starttimevars[i] >= staytimeplaces[i], "Stay at place greater than required "+str(i)
        else:
           prob += endtimevars[i] >= starttimevars[i], "Stay at place greater than required "+str(i)
        
    for i in range(0,len(endtimevars)-1):
    	prob += starttimevars[i] >= traveltime[0][i+1], "Visit one city from home "+str(i)
    	prob += starttimevars[len(endtimevars)-1] - endtimevars[i] >= traveltime[i+1][0], "Visit home from one city "+str(i)

    num = 0

    for i in range(1,len(locs)-1):
        for j in range(i+1,len(locs)):
                prob += starttimevars[j-1]- endtimevars[i-1]+(M*binvars[num]) <= M - traveltime[i][j], "Prevent sub-tour part A "+str(i)+str(j)
                prob += endtimevars[i-1]- starttimevars[j-1]-(M*binvars[num]) <= 0 - traveltime[i][j], "Prevent sub-tour part B "+str(i)+str(j)
                if((i-1 in range(0,len(staytimeplaces))) and (j-1 in range(0,len(staytimeplaces)))):
                    prob += endtimevars[j-1]-endtimevars[i-1]+(M*binvars[num]) <= M - (traveltime[i][j]+staytimeplaces[j-1]), "Prevent sub-tour part C "+str(i)+str(j)
                    prob += endtimevars[i-1]-endtimevars[j-1]-(M*binvars[num]) <= 0 - (traveltime[i][j]+staytimeplaces[j-1]), "Prevent sub-tour part D "+str(i)+str(j)
                    prob += starttimevars[j-1]-starttimevars[i-1]+(M*binvars[num]) <= M - (traveltime[i][j]+staytimeplaces[j-1]), "Prevent sub-tour part E "+str(i)+str(j)
                    prob += starttimevars[i-1]-starttimevars[j-1]-(M*binvars[num]) <= 0 - (traveltime[i][j]+staytimeplaces[j-1]), "Prevent sub-tour part F "+str(i)+str(j)
                num = num + 1

    #for i in range(0,len(starttimeplaces)):
        #prob += timevars[i] - staytimeplaces[i] >= starttimeplaces[i], "Start Time for Places "+str(i)
        #prob += timevars[i] <= endtimeplaces[i], "End Time for Places "+str(i)
    bintimeplaces = []
    for i in range(0,len(timeplaces)):
        bintimeplaces.append([])
        for j in range(0,len(timeplaces[i])):
                bintimeplaces[i].append(LpVariable("BinOr"+str(i)+str(j),0,1, LpInteger))
        
    for i in range(0,len(timeplaces)):
        sum0 = 0
        sum1 = 0
        sumbin = 0
        probtype = 0
        for j in range(0,len(timeplaces[i])):
            if(len(timeplaces[i][j])==1):
                probtype = 1
                sum0 = sum0 + (timeplaces[i][j][0]*bintimeplaces[i][j])
                sumbin = sumbin + bintimeplaces[i][j]
            else:
                probtype = 2
                sum0 = sum0 + (timeplaces[i][j][0]*bintimeplaces[i][j])
                sum1 = sum1 + (timeplaces[i][j][1]*bintimeplaces[i][j])
                sumbin = sumbin + bintimeplaces[i][j]
                
                
        if(probtype==1):
            prob += starttimevars[i] == sum0, "Start Time for Places "+str(i)
            prob += sumbin == 1, "Sum Ors for Places "+str(i)
        else:
            prob += starttimevars[i] >= sum0, "Start Time for Places "+str(i)
            prob += endtimevars[i] <= sum1, "End Time for Places "+str(i)
            prob += sumbin == 1, "Sum Ors for Places "+str(i)
            

    for i in range(0,numdays-1):
        #prob += starttimevars[len(places)+i] >= starttimehomes[i], "Start Time for Homes "+str(i)
        prob += endtimevars[len(places)+i] >= endtimehomes[i], "End Time for Homes "+str(i)

    #prob.writeLP("RoutingModel.lp")
    prob.solve()
    if(LpStatus[prob.status]=="Optimal"):
        #print("Time = ", value(prob.objective))
        times = [value(x) for x in starttimevars]
        endtimes = [value(x) for x in endtimevars]
        routeString = makeroute(numdays, places,times,staytimeplaces)
        return [times,"Solution Found", routeString[0],routeString[1],endtimes]
    else:
        return [[],"Solution not found"]

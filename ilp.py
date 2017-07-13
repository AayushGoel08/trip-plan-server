from pulp import *
import math
import datetime
import time
import calendar

def triplimit(start,end):
    durationmin = int((end - start).total_seconds()/60)
    durationdays = int(math.ceil(durationmin/1440))

    return [durationmin,durationdays]

def dateconversion(start, end, acttype,hours):
    
    durationmin = int((end - start).total_seconds()/60)
    durationdays = int(math.ceil(durationmin/1440))

    timepoints = []
    
    if(acttype=="Slots"):
        data = hours.split(" - ")
        times = []
        days = []
        if(data[0]=="Daily"):
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
            daystruct = list(calendar.day_name)
            days = data[0].split(", ")
            for i in range(0, len(days)):
                days[i] = daystruct.index(days[i])
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
        data = hours.split(", ")
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

                
def ilp(sleepstart, home0, places, timeplaces, staytimeplaces, duration, numdays):
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
            else:
                traveltime[i].append(distancemat[locs[i][1]-1][locs[j][1]-1])
            if(locs[j][0]=="place"):
                totaltime[i].append(traveltime[i][j]+staytimeplaces[j-1])
            elif(locs[j][0]=="homeint"):
                totaltime[i].append(traveltime[i][j]+stayhomes[j-1-len(places)])
            else:
                totaltime[i].append(traveltime[i][j])
    #print(traveltime)
    prob = LpProblem("Travel Time",LpMinimize)
    prob += objvar, "Minimize travel time"
    for i in range(0,len(timevars)-1):
    	prob += timevars[i] >= totaltime[0][i+1], "Visit one city from home "+str(i)
    	prob += timevars[len(timevars)-1] - timevars[i] >= totaltime[i+1][0], "Visit home from one city "+str(i)

    num = 0

    for i in range(1,len(locs)-1):
        for j in range(i+1,len(locs)):
                if((i-1 in range(0,len(staytimeplaces))) and (j-1 in range(0,len(staytimeplaces)))):
                    prob += timevars[j-1]-timevars[i-1]-staytimeplaces[j-1]+staytimeplaces[i-1]+(M*binvars[num]) <= M - totaltime[i][j], "Prevent sub-tour part C "+str(i)+str(j)
                prob += timevars[j-1]-timevars[i-1]+(M*binvars[num]) <= M - totaltime[i][j], "Prevent sub-tour part A "+str(i)+str(j)
                prob += timevars[i-1]-timevars[j-1]-(M*binvars[num]) <= 0 - totaltime[i][j], "Prevent sub-tour part B "+str(i)+str(j)
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
            prob += timevars[i] - staytimeplaces[i] == sum0, "Start Time for Places "+str(i)
            prob += sumbin == 1, "Sum Ors for Places "+str(i)
        else:
            prob += timevars[i] - staytimeplaces[i] >= sum0, "Start Time for Places "+str(i)
            prob += timevars[i] <= sum1, "End Time for Places "+str(i)
            prob += sumbin == 1, "Sum Ors for Places "+str(i)
            

    for i in range(0,numdays-1):
        prob += timevars[len(places)+i] - stayhomes[i] >= starttimehomes[i], "Start Time for Homes "+str(i)
        prob += timevars[len(places)+i] <= endtimehomes[i], "End Time for Homes "+str(i)

    #prob.writeLP("RoutingModel.lp")
    prob.solve()
    if(LpStatus[prob.status]=="Optimal"):
        #print("Time = ", value(prob.objective))
        times = [value(x) for x in timevars]
        return [times,"Solution Found"]
    else:
        return [[],"Solution not found"]


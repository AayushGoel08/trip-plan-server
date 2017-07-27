from pulp import *
import math
import datetime
import time
import calendar

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


    objvar = duration - endtimevars[len(endtimevars)-1]

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
            else:
                traveltime[i].append(distancemat[locs[i][1]-1][locs[j][1]-1])
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

    prob.writeLP("RoutingModel.lp")
    prob.solve()
    if(LpStatus[prob.status]=="Optimal"):
        print("Time = ", value(prob.objective))
        for i in range(0,len(endtimevars)):
            print(value(starttimevars[i]) ,"-",value(endtimevars[i]))
        return "Solution Found"
    else:
        return "Solution not found"

locs = [["Skydiving","Dlouhá 612/6, 110 00 Staré Město, Czechia",250,"Slots","Daily - 9, 10, 11, 12, 13, 14, 15, 16",180,"Yes"],["Shooting","Vinohradská 2279/164, 130 00 Praha 3, Czechia",50,"Slots","Monday, Tuesday, Wednesday, Thursday, Friday, Saturday - 10, 11, 12, 13, 14, 15",180,"Yes"],["John Lennon Wall","Velkopřevorské náměstí, Malá Strana, 100 00 Praha 1, Czechia",0,"Unrestricted","-",30,"No"],["Sex Machines Museum","Melantrichova 476/18, 110 00 Praha 1-Staré Město, Czechia",10,"Regular","Daily - 10 to 23",60,"No"],["Museum of Torture","Celetná 558/12, 110 00 Staré Město, Czechia",10,"Regular","Daily - 10 to 20",60,"No"],["Pub-crawl","Celetná 558/12, 110 00 Staré Město, Czechia",22,"Slots","Daily - 19:45, 20:45",240,"Yes"],["Ice Bar","200 1, Novotného lávka 200/5, 110 00 Praha 1-Staré Město, Czechia",12,"Regular","Daily - 12 to 5",60,"No"],["Top of old town hall tower","Staroměstské nám. 1/3, 110 00 Praha 1-Staré Město, Czechia",10,"Regular","Daily - 11 to 22",60,"No"],["Astronomical Clock at 'o clock","Staroměstské nám. 1/4, 110 00 Praha 1-Staré Město, Czechia",0,"Unrestricted","-",20,"No"],["Beer Museum","Smetanovo nábř. 205/22, 110 00 Praha 1-Staré Město, Czechia",11,"Regular","Daily - 10 to 20",60,"No"],["Drink becherovka - Prague's local drink","Přemyslovská 2845/43, 130 00 Praha 3, Czechia",5,"Regular","Daily - 8 to 22",10,"No"],["Lego Museum","Národní 362/31, 110 00 Praha 1-Staré Město-Staré Město, Czechia",8,"Regular","Daily - 10 to 20",60,"No"],["U Pinkasů restaurant - Pilsner Urquell tasting room","Jungmannovo nám. 15/16, 110 00 Praha 1-Můstek, Czechia",10,"Regular","Daily - 10 to 23:30",60,"No"],["Museum of Instruments","Karmelitská 388/2, 118 00 Praha 1-Malá Strana, Czechia",5,"Regular","Monday, Wednesday, Thursday, Friday, Saturday, Sunday - 10 to 18",90,"No"],["Museum of Alchemists and Magicians of Old Prague","Jánský vršek 8, 118 00 Praha 1-Malá Strana, Czechia",7.5,"Regular","Daily - 10 to 20",90,"No"],["Museum of Miniatures","Strahovské nádvoří 11, 118 00 Praha 1, Czechia",4,"Regular","Daily - 9 to 17",90,"No"],["Hot Cholcolate at Café Kaficko","Maltézské nám. 473/15, 118 00 Praha 1-Malá Strana, Czechia",5,"Regular","Daily - 10 to 20",90,"No"],["Panorama of Prague from Letna Park","170 00 Prague 7, Czechia",0,"Unrestricted","-",60,"No"],["Eat a Trdelnik","Karlova 190/1, 110 00 Praha 1-Staré Město, Czechia",3,"Regular","Daily - 10 to 22",30,"No"],["Communism and Nuclear Bunker Tour","Malé nám. 11, 110 00 Praha 1-Staré Město, Czechia",23,"Slots","Daily - 10:30, 14:30",120,"No"],["Glance at the Dancing House","Jiráskovo nám. 1981/6, 120 00 Praha 2-Nové Město, Czechia",0,"Unrestricted","-",10,"No"],["Mind Maze Escape Game","Tyršova 9, 120 00 Praha 2-Nové Město, Czechia",23,"Regular","Daily - 10:30 to 22",90,"Yes"],["Drink Absinthe","Jilská 7, 110 00 Praha-Staré Město, Czechia",10,"Regular","Daily - 12 to 0",60,"No"],["Clubbing at Klub Karlovy Lazne","Smetanovo nábř. 198/1, 110 00 Staré Město, Czechia",6,"Regular","Daily - 21 to 5",180,"No"],["Prague beer and food tour","New Town, 110 00 Prague 1, Czechia",55,"Slots","Daily - 17",240,"Yes"],["Take a stroll across the Charles Bridge","Karlův most, 110 00 Praha 1, Czechia",0,"Unrestricted","-",20,"No"],["Off Road Quad Bikes","Dlouhá 705/16, 110 00 Praha 1-Staré Město, Czechia",70,"Slots","Daily - 10, 12:30, 15",150,"Yes"],["Four seasons vivaldi concert","Karlova 183/14, 110 00 Staré Město, Czechia",24,"Occurrence","11 July 2017 - 19, 12 July 2017 - 19,  15 July - 19, 17 July 2017 - 19, 18 July 2017 - 19",65,"Yes"],["Swan Lake ballet","nám. Republiky 3/4, 110 00 Praha 1-Nové Město, Czechia",35,"Occurrence","13 July 2017 - 15, 15 July 2017 - 15,  17 July 2017 - 15, 19 July 2017 - 15, 21 July 2017 - 15",65,"Yes"],["System of a down concert","Českomoravská 2345/17, 190 00 Praha 9, Czechia",70,"Occurrence","19 July 2017 - 13",180,"Yes"],["Foo fighters concert","Českomoravská 2345/17, 190 00 Praha 9, Czechia",75,"Occurrence","18 July 2017 - 20",180,"Yes"],["Romeo and Juliet ballet","Národní 2, 110 00 Nové Město, Czechia",35,"Occurrence","18 August 2017 - 20:30, 20 August 2017 - 20:30, 25 August 2017 - 20:30, 27 August 2017 - 20:30, 2 September 2017 - 19:30",100,"Yes"],["Phantom - Black Light theatre","Karoliny Světlé 286/18, 110 00 Praha 1-Staré Město, Czechia",22,"Slots","Tuesday, Thursday, Friday, Saturday - 20",90,"Yes"],["Mini Beer festival","Mariánské hradby, 118 00 Praha 1, Czechia",10,"Duration","17 July 2017 to 18 July 2017 - 9 to 17",120,"No"],["Metronome festival","Výstaviště, 170 00 Praha 7, Czechia",105,"Duration","23 July 2017 to 24 July 2017 - 13 to 5",240,"Yes"],["Petrin Tower and view from top","Petřínské sady, 118 00 Praha 1, Czechia",6,"Regular","Daily - 10 to 22",60,"No"],["Palladium shopping centre prague","nám. Republiky 1, 110 00 Nové Město, Czechia",20,"Regular","Daily - 9 to 21",90,"No"],["KGB Museum","Vlašská 591/13, 118 00 Malá Strana, Czechia",10,"Regular","Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday - 10 to 17",60,"No"],["Museum of Chamber pots and toilets","Michalská 429/1, 110 00 Staré Město, Czechia",6,"Regular","Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday - 10 to 18",60,"No"],["Lobkowicz palace","Jiřská 3, 119 00 Praha 1, Czechia",11,"Regular","Daily - 10 to 18",60,"No"]]

start = datetime.datetime(2017,7,17,9,0)
end = datetime.datetime(2017,7,18,16,0)
sleepstart = int((((start+datetime.timedelta(days=1)).replace(hour=1, minute=0)-start).total_seconds()/60))
timeplaces = []
staytimeplaces = []
home0 = 9


places = [1,2,3,4,7,15,16,17,18,37,40]
timebooked = ["17-Jul-2017 11:00","","","","","","","","","",""]
#places = [1,3,4,7]
numduration = triplimit(start,end)
print(numduration[0])
for i in places:
    if(timebooked[places.index(i)]==""):
        timeplaces.append(dateconversion(start,end,locs[i-1][3],locs[i-1][4]))
    else:
        timeplaces.append([dateconversionsimple(start,timebooked[places.index(i)])])
    staytimeplaces.append(locs[i-1][5])
print(sleepstart)
print(timeplaces)
print(staytimeplaces)
print(ilp(sleepstart, home0, places,timeplaces,staytimeplaces, numduration[0], numduration[1]))

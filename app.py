from flask import Flask
from flask import request
import aiohttp
import asyncio
import requests
import pdb
import json
import csv
import time
import datetime
from android_script import get_coordinates

app = Flask(__name__)


BASE_URL = "https://data.smartdublin.ie/cgi-bin/rtpi"
stop_endpoint = "/busstopinformation"
real_endpoint = "{}/realtimebusinformation?stopid=".format(BASE_URL)
urls_bus = []
urls_luas = []
urls_rail = []

        
def csvsaver(csvname,itemlist):


    with open(csvname, 'w') as f:
        
        print(len(itemlist))
        temp = json.loads(itemlist[5])
        results_dict = temp['results'][0]
        results_dict["stopid"] = 0
        w = csv.DictWriter(f,results_dict.keys())
        w.writeheader()

        for item in itemlist:

            jsonitem = json.loads(item)
            #w.writerow({})

            x = 0

            while x < jsonitem['numberofresults']:
                

                results_dict = jsonitem['results'][x]
                results_dict["stopid"] = jsonitem["stopid"]

                w.writerow(results_dict)
                x = x + 1



async def fetch(session, url, sema):
    async with sema, session.get(url) as response:
        return await response.text()

async def updatedata(urls,csvname):
    
    tasks = []
    sema = asyncio.BoundedSemaphore(value=500)
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch(session, url, sema))
        
        responses = await asyncio.gather(*tasks)

    csvsaver(csvname,responses)
    

@app.route("/busroutes")
def busroutes():
    

    routeID = request.args.get("route", default = "NA", type = str)
    operator = request.args.get("operator",default = "NA",type = str)

    if (routeID == "NA") or (operator == "NA"):
        return ('Bad Request',400)
    


    stopresponse = requests.get("https://data.smartdublin.ie/cgi-bin/rtpi/routeinformation?routeid={}&operator={}".format(routeID,operator))
    stops = stopresponse.json()

    if(stops['errorcode'] != "0"):
        return ('Server Error',500)


    #pdb.set_trace()
    return(stops)

@app.route("/status")
def status():
    
    currentDT = datetime.datetime.now()
    currentMinute = currentDT.minute
    statusDict={}

    if currentMinute >= 0 and currentMinute < 15:
        statusDict['bus'] = True
        statusDict['luas'] = True

    if (currentMinute >= 15 ) and (currentMinute < 30):
        statusDict['bus'] = False
        statusDict['luas'] = True

    if (currentMinute >= 30 ) and (currentMinute < 45):
        statusDict['bus'] = True
        statusDict['luas'] = False
	
    if (currentMinute >= 45 ) and (currentMinute < 60):
        statusDict['bus'] = False
        statusDict['luas'] = False

    statusjson = json.dumps(statusDict)
    return(statusjson)


@app.route("/getcoords")
def getcoords():
    #http://127.0.0.1:5000/getcoords?latstart=53.2815126&longstart=-6.2341631&latend=53.3881208173444&longend=-6.2659470210&case=0
    #http://127.0.0.1:5000/getcoords?latstart=53.2965476&longstart=-6.2201313&latend=53.2996109&longend=-6.2178796&case=0

    latstart = request.args.get("latstart", default = 53.2815126, type = float)
    longstart = request.args.get("longstart",default = -6.2341631,type = float)   
    latend = request.args.get("latend", default = 53.3881208173444, type = float)
    longend = request.args.get("longend",default = -6.2659470210,type = float) 
    usercase = request.args.get("case",default = 0,type = int)
    coords = get_coordinates((latstart, longstart),(latend, longend), usercase, 'full_graph.json')

    return(coords)


     
@app.route('/update')              
def update():


    #pdb.set_trace()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(updatedata(urls_rail,"rail.csv"))
    print("Done rails")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(updatedata(urls_luas,"luas.csv"))
    print("Done luas")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(updatedata(urls_bus,"bus.csv"))
    print("Done bus")


    return ('',204)
    



@app.route('/luas')
def luas():
    f = open("luas.csv","r")
    if f.mode == 'r':
        contents = f.read()
        return contents
        
    return ('',502)
    
@app.route('/bus')
def bus():
    f = open("bus.csv","r")
    if f.mode == 'r':
        contents = f.read()
        return contents
        
    return ('',502)
    
@app.route('/rail')
def rail():
    f = open("rail.csv","r")
    if f.mode == 'r':
        contents = f.read()
        return contents
        
    return ('',502)

@app.before_first_request  
def stopinit():

    #get all stop locations etc
    stop_list_luas = []
    stop_list_bus = []
    stop_list_rail = []
    stopresponse = requests.get(BASE_URL + stop_endpoint)
    stops = stopresponse.json()

    #Filter stops to dublin and sort to different lists
    for stop in stops['results']:
        lat = float(stop['latitude'])
        lon = float(stop['longitude'])
        op = stop['operators'][0]['name']


        if lat < 53.4408 and lat > 53.21032:    
            if lon > -6.56434:
                if op == 'LUAS':
                    stop_list_luas.append(stop['stopid'])
                elif op == 'ir':
                    stop_list_rail.append(stop['stopid'])
                else:
                    stop_list_bus.append(stop['stopid'])
                
    for stop in stop_list_rail:
        urls_rail.append("{}{}".format(real_endpoint, stop))
    for stop in stop_list_luas:
        urls_luas.append("{}{}".format(real_endpoint, stop))
    for stop in stop_list_bus:
        urls_bus.append("{}{}".format(real_endpoint, stop))

if __name__ == '__main__':
    app.run()

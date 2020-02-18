from flask import Flask
#from flask.ext.aiohttp import AioHTTP
import aiohttp
import asyncio
import requests
import pdb
import json
import csv
import pandas
import pickle
import pprint
import tornado

app = Flask(__name__)


BASE_URL = "https://data.smartdublin.ie/cgi-bin/rtpi"
stop_endpoint = "/busstopinformation"
real_endpoint = "{}/realtimebusinformation?stopid=".format(BASE_URL)
urls_bus = []
urls_luas = []
urls_rail = []

        
def csvsaver(csvname,itemlist):

    with open(csvname, 'w') as f:
        
        #temp = json.loads(itemlist[5])
        results_dict = itemlist[5]['results'][0]
        results_dict["stopid"] = 0
        w = csv.DictWriter(f,results_dict.keys())
        w.writeheader()

        for item in itemlist:

            jsonitem = item
            #w.writerow({})

            x = 0

            while x < jsonitem['numberofresults']:
                

                results_dict = jsonitem['results'][x]
                results_dict["stopid"] = jsonitem["stopid"]

                w.writerow(results_dict)
                x = x + 1




def updatedata(urls,csvname):

    responses = []


    for url in urls:
        responses.append(requests.get(url).json())
        print(url)

    csvsaver(csvname,responses)
    return ("",204)


     
@app.route('/update')              
def update():

    #pdb.set_trace()
    updatedata(urls_rail,"rail.csv")
    print("Done rails")
    updatedata(urls_luas,"luas.csv")
    print("Done luas")
    updatedata(urls_bus,"bus.csv")
    print("Done bus")

    return ('',204)
    



@app.route('/luas')
def luas():
    f = open("luas.csv","r")
    if f.mode == 'r':
        contents = f.read()
        return contents
        
    return ('',204)
    
@app.route('/bus')
def bus():
    f = open("bus.csv","r")
    if f.mode == 'r':
        contents = f.read()
        return contents
        
    return ('',204)
    
@app.route('/rail')
def rail():
    f = open("rail.csv","r")
    if f.mode == 'r':
        contents = f.read()
        return contents
        
    return ('',204)

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

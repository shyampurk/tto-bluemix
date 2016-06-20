import datetime
import pymongo
from pymongo import MongoClient
import sys
import requests 
import demjson
import pytz


uri ='mongodb://rajeevtto:radiostud@ds035315-a0.mongolab.com:35315,ds035315-a1.mongolab.com:35315/newttobackground?replicaSet=rs-ds035315'
client = MongoClient(uri)


newttobackground = client.newttobackground


client_data = {1:{"timeZone":"US/Eastern"},2:{"timeZone":"US/Eastern"},3:{"timeZone":"US/Pacific"}}

print '\n\tSelect the route'
print ("\n\t1 -->NEWARK-EDISON \n\t2-->BROOKLYN-DENVILLE \n\t3-->MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL")
route = int(raw_input("\n\tEnter the value 1/2/3 ::"))
induceTime = raw_input("\n\tEnter the Time ::")
induceTime = datetime.datetime.strptime(induceTime,"%Y-%m-%d %H:%M:%S")

zone = pytz.timezone(client_data[route]["timeZone"])
recommendedDepTime = zone.localize(induceTime)
			

if (recommendedDepTime.strftime("%d") == datetime.datetime.now(pytz.timezone(client_data[route]['timeZone'])).strftime("%d")):
	minval = 0
	maxval = 1
else:
	minval = 1
	maxval = 2

print minval,maxval
print "\n\t       THE PRESENT WEATHER AND TEMPARATURE FOR THE ROUTE YOU HAVE SELECTED"
if route == 3:
	sanfranciscoweatherforecast_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid= 2487956&format=json&env=store")	
	sanfranciscoweatherforecast_data = sanfranciscoweatherforecast_api.text
	sanfrancisco_weatherforecast = demjson.decode(sanfranciscoweatherforecast_data)

	print "\n\t             MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"
	
		
	for i in range(minval,maxval,1):
		sfday= sanfrancisco_weatherforecast['query']['results']['channel']['item']['forecast'][i]['day']
		sfhigh = int(sanfrancisco_weatherforecast['query']['results']['channel']['item']['forecast'][i]['high'])
		sflow = int(sanfrancisco_weatherforecast['query']['results']['channel']['item']['forecast'][i]['low'])
		sfavg = (sfhigh+sflow)/2
		sfcode = sanfrancisco_weatherforecast['query']['results']['channel']['item']['forecast'][i]['code']
		
		sfdate = sanfrancisco_weatherforecast['query']['results']['channel']['item']['forecast'][i]['date']
		
		print "\n sanfrancisco",sfdate,"-->","weathercode:",sfcode,"maxTemparature:",sfhigh,"minTemparature:",sflow,"avgTemparature:",sfavg

if route == 1:		
	newarkweatherforecast_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid= 2459299&format=json&env=store")	
	newarkweatherforecast_data = newarkweatherforecast_api.text
	newark_weatherforecast = demjson.decode(newarkweatherforecast_data)

	edisonweatherforecast_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid= 56250394&format=json&env=store")	
	edisonweatherforecast_data = edisonweatherforecast_api.text
	edison_weatherforecast = demjson.decode(edisonweatherforecast_data)

	print "\n\t       NEWARK-EDISON"
	for i in range(minval,maxval,1):
		nday= newark_weatherforecast['query']['results']['channel']['item']['forecast'][i]['day']
		nhigh = int(newark_weatherforecast['query']['results']['channel']['item']['forecast'][i]['high'])
		nlow = int(newark_weatherforecast['query']['results']['channel']['item']['forecast'][i]['low'])
		navg =(nhigh+nlow)/2
		
		ncode = newark_weatherforecast['query']['results']['channel']['item']['forecast'][i]['code']
		
		ndate = newark_weatherforecast['query']['results']['channel']['item']['forecast'][i]['date']
		
		eday= edison_weatherforecast['query']['results']['channel']['item']['forecast'][i]['day']
		ehigh = int(edison_weatherforecast['query']['results']['channel']['item']['forecast'][i]['high'])
		elow = int(edison_weatherforecast['query']['results']['channel']['item']['forecast'][i]['low'])
		eavg =(ehigh+elow)/2
		
		ecode = edison_weatherforecast['query']['results']['channel']['item']['forecast'][i]['code']
		
		edate = edison_weatherforecast['query']['results']['channel']['item']['forecast'][i]['date']
			
		print "\n NEWARK",ndate,"-->","weathercode:",ncode,"maxTemparature:",nhigh,"minTemparature:",nlow,"avgTemparature:",navg
		
		print "\n EDISON",edate,"-->","weathercode:",ecode,"maxTemparature:",ehigh,"minTemparature:",elow,"avgTemparature:",eavg

if route == 2:
	brooklynweatherforecast_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid= 2459115&format=json&env=store")	
	brooklynweatherforecast_data = brooklynweatherforecast_api.text
	brooklyn_weatherforecast = demjson.decode(brooklynweatherforecast_data)

	denvilleweatherforecast_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid= 2391338&format=json&env=store")	
	denvilleweatherforecast_data = denvilleweatherforecast_api.text
	denville_weatherforecast = demjson.decode(denvilleweatherforecast_data)


	
	print "\n\t    BROOKLYN-DENVILLE"
	for i in range(minval,maxval,1):
		bday= brooklyn_weatherforecast['query']['results']['channel']['item']['forecast'][i]['day']
		bhigh = int(brooklyn_weatherforecast['query']['results']['channel']['item']['forecast'][i]['high'])
		blow = int(brooklyn_weatherforecast['query']['results']['channel']['item']['forecast'][i]['low'])
		bavg =(bhigh+blow)/2
		
		bcode = brooklyn_weatherforecast['query']['results']['channel']['item']['forecast'][i]['code']
		
		bdate = brooklyn_weatherforecast['query']['results']['channel']['item']['forecast'][i]['date']
		
		dday= denville_weatherforecast['query']['results']['channel']['item']['forecast'][i]['day']
		dhigh = int(denville_weatherforecast['query']['results']['channel']['item']['forecast'][i]['high'])
		dlow = int(denville_weatherforecast['query']['results']['channel']['item']['forecast'][i]['low'])
		davg =(dhigh+dlow)/2
		
		dcode = denville_weatherforecast['query']['results']['channel']['item']['forecast'][i]['code']
		
		ddate = denville_weatherforecast['query']['results']['channel']['item']['forecast'][i]['date']
		
		print "\n BROOKLYN",bdate,"-->","weathercode:",bcode,"maxTemparature:",bhigh,"minTemparature:",blow,"avgTemparature:",bavg
		
		print "\n DENVILLE",ddate,"-->","weathercode:",dcode,"maxTemparature:",dhigh,"minTemparature:",dlow,"avgTemparature:",davg

print '\n\t Select the weather'
print '\n\t-----------------------------------------------------------------------------------------------------------------------'
print "0 -->tornado\t1 -->tropical storm\t2-->hurricane\t3-->severe thunderstorms\t4-->thunderstorms\t5-->mixed rain and snow\n\n6-->mixed rain and sleet\t7-->mixed snow and sleet\t8-->freezing drizzle\t9-->drizzle\t10-->freezing rain\n\n11-->showers\t12-->showers\t13-->snow flurries\t14-->light snow showers\t15-->blowing snow\n\n16-->snow\t17-->hail\t18-->sleet\t19-->dust\t20-->foggy\n\n21-->haze\t22-->smoky\t23-->blustery\t24-->windy\t25-->cold\n\n26-->cloudy\t27-->mostly cloudy (night)\t28-->mostly cloudy (day)\t29-->partly cloudy (night)\t30-->partly cloudy (day)\n\n31-->clear (night)\t32-->sunny\t33-->fair (night)\t34-->fair (day)\t35-->mixed rain and hail\n\n36-->hot\t37-->isolated thunderstorms\t38-->scattered thunderstorms\t39-->scattered thunderstorms\t40-->scattered showers\n\n41-->heavy snow\t42-->scattered snow showers\t43-->heavy snow\t44-->partly cloudy\t45-->thundershowers\n\n46-->snow showers\t47-->isolated thundershowers"
print '\n\t-----------------------------------------------------------------------------------------------------------------------'
induceWeather = raw_input("\n\t Enter the numeric corresponding to the weather :: ")
induceTemparature = raw_input("\n\t Enter the Temparature ::")

	

if (route == 1):

	newarkedison_doc = {
					"route":"NEWARK-EDISON",
					"induceTime":induceTime,
					"induceWeather":[int(induceWeather),int(induceWeather)],
					"induceTemparature":[int(induceTemparature),int(induceTemparature)]
					}

	newarkedison_docid = newttobackground.ttoinducecoll.insert_one(newarkedison_doc)

elif(route == 2):
	brooklyndenville_doc = {
					"route":"BROOKLYN-DENVILLE",
					"induceTime":induceTime,
					"induceWeather":[induceWeather,induceWeather],
					"induceTemparature":[induceTemparature,induceTemparature]
					}
	
	brooklyndenville_docid = newttobackground.ttoinducecoll.insert_one(brooklyndenville_doc)

elif(route == 3):
	sanfrancisco_doc = {
					"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL",
					"induceTime":induceTime,
					"induceWeather":[induceWeather,induceWeather],
					"induceTemparature":[induceTemparature,induceTemparature]
					}
	
	sanfrancisco_docid = newttobackground.ttoinducecoll.insert_one(sanfrancisco_doc)


else:
	print 'wrong selection'
	sys.exit()	









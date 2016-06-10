import datetime
import pymongo
from pymongo import MongoClient
import sys




uri ='mongodb://rajeevtto:radiostud@ds035315-a0.mongolab.com:35315,ds035315-a1.mongolab.com:35315/newttobackground?replicaSet=rs-ds035315'
client = MongoClient(uri)


newttobackground = client.newttobackground


print 'Select the route'
print ("\n\t1 -->NEWARK-EDISON \n\t2-->BROOKLYN-DENVILLE \n\t3-->MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL")
route = int(raw_input("\n\tEnter the value 1/2/3 ::"))
induceTime = raw_input("\n\tEnter the Time ::")
induceTime = datetime.datetime.strptime(induceTime,"%Y-%m-%d %H:%M:%S")

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
	
	sanfrancisco_docid = newttobackground.ttoinducecoll.insert_one(brooklyndenville_doc)


else:
	print 'wrong selection'
	sys.exit()	









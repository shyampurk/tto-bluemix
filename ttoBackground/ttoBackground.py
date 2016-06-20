import requests
import demjson
from demjson import JSONDecodeError
import datetime
import time
import pytz
import pymongo
import threading
from pymongo import MongoClient
import logging

import ne_testprep
import bd_testprep
import sf_testprep
import ne_scikit
import bd_scikit
import sf_scikit

LOG_FILENAME = 'TTOBackgroundLogs.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


uri ='mongodb://rajeevtto:radiostud@ds035315-a0.mongolab.com:35315,ds035315-a1.mongolab.com:35315/newttobackground?replicaSet=rs-ds035315'
client = MongoClient(uri)


newttobackground = client.newttobackground
ttobgcoll = newttobackground.ttobgcoll

count = 4320
Limit = 1
Day_List = ['','Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']


def function_routenewarkedison():
	'''
	ROUTE    --> GardenStatePkwy,Newark,NJ,USA to Edison,NJ,USA <--
	'''
	
	global count,Limit
	while True:
		
		newarkedison_time = datetime.datetime.now(pytz.timezone('US/Eastern')) 
		newarkedison_dayname = newarkedison_time.strftime("%A")
		newarkedison_hour = int(newarkedison_time.strftime("%H"))	
		newarkedison_minute = int(newarkedison_time.strftime("%M"))
		newarkedison_second = int(newarkedison_time.strftime("%S"))
		newarkedison_year 	= int(newarkedison_time.strftime("%Y"))
		newarkedison_month	= int(newarkedison_time.strftime("%m"))
		newarkedison_day	= int(newarkedison_time.strftime("%d"))

		ne_calc_minute = newarkedison_minute%10
		#ne_calc_second = 60-newarkedison_second
		newark_edison_directions = "NONE"
		newark_weather = "NONE"
		edison_weather = "NONE"
		newarkedison_incidents = "NONE"
		
		
	
		if (ne_calc_minute == 0):
			newarkedison_loctime = datetime.datetime(newarkedison_year,newarkedison_month,newarkedison_day,newarkedison_hour,newarkedison_minute,newarkedison_second)
			newarkedison_delayFromFreeFlow = []
			newarkedison_delayFromTypical = []
			nelist_id = []
			netime = []
			neroute = "NEWARK-EDISON"
			necity1 = "NEWARK"
			necity2 =  "EDISON"
			neretry1 = 0
			neretry2 = 0
			neretry3 = 0
			neretry4 = 0
			try:	
				# DIRECTIONS API
				while(neretry1 <=2):
					try:
						newark_edison_api = requests.get('http://www.mapquestapi.com/directions/v2/route?key=AnGMNiGt9WoQo6yaOiJgeRkFlYAIHTGU&from=40.731507,-74.174388&to=40.525525,-74.388231&doReverseGeocode=false')
						logging.info( "ne directions api status %s and reason %s "%(newark_edison_api.status_code,newark_edison_api.reason))
						neretry1 = 3
						newark_edison_data =  newark_edison_api.text
						newark_edison_directions = demjson.decode(newark_edison_data)	
					except requests.exceptions.ConnectionError as cne_directions:
						neretry1 = neretry1+1
						logging.error( "%s,%s is the conn-exception occured at %s for the route %s"%(cne_directions,type(cne_directions),newarkedison_time,neroute)) 
					except requests.exceptions.HTTPError as hne_directions:
						logging.error( "%s,%s is the http-exception occured at %s for the route %s"%(hne_directions,type(hne_directions),newarkedison_time,neroute))
					except requests.exceptions.ReadTimeout as rne_directions:
						logging.error( "%s,%s is the readtimeout-exception occured at %s for the route %s"%(rne_directions,type(rne_directions),newarkedison_time,neroute))
					except requests.exceptions.Timeout as tne_directions:
						logging.error( "%s,%s is the timeout-exception occured at %s for the route %s"%(tne_directions,type(tne_directions),newarkedison_time,neroute))
					except Exception as ene_directions:
						logging.error( "%s,%s is the exception occured at %s for the route %s"%(ene_directions,type(ene_directions),newarkedison_time,neroute))				
					except demjson.JSONDecodeError as nejsonerror_directions:
						logging.error( "the directions json error exception %s %s for the route %s at %s " %(nejsonerror_directions,type(nejsonerror_directions),neroute,newarkedison_time))
						
					if (newark_edison_api.status_code==200):
						if 'info' in newark_edison_directions: 
							del newark_edison_directions['info']
					else:
						pass
				# WEATHER API
				while(neretry2 <=2): 
					try:
						newarkweather_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select item.condition from weather.forecast where woeid= 2459299&format=json")
						logging.info( "newark weather api status %s and reason %s"%(newarkweather_api.status_code,newarkweather_api.reason))
						neretry2 = 3
						newarkweather_data = newarkweather_api.text
						newark_weather = demjson.decode(newarkweather_data)
					except requests.exceptions.ConnectionError as cn_weather:
						neretry2 = neretry2+1
						logging.error( "%s,%s is the conn-exception occured at %s for the city %s"%(cn_weather,type(cn_weather),newarkedison_time,necity1)) 
					except requests.exceptions.HTTPError as hn_weather:
						logging.error( "%s,%s is the conn-exception occured at %s for the city %s"%(hn_weather,type(hn_weather),newarkedison_time,necity1))
					except requests.exceptions.ReadTimeout as rn_weather:
						logging.error( "%s,%s is the readtimeout-exception occured at %s for the city %s"%(rn_weather,type(rn_weather),newarkedison_time,necity1))
					except requests.exceptions.Timeout as tn_weather:
						logging.error( "%s,%s is the timeout-exception occured at %s for the city %s"%(tn_weather,type(tn_weather),newarkedison_time,necity1))
					except Exception as en_weather:
						logging.error( "%s,%s is the exception occured at %s for the city %s"%(en_weather,type(en_weather),newarkedison_time,necity1))				
					except demjson.JSONDecodeError as njsonerror_weather:
						logging.error( "the weather json error exception %s  %s for city %s at %s " %(njsonerror_weather,type(njsonerror_weather),necity1,newarkedison_time))
				while (neretry3 <=2):	
					try:
						edisonweather_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select item.condition from weather.forecast where woeid=56250394&format=json")
						logging.info( "edison weather api status %s and reason %s"%(edisonweather_api.status_code,edisonweather_api.reason))
						neretry3 = 3
						edisonweather_data = edisonweather_api.text
						edison_weather = demjson.decode(edisonweather_data)
					except requests.exceptions.ConnectionError as ce_weather:
						neretry3 = neretry3+1
						logging.error( "%s,%s is the conn-exception occured at %s for the city %s"%(ce_weather,type(ce_weather),newarkedison_time,necity2))
					except requests.exceptions.HTTPError as he_weather:
						logging.error( "%s,%s is the http-exception occured at %s for the city %s"%(he_weather,type(he_weather),newarkedison_time,necity2))
					except requests.exceptions.ReadTimeout as re_weather:
						logging.error( "%s,%s is the readtimeout-exception occured at %s for the city %s"%(re_weather,type(re_weather),newarkedison_time,necity2))
					except requests.exceptions.Timeout as te_weather:
						logging.error( "%s,%s is the exception occured at %s for the city %s"%(te_weather,type(te_weather),newarkedison_time,necity2))
					except Exception as ee_weather:
						logging.error( "%s,%s is the exception occured at %s for the city %s"%(ee_weather,type(ee_weather),newarkedison_time,necity2))
					
					except demjson.JSONDecodeError as ejsonerror_weather:
						logging.error( "the weather json error exception %s %s for city %s at %s " %(ejsonerror_weather,type(ejsonerror_weather),necity2,newarkedison_time))

				
				# TRAFFIC API
				
				while (neretry4<=2):
					try:
						newarkedison_incidents_api = requests.get('http://www.mapquestapi.com/traffic/v2/incidents?key=0BLeZWB9UiKqUXD8eGtLbwOoLAcd3Prh&boundingBox=40.7467527,-74.2154055,40.5382588,-74.4480655&filters=construction,incidents,congestion,events&inFormat=kvp&outFormat=json')
						logging.info( "ne incidents api status %s and reason %s"%(newarkedison_incidents_api.status_code,newarkedison_incidents_api.reason))
						neretry4=3
						newarkedison_data = newarkedison_incidents_api.text
						newarkedison_incidents = demjson.decode(newarkedison_data)
						newarkedison_length = len(newarkedison_incidents['incidents'])
					except requests.exceptions.ConnectionError as cne_incidents:
						neretry4 = neretry4+1
						logging.error( "%s,%s is the conn-exception occured at %s for the route %s"%(cne_incidents,type(cne_incidents),newarkedison_time,neroute)) 
					except requests.exceptions.HTTPError as hne_incidents:
						logging.error( "%s,%s is the http-exception occured at %s for the route %s"%(hne_incidents,type(hne_incidents),newarkedison_time,neroute))
					except requests.exceptions.ReadTimeout as rne_incidents:
						logging.error( "%s,%s is the readtimeout-exception occured at %s for the route %s"%(rne_incidents,type(rne_incidents),newarkedison_time,neroute,newarkedison_time,neroute))
					except requests.exceptions.Timeout as tne_incidents:
						logging.error( "%s,%s is the timeout-exception occured at %s for the route %s"%(tne_incidents,type(tne_incidents),newarkedison_time,neroute))
					except Exception as ene_incidents:
						logging.error( "%s,%s is the exception occured at %s for the route %s"%(ene_incidents,type(ene_incidents),newarkedison_time,neroute))
			
					except demjson.JSONDecodeError as nejsonerror_incidents:
						logging.error( "the incidents json error exception %s %s for the route %s at %s " % (nejsonerror_incidents,type(nejsonerror_incidents),neroute,newarkedison_time))
				
					
					if (newarkedison_incidents_api.status_code==200):
						if 'info' in newarkedison_incidents: 
							del newarkedison_incidents['info']
					
				
						for i in range(newarkedison_length):	
							newarkedison_delayFromFreeFlow.append(float(newarkedison_incidents["incidents"][i]["delayFromFreeFlow"]))
							newarkedison_delayFromTypical.append(float(newarkedison_incidents["incidents"][i]["delayFromTypical"]))
						
						for i in range(newarkedison_length):
								newarkedison_incidents["incidents"][i]["delayFromTypical"] = newarkedison_delayFromFreeFlow[i]
								newarkedison_incidents["incidents"][i]["delayFromFreeFlow"] = newarkedison_delayFromTypical[i]
					else:
						pass
			except Exception as nemainException:
				newark_edison_directions = "NONE"
				newark_weather = "NONE"
				edison_weather = "NONE"
				newarkedison_incidents = "NONE"
		
				logging.error( "%s,%s is the exception occured for nemainException"%(nemainException,type(nemainException)))
							

			ne_flag = False	
			try:		
				if (newark_edison_directions == 'NONE' or newark_edison_directions['route']['realTime'] >10000000 or newark_edison_directions['route']['realTime'] == 'None'or newark_edison_directions['route']['distance'] == 'None' or newark_edison_directions['route']['time'] == 'None' or newark_weather == 'NONE' or newark_weather.has_key('error') or newark_weather['query']['results'] == None or newark_weather['query'] == None or newark_weather['query']['results']['channel']['item']['condition']['code'] == 3200 or edison_weather == 'NONE' or edison_weather.has_key('error') or edison_weather['query']['results'] == None or edison_weather['query'] == None or edison_weather['query']['results']['channel']['item']['condition']['code'] == 3200):
					ne_flag = False
				else:
					ne_flag = True
			except Exception as flagcheckexception:
				logging.error( "%s,%s is the exception occured for flagcheckexception"%(flagcheckexception,type(flagcheckexception)))
			
			
			newarkedison_doc = {
					"route":"NEWARK-EDISON",
					"recorddate":newarkedison_loctime,
					"recorddayname":newarkedison_dayname,
					"directions":newark_edison_directions,
					"weather":[newark_weather,edison_weather],
					"traffic":newarkedison_incidents,
					"Flag":ne_flag
			}
			newarkedison_docid = ttobgcoll.insert_one(newarkedison_doc)
			
			# printing the time after completion of the tasks
			logging.info( "Received newarkedison data by %s"%(str(datetime.datetime.now(pytz.timezone('US/Eastern')))))
			# getting the number of documents in the db
			try:
				necnt = newttobackground.ttobgcoll.find({"route":"NEWARK-EDISON"}).count()
				if (necnt>count):
				 	for newarkedison_doc in ttobgcoll.find({"route":"NEWARK-EDISON"}).sort('recorddate',pymongo.ASCENDING).limit(Limit):
				 		nelist_id.append(newarkedison_doc['_id'])
				 		netime.append(newarkedison_doc['recorddate'])
				 		logging.info( "NEWARK-EDISON")
				 		logging.info( nelist_id)
				 		logging.info( netime)
				 	for neid in nelist_id:
				 		newttobackground.ttobgcoll.remove({"_id":neid})
			 		
			 		del nelist_id
					del netime
			except Exception as nerollover_error:
				logging.error( "%s,%s is the rollover exception occured at %s for the route %s "%(nerollover_error,type(nerollover_error),newarkedison_time,neroute))
		
			
			del	newarkedison_delayFromFreeFlow
			del	newarkedison_delayFromTypical

			ne_cursor = newttobackground.ttobgcoll.find({"route":"NEWARK-EDISON","recorddate":newarkedison_loctime})

			Limit = 1
			
			try:
				for neval in ne_cursor:
					if (neval['Flag'] == True):

						n_t = float(neval['weather'][0]['query']['results']['channel']['item']['condition']['temp'])
						n_w = int(neval['weather'][0]['query']['results']['channel']['item']['condition']['code'])
						e_t = float(neval['weather'][1]['query']['results']['channel']['item']['condition']['temp'])
						e_w = int(neval['weather'][1]['query']['results']['channel']['item']['condition']['code'])
						 
						v1 = int(neval['recorddate'].strftime("%H"))
						v2 = int(neval['recorddate'].strftime("%M"))
						v1 = (v1)*6
						v2 = (v2+10)/10
						zone = v1+v2
					
						for day in Day_List:
							if neval['recorddayname'] == day:
								codedday = Day_List.index(day)
								

						newarkedison_doc = {
									"route":"NEWARK-EDISON",
									"Date":neval['recorddate'],
									"Day":neval['recorddayname'],
									"Temparature": [n_t,e_t],
									"CodedWeather" : [n_w,e_w],
									"CodedDay":codedday,
									"Zone":zone,
									"realTime":neval['directions']['route']['realTime']
									
									}
						newarkedison_docid = newttobackground.ttoopvalcoll.insert_one(newarkedison_doc)

					else:
						pass
						''' This is an important exception need to concentrated because if one has no proper val for that particular zone
						what will be the prediction for the 12 hr ahead for that particular zone we have to say we dont have data or we can show the 
						previous one'''

						



			except Exception as e:
				logging.error("ttoopvalcoll upload error in newarkedison %s,%s"(e,type(e)))

			'''INDUCE TIME PROGRAM'''	
			induceTime = []
			induceWeather = []
			induceTemparature = []

			try:
				cnt = newttobackground.ttoinducecoll.find({"route":"NEWARK-EDISON"}).count()
				if cnt >0:
					cursor = newttobackground.ttoinducecoll.find({"route":"NEWARK-EDISON"})
					
					for doc in cursor:
						induceTime.append(doc['induceTime'])
						induceWeather.append([doc['induceWeather'][0],doc['induceWeather'][1]])
						induceTemparature.append([doc['induceTemparature'][0],doc['induceTemparature'][1]])
				else:
					pass

			except Exception as e:
				print e	
	


			ne_df,netestprep_return = ne_testprep.nealgo(newarkedison_loctime,induceTime,induceWeather,induceTemparature)
					
			if (netestprep_return == True):
				nescikit_return = ne_scikit.ne_scikitalgo(ne_df)
			else:
				pass

			idlist = []	
			if (newttobackground.ttoinducecoll.find({"route":"NEWARK-EDISON"}).count() > 0):
				cursor = newttobackground.ttoinducecoll.find({"route":"NEWARK-EDISON"})
				for doc in cursor:
					idlist.append(doc['_id'])
				newttobackground.ttoinducecoll.remove({'_id':{"$in":idlist}}) # Dangerous line

			else:
				pass
	
					
			time.sleep(580-newarkedison_second)
			


def function_routebrooklyndenville():
	'''
	ROUTE -->AT-Avenue,Brooklyn,NY,USA to Denville,NJ,USA<--

	'''
	#client = MongoClient(uri)
	global count,Limit	
	while True:
		
		
		brooklyndenville_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
		
		brooklyndenville_dayname = brooklyndenville_time.strftime("%A")
		brooklyndenville_hour = int(brooklyndenville_time.strftime("%H"))	
		brooklyndenville_minute = int(brooklyndenville_time.strftime("%M"))
		brooklyndenville_second = int(brooklyndenville_time.strftime("%S"))
		brooklyndenville_year = int(brooklyndenville_time.strftime("%Y"))
		brooklyndenville_month	= int(brooklyndenville_time.strftime("%m"))
		brooklyndenville_day	= int(brooklyndenville_time.strftime("%d")) 
		bd_calc_minute = brooklyndenville_minute%10
		#bd_calc_second = 60-brooklyndenville_second
		brooklyn_denville_directions = "NONE"
		brooklyn_weather = "NONE"
		denville_weather = "NONE"
		brooklyndenville_incidents = "NONE"
		
		if (bd_calc_minute == 0):
			brooklyndenville_loctime = datetime.datetime(brooklyndenville_year,brooklyndenville_month,brooklyndenville_day,brooklyndenville_hour,brooklyndenville_minute,brooklyndenville_second)
			brooklyndenville_delayFromFreeFlow = []
			brooklyndenville_delayFromTypical = []
			bdlist_id = []
			bdtime = []
			bdroute = "BROOKLYN-DENVILLE"
			bdcity1 = "BROOKLYN"
			bdcity2 = "DENVILLE"
			bdretry1= 0
			bdretry2 =0
			bdretry3 =0
			bdretry4 =0

			#logging.info( brooklyndenville_time
			try:
				#DIRECTIONS API
				while (bdretry1<=2):
					try:
						brooklyn_denville_api = requests.get('http://www.mapquestapi.com/directions/v2/route?key=AnGMNiGt9WoQo6yaOiJgeRkFlYAIHTGU&from=40.692529,-73.990996&to=40.889066,-74.4786&doReverseGeocode=false')
						logging.info( "bd directions api status %s and reason %s"%(brooklyn_denville_api.status_code,brooklyn_denville_api.reason))
						bdretry1 = 3
						brooklyn_denville_data = brooklyn_denville_api.text
						brooklyn_denville_directions   = demjson.decode(brooklyn_denville_data)
					
					except requests.exceptions.ConnectionError as cbd_directions:
						bdretry1 = bdretry1+1
						logging.error( "%s,%s is the conn-exception occured at %s for the route %s"%(cbd_directions,type(cbd_directions),brooklyndenville_time,bdroute)) 
					except requests.exceptions.HTTPError as hbd_directions:
						logging.error( "%s,%s is the http-exception occured at %s for the route %s"%(hbd_directions,type(hbd_directions),brooklyndenville_time,bdroute))
					except requests.exceptions.ReadTimeout as rbd_directions:
						logging.error( "%s,%s is the readtimeout-exception occured at %s for the route %s"%(rbd_directions,type(rbd_directions),brooklyndenville_time,bdroute))
					except requests.exceptions.Timeout as tbd_directions:
						logging.error( "%s,%s is the timeout-exception occured at %s for the route %s"%(tbd_directions,type(tbd_directions),brooklyndenville_time,bdroute))
					except Exception as ebd_directions:
						logging.error( ",%s,%s is the exception occured at %s for the route %s"%(ebd_directions,type(ebd_directions),brooklyndenville_time,bdroute))
					except demjson.JSONDecodeError as bdjsonerror_directions:
						#logging.error( "the error %s %s"%(bdjsonerror_directions,type(bdjsonerror_directions))
						logging.error( "the directions json error %s %s for the route %s at %s"%(bdjsonerror_directions,type(bdjsonerror_directions),bdroute,brooklyndenville_time))
								

					if (brooklyn_denville_api.status_code == 200):
						if 'info' in brooklyn_denville_directions: 
							del brooklyn_denville_directions['info']
					else: 
						pass
				#WEATHER API
				while (bdretry2<=2):	
					try:
						brooklynweather_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select item.condition from weather.forecast where woeid=2459115&format=json")
						logging.info( "brooklyn weather api status %s and reason %s "%(brooklynweather_api.status_code,brooklynweather_api.reason))
						bdretry2 = 3
						brooklynweather_data = brooklynweather_api.text
						brooklyn_weather = demjson.decode(brooklynweather_data)	
						
					
					except requests.exceptions.ConnectionError as cb_weather:
						bdretry2 = bdretry2+1
						logging.error( "%s,%s is the conn-exception occured at %s for the city %s"%(cb_weather,type(cb_weather),brooklyndenville_time,bdcity1)) 
					except requests.exceptions.HTTPError as hb_weather:
						logging.error( "%s,%s is the http-exception occured at %s for the city %s"%(hb_weather,type(hb_weather),brooklyndenville_time,bdcity1))
					except requests.exceptions.ReadTimeout as rb_weather:
						logging.error( "%s,%s is the readtimeout-exception occured at %s for the city %s"%(rb_weather,type(rb_weather),brooklyndenville_time,bdcity1))
					except requests.exceptions.Timeout as tb_weather:
						logging.error( "%s,%s is the timeout-exception occured at %s for the city %s"%(tb_weather,type(tb_weather),brooklyndenville_time,bdcity1))
					except Exception as eb_weather:
						logging.error( "%s,%s is the exception occured at %s for the city %s"%(eb_weather,type(eb_weather),brooklyndenville_time,bdcity1))
					
					except demjson.JSONDecodeError as bjsonerror_weather:
						logging.error( "the weather json error %s %s for city %s at %s"%(bjsonerror_weather,type(bjsonerror_weather),bdcity1,brooklyndenville_time))
					
			
				while(bdretry3<=2):	
					try:
						denvilleweather_api= requests.get("https://query.yahooapis.com/v1/public/yql?q=select item.condition from weather.forecast where woeid=2391338&format=json")
						logging.info( "denville weather api status %s and reason %s"%(denvilleweather_api.status_code,denvilleweather_api.reason))
						bdretry3 = 3
						denvilleweather_data = denvilleweather_api.text
						denville_weather = demjson.decode(denvilleweather_data)
					except requests.exceptions.ConnectionError as cd_weather:
						bdretry3= bdretry3+1
						logging.error( "%s,%s is the conn-exception occured at %s for the city  %s"%(cd_weather,type(cd_weather),brooklyndenville_time,bdcity2)) 
					except requests.exceptions.HTTPError as hd_weather:
						logging.error( "%s,%s is the http-exception occured at %s for the city %s"%(hd_weather,type(hd_weather),brooklyndenville_time,bdcity2))
					except requests.exceptions.ReadTimeout as rd_weather:
						logging.error( "%s,%s is the readtimeout-exception occured at %s for the city %s"%(rd_weather,type(rd_weather),brooklyndenville_time,bdcity2))
					except requests.exceptions.Timeout as td_weather:
						logging.error( "%s,%s is the timeout-exception occured at %s for the city %s"%(td_weather,type(td_weather),brooklyndenville_time,bdcity2))
					except Exception as ed_weather:
						logging.error( "%s,%s is the exception occured at %s for the city %s"%(ed_weather,type(ed_weather),brooklyndenville_time,bdcity2))
					except demjson.JSONDecodeError as ejsonerror_weather:
						logging.error( "the weather json error %s %s for city %s at %s"%(ejsonerror_weather,type(ejsonerror_weather),bdcity2,brooklyndenville_time))

				#TRAFFIC API
				
				while(bdretry4<=2):
					try:
						brooklyndenville_incidents_api=requests.get('http://www.mapquestapi.com/traffic/v2/incidents?key=0BLeZWB9UiKqUXD8eGtLbwOoLAcd3Prh&boundingBox=40.6529731,-73.9461878,40.8842586,-74.5561109&filters=construction,incidents,congestion,events&inFormat=kvp&outFormat=json')
						logging.info( "bd incidents api status %s and reason %s"%(brooklyndenville_incidents_api.status_code,brooklyndenville_incidents_api.reason))
						bdretry4=3
						brooklyndenville_data = brooklyndenville_incidents_api.text
						brooklyndenville_incidents = demjson.decode(brooklyndenville_data)
						brooklyndenville_length = len(brooklyndenville_incidents['incidents'])
					except requests.exceptions.ConnectionError as cbd_incidents:
						bdretry4=bdretry4+1
						logging.error( "%s,%s is the conn-exception occured at %s for the route %s"%(cbd_incidents,type(cbd_incidents),brooklyndenville_time,bdroute)) 
					except requests.exceptions.HTTPError as hbd_incidents:
						logging.error( "%s,%s is the http-exception occured at %s for the route %s"%(hbd_incidents,type(hbd_incidents),brooklyndenville_time,bdroute))
					except requests.exceptions.ReadTimeout as rbd_incidents:
						logging.error( "%s,%s is the readtimeout-exception occured at %s for the route %s"%(rbd_incidents,type(rbd_incidents),brooklyndenville_time,bdroute))
					except requests.exceptions.Timeout as tbd_incidents:
						logging.error( "%s,%s is the timeout-exception occured at %s for the route %s"%(tbd_incidents,type(tbd_incidents),brooklyndenville_time,bdroute))
					except Exception as ebd_incidents:
						logging.error( "%s,%s is the exception occured at %s for the route %s"%(ebd_incidents,type(ebd_incidents),brooklyndenville_time,bdroute))
					except demjson.JSONDecodeError as bdjsonerror_incidents:
						logging.error( "the incidents json error %s %s for the route %s at %s"%(bdjsonerror_incidents,type(bdjsonerror_incidents),bdroute,brooklyndenville_time))
					
					if (brooklyndenville_incidents_api.status_code==200):
						if 'info' in brooklyndenville_incidents: 
							del brooklyndenville_incidents['info']
					

						for i in range(0,brooklyndenville_length):	
							brooklyndenville_delayFromFreeFlow.append(float(brooklyndenville_incidents["incidents"][i]["delayFromFreeFlow"]))
							brooklyndenville_delayFromTypical.append(float(brooklyndenville_incidents["incidents"][i]["delayFromTypical"]))
						
						for i in range(0,brooklyndenville_length):
								brooklyndenville_incidents["incidents"][i]["delayFromTypical"] = brooklyndenville_delayFromFreeFlow[i]
								brooklyndenville_incidents["incidents"][i]["delayFromFreeFlow"] = brooklyndenville_delayFromTypical[i]
					else:
						pass
			except Exception as bdmainException:
				logging.error( "%s,%s is the exception occured for bdmainException"%(bdmainException,type(bdmainException)))
				brooklyn_denville_directions = "NONE"
				brooklyn_weather = "NONE"
				denville_weather = "NONE"
				brooklyndenville_incidents = "NONE"
				
			bd_flag = False
			try:		
				if (brooklyn_denville_directions == 'NONE' or brooklyn_denville_directions['route']['realTime'] > 10000000 or brooklyn_denville_directions['route']['realTime'] == 'None'or brooklyn_denville_directions['route']['distance'] == 'None' or brooklyn_denville_directions['route']['time'] == 'None' or brooklyn_weather == 'NONE' or brooklyn_weather.has_key('error') or brooklyn_weather['query']['results'] == None or brooklyn_weather['query'] == None or brooklyn_weather['query']['results']['channel']['item']['condition']['code'] == 3200 or denville_weather == 'NONE' or denville_weather.has_key('error') or denville_weather['query']['results'] == None or denville_weather['query'] == None or denville_weather['query']['results']['channel']['item']['condition']['code'] == 3200):
					bd_flag = False
				else:
					bd_flag = True
			except Exception as flagcheckexception:
				logging.error( "%s,%s is the exception occured for flagcheckexception"%(flagcheckexception,type(flagcheckexception)))
						
						
				
			
			
			brooklyndenville_doc = {
						"route":"BROOKLYN-DENVILLE",
						"recorddate":brooklyndenville_loctime,
						"recorddayname" :brooklyndenville_dayname,
						"directions":brooklyn_denville_directions,
						"weather":[brooklyn_weather,denville_weather],
						"traffic":brooklyndenville_incidents,
						"Flag":bd_flag
				}
			brooklyndenville_docid = ttobgcoll.insert_one(brooklyndenville_doc)
			logging.info( "Received brooklyndenville data by%s"%(str(datetime.datetime.now(pytz.timezone('US/Eastern')))))
			
			try:
				bdcnt = newttobackground.ttobgcoll.find({"route":"BROOKLYN-DENVILLE"}).count()
				if (bdcnt > count):
					for brooklyndenville_doc in newttobackground.ttobgcoll.find({"route":"BROOKLYN-DENVILLE"}).sort('recorddate',pymongo.ASCENDING).limit(Limit):
						bdlist_id.append(brooklyndenville_doc['_id'])
						bdtime.append(brooklyndenville_doc['recorddate'])
						logging.info("BROOKLYN-DENVILLE")
				 		logging.info(bdlist_id)
				 		logging.info(bdtime)
				 	for bdid in bdlist_id:
				 		# logging.info(bdid)
				 		newttobackground.ttobgcoll.remove({"_id":bdid})
			 		
			 		del bdlist_id
			 		del bdtime
			except Exception as bdrollover_error:
				logging.error( "%s,%s is the rollover exception occured at %s for the route %s"%(bdrollover_error,type(bdrollover_error),brooklyndenville_time,bdroute))
			
			del	brooklyndenville_delayFromFreeFlow
			del	brooklyndenville_delayFromTypical 
			Limit = 1
			bd_cursor = newttobackground.ttobgcoll.find({"route":"BROOKLYN-DENVILLE","recorddate":brooklyndenville_loctime})

			
			
			try:
				for bdval in bd_cursor:
					if (bdval['Flag'] == True):

						b_t = float(bdval['weather'][0]['query']['results']['channel']['item']['condition']['temp'])
						b_w = int(bdval['weather'][0]['query']['results']['channel']['item']['condition']['code'])
						d_t = float(bdval['weather'][1]['query']['results']['channel']['item']['condition']['temp'])
						d_w = int(bdval['weather'][1]['query']['results']['channel']['item']['condition']['code'])
						 
						v1 = int(bdval['recorddate'].strftime("%H"))
						v2 = int(bdval['recorddate'].strftime("%M"))
						v1 = (v1)*6
						v2 = (v2+10)/10
						zone = v1+v2
					
						Day_List = ['','Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
						for day in Day_List:
							if bdval['recorddayname'] == day:
								codedday = Day_List.index(day)
								

						brooklyndenville_doc = {
									"route":"BROOKLYN-DENVILLE",
									"Date":bdval['recorddate'],
									"Day":bdval['recorddayname'],
									"Temparature": [b_t,d_t],
									"CodedWeather" : [b_w,d_w],
									"CodedDay":codedday,
									"Zone":zone,
									"realTime":bdval['directions']['route']['realTime']
									
									}
						brooklyndenville_docid = newttobackground.ttoopvalcoll.insert_one(brooklyndenville_doc)

					else:
						pass
						''' This is an important exception need to concentrated because if one has no proper val for that particular zone
						what will be the prediction for the 12 hr ahead for that particular zone we have to say we dont have data or we can show the 
						previous one'''



			except Exception as e:
				logging.error("ttoopvalcoll upload error in brooklyndenville %s,%s"%(e,type(e)))

			'''INDUCE TIME PROGRAM'''		
			induceTime = []
			induceWeather = []
			induceTemparature = []	
			try:
				cnt = newttobackground.ttoinducecoll.find({"route":"BROOKLYN-DENVILLE"}).count()
				if cnt >0:
					cursor = newttobackground.ttoinducecoll.find({"route":"BROOKLYN-DENVILLE"})
					
					for doc in cursor:
						induceTime.append(doc['induceTime'])
						induceWeather.append([doc['induceWeather'][0],doc['induceWeather'][1]])
						induceTemparature.append([doc['induceTemparature'][0],doc['induceTemparature'][1]])
				else:
					pass
							
			except Exception as e:
				print e		

			bd_df,bdtestprep_return = bd_testprep.bdalgo(brooklyndenville_loctime,induceTime,induceWeather,induceTemparature)
			
			if (bdtestprep_return == True):
				bdscikit_return = bd_scikit.bd_scikitalgo(bd_df)
			else:
				pass

			idlist = []	
			if (newttobackground.ttoinducecoll.find({"route":"BROOKLYN-DENVILLE"}).count() > 0):
				cursor = newttobackground.ttoinducecoll.find({"route":"BROOKLYN-DENVILLE"})
				for doc in cursor:
					idlist.append(doc['_id'])
				newttobackground.ttoinducecoll.remove({'_id':{"$in":idlist}}) # Dangerous line

			else:
				pass	

	
			

			time.sleep(580-brooklyndenville_second)	
			


def function_routesanfrancisco():
	'''
	ROUTE --> Mount zion Radiology,1600 Divisadero St,SF,USA to 
											SF General Hospital and Trauma Center,1001 Potrero Ave,San Francisco,CA 94110,USA<--
	'''
	global count,Limit
	while True:
		
		sanfrancisco_time = datetime.datetime.now(pytz.timezone('US/Pacific'))
		sanfrancisco_dayname = sanfrancisco_time.strftime("%A")
		sanfrancisco_hour = int(sanfrancisco_time.strftime("%H"))	
		sanfrancisco_minute = int(sanfrancisco_time.strftime("%M"))
		sanfrancisco_second = int(sanfrancisco_time.strftime("%S"))
		sanfrancisco_year = int(sanfrancisco_time.strftime("%Y"))
		sanfrancisco_month	=int(sanfrancisco_time.strftime("%m"))
		sanfrancisco_day	= int(sanfrancisco_time.strftime("%d")) 
		
		sf_calc_minute = sanfrancisco_minute%10
		#sf_calc_second = 60-sanfrancisco_second
		sanfrancisco_directions = "NONE"
		sanfrancisco_weather = "NONE"
		sanfrancisco_incidents = "NONE"
		
		

		if (sf_calc_minute == 0):
			sanfrancisco_loctime = datetime.datetime(sanfrancisco_year,sanfrancisco_month,sanfrancisco_day,sanfrancisco_hour,sanfrancisco_minute,sanfrancisco_second)
			sfroute = "MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"
			sfcity = "SANFRANCISCO"
			sanfrancisco_delayFromFreeFlow = []
			sanfrancisco_delayFromTypical = []
			sflist_id = []
			sftime = []
			sfretry1 = 0
			sfretry2 = 0 
			sfretry3 = 0
			try:
				while (sfretry1 <=2):
					try:
						sanfrancisco_api = requests.get('http://www.mapquestapi.com/directions/v2/route?key=AnGMNiGt9WoQo6yaOiJgeRkFlYAIHTGU&from=37.786452,-122.440168&to=37.749202,-122.41575&doReverseGeocode=false')
						logging.info( "sf directions api status %s and reason %s "%(sanfrancisco_api.status_code,sanfrancisco_api.reason))
						sfretry1 = 3
						sanfrancisco_data = sanfrancisco_api.text
						sanfrancisco_directions = demjson.decode(sanfrancisco_data)
					
					except requests.exceptions.ConnectionError as csf_directions:
						sfretry1 = sfretry1+1
						logging.error( "%s,%s is the conn-exception occured at %s for the route %s"%(csf_directions,type(csf_directions),sanfrancisco_time,sfroute)) 
					except requests.exceptions.HTTPError as hsf_directions:
						logging.error( "%s,%s is the http-exception occured at %s for the route %s"%(hsf_directions,type(hsf_directions),sanfrancisco_time,sfroute))
					except requests.exceptions.ReadTimeout as rsf_directions:
						logging.error( "%s,%s is the readtimeout-exception occured at %s for the route %s"%(rsf_directions,type(rsf_directions),sanfrancisco_time,sfroute))
					except requests.exceptions.Timeout as tsf_directions:
						logging.error( "%s,%s is the timeout-exception occured at %s for the route %s"%(tsf_directions,type(tsf_directions),sanfrancisco_time,sfroute))
					except Exception as esf_directions:
						logging.error( "%s,%s is the exception occured at %s for the route %s"%(esf_directions,type(esf_directions),sanfrancisco_time,sfroute))

					except demjson.JSONDecodeError as sfjsonerror_directions:
						logging.error( "the directions json error %s %s for the route %s at %s"%(sfjsonerror_directions,type(sfjsonerror_directions),sfroute,sanfrancisco_time))
					
					if (sanfrancisco_api.status_code ==200):
						if 'info' in sanfrancisco_directions:
							del sanfrancisco_directions['info']
					else:
						pass
				while (sfretry2<=2):
					try:
						sanfranciscoweather_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select item.condition from weather.forecast where woeid=2487956&format=json")
						logging.info( "sf weather api status %s and reason %s"%(sanfranciscoweather_api.status_code,sanfranciscoweather_api.reason))
						sfretry2 = 3
						sanfranciscoweather_data = sanfranciscoweather_api.text
						sanfrancisco_weather  = demjson.decode(sanfranciscoweather_data)
					except requests.exceptions.ConnectionError as csf_weather:
						sfretry2 = sfretry2+1
						logging.error( "%s,%s is the conn-exception occured at %s for the route %s"%(csf_weather,type(csf_weather),sanfrancisco_time,sfcity)) 
					except requests.exceptions.HTTPError as hsf_weather:
						logging.error( "%s,%s is the http-exception occured at %s for the route %s"%(hsf_weather,type(hsf_weather),sanfrancisco_time,sfcity))
					except requests.exceptions.ReadTimeout as rsf_weather:
						logging.error( "%s,%s is the readtimeout-exception occured at %s for the route %s"%(rsf_weather,type(rsf_weather),sanfrancisco_time,sfcity))
					except requests.exceptions.Timeout as tsf_weather:
						logging.error( "%s,%s is the timeout-exception occured at %s for the route %s"%(tsf_weather,type(tsf_weather),sanfrancisco_time,sfcity))
					except Exception as esf_weather:
						logging.error( "%s,%s is the exception occured at %s for the route %s"%(esf_weather,type(esf_weather),sanfrancisco_time,sfcity))
					except demjson.JSONDecodeError as sfjsonerror_weather:
						logging.error( "the weather json error %s %s for the city  at %s"(sfjsonerror_weather,type(sfjsonerror_weather),sfcity,sanfrancisco_time))

				while (sfretry3<=2):	
					try:
						sanfrancisco_incidents_api=requests.get('http://www.mapquestapi.com/traffic/v2/incidents?key=0BLeZWB9UiKqUXD8eGtLbwOoLAcd3Prh&boundingBox=37.78461,-122.4415687,37.7563513,-122.4069454&filters=construction,incidents,congestion,events&inFormat=kvp&outFormat=json')
						logging.info( "sf incidents api status %s and reason %s"%(sanfrancisco_incidents_api.status_code,sanfrancisco_incidents_api.reason))
						sfretry3=3
						sanfrancisco_data = sanfrancisco_incidents_api.text
						sanfrancisco_incidents = demjson.decode(sanfrancisco_data)
						sanfrancisco_length = len(sanfrancisco_incidents['incidents'])
					except requests.exceptions.ConnectionError as csf_incidents:
						sfretry3 = sfretry3+1
						logging.error( "%s,%s is the conn-exception occured at %s for the route %s"%(csf_incidents,type(csf_incidents),sanfrancisco_time,sfroute)) 
					except requests.exceptions.HTTPError as hsf_incidents:
						logging.error( "%s,%s is the http-exception occured at %s for the route %s"%(hsf_incidents,type(hsf_incidents),sanfrancisco_time,sfroute))
					except requests.exceptions.ReadTimeout as rsf_incidents:
						logging.error( "%s,%s is the readtimeout-exception occured at %s for the route %s"%(rsf_incidents,type(rsf_incidents),sanfrancisco_time,sfroute))
					except requests.exceptions.Timeout as tsf_incidents:
						logging.error( "%s,%s is the timeout-exception occured at %s for the route %s"%(tsf_incidents,type(tsf_incidents),sanfrancisco_time,sfroute))
					except Exception as esf_incidents:
						logging.error( "%s,%s is the exception occured at %s for the route %s"%(esf_incidents,type(esf_incidents),sanfrancisco_time,sfroute))
					except demjson.JSONDecodeError as sfjsonerror_incidents:
						logging.error( "the incidents json error %s %s for the route %s at %s"(sfjsonerror_incidents,type(sfjsonerror_incidents),sfroute,sanfrancisco_time))
					if (sanfrancisco_incidents_api.status_code == 200):
						if 'info' in sanfrancisco_incidents:
							del sanfrancisco_incidents['info']
						for i in range(0,sanfrancisco_length):	
							sanfrancisco_delayFromFreeFlow.append(float(sanfrancisco_incidents["incidents"][i]["delayFromFreeFlow"]))
							sanfrancisco_delayFromTypical.append(float(sanfrancisco_incidents["incidents"][i]["delayFromTypical"]))
						
						for i in range(0,sanfrancisco_length):
							sanfrancisco_incidents["incidents"][i]["delayFromTypical"] = sanfrancisco_delayFromFreeFlow[i]
							sanfrancisco_incidents["incidents"][i]["delayFromFreeFlow"] =sanfrancisco_delayFromTypical[i]
				
					else:
						pass
			except Exception as sfmainException:
				logging.error( "%s,%s is the exception occured for sfmainException"%(sfmainException,type(sfmainException)))
				sanfrancisco_directions = "NONE"
				sanfrancisco_weather = "NONE"
				sanfrancisco_incidents = "NONE"
						
			sf_flag = False	
			try:
				if (sanfrancisco_directions == 'NONE' or sanfrancisco_directions['route']['realTime'] > 10000000 or sanfrancisco_directions['route']['realTime'] == 'None'or sanfrancisco_directions['route']['distance'] == 'None' or sanfrancisco_directions['route']['time'] == 'None' or sanfrancisco_weather == 'NONE' or sanfrancisco_weather.has_key('error') or sanfrancisco_weather['query']['results'] == None or sanfrancisco_weather['query'] == None or sanfrancisco_weather['query']['results']['channel']['item']['condition']['code'] == 3200):
					sf_flag = False
				else:
					sf_flag = True
			except Exception as flagcheckexception:
				logging.error( "%s,%s is the exception occured for flagcheckexception"%(flagcheckexception,type(flagcheckexception)))
						
						
				
			
			
			sanfrancisco_doc = {
					"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL",
					"recorddate": sanfrancisco_loctime,
					"recorddayname" : sanfrancisco_dayname,
					"directions":sanfrancisco_directions,
					"weather":[sanfrancisco_weather],
					"traffic":sanfrancisco_incidents,
					"Flag":sf_flag
			}
			sanfrancisco_docid = ttobgcoll.insert_one(sanfrancisco_doc)
			logging.info( "Received the sanfrancisco data by %s"%(str(datetime.datetime.now(pytz.timezone('US/Pacific')))))
			
			try:
				sfcnt = newttobackground.ttobgcoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"}).count()
				if (sfcnt > count):
					for sanfrancisco_doc in ttobgcoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"}).sort('recorddate', pymongo.ASCENDING).limit(Limit):
						sflist_id.append(sanfrancisco_doc['_id'])
						sftime.append(sanfrancisco_doc['recorddate'])
						logging.info("MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL")
				 		logging.info(sflist_id)
				 		logging.info(sftime)				
				 	for sfid in sflist_id:			 		
				 		newttobackground.ttobgcoll.remove({"_id":sfid})
			 		
			 		del sflist_id
			 		del sftime
			except Exception as sfrollover_error:
				logging.error( "%s,%s is the rollover exception occured at %s for the route %s"%(sfrollover_error,type(sfrollover_error),sanfrancisco_time,sfroute))
	
			del	sanfrancisco_delayFromFreeFlow
			del	sanfrancisco_delayFromTypical


			Limit = 1
			sf_cursor = newttobackground.ttobgcoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL","recorddate":sanfrancisco_loctime})

			
			try:
				for sfval in sf_cursor:
					if (sfval['Flag'] == True):

						sf_t = float(sfval['weather'][0]['query']['results']['channel']['item']['condition']['temp'])
						sf_w = int(sfval['weather'][0]['query']['results']['channel']['item']['condition']['code'])
						
						v1 = int(sfval['recorddate'].strftime("%H"))
						v2 = int(sfval['recorddate'].strftime("%M"))
						v1 = (v1)*6
						v2 = (v2+10)/10
						zone = v1+v2
					
						Day_List = ['','Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
						for day in Day_List:
							if sfval['recorddayname'] == day:
								codedday = Day_List.index(day)
								

						sanfrancisco_doc = {
									"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL",
									"Date":sfval['recorddate'],
									"Day":sfval['recorddayname'],
									"Temparature": [sf_t],
									"CodedWeather" : [sf_w],
									"CodedDay":codedday,
									"Zone":zone,
									"realTime":sfval['directions']['route']['realTime']									
									}
						sanfrancisco_docid = newttobackground.ttoopvalcoll.insert_one(sanfrancisco_doc)

					else:
						pass
						''' This is an important exception need to concentrated because if one has no proper val for that particular zone
					what will be the prediction for the 12 hr ahead for that particular zone we have to say we dont have data or we can show the 
					previous one'''		
			except Exception as e:
				logging.error("ttoopvalcoll upload error in sanfrancisco %s,%s"%(e,type(e)))		

			'''INDUCE TIME PROGRAM'''	
			induceTime = []
			induceWeather = []
			induceTemparature = []	

			try:
				cnt = newttobackground.ttoinducecoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"}).count()
				if cnt >0:
					cursor = newttobackground.ttoinducecoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"})
					
					for doc in cursor:
						induceTime.append(doc['induceTime'])
						induceWeather.append([doc['induceWeather'][0],doc['induceWeather'][1]])
						induceTemparature.append([doc['induceTemparature'][0],doc['induceTemparature'][1]])
				else:
					pass
								
			except Exception as e:
				print e			

			sf_df,sftestprep_return = sf_testprep.sfalgo(sanfrancisco_loctime,induceTime,induceWeather,induceTemparature)
			
			if (sftestprep_return == True):				
				sfscikit_return= sf_scikit.sf_scikitalgo(sf_df)	
			else:
				pass				
	
			idlist = []	
			if (newttobackground.ttoinducecoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"}).count() > 0):
				cursor = newttobackground.ttoinducecoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"})
				for doc in cursor:
					idlist.append(doc['_id'])
				newttobackground.ttoinducecoll.remove({'_id':{"$in":idlist}}) # Dangerous line

			else:
				pass

			time.sleep(580-sanfrancisco_second)
			
if __name__ == '__main__':
	try:
		t1 = threading.Thread(target = function_routenewarkedison)
		t2 = threading.Thread(target = function_routebrooklyndenville)
		t3 = threading.Thread(target = function_routesanfrancisco)
		t1.start()
		t2.start()
		t3.start()
		
	except:
		logging.error( "ERROR : Unable to create thread")
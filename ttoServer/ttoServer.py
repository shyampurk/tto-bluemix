import pymongo
from pymongo import MongoClient

import datetime
import pytz

import math
import time
import datetime

from pubnub import Pubnub

import threading
import time

import logging

pub_key ='pub-c-f2fc0469-ad0f-4756-be0c-e003d1392d43'
sub_key ='sub-c-4d48a9d8-1c1b-11e6-9327-02ee2ddab7fe'


LOG_FILENAME = 'TTOserverlogs.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


g_minit = 10
g_sleepTime = 580
g_divCompare = 3

client_data = {}
beforeJourneyClientList = {}
startedJourneyClientList = {}
commonClientIDList = []
commonStartedClientIDList = []


zone_ttimedct = {"NEWARK-EDISON":["US/Eastern",1719],"BROOKLYN-DENVILLE":["US/Eastern",2921],"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL":["US/Pacific",767]}



'''****************************************************************************************
Function Name 	:	publish_handler  (pubnub operation)
Description		:	Function used to publish the data to the client
Parameters 		:	channel          - UUID of the client   
					result           - The result i.e.,   
****************************************************************************************'''
def publish_handler(channel,result):
	try:	
		if (client_data[channel]['recommndsentproceed'] == True):	
			pbtry = 0
			while (pbtry<3):
				try:
					pbreturn = pubnub.publish(channel = channel ,message =result,error=error)
					if (pbreturn[0] == 1):
						return None
					elif(pbreturn[0] == 0):
						logging.error("The publish return error  %s for the Task %s for the client %s"%(pbreturn[1],channel,details['DISPLAY_NAME']))
						pbtry+=1
					else:
						pass
				except Exception as error_pdhandler:
					logging.error("The error_pdhandler Exception is %s,%s,%s"%(error_pdhandler,type(error_pdhandler)))

					pbtry+=1
		else:
			pass
	except Exception as pubhandlerError:
		logging.error("The publish function Exception is %s,%s,%s"%(pubhandlerError,type(pubhandlerError),str(result)))

					

'''****************************************************************************************
Function Name 	:	alertpublish_handler  (pubnub operation)
Description		:	Function used to publish the data to the client
Parameters 		:	channel          - UUID of the client   
					result           - The result i.e.,   
****************************************************************************************'''		
def alertpublish_handler(channel,result):
	try:	
		if (client_data[channel]['alertsentproceed'] == True):	
			pbtry = 0
			while (pbtry<3):
				try:
					pbreturn = pubnub.publish(channel = channel ,message =result,error=error)
					if (pbreturn[0] == 1):
						client_data[channel].update({"alertsentproceed":False})
						return None
					elif(pbreturn[0] == 0):
						logging.error("The publish return error  %s for the Task %s for the client %s"%(pbreturn[1],channel,details['DISPLAY_NAME']))
						pbtry+=1
					else:
						pass
				except Exception as error_pdhandler:
					logging.error("The alerterror_pdhandler Exception is %s,%s,%s"%(error_pdhandler,type(error_pdhandler)))

					pbtry+=1
		else:
			pass
	except Exception as alertpubhandlerError:
		logging.error("The publish function Exception is %s,%s,%s"%(alertpubhandlerError,type(alertpubhandlerError),str(result)))

				

'''****************************************************************************************
Function Name 	:	recommendationAlgoFunc  (Algorithm operation)
Description		:	Function used to do the Algorithm
Parameters 		:	DesiredArrivalTime - client's Desired ArrivalTime to the Destination   
					clientID           - client's UUID   
****************************************************************************************'''			
def recommendationAlgoFunc(DesiredArrivalTime,clientID):
	try:
		global newttobackground
		proceed = False
		route_time = datetime.datetime.now(pytz.timezone(client_data[clientID]['timeZone'])) 
		theorytimeinsecs = client_data[clientID]['theoryTime']
		theorytimeinminutes = theorytimeinsecs/60.0 #Theory time in minutes
		

		if (theorytimeinminutes%10 >= 5):				
			rem = 10.0-theorytimeinminutes%10
			
		else:
			rem = theorytimeinminutes%10
			rem = -rem
			
		reminminutes = rem
		

		reminsecs =  rem*60
		
		Limit = 1
		for newarkedison_doc in newttobackground.ttobgcoll.find({"route":client_data[clientID]['routeName']}).sort('recorddate', pymongo.DESCENDING).limit(Limit):
				endDate = newarkedison_doc['recorddate']
		
		diff = DesiredArrivalTime-route_time

		day  = diff.days
		hour = (day*24 + diff.seconds/3600)
		
		realtimeinminutes = []
		time = []
		realtimeinsec = []
		cursor = newttobackground.ttoresultcoll.find({"route":client_data[clientID]['routeName']}).sort('time', pymongo.ASCENDING).limit(150)
		
		if (0<=hour <= 12 and day < 1 and day >= -1):
			proceed = True
			for nedoc in cursor:
				 time.append(nedoc['time'])
				 realtimeinminutes.append(nedoc['predictioninmins'])
				 realtimeinsec.append(nedoc['predictioninsecs'])
		else:
			
			result = {"responseType":4,"message":"Desired Arrival Time is more than 12 hours away"}
			publish_handler(clientID,result)
			proceed = False
			del client_data[clientID]
			
		timediffinminutes = []
		timediffinsecs = []
		if (proceed == True):
			for i,j in zip(realtimeinsec,realtimeinminutes):
				timediffinsecs.append((((float(i)-(theorytimeinsecs)))+reminsecs))
				timediffinminutes.append((((float(j)-(theorytimeinminutes)))+reminminutes))
			
			for i in range(len(time)):
				if (int(DesiredArrivalTime.strftime("%H")) == int(time[i].strftime("%H")) and int(DesiredArrivalTime.strftime("%M")) == int(time[i].strftime("%M"))):
					DesiredArrivalTimeIndexInList = time.index(time[i])
							
			try:
					
				pred_minutes = []
				for i in range(len(timediffinminutes)):
					pred_minutes.append(float(timediffinminutes[i]+theorytimeinminutes))
				

				'''DISCUSSED METHOD'''
				startpointIndex = int(DesiredArrivalTimeIndexInList-(theorytimeinminutes/10))
				
				

				i = startpointIndex
				recommendationFlag = True
				checkedOnce = []
				recommendationResult = {}
				listlen = len(time)
				j = 0
				while (recommendationFlag == True):
				
					predictedArrivalTime = time[i]+datetime.timedelta(minutes=pred_minutes[i])
					replaceapproach = predictedArrivalTime.replace(tzinfo=pytz.timezone(client_data[clientID]['timeZone']))
					zone = pytz.timezone(client_data[clientID]["timeZone"])
					predictedArrivalTime = zone.localize(predictedArrivalTime)
					
					diff = DesiredArrivalTime - predictedArrivalTime

					diff_minutes = (diff.days *24*60)+(diff.seconds/60)

					
					
					if (diff_minutes == 0): #This condition is the top priority
						pred_minutesReal = pred_minutes[i]-reminminutes
						recommendationResult.update({"onTime":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"You will reach ontime","pred_minutesReal":pred_minutesReal}})		
						recommendationFlag = False

					elif (0<=diff_minutes<=10):
						pred_minutesReal = pred_minutes[i]-reminminutes
						if(time[i] not in checkedOnce):
							
							checkedOnce.append(time[i])
							recommendationResult.update({"Early":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"You will be %s min early"%(abs(diff_minutes)),"pred_minutesReal":pred_minutesReal}})
							i+=1#This line should be here
						else:
							recommendationResult.update({"Early":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"You will be %s min early"%(abs(diff_minutes)),"pred_minutesReal":pred_minutesReal}})
							recommendationFlag = False
					

					else:
						pred_minutesReal = pred_minutes[i]-reminminutes
						if (time[i] not in checkedOnce):
							
							checkedOnce.append(time[i])
							recommendationResult.update({"Late":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"You will be %s min late"%(abs(diff_minutes)),"pred_minutesReal":pred_minutesReal}})		
							i-=1 #This line should be here
						else:
							recommendationResult.update({"Late":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"You will be %s min late"%(abs(diff_minutes)),"pred_minutesReal":pred_minutesReal}})		
							recommendationFlag = False

						
				
				recommresult = []
				
				for val in recommendationResult.keys():
					recommresult.append(recommendationResult[val])
				
				pub_dict = {"responseType":1,"route_name":client_data[clientID]['routeName'],"arrival_time":str(DesiredArrivalTime),"recommendation":recommresult}
				publish_handler(client_data[clientID]["clientID"],pub_dict)
				
						

				client_data[clientID].update({"recommndsentproceed":False})
				
				recommendedDepTimeAlgoFunc = []
				for i in range(len(recommresult)):
					recommendedDepTimeAlgoFunc.append(recommresult[i]["predictedDepartureTime"])

				return pub_dict,recommendedDepTimeAlgoFunc
			except Exception as e:
				logging.error("The error occured in recommalgoinnerError is %s,%s"%(e,type(e)))
		
				result = {"responseType":4,"message":"oops!! Internal problem"}
				publish_handler(clientID,result)
					

		else:
			pass

	except Exception as recommalgoError:
		result = {"responseType":4,"message":"oops!! Internal problem"}
		publish_handler(clientID,result)

		logging.error("The error occured in recommalgoError is %s,%s"%(recommalgoError,type(recommalgoError)))
			




'''****************************************************************************************
Function Name 	:	Alerts  (Algorithm operation)
Description		:	Function used to get and send the Alerts to the client
Parameters 		:	clientID - client's UUID   
					alert    - Flag(True-->When journey started , False -->before journey) internal operation purpose
****************************************************************************************'''	
def Alerts(clientID,alert):
	try:	
		Limit = 1

		alertList = [] #according to documentation
				
		routeName = client_data[clientID]["routeName"]
				
		#Alerts are in the ttobgcoll collection so getting the latest alerts for the route 
		for newarkedison_doc in newttobackground.ttobgcoll.find({"route":routeName}).sort('recorddate', pymongo.DESCENDING).limit(Limit):
			endDate = newarkedison_doc['recorddate']
			
		for nedoc in newttobackground.ttobgcoll.find({"route":routeName,"recorddate":endDate}):
			length = len(nedoc['traffic']['incidents'])

		alertseverity = []
		
		for i in range(length):
			if nedoc['traffic']['incidents'][i]['type'] == 4:
				
				alertList.append({"eventType":nedoc['traffic']['incidents'][i]['type'],"shortDesc":nedoc['traffic']['incidents'][i]['shortDesc']})
				alertseverity.append(nedoc['traffic']['incidents'][i]['severity'])
				

		if (len(alertseverity)>1):
			secltdalert = max(alertseverity)
			maxseverealertIndex = alertseverity.index(secltdalert)
			
			alertList = [alertList[maxseverealertIndex]]

		

		alertpub_dict = {"responseType":2,"message":alertList}
		# if there are any alerts then send or dont
		if (len(alertList)>0):
			if alert == True:
				alertpublish_handler(clientID,alertpub_dict)
			else:
				publish_handler(clientID,alertpub_dict)	

	except Exception as alertError:
		logging.error("The error occured in alertError is %s,%s"%(alertError,type(alertError)))
		logging.info(nedoc)				




'''****************************************************************************************
Function Name 	:	beforeJourneyTenminUpdate  (Algorithm operation)
Description		:	Function used invoke the beforeJourney function every ten minute
****************************************************************************************'''	
def beforeJourneyTenminUpdate():
	try:	
		global g_minit,g_sleepTime,g_divCompare
		i = 0
		while True:
			if (len(beforeJourneyClientList.keys())>0):
				for cid in beforeJourneyClientList.keys():
					numofclients = len(beforeJourneyClientList.keys())
					
					if cid in beforeJourneyClientList.keys():
						if i<numofclients:
							try:
								if(int(datetime.datetime.now(pytz.timezone(client_data[cid]['timeZone'])).strftime("%M"))%g_minit == g_divCompare):
									client_data[cid].update({"everyTenminproceed":True})
									i+=1
								else:
									pass
							except Exception as e:
								logging.error("The beforeJourneyTenminUpdateinternalError Exception is %s,%s,%s"%(e,type(e)))
 
								pass

						else:
							i = 0
							time.sleep(g_sleepTime)
					else:
						pass		
										
			else:
				pass
	except Exception as beforeJourneyTenminUpdateError:			
		logging.error("The error occured in beforeJourneyTenminUpdateError is %s,%s"%(beforeJourneyTenminUpdateError,type(beforeJourneyTenminUpdateError)))
					


'''****************************************************************************************
Function Name 	:	startedJourneyTenminUpdate (Algorithm operation)
Description		:	Function used invoke the startedJourney function every ten minute
****************************************************************************************'''
def startedJourneyTenminUpdate():	
		
	try:
		global g_minit,g_sleepTime,g_divCompare
		i = 0
		while True:
			if (len(startedJourneyClientList.keys())>0):
				for cid in startedJourneyClientList.keys():
					if cid in commonStartedClientIDList:	
						numofclients = len(startedJourneyClientList.keys())
						if i<numofclients:
							try:	
								if (int(datetime.datetime.now(pytz.timezone(client_data[cid]['timeZone'])).strftime("%M"))%g_minit == g_divCompare):
									startedJourneyClientList[cid].update({"alertsentproceed":True})
									client_data[cid].update({"everyTenminproceed":True})
								else:
									pass
							except Exception as e:
								
								logging.error("The startedJourneyTenminUpdateinternalError Exception is %s,%s,%s"%(e,type(e)))	
								pass		
							

						else:
							i = 0
							time.sleep(g_sleepTime)

					else:
						pass	
			else:
				pass
	except Exception as startedJourneyTenminUpdateError:			
		logging.error("The error occured in startedJourneyTenminUpdateError is %s,%s"%(startedJourneyTenminUpdateError,type(startedJourneyTenminUpdateError)))
				

		


'''****************************************************************************************
Function Name 	:	stopJourney  (Algorithm operation)
Description		:	Function used to delete the invalid clients from the internal Algorithm operations
****************************************************************************************'''		
def stopJourney(stpCid):
	try:	
		delCid = stpCid
		if delCid in client_data.keys():	
			del client_data[delCid]
		
		if delCid in commonClientIDList:
			index = commonClientIDList.index(delCid)
			del commonClientIDList[index]

		if delCid in commonStartedClientIDList:
			index = commonStartedClientIDList.index(delCid)
			del commonStartedClientIDList[index]
	except Exception as stopJourneyError:
		logging.error("The error occured in stopJourneyError is %s,%s"%(stopJourneyError,type(stopJourneyError)))				



'''****************************************************************************************
Function Name 	:	recommendationAlertFunc  (Algorithm operation)
Description		:	Function used to get and send the Alerts to the client
Parameters 		:	recommtime       - client's Recommended Departure Time
					cid              - client's UUID   
					pred_minutesReal - The travel duration time for the Recommended Departure Time
****************************************************************************************'''	
def recommendationAlertFunc(recommtime,cid,pred_minutesReal):
	try:	
		recommendationAlertPredictions = []
		recommendationAlertTime = []
		cursor = newttobackground.ttoresultcoll.find({"route":client_data[cid]['routeName']})
		
		for doc in cursor:
			recommendationAlertPredictions.append(doc['predictioninmins'])
			recommendationAlertTime.append(doc['time'])

		if recommtime in recommendationAlertTime:
			recommendationAlertIndex = recommendationAlertTime.index(recommtime)
		val = int(recommendationAlertPredictions[recommendationAlertIndex]) * 60
		pred_minutesReal = int(pred_minutesReal) * 60

		
		if pred_minutesReal == val:
			return 1,0
		else:
			diff = pred_minutesReal - val
			return 0,float(diff)/60.0
	except Exception as recommendationAlertFuncError:
		logging.error("The error occured in recommendationAlertFuncError is %s,%s"%(recommendationAlertFuncError,type(recommendationAlertFuncError)))
		



'''****************************************************************************************
Function Name 	:	beforeJourney (Algorithm operation)
Description		:	Function responsible for updates regarding the change in Recommendation change
					and Alerts before journey starts 
****************************************************************************************'''	
def beforeJourney():
	try:
		global g_minit,g_divCompare
		while True:
			if (len(beforeJourneyClientList.keys())>0):
				for cid in beforeJourneyClientList.keys():
					if cid in commonClientIDList:
						localDict = client_data[cid]

						presentrouteTime =  datetime.datetime.now(pytz.timezone(localDict['timeZone']))

						recommendedTime = beforeJourneyClientList[cid]["recommendedDepTime"]
						
						diff = recommendedTime-presentrouteTime 
						diffMin = (diff.days * 24 * 60) + (diff.seconds/60)
							
						# enters into this condition only clients recommendation time is 2hrs ahead
						# and executes every10min thats why one more condition checking for 10mins
						if (10<=diffMin<= 720):
							val = datetime.datetime.now(pytz.timezone(localDict['timeZone'])).strftime("%M")
							if (int(val)%g_minit == g_divCompare and localDict['everyTenminproceed'] == True):#make sure you are dividing with 10 for the 10min purpose
								arrivalTime = datetime.datetime.strptime(localDict["arrivalTime"], "%Y-%m-%d %H:%M:%S")
								zone = pytz.timezone(localDict["timeZone"])
								arrivalTime = zone.localize(arrivalTime)
								
								
								existedRecommendation = beforeJourneyClientList[cid]["recommendedDepTime"]
								existedpredminutesReal = beforeJourneyClientList[cid]["pred_minutesReal"]

								existedRecommendation = existedRecommendation.replace(tzinfo=None)
								
								result,val = recommendationAlertFunc(existedRecommendation,cid,existedpredminutesReal)
								
								if result == "notsame":
									localDict.update({"recommndsentproceed":True})
									# means new recommendation
									localDict.update({"everyTenminproceed":False})
									# means comeback after 10mins

									if val > 0:
										message = {"responseType":3,"message":"You should start %smin after %s"%(int(val),str(recommendedTime))}
									if val < 0:	
										message = {"responseType":3,"message":"You should start %smin earlier than %s "%(abs(int(val)),str(recommendedTime))}
									publish_handler(cid,message)
								else:
									# localDict.update({"recommndsentproceed":False})
									# # means new recommendation
									localDict.update({"everyTenminproceed":False})
									# means comeback after 10mins
									pass
											
								
								# now Alerts
								localDict.update({"recommndsentproceed":True})
								Alerts(cid,False) 
								localDict.update({"recommndsentproceed":False})

								# updating to main dictionary
								if cid in client_data.keys():
									client_data[cid].update({"recommndsentproceed":localDict["recommndsentproceed"],"everyTenminproceed":localDict["everyTenminproceed"]})

							else:
								pass		

					else:
						#  it means client started the journey moved to startjourneylist
						del beforeJourneyClientList[cid]
			else:
				pass

	except Exception as beforejourneyError:								
		logging.error("The error occured in beforejourneyError is %s,%s"%(beforejourneyError,type(beforejourneyError)))




'''****************************************************************************************
Function Name 	:	startedJourney (Algorithm operation)
Description		:	Function responsible to send Alerts if any after journey starts
****************************************************************************************'''	
def startedJourney():
	try:	
		global g_minit,g_sleepTime,g_divCompare
		while True:
			if (len(startedJourneyClientList.keys())>0):
				for strtCid in startedJourneyClientList.keys():
					if strtCid in commonStartedClientIDList:
						presentrouteTimeminute = int(datetime.datetime.now(pytz.timezone(client_data[strtCid]['timeZone'])).strftime("%M"))

						if (presentrouteTimeminute%g_minit == g_divCompare and client_data[strtCid]['everyTenminproceed'] == True):
							Alerts(strtCid,True)
							client_data[strtCid].update({"everyTenminproceed":False})	
								
						else:
							pass
					else:
						del startedJourneyClientList[strtCid]
						
					
			else:
				pass
	except Exception as startedJourneyError:
		logging.error("The error occured in startedJourneyError is %s,%s"%(startedJourneyError,type(startedJourneyError)))
							


'''****************************************************************************************
Function Name 	:	delCheck  (Algorithm operation)
Description		:	Function responsible to delete the expired clients
****************************************************************************************'''
def delCheck():
	try:
		global g_sleepTime
		while True:
			if len(client_data.keys())>0:
				
				for clientID in client_data.keys():
					DAT = datetime.datetime.strptime(client_data[clientID]["arrivalTime"], "%Y-%m-%d %H:%M:%S")	
					
					zone = pytz.timezone(client_data[clientID]["timeZone"])
					DAT = zone.localize(DAT)
					
					presentrouteTime =  datetime.datetime.now(pytz.timezone(client_data[clientID]['timeZone']))
					diff = DAT - presentrouteTime 
					diff_minutes = (diff.days *24*60)+(diff.seconds/60)
					if diff_minutes < 0:
						
						if clientID in client_data.keys():
							del client_data[clientID]
						
					else:
						pass
				time.sleep(g_sleepTime)		
			else:
				pass
	except Exception as delCheckError:
		logging.error("The error occured in delCheckError is %s,%s"%(delCheckError,type(delCheckError)))				




'''****************************************************************************************
Function Name 	:	tto_callback  (Callback operation)
Description		:	Callback function listens to the channel for the messages
Parameters 		:	message - message from the client
					channel - UUID of the client
****************************************************************************************'''
def tto_callback(message,channel):
	try:	
		clientID = str(message['CID'])
		requestType = int(message['requestType'])
			
		if clientID in client_data.keys():
			
			if requestType == 1: # request for the recommendation 
				# here client should be there in the commonClientIDList because we are adding it at time of entrance
				if clientID not in commonClientIDList:
					commonClientIDList.append(clientID)

				routeName = str(message['routeName'])#only in requesttype 1 we will get it
				# adding necessary client data
				client_data[clientID] = {"clientID":clientID,"timeZone":zone_ttimedct[routeName][0],"theoryTime":zone_ttimedct[routeName][1],"arrivalTime":message['arrivalTime'],"routeName":routeName,"everyTenminproceed":False,"recommndsentproceed":True,"alertsentproceed":False}	
				# datetime format
				arrivalTime = datetime.datetime.strptime(message['arrivalTime'], "%Y-%m-%d %H:%M:%S")
				# adding timezone using localizing technique
				zone = pytz.timezone(client_data[clientID]["timeZone"])
				arrivalTime = zone.localize(arrivalTime)
				
				recommendationAlgoFunc(arrivalTime,clientID)#calling the recommendation algorithm function

			if requestType == 2: #request for starting the journey
				
				startTime = datetime.datetime.strptime(message["startTime"],"%Y-%m-%d %H:%M:%S")
				
				zone = pytz.timezone(client_data[clientID]["timeZone"])
				arrivalTime = zone.localize(startTime)
				
				
				startedJourneyClientList.update({clientID:{"clientID":clientID,"recommendedTime":startTime}})
				# updating alertsentproceed so the alerts will work for the client
				client_data[clientID].update({"alertsentproceed":True}) 
				# callling the alertsent function 
				Alerts(clientID,True)
				
				# incase if the client started journey immeddiately before entering into the beforejourney list
				if clientID in commonClientIDList:
					index = commonClientIDList.index(clientID)
					del commonClientIDList[index]
					# del beforeJourneyClientList[message['CID']]
				
				# sharing client id with started journey list so that there wont any problem for the dependency functions 
				if clientID not in commonStartedClientIDList:
					commonStartedClientIDList.append(clientID)

			if requestType == 3: #when clients ends the journey
				stpCid = str(message['CID'])
				stopJourney(stpCid)			

			if requestType == 4:# confirmation from the client to remember the query
				recommendedDepTime = datetime.datetime.strptime(message['recommendedDepTime'], "%Y-%m-%d %H:%M:%S")	
				
				zone = pytz.timezone(client_data[clientID]["timeZone"])
				recommendedDepTime = zone.localize(recommendedDepTime)
				
				beforeJourneyClientList[clientID] = {"clientID":clientID,"recommendedDepTime":recommendedDepTime,"pred_minutesReal":message['pred_minutesReal']}				
				
				
		else:
			if requestType == 1:

				if clientID not in commonClientIDList:
					commonClientIDList.append(clientID)

				routeName = str(message['routeName'])#only in requesttype 1 we will get it
				# adding necessary client data
				client_data[clientID] = {"clientID":clientID,"timeZone":zone_ttimedct[routeName][0],"theoryTime":zone_ttimedct[routeName][1],"arrivalTime":message['arrivalTime'],"routeName":routeName,"everyTenminproceed":False,"recommndsentproceed":True,"alertsentproceed":False}	
				# datetime format
				arrivalTime = datetime.datetime.strptime(message['arrivalTime'], "%Y-%m-%d %H:%M:%S")
				# adding timezone using localizing technique
				zone = pytz.timezone(client_data[clientID]["timeZone"])
				arrivalTime = zone.localize(arrivalTime)
				
				recommendationAlgoFunc(arrivalTime,clientID)#calling the recommendation algorithm function
	except Exception as callbackError:
		logging.error("The error occured in callbackError is %s,%s"%(callbackError,type(callbackError)))

					
		
		


'''****************************************************************************************
Function Name 	:	error
Description		:	If error in the channel, prints the error
Parameters 		:	message - error message
****************************************************************************************'''
def error(message):
    logging.error("ERROR on Pubnub: " + str(message))

'''****************************************************************************************
Function Name 	:	connect
Description		:	Responds if server connects with pubnub
Parameters 		:	message - connect message
****************************************************************************************'''	
def connect(message):
	logging.info("CONNECTED")

'''****************************************************************************************
Function Name 	:	reconnect
Description		:	Responds if server reconnects with pubnub
Parameters 		:	message - reconnect message
****************************************************************************************'''	
def reconnect(message):
    logging.info("RECONNECTED")

'''****************************************************************************************
Function Name 	:	disconnect
Description		:	Responds if server disconnects from pubnub
Parameters 		:	message - disconnect message
****************************************************************************************'''
def disconnect(message):
     logging.info("DISCONNECTED")



'''****************************************************************************************
Function Name 	:	channel_subscriptions  (pubnub operation)
Description		:	Function intializes the pubnub subscribing to a specific channel
****************************************************************************************'''
def channel_subscriptions():
	global pubnub
	try:
		pubnub.subscribe(channels='ttotest1', callback=tto_callback,error=error,
		connect=connect, reconnect=reconnect, disconnect=disconnect)
	except Exception as channelsubserror:
		logging.error("The error occured in channel_subscriptions is %s,%s"%(channelsubserror,type(channelsubserror)))


'''****************************************************************************************
Function Name 	:	mongoInit  (Mongodb operation)
Description		:	Function initalizes the mongodb connection
****************************************************************************************'''
def mongoInit():
	global newttobackground
	try:
		uri ='mongodb://rajeevtto:radiostud@ds035315-a0.mongolab.com:35315,ds035315-a1.mongolab.com:35315/newttobackground?replicaSet=rs-ds035315'
		client = MongoClient(uri)
		newttobackground = client.newttobackground
		
		logging.info('connected')
	except Exception as e:
		logging.error("The error occured in mongoInit is %s,%s"%(e,type(e)))


'''****************************************************************************************
Function Name 	:	pub_Init  (pubnub operation)
Description		:	Function intializes the pubnub connection
****************************************************************************************'''
def pub_Init():
	global pubnub
	
	try:
		pubnub = Pubnub(publish_key=pub_key,subscribe_key=sub_key) 
		return True
	except Exception as pubException:
		logging.error("The pubException is %s,%s"%(pubException,type(pubException)))

		return False


'''****************************************************************************************
Function Name 	:	Init (Functional operation)
Description		:	Function initializes the pubinit and mongoinit
****************************************************************************************'''
def Init():
	dBreturn = mongoInit()
	pbreturn = pub_Init()
	if (dBreturn == False or pbreturn == False):
		logging.info("Program Terminated")
		sys.exit()
	else:
		channel_subscriptions()	


if __name__ == '__main__':
	try:
		f1 = threading.Thread(target = Init)
		f2 = threading.Thread(target = beforeJourney)
		f3 = threading.Thread(target = startedJourney)
		f4 = threading.Thread(target = beforeJourneyTenminUpdate)
		f5 = threading.Thread(target = startedJourneyTenminUpdate)
		f6 = threading.Thread(target = delCheck)
		f1.start()
		f2.start()
		f4.start()
		f3.start()
		f5.start()
		f6.start()
	except Exception as e:
		logging.error("The main Exception is %s,%s"%(e,type(e)))
	

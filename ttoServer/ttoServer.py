import pymongo
from pymongo import MongoClient

import datetime
import pytz

import math
import time
import datetime

from pubnub import Pubnub

import threading

import logging

pub_key ='pub-c-f2fc0469-ad0f-4756-be0c-e003d1392d43'
sub_key ='sub-c-4d48a9d8-1c1b-11e6-9327-02ee2ddab7fe'


LOG_FILENAME = 'TTO_serverlogs.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


g_minit = 10
g_sleepTime = 580
g_divCompare = 3

# Dictionaries and Lists to store the Data
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
					result           - The result i.e.,   The dictionary contains recommendations or alerts
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
						logging.error("The publish return error  %s for the client %s\n"%(pbreturn[1],channel))
						pbtry+=1
					else:
						pass
				except Exception as error_pdhandler:
					logging.error("The error_pdhandler Exception is %s,%s\n"%(error_pdhandler,type(error_pdhandler)))

					pbtry+=1
		else:
			pass
	except Exception as pubhandlerError:
		logging.error("The publish function Exception is %s,%s,%s\n"%(pubhandlerError,type(pubhandlerError),str(result)))

					

'''****************************************************************************************
Function Name 	:	alertpublish_handler  (pubnub operation)
Description		:	Function used to publish the data to the client
Parameters 		:	channel          - UUID of the client   
					result           - The result i.e.,   The dictionary contains recommendations or alerts
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
						logging.error("The publish return error  %s for the client %s\n"%(pbreturn[1],channel))
						pbtry+=1
					else:
						pass
				except Exception as error_pdhandler:
					logging.error("The alerterror_pdhandler Exception is %s,%s\n"%(error_pdhandler,type(error_pdhandler)))

					pbtry+=1
		else:
			pass
	except Exception as alertpubhandlerError:
		logging.error("The alertpublish function Exception is %s,%s,%s\n"%(alertpubhandlerError,type(alertpubhandlerError),str(result)))

				

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
		
		dateproceed = False

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

		# All the mongolab operations are inside the try exception block
		try:
			# This is to get the latest date in the mongodb
			dateCursor = newttobackground.ttobgcoll.find({"route":client_data[clientID]['routeName']}).sort('recorddate', pymongo.DESCENDING).limit(Limit)
			
			for newarkedison_doc in dateCursor:
					endDate = newarkedison_doc['recorddate']
			dateproceed = True		
		except Exception as e:
			dateproceed = False
			result = {"responseType":4,"message":"oops!! Internal problem"}
			publish_handler(clientID,result)
			logging.error("The dateCursor error is %s,%s\n"%(e,type(e)))

		if dateproceed == True:

			diff = DesiredArrivalTime-route_time

			day  = diff.days
			hour = (day*24 + diff.seconds/3600)
			
			realtimeinminutes = []
			time = []
			realtimeinsec = []
				
			try:
				#This is to get the predictions from the result collection 
				cursor = newttobackground.ttoresultcoll.find({"route":client_data[clientID]['routeName']}).sort('time', pymongo.ASCENDING).limit(150)
				
				if (0<=hour <= 12 and 0<=day<=1):
					
					proceed = True
					for nedoc in cursor:
						 time.append(nedoc['time'])
						 realtimeinminutes.append(nedoc['predictioninmins'])
						 realtimeinsec.append(nedoc['predictioninsecs'])
				else:
					if day < 0:
						result = {"responseType":4,"message":"Desired Arrival Time is below 12 hours range"}
					else:	
						result = {"responseType":4,"message":"Desired Arrival Time is more than 12 hours away"}
					publish_handler(clientID,result)
					proceed = False
					del client_data[clientID]
			except Exception as e:
				logging.error("The testdatacursor error is %s,%s\n"%(e,type(e)))
				proceed = False
				result = {"responseType":4,"message":"oops!! Internal problem"}
				publish_handler(clientID,result)

			timediffinminutes = []
			timediffinsecs = []
			if (proceed == True):
				for i,j in zip(realtimeinsec,realtimeinminutes):
					timediffinsecs.append((((float(i)-(theorytimeinsecs)))+reminsecs))
					timediffinminutes.append((((float(j)-(theorytimeinminutes)))+reminminutes))
				
				DesiredArrivalTimeIndexInList = -1
				
				for i in range(len(time)):
					if (int(DesiredArrivalTime.strftime("%H")) == int(time[i].strftime("%H")) and int(DesiredArrivalTime.strftime("%M")) == int(time[i].strftime("%M"))):
						DesiredArrivalTimeIndexInList = time.index(time[i])
								
				try:
					if DesiredArrivalTimeIndexInList != -1:		
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
									recommendationResult.update({"Early":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"You will reach %s min early"%(abs(diff_minutes)),"pred_minutesReal":pred_minutesReal}})
									i+=1#This line should be here
								else:
									recommendationResult.update({"Early":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"You will reach %s min early"%(abs(diff_minutes)),"pred_minutesReal":pred_minutesReal}})
									recommendationFlag = False
							

							else:
								pred_minutesReal = pred_minutes[i]-reminminutes
								if (time[i] not in checkedOnce):
									
									checkedOnce.append(time[i])
									recommendationResult.update({"Late":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"You will reach %s min late"%(abs(diff_minutes)),"pred_minutesReal":pred_minutesReal}})		
									i-=1 #This line should be here
								else:
									recommendationResult.update({"Late":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"You will reach %s min late"%(abs(diff_minutes)),"pred_minutesReal":pred_minutesReal}})		
									recommendationFlag = False

								
						
						recommresult = []
						
						for val in recommendationResult.keys():
							recommresult.append(recommendationResult[val])
						
						pub_dict = {"responseType":1,"route_name":client_data[clientID]['routeName'],"arrival_time":str(DesiredArrivalTime.replace(tzinfo=None)),"recommendation":recommresult}
						publish_handler(client_data[clientID]["clientID"],pub_dict)
						logging.info("The sent message for the recommendationmessage%s\n"%(str(pub_dict)))
							
						client_data[clientID].update({"recommndsentproceed":False})
						
						# recommendedDepTimeAlgoFunc = []
						# for i in range(len(recommresult)):
						# 	recommendedDepTimeAlgoFunc.append(recommresult[i]["predictedDepartureTime"])


						# return pub_dict,recommendedDepTimeAlgoFunc
						
				except Exception as e:
					logging.error("The error occured in recommalgoinnerError is %s,%s\n"%(e,type(e)))
			
					result = {"responseType":4,"message":"oops!! Internal problem"}
					publish_handler(clientID,result)


	except Exception as recommalgoError:
		result = {"responseType":4,"message":"oops!! Internal problem"}
		publish_handler(clientID,result)

		logging.error("The error occured in recommalgoError is %s,%s\n"%(recommalgoError,type(recommalgoError)))
			




'''****************************************************************************************
Function Name 	:	Alerts  (Algorithm operation)
Description		:	Function used to get and send the Alerts to the client
Parameters 		:	clientID - client's UUID   
					alert    - Flag(True-->When journey started , False -->before journey) internal operation purpose
****************************************************************************************'''	
def Alerts(clientID,alert):
	try:	
		Limit = 1

		alertList = [] 
				
		routeName = client_data[clientID]["routeName"]
		
		alertcursorproceed = False
		length = -1	

		try:		
			#Alerts are in the ttobgcoll collection so getting the latest alerts for the route 
			for newarkedison_doc in newttobackground.ttobgcoll.find({"route":routeName}).sort('recorddate', pymongo.DESCENDING).limit(Limit):
				endDate = newarkedison_doc['recorddate']
				
			for nedoc in newttobackground.ttobgcoll.find({"route":routeName,"recorddate":endDate}):
				length = len(nedoc['traffic']['incidents'])
			alertcursorproceed = True	
		except Exception as e:
			logging.error("The latestalertcursor error is %s,%s\n"%(e,type(e)))

		alertseverity = []
		
		if (alertcursorproceed == True and length != -1):
			for i in range(length):
				if nedoc['traffic']['incidents'][i]['type'] == 4:
					
					alertList.append({"eventType":nedoc['traffic']['incidents'][i]['type'],"shortDesc":nedoc['traffic']['incidents'][i]['shortDesc']})
					alertseverity.append(nedoc['traffic']['incidents'][i]['severity'])
					

			if (len(alertseverity)>1):
				secltdalert = max(alertseverity)
				maxseverealertIndex = alertseverity.index(secltdalert)
				
				alertList = [alertList[maxseverealertIndex]]

			

			alertpub_dict = {"responseType":2,"message":alertList}
			logging.info("AlertsMessage-->%s,%s\n"%(str(alertpub_dict),str(clientID)))
			# if there are any alerts then send or dont
			if (len(alertList)>0):
				if alert == True:
					alertpublish_handler(clientID,alertpub_dict)
				else:
					publish_handler(clientID,alertpub_dict)
		else:
			pass				

	except Exception as alertError:
		logging.error("The error occured in alertError is %s,%s\n"%(alertError,type(alertError)))
		logging.info(str(nedoc)+"\n")				




'''****************************************************************************************
Function Name 	:	beforeJourneyTenminUpdate  (Algorithm operation)
Description		:	Function used invoke the beforeJourney function every ten minute
****************************************************************************************'''	
def beforeJourneyTenminUpdate():
	while True:
		try:	
			global g_minit,g_sleepTime,g_divCompare
			i = 0
			while True:
				if (len(beforeJourneyClientList.keys())>0):
					
					localDictbeforeJourneyupdate = client_data

					for cid in beforeJourneyClientList.keys():
						numofclients = len(beforeJourneyClientList.keys())
						
						if cid in beforeJourneyClientList.keys():
							if i<numofclients:
								try:
									if(int(datetime.datetime.now(pytz.timezone(localDictbeforeJourneyupdate[cid]['timeZone'])).strftime("%M"))%g_minit == g_divCompare):
										
										if cid in client_data.keys():
											client_data[cid].update({"everyTenminproceed":True})
										
										i+=1
									
								except Exception as e:
									print client_data,cid
									logging.error("The beforeJourneyTenminUpdateinternalError Exception is %s,%s\n"%(e,type(e)))
	 
									

							else:
								i = 0
								time.sleep(g_sleepTime)
				
		except Exception as beforeJourneyTenminUpdateError:			
			logging.error("The error occured in beforeJourneyTenminUpdateError is %s,%s\n"%(beforeJourneyTenminUpdateError,type(beforeJourneyTenminUpdateError)))
						


'''****************************************************************************************
Function Name 	:	startedJourneyTenminUpdate (Algorithm operation)
Description		:	Function used invoke the startedJourney function every ten minute
****************************************************************************************'''
def startedJourneyTenminUpdate():	
	while True:		
		try:
			global g_minit,g_sleepTime,g_divCompare
			i = 0
			while True:
				if (len(startedJourneyClientList.keys())>0):

					localDictStartedJourneyupdate = client_data
					
					for cid in startedJourneyClientList.keys():
						if cid in commonStartedClientIDList:	
							numofclients = len(startedJourneyClientList.keys())
							if i<numofclients:
								try:	
									if (int(datetime.datetime.now(pytz.timezone(localDictStartedJourneyupdate[cid]['timeZone'])).strftime("%M"))%g_minit == g_divCompare):
										
										if cid in startedJourneyClientList.keys():
											startedJourneyClientList[cid].update({"alertsentproceed":True})
										
										if cid in client_data.keys():
											client_data[cid].update({"everyTenminproceed":True})
										
										i+=1	
									
								except Exception as e:
									
									logging.error("The startedJourneyTenminUpdateinternalError Exception is %s,%s\n"%(e,type(e)))	
											
								

							else:
								i = 0
								time.sleep(g_sleepTime)

		except Exception as startedJourneyTenminUpdateError:			
			logging.error("The error occured in startedJourneyTenminUpdateError is %s,%s\n"%(startedJourneyTenminUpdateError,type(startedJourneyTenminUpdateError)))
					

		


'''****************************************************************************************
Function Name 	:	stopJourney  (Algorithm operation)
Description		:	Function used to delete the invalid clients from the internal Algorithm operations
****************************************************************************************'''		
def stopJourney(stpCid):
	# Deleting clients from only commonclient lists and client_data
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
		logging.error("The error occured in stopJourneyError is %s,%s\n"%(stopJourneyError,type(stopJourneyError)))				



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
		recommendationAlertIndex = -1	
	
		recommtime = recommtime.replace(second=0)
		try:	
			cursor = newttobackground.ttoresultcoll.find({"route":client_data[cid]['routeName']})
			
			for doc in cursor:
				recommendationAlertPredictions.append(doc['predictioninmins'])
				recommendationAlertTime.append(doc['time'].replace(second=0))

			if recommtime in recommendationAlertTime:
				recommendationAlertIndex = recommendationAlertTime.index(recommtime)
			
			
		except Exception as e:
			logging.error("The error occured in internal recommendationAlertFunc is %s,%s\n"%(e,type(e)))	
		
		if (recommendationAlertIndex != -1):
			val = int(recommendationAlertPredictions[recommendationAlertIndex]) * 60
			pred_minutesReal = int(pred_minutesReal) * 60

			if pred_minutesReal == val:
				logging.info("recommendationAlertMessage--> no change%s,%s\n"%(str(val),str(pred_minutesReal)))
				return 1,0
			else:
				diff = pred_minutesReal - val
				
				logging.info("recommendationAlertMessage-->change in predictions %s,%s,%s\n"%(str(val),str(pred_minutesReal),str(float(diff)/60.0)))
				return 0,float(diff)/60.0
		else:
			logging.info("The recommtime-->%s"%(str(recommtime)))
			pass	

	except Exception as recommendationAlertFuncError:

		logging.error("The error occured in recommendationAlertFuncError is %s,%s\n"%(recommendationAlertFuncError,type(recommendationAlertFuncError)))
		



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
				
				localDict = client_data[cid]

				for cid in beforeJourneyClientList.keys():
					if cid in commonClientIDList:
						

						presentrouteTime =  datetime.datetime.now(pytz.timezone(localDict['timeZone']))

						recommendedTime = beforeJourneyClientList[cid]["recommendedDepTime"]
						
						diff = recommendedTime-presentrouteTime 
						diffMin = (diff.days * 24 * 60) + (diff.seconds/60)
							
						# executes every10min thats why one more condition checking for 10mins
						if (0<=diffMin<= 720):
							val = datetime.datetime.now(pytz.timezone(localDict['timeZone'])).strftime("%M")
							if (int(val)%g_minit == g_divCompare and localDict['everyTenminproceed'] == True):#make sure you are dividing with 10 for the 10min purpose
								arrivalTime = datetime.datetime.strptime(localDict["arrivalTime"], "%Y-%m-%d %H:%M:%S")
								zone = pytz.timezone(localDict["timeZone"])
								arrivalTime = zone.localize(arrivalTime)
								
								
								existedRecommendation = beforeJourneyClientList[cid]["recommendedDepTime"]
								existedpredminutesReal = beforeJourneyClientList[cid]["pred_minutesReal"]

								existedRecommendation = existedRecommendation.replace(tzinfo=None)
								
								result,val = recommendationAlertFunc(existedRecommendation,cid,existedpredminutesReal)
								logging.info("beforejourneyMessage-->clients now%s\n"%(str(cid)))
								if result == 0:#Different prediction 
									localDict.update({"recommndsentproceed":True})
									# means new recommendation
									localDict.update({"everyTenminproceed":False})
									# means comeback after 10mins

									if val > 0:
										message = {"responseType":3,"message":"You should start %smin after %s"%(int(val),str(recommendedTime.replace(second=0,tzinfo=None)))}
									if val < 0:	
										message = {"responseType":3,"message":"You should start %smin earlier than %s "%(abs(int(val)),str(recommendedTime.replace(second=0,tzinfo=None)))}
									logging.info("recommendationAlert -->%s"%(str(message)))
									publish_handler(cid,message)
								else:
									# # means new recommendation
									localDict.update({"everyTenminproceed":False})
									
											
								
								#Alerts
								localDict.update({"recommndsentproceed":True})
								Alerts(cid,False) 
								localDict.update({"recommndsentproceed":False})

								# updating to main dictionary
								if cid in client_data.keys():
									client_data[cid].update({"recommndsentproceed":localDict["recommndsentproceed"],"everyTenminproceed":localDict["everyTenminproceed"]})
									

					else:
						#  it means client started the journey moved to startjourneylist
						del beforeJourneyClientList[cid]
			

	except Exception as beforejourneyError:								
		logging.error("The error occured in beforejourneyError is %s,%s\n"%(beforejourneyError,type(beforejourneyError)))




'''****************************************************************************************
Function Name 	:	startedJourney (Algorithm operation)
Description		:	Function responsible to send Alerts if any after journey starts
****************************************************************************************'''	
def startedJourney():
	while True:
		try:	
			global g_minit,g_sleepTime,g_divCompare
			while True:
				if (len(startedJourneyClientList.keys()) == len(commonStartedClientIDList)):
					localDictStartedJourney = client_data
					for strtCid in startedJourneyClientList.keys():
						
						if strtCid in commonStartedClientIDList:

							presentrouteTimeminute = int(datetime.datetime.now(pytz.timezone(localDictStartedJourney[strtCid]['timeZone'])).strftime("%M"))
							if (presentrouteTimeminute%g_minit == g_divCompare and localDictStartedJourney[strtCid]['everyTenminproceed'] == True):
								logging.info("startedJourneyMessage--> Clients now%s\n"%(str(strtCid)))
							
								Alerts(strtCid,True)
								if strtCid in client_data.keys():
									client_data[strtCid].update({"everyTenminproceed":False})
										
										
						
				else:
					for strtCid in startedJourneyClientList.keys():
						if strtCid not in commonStartedClientIDList:
							del startedJourneyClientList[strtCid]
								
					

		except Exception as startedJourneyError:
			logging.error("The error occured in startedJourneyError is %s,%s\n"%(startedJourneyError,type(startedJourneyError)))
							


'''****************************************************************************************
Function Name 	:	delCheck  (Algorithm operation)
Description		:	Function responsible to delete the expired clients
****************************************************************************************'''
def delCheck():
	while True:
		try:
			global g_sleepTime,g_minit
			i=0
			while True:
				if len(client_data.keys())>0:
					localDictDelcheck = client_data
					for clientID in localDictDelcheck.keys():

						numofclients = len(localDictDelcheck.keys())
						if i<numofclients:

							if (int(datetime.datetime.now(pytz.timezone(localDictDelcheck[clientID]['timeZone'])).strftime("%M"))%g_minit == 0):
								
								if clientID in localDictDelcheck.keys():
									DAT = datetime.datetime.strptime(str(localDictDelcheck[clientID]["arrivalTime"]), "%Y-%m-%d %H:%M:%S")	
									
									zone = pytz.timezone(localDictDelcheck[clientID]["timeZone"])
									DAT = zone.localize(DAT)
									# Deleting the clients that crossed the Arrival time range.
									travelTime = int(localDictDelcheck[clientID]['theoryTime'])+3600
									journeyEndTime = DAT + datetime.timedelta(seconds=travelTime)# journey time with extra 20min buffer
								
									presentrouteTime =  datetime.datetime.now(pytz.timezone(localDictDelcheck[clientID]['timeZone']))
													
									diff = journeyEndTime - presentrouteTime 
									diff_minutes = (diff.days *24*60)+(diff.seconds/60)		
									
									if diff_minutes<=0:
								
										# clearing the startedJourneyList dictionary.
										if clientID in startedJourneyClientList.keys():
											logging.info("delCheckMessage--> Something to Delete in startedJourneyClientList %s,%s\n"%(str(clientID),str(DAT)))
											del startedJourneyClientList[clientID]
											if clientID in client_data.keys():
												logging.info("delCheckMessage--> Something to Delete in client_data %s,%s\n"%(str(clientID),str(DAT)))
												del client_data[clientID]

										#clearing the commonStartedClientIDList. 
										if clientID in commonStartedClientIDList:
											logging.info("delCheckMessage--> Something to Delete in commonStartedClientIDList %s,%s\n"%(str(clientID),str(DAT)))
											
											index = commonStartedClientIDList.index(clientID)
											del commonStartedClientIDList[index]
											



										
									else:
										# timerange over checking else part
										logging.info("delCheckMessage--> Nothing to Delete%s,%s\n"%(str(clientID),str(DAT)))
										pass
								else:
									# client_data keys checking else part
									pass
								
								i+=1
											
							else:
								# entered 10min interval checking else part
								pass				
						else:
							i=0
							time.sleep(g_sleepTime)		
				
		except Exception as delCheckError:
			logging.error("The error occured in delCheckError is %s,%s\n"%(delCheckError,type(delCheckError)))				




'''****************************************************************************************
Function Name 	:	tto_callback  (Callback operation)
Description		:	Callback function listens to the channel for the messages
Parameters 		:	message - message from the client
					channel - UUID of the client
****************************************************************************************'''
def tto_callback(message,channel):
	try:
		if message.has_key("requestType") and message.has_key("CID"):
			logging.info(str(message)+"\n")#printing the message we receive from the client
			clientID = str(message['CID'])
			requestType = int(message['requestType'])
					
			if clientID in client_data.keys():
				
				if requestType == 1: # request for the recommendation 
					# here client should be there in the commonClientIDList because we are adding it at time of entrance
					if clientID not in commonClientIDList:
						commonClientIDList.append(clientID)

					routeName = str(message['routeName'])#only in requesttype 1 we will get it
					# adding necessary client data
					# client_data[clientID] = {"clientID":clientID,"timeZone":zone_ttimedct[routeName][0],"theoryTime":zone_ttimedct[routeName][1],"arrivalTime":str(message['arrivalTime']),"routeName":routeName,"everyTenminproceed":False,"recommndsentproceed":True,"alertsentproceed":False}	
					
					if not client_data.has_key(clientID):
						client_data.setdefault(clientID,{"clientID":clientID,"timeZone":zone_ttimedct[routeName][0],"theoryTime":zone_ttimedct[routeName][1],"arrivalTime":str(message['arrivalTime']),"routeName":routeName,"everyTenminproceed":False,"recommndsentproceed":True,"alertsentproceed":False})	


					# datetime format
					arrivalTime = datetime.datetime.strptime(str(message['arrivalTime']), "%Y-%m-%d %H:%M:%S")
					# adding timezone using localizing technique
					zone = pytz.timezone(client_data[clientID]["timeZone"])
					arrivalTime = zone.localize(arrivalTime)
					
					recommendationAlgoFunc(arrivalTime,clientID)#calling the recommendation algorithm function

				if requestType == 2: #request for starting the journey
					
					startTime = datetime.datetime.strptime(str(message["startTime"]),"%Y-%m-%d %H:%M:%S")
					
					zone = pytz.timezone(client_data[clientID]["timeZone"])
					arrivalTime = zone.localize(startTime)
					
					# sharing client id with started journey list so that there wont any problem for the dependency functions 
					if clientID not in commonStartedClientIDList:
						commonStartedClientIDList.append(clientID)
					
					# startedJourneyClientList.update({clientID:{"clientID":clientID,"recommendedTime":startTime}})
					if not startedJourneyClientList.has_key(clientID):
						startedJourneyClientList.setdefault(clientID,{"clientID":clientID,"recommendedTime":arrivalTime})
					
					
					
					# incase if the client started journey immeddiately before entering into the beforejourney list
					if clientID in commonClientIDList:
						index = commonClientIDList.index(clientID)
						del commonClientIDList[index]
						# del beforeJourneyClientList[message['CID']]
					
					# updating alertsentproceed so the alerts will work for the client
					client_data[clientID].update({"alertsentproceed":True}) 
						
					
					# callling the alertsent function 
					Alerts(clientID,True)
					
				

					logging.info("The clients in startedJourney stage %s\n"%(str(startedJourneyClientList)))	
				if requestType == 3: #when clients ends the journey
					stpCid = str(message['CID'])
					stopJourney(stpCid)			

				if requestType == 4:# confirmation from the client to remember the query
					recommendedDepTime = datetime.datetime.strptime(message['recommendedDepTime'], "%Y-%m-%d %H:%M:%S")	
					
					zone = pytz.timezone(client_data[clientID]["timeZone"])
					recommendedDepTime = zone.localize(recommendedDepTime)
					
					# beforeJourneyClientList[clientID] = {"clientID":clientID,"recommendedDepTime":recommendedDepTime,"pred_minutesReal":message['pred_minutesReal']}				
					
					if not beforeJourneyClientList.has_key(clientID):
						beforeJourneyClientList.setdefault(clientID,{"clientID":clientID,"recommendedDepTime":recommendedDepTime,"pred_minutesReal":message['pred_minutesReal']})
					

					logging.info("The clients in the beforeJourney stage%s\n"%(str(beforeJourneyClientList)))
					
			else:
				
				
				if requestType == 1:
					
					if clientID not in commonClientIDList:
						commonClientIDList.append(clientID)

					routeName = str(message['routeName'])#only in requesttype 1 we will get it
					# adding necessary client data
					# client_data[clientID] = {"clientID":clientID,"timeZone":zone_ttimedct[routeName][0],"theoryTime":zone_ttimedct[routeName][1],"arrivalTime":str(message['arrivalTime']),"routeName":routeName,"everyTenminproceed":False,"recommndsentproceed":True,"alertsentproceed":False}	
					
					if not client_data.has_key(clientID):
						client_data.setdefault(clientID,{"clientID":clientID,"timeZone":zone_ttimedct[routeName][0],"theoryTime":zone_ttimedct[routeName][1],"arrivalTime":str(message['arrivalTime']),"routeName":routeName,"everyTenminproceed":False,"recommndsentproceed":True,"alertsentproceed":False})


					# datetime format
					arrivalTime = datetime.datetime.strptime(message['arrivalTime'], "%Y-%m-%d %H:%M:%S")
					# adding timezone using localizing technique
					zone = pytz.timezone(client_data[clientID]["timeZone"])
					arrivalTime = zone.localize(arrivalTime)
					
					recommendationAlgoFunc(arrivalTime,clientID)#calling the recommendation algorithm function
		else:
			pass		
	except Exception as callbackError:
		logging.error("The error occured in callbackError is %s,%s\n"%(callbackError,type(callbackError)))

					
		
		


'''****************************************************************************************
Function Name 	:	error
Description		:	If error in the channel, prints the error
Parameters 		:	message - error message
****************************************************************************************'''
def error(message):
    logging.error("ERROR on Pubnub: " + str(message)+"\n")

'''****************************************************************************************
Function Name 	:	connect
Description		:	Responds if server connects with pubnub
Parameters 		:	message - connect message
****************************************************************************************'''	
def connect(message):
	logging.info("CONNECTED\n")

'''****************************************************************************************
Function Name 	:	reconnect
Description		:	Responds if server reconnects with pubnub
Parameters 		:	message - reconnect message
****************************************************************************************'''	
def reconnect(message):
    logging.info("RECONNECTED\n")

'''****************************************************************************************
Function Name 	:	disconnect
Description		:	Responds if server disconnects from pubnub
Parameters 		:	message - disconnect message
****************************************************************************************'''
def disconnect(message):
     logging.info("DISCONNECTED\n")



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
		logging.error("The error occured in channel_subscriptions is %s,%s\n"%(channelsubserror,type(channelsubserror)))


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
		
		logging.info('connected\n')
	except Exception as e:
		logging.error("The error occured in mongoInit is %s,%s\n"%(e,type(e)))


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
		logging.error("The pubException is %s,%s\n"%(pubException,type(pubException)))

		return False


'''****************************************************************************************
Function Name 	:	Init (Functional operation)
Description		:	Function initializes the pubinit and mongoinit
****************************************************************************************'''
def Init():
	dBreturn = mongoInit()
	pbreturn = pub_Init()
	if (dBreturn == False or pbreturn == False):
		logging.info("Program Terminated\n")
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
		logging.error("The main Exception is %s,%s\n"%(e,type(e)))
	

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

pub_key ='pub-c-f2fc0469-ad0f-4756-be0c-e003d1392d43'
sub_key ='sub-c-4d48a9d8-1c1b-11e6-9327-02ee2ddab7fe'

minit = 10
limit = 580
divCompare = 3

client_data = {}
beforeJourneyClientList = {}
startedJourneyClientList = {}
commonClientIDList = []
commonStartedClientIDList = []

zone_ttimedct = {"NEWARK-EDISON":["US/Eastern",1719],"BROOKLYN-DENVILLE":["US/Eastern",2921],"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL":["US/Pacific",767]}

def publish_handler(channel,result):
	if (client_data[channel]['recommndsentproceed'] == True):	
		
		print "recommndsentproceed",client_data[channel]['recommndsentproceed']
		pbtry = 0
		while (pbtry<3):
			try:
				pbreturn = pubnub.publish(channel = channel ,message =result,error=error)
				if (pbreturn[0] == 1):
					return None
				elif(pbreturn[0] == 0):
					print ("The publish return error  %s for the Task %s for the client %s"%(pbreturn[1],channel,details['DISPLAY_NAME']))
					pbtry+=1
				else:
					pass
			except Exception as error_pdhandler:
				print error_pdhandler
				pbtry+=1
	else:
		pass
		
def alertpublish_handler(channel,result):
	if (client_data[channel]['alertsentproceed'] == True):	
		
		print "alertsentproceed",client_data[channel]['alertsentproceed']
		pbtry = 0
		while (pbtry<3):
			try:
				pbreturn = pubnub.publish(channel = channel ,message =result,error=error)
				if (pbreturn[0] == 1):
					client_data[channel].update({"alertsentproceed":False})
					return None
				elif(pbreturn[0] == 0):
					print ("The publish return error  %s for the Task %s for the client %s"%(pbreturn[1],channel,details['DISPLAY_NAME']))
					pbtry+=1
				else:
					pass
			except Exception as error_pdhandler:
				print error_pdhandler
				pbtry+=1
	else:
		pass
		
def recommendationAlgoFunc(DesiredArrivalTime,clientID):
	global newttobackground
	proceed = False
	route_time = datetime.datetime.now(pytz.timezone(client_data[clientID]['timeZone'])) 
	theorytimeinsecs = client_data[clientID]['theoryTime']
	theorytimeinminutes = theorytimeinsecs/60.0 #Theory time in minutes
	print theorytimeinminutes
	if (theorytimeinminutes%10 >= 5):				
		rem = 10.0-theorytimeinminutes%10
		
	else:
		rem = theorytimeinminutes%10
		rem = -rem
		
	reminminutes = rem
	print reminminutes,'inminutes'
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
	cursor = newttobackground.ttoresultcoll.find({"route":client_data[clientID]['routeName']})
	if (0<=hour <= 12 and day < 1 and day >= -1):
		print day,hour
		proceed = True
		for nedoc in cursor:
			 time.append(nedoc['time'])
			 realtimeinminutes.append(nedoc['predictioninmins'])
			 realtimeinsec.append(nedoc['predictioninsecs'])
	else:
		print day,hour
		
		result = {"responseType":4,"message":"oops!! time not in range"}
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
			print DesiredArrivalTimeIndexInList
				
			print time[DesiredArrivalTimeIndexInList]
			print realtimeinminutes[DesiredArrivalTimeIndexInList]	
				
			pred_minutes = []
			for i in range(len(timediffinminutes)):
				pred_minutes.append(float(timediffinminutes[i]+theorytimeinminutes))
			

			'''DISCUSSED METHOD'''
			startpointIndex = int(DesiredArrivalTimeIndexInList-(theorytimeinminutes/10))
			print startpointIndex
			print time[startpointIndex]
			print realtimeinminutes[startpointIndex]
			print pred_minutes[startpointIndex]
			print timediffinminutes[startpointIndex]

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

				print diff_minutes,pred_minutes[i],time[i]

				
				if (diff_minutes == 0): #This condition is the top priority
					recommendationResult.update({"onTime":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"you will reach ontime","diffMinutes":diff_minutes}})		
					recommendationFlag = False

				elif (0<=diff_minutes<=10):
					if(time[i] not in checkedOnce):
						
						checkedOnce.append(time[i])
						recommendationResult.update({"Early":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"you will be %s min Early"%(abs(diff_minutes)),"diffMinutes":diff_minutes}})
						i+=1#This line should be here
					else:
						recommendationResult.update({"Early":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"you will be %s min Early"%(abs(diff_minutes)),"diffMinutes":diff_minutes}})
						recommendationFlag = False
				

				else:
					if (time[i] not in checkedOnce):
						
						checkedOnce.append(time[i])
						recommendationResult.update({"Late":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"you will be %s min Late"%(abs(diff_minutes)),"diffMinutes":diff_minutes}})		
						i-=1 #This line should be here
					else:
						recommendationResult.update({"Late":{"predictedDepartureTime":str(time[i].replace(second=0,tzinfo=None)),"predictedArrivalTime":str(predictedArrivalTime.replace(tzinfo=None)),"dep_note":"you will be %s min Late"%(abs(diff_minutes)),"diffMinutes":diff_minutes}})		
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
			print e
			result = {"responseType":4,"message":"oops!! Internal problem"}
			publish_handler(clientID,result)
				

	else:
		pass




def Alerts(clientID,alert):
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
			print 'accidents are there'
			
			alertList.append({"eventType":nedoc['traffic']['incidents'][i]['type'],"shortDesc":nedoc['traffic']['incidents'][i]['shortDesc']})
			alertseverity.append(nedoc['traffic']['incidents'][i]['severity'])
			

	print alertseverity
	if (len(alertseverity)>1):
		secltdalert = max(alertseverity)
		maxseverealertIndex = alertseverity.index(secltdalert)
		
		print maxseverealertIndex
		alertList = [alertList[maxseverealertIndex]]

	

	alertpub_dict = {"responseType":2,"message":alertList}
	print alertpub_dict
	print len(alertList),"accident alert length"
	# if there are any alerts then send or dont
	if (len(alertList)>0):
		if alert == True:
			alertpublish_handler(clientID,alertpub_dict)
		else:
			publish_handler(clientID,alertpub_dict)	


def beforeJourneyTenminUpdate():
	global minit,limit,divCompare
	i = 0
	while True:
		if (len(beforeJourneyClientList.keys())>0):
			for cid in beforeJourneyClientList.keys():
				numofclients = len(beforeJourneyClientList.keys())
				
				if cid in beforeJourneyClientList.keys():
					if i<numofclients:
						try:
							if(int(datetime.datetime.now(pytz.timezone(client_data[cid]['timeZone'])).strftime("%M"))%minit == divCompare):
								client_data[cid].update({"everyTenminproceed":True})
								i+=1
							else:
								pass
						except Exception as e:
							print e 
							pass

					else:
						i = 0
						time.sleep(limit)
				else:
					pass		
									
		else:
			pass

def startedJourneyTenminUpdate():	
	global minit,limit,divCompare
	i = 0
	while True:
		if (len(startedJourneyClientList.keys())>0):
			for cid in startedJourneyClientList.keys():
				if cid in commonStartedClientIDList:	
					numofclients = len(startedJourneyClientList.keys())
					if i<numofclients:
						try:	
							if (int(datetime.datetime.now(pytz.timezone(client_data[cid]['timeZone'])).strftime("%M"))%minit == divCompare):
								startedJourneyClientList[cid].update({"alertsentproceed":True})
								client_data[cid].update({"everyTenminproceed":True})
							else:
								pass
						except Exception as e:
							print e	
							pass		
						

					else:
						i = 0
						time.sleep(limit)

				else:
					pass	
		else:
			pass




		
def stopJourney(stpCid):
	delCid = stpCid
	if delCid in client_data.keys():	
		del client_data[delCid]
	
	if delCid in commonClientIDList:
		index = commonClientIDList.index(delCid)
		del commonClientIDList[index]

	if delCid in commonStartedClientIDList:
		index = commonStartedClientIDList.index(delCid)
		del commonStartedClientIDList[index]


	print startedJourneyClientList
	print beforeJourneyClientList
	print client_data



def beforeJourney():
	global minit,divCompare
	while True:
		if (len(beforeJourneyClientList.keys())>0):
			for cid in beforeJourneyClientList.keys():
				if cid in commonClientIDList:
					localDict = client_data[cid]

					presentrouteTime =  datetime.datetime.now(pytz.timezone(localDict['timeZone']))

					recommendedTime = beforeJourneyClientList[cid]["recommendedDepTime"]
					# recommendedTime = (recommendedTime,"%Y-%m-%d %H:%M:%S")
					# zone = pytz.timezone(localDict["timeZone"])
					# recommendedTime = zone.localize(recommendedTime)
					
					diff = recommendedTime-presentrouteTime 
					diffMin = (diff.days * 24 * 60) + (diff.seconds/60)
						
					# enters into this condition only clients recommendation time is 2hrs ahead
					# and executes every10min thats why one more condition checking for 10mins
					if (10<=diffMin<= 120):
						val = datetime.datetime.now(pytz.timezone(localDict['timeZone'])).strftime("%M")
						if (int(val)%minit == divCompare and localDict['everyTenminproceed'] == True):#make sure you are dividing with 10 for the 10min purpose
							arrivalTime = datetime.datetime.strptime(localDict["arrivalTime"], "%Y-%m-%d %H:%M:%S")
							zone = pytz.timezone(localDict["timeZone"])
							arrivalTime = zone.localize(arrivalTime)
							
							
							existedRecommendation = beforeJourneyClientList[cid]["recommendedDepTime"]
							existeddiffMinutes = beforeJourneyClientList[cid]["diffMinutes"]

							# if you call this function in the beginning even if there is no change client will get the message
							# so if i write this here i have to call the publish function in the before function once the flag is set if the recommendation has changed
							pub_dict,recommendedDepTimeAlgoFunc = recommendationAlgoFunc(arrivalTime,cid)#calling the recommendation algorithm function
							recommTime = beforeJourneyClientList[cid]["recommendedDepTime"]
							recommTime = recommTime.replace(tzinfo=None)
							
							for i in range(len(recommendedDepTimeAlgoFunc)):
								if str(recommTime) == recommendedDepTimeAlgoFunc[i]:
									index = recommendedDepTimeAlgoFunc.index(str(recommTime))
									if beforeJourneyClientList[cid]["diffMinutes"]  == pub_dict["recommendation"][index]["diffMinutes"]:
										localDict.update({"recommndsentproceed":False})
										# means no new recommendation 
										localDict.update({"everyTenminproceed":False})
										# means comeback after 10 mins
										break
									else:
										localDict.update({"recommndsentproceed":True})
										# means new recommendation
										localDict.update({"everyTenminproceed":False})
										# means comeback after 10mins

										# sending only updated recommendation 
										recommresult = [pub_dict["recommendation"][index]]

										pub_dict.update({"responseType":3,"recommendation":recommresult})
										publish_handler(cid,pub_dict)
										break
								else:
									if i == len(recommendedDepTimeAlgoFunc)-1:
										localDict.update({"recommndsentproceed":True})
										# means new recommendation
										localDict.update({"everyTenminproceed":False})
										# means comeback after 10mins
										
										pub_dict.update({"responseType":3})
										publish_handler(cid,pub_dict)
										break

								

							
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


def startedJourney():
	global minit,limit,divCompare
	while True:
		if (len(startedJourneyClientList.keys())>0):
			for strtCid in startedJourneyClientList.keys():
				if strtCid in commonStartedClientIDList:
					presentrouteTimeminute = int(datetime.datetime.now(pytz.timezone(client_data[strtCid]['timeZone'])).strftime("%M"))

					if (presentrouteTimeminute%minit == divCompare and client_data[strtCid]['everyTenminproceed'] == True):
						Alerts(strtCid,True)
						client_data[strtCid].update({"everyTenminproceed":False})	
							
					else:
						pass
				else:
					del startedJourneyClientList[strtCid]
					
				
		else:
			pass			


def tto_callback(message,channel):
	print (str(message)+"\n")
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
			
			beforeJourneyClientList[clientID] = {"clientID":clientID,"recommendedDepTime":recommendedDepTime,"diffMinutes":message['diffMinutes']}				
			

			print beforeJourneyClientList,"we got the confirmation"
			# client_data[clientID].update({"everyTenminproceed":True})
			
			
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
		
				
		
		


'''****************************************************************************************
Function Name 	:	error
Description		:	If error in the channel, prints the error
Parameters 		:	message - error message
****************************************************************************************'''
def error(message):
    print("ERROR on Pubnub: " + str(message))

'''****************************************************************************************
Function Name 	:	connect
Description		:	Responds if server connects with pubnub
Parameters 		:	message - connect message
****************************************************************************************'''	
def connect(message):
	print("CONNECTED")

'''****************************************************************************************
Function Name 	:	reconnect
Description		:	Responds if server reconnects with pubnub
Parameters 		:	message - reconnect message
****************************************************************************************'''	
def reconnect(message):
    print ("RECONNECTED")

'''****************************************************************************************
Function Name 	:	disconnect
Description		:	Responds if server disconnects from pubnub
Parameters 		:	message - disconnect message
****************************************************************************************'''
def disconnect(message):
     print("DISCONNECTED")

def channel_subscriptions():
	global pubnub
	try:
		pubnub.subscribe(channels='ttotest1', callback=tto_callback,error=error,
		connect=connect, reconnect=reconnect, disconnect=disconnect)
	except Exception as channelsubserror:
		print channelsubserror

def mongoInit():
	global newttobackground
	try:
		uri ='mongodb://rajeevtto:radiostud@ds035315-a0.mongolab.com:35315,ds035315-a1.mongolab.com:35315/newttobackground?replicaSet=rs-ds035315'
		client = MongoClient(uri)
		newttobackground = client.newttobackground
		
		print 'connected'
	except Exception as e:
		print e

def pub_Init():
	global pubnub
	
	try:
		pubnub = Pubnub(publish_key=pub_key,subscribe_key=sub_key) 
		return True
	except Exception as pubException:
		print pubException
		return False

def Init():
	dBreturn = mongoInit()
	pbreturn = pub_Init()
	if (dBreturn == False or pbreturn == False):
		print ("Program Terminated")
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
		f1.start()
		f2.start()
		f4.start()
		f3.start()
		f5.start()
	except Exception as e:
		print e	

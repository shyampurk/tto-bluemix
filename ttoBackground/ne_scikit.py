from itertools import chain
from sklearn.neighbors import NearestNeighbors as nn
import pymongo
from pymongo import MongoClient

import datetime
import pytz
import logging
# this is for deprecation warnings,
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)  


LOG_FILENAME = 'TTOBackgroundLogs.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')



def ne_scikitalgo(ne_df):

# def ne_scikitalgo():       
	try:
		uri ='mongodb://rajeevtto:radiostud@ds035315-a0.mongolab.com:35315,ds035315-a1.mongolab.com:35315/newttobackground?replicaSet=rs-ds035315'
		client = MongoClient(uri)
		
		newttobackground = client.newttobackground
		
		logging.info('connected')
	
		ne_cursor = newttobackground.ttoopvalcoll.find({"route":"NEWARK-EDISON"})
		netestData = []
		netrainData = []
		nerealTime = []
		time = []
		
		

		for doc in ne_cursor:
			netrainData.append([float(doc['Zone']),float(doc['Temparature'][0]),float(doc['Temparature'][1]),float(doc['CodedWeather'][0]),float(doc['CodedWeather'][1]),float(doc['CodedDay'])])
			
			nerealTime.append(doc['realTime'])

		for z,t1,t2,w1,w2,c,d in zip(ne_df['Zone'],ne_df['Temparature1'],ne_df['Temparature2'],ne_df['CodedWeather1'],ne_df['CodedWeather2'],ne_df['CodedDay'],ne_df['Date']):
			netestData.append([float(z),float(t1),float(t2),float(w1),float(w2),c])
			time.append(d)

		logging.info("netrainData length %d"%(len(netrainData)))
		logging.info("netestData length %d"%(len(netestData)))

		

		neigh = nn(n_neighbors = 5)
		neigh.fit(netrainData)
		nn(algorithm = 'auto',metric = 'euclidean')


		distances = []
		indexs = []
		data = []

		for i in netestData:
			data.append(neigh.kneighbors(i))

		for i in range(len(data)):
			distances.append(data[i][0])
			indexs.append(data[i][1])


		predicted_ind = []
		predicted_val = []  # we are considering the realTime in this case



		for i in range(len(indexs)):
			predicted_ind.append(indexs[i][0])


		new_predicted_ind = list(chain.from_iterable(predicted_ind))
		
		for k in new_predicted_ind:
			predicted_val.append(nerealTime[k])  # nerealTime is the list where training set realTime values stored



		# seperating them as list of five for individual 5 neighbors

		listoffive = []

		for i in range(0,len(predicted_val),5):
			listoffive.append(predicted_val[i:i+5])
		
		prediction = []
		for i in range(len(listoffive)):
			prediction.append(listoffive[i][0])
		
		predictioninmins = []
		for i in prediction:
			predictioninmins.append(float(i)/60.0)

		docCount = newttobackground.ttoresultcoll.find({"route":"NEWARK-EDISON"}).count()
		logging.info('NE -> before adding new results docCount %d'%(docCount))
		
		
		'''for testing purpose im closing it i will comeback again'''
		lowleveldelList = [] # for the below 6hrs range
		highleveldelList = [] # for the regular update delete pupose
		newarkedison_time = datetime.datetime.now(pytz.timezone('US/Eastern')) 
		newarkedison_dayname = newarkedison_time.strftime("%A")
		newarkedison_hour = int(newarkedison_time.strftime("%H"))	
		newarkedison_minute = int(newarkedison_time.strftime("%M"))
		newarkedison_second = int(newarkedison_time.strftime("%S"))
		newarkedison_year 	= int(newarkedison_time.strftime("%Y"))
		newarkedison_month	= int(newarkedison_time.strftime("%m"))
		newarkedison_day	= int(newarkedison_time.strftime("%d"))
		presentTime = datetime.datetime(newarkedison_year,newarkedison_month,newarkedison_day,newarkedison_hour,newarkedison_minute,newarkedison_second)
		
		sixhrLimit = presentTime-datetime.timedelta(hours=6)
		logging.info("ne six hours back time %s"%(str(sixhrLimit)))

		highleveldelCursor = newttobackground.ttoresultcoll.find({"route":"NEWARK-EDISON","time" :{ "$gt":presentTime}})
		lowleveldelCursor = newttobackground.ttoresultcoll.find({"route":"NEWARK-EDISON","time" :{ "$lt":sixhrLimit}})
		
		for docid in highleveldelCursor:
			highleveldelList.append(docid['_id'])
		for docid in lowleveldelCursor:
			lowleveldelList.append(docid['_id'])
		combinedDelList = []
		combinedDelList.extend(lowleveldelList)
		combinedDelList.extend(highleveldelList)
		
		logging.info("ne docs before sixhourslimit %d"%(len(lowleveldelList)))
		logging.info("ne regular update doc length %d"%(len(highleveldelList)))	
		
		

		newttobackground.ttoresultcoll.remove({'_id':{"$in":combinedDelList}}) # Dangerous line
			


		
		for i in range(len(time)):
			doc = {
					"route":"NEWARK-EDISON",

					"time":time[i],
					"predictioninsecs":prediction[i],
					"predictioninmins":predictioninmins[i]
							}
			docid = newttobackground.ttoresultcoll.insert_one(doc)
			del doc
		
		docCount = newttobackground.ttoresultcoll.find({"route":"NEWARK-EDISON"}).count()
		logging.info('NE -> after adding new results docCount %d'%(docCount))
		
		return True	
	except Exception as e:
		logging.error("The exception occured in ne_scikit %s,%s"%(e,type(e)))
		return False	

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




def sf_scikitalgo(sf_df):
	try:
		uri ='mongodb://rajeevtto:radiostud@ds035315-a0.mongolab.com:35315,ds035315-a1.mongolab.com:35315/newttobackground?replicaSet=rs-ds035315'
		client = MongoClient(uri)
		
		newttobackground = client.newttobackground
		
		logging.info('connected')
	
		sf_cursor = newttobackground.ttoopvalcoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"})
		sftestData = []
		sftrainData = []
		sfrealTime = []
		time =[]

		
		for doc in sf_cursor:
			sftrainData.append([float(doc['Zone']),float(doc['Temparature'][0]),float(doc['CodedWeather'][0]),float(doc['CodedDay'])])
			sfrealTime.append(doc['realTime'])

		for z,t1,w1,c,d in zip(sf_df['Zone'],sf_df['Temparature1'],sf_df['CodedWeather1'],sf_df['CodedDay'],sf_df['Date']):
			sftestData.append([float(z),float(t1),float(w1),c])
			time.append(d)	
	
			
					

		logging.info("sftrainData length %d"%(len(sftrainData)))
		logging.info("sftestData length %d"%(len(sftestData)))

		neigh = nn(n_neighbors = 5)
		neigh.fit(sftrainData)
		nn(algorithm = 'auto',metric = 'euclidean')


		distances = []
		indexs = []
		data = []

		for i in sftestData:
			data.append(neigh.kneighbors(i))

		for i in range(len(data)):
			distances.append(data[i][0])
			indexs.append(data[i][1])


		predicted_ind = []
		predicted_val = []  # we are considering the realTime in this case
		


		for i in range(len(indexs)):
			predicted_ind.append(indexs[i][0])


		new_predicted_ind = list(chain.from_iterable(predicted_ind))
		
		
		# extracting realTime of predictions
		for k in new_predicted_ind:
			predicted_val.append(sfrealTime[k])  # sfrealTime is the list where training set realTime values stored

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


		
		docCount = newttobackground.ttoresultcoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"}).count()	
		logging.info('SF -> before adding new results docCount %d'%(docCount))


		
		lowleveldelList = [] # for the below 6hrs range
		highleveldelList = [] # for the regular update delete pupose

		sanfrancisco_time = datetime.datetime.now(pytz.timezone('US/Pacific'))
		sanfrancisco_dayname = sanfrancisco_time.strftime("%A")
		sanfrancisco_hour = int(sanfrancisco_time.strftime("%H"))	
		sanfrancisco_minute = int(sanfrancisco_time.strftime("%M"))
		sanfrancisco_second = int(sanfrancisco_time.strftime("%S"))
		sanfrancisco_year = int(sanfrancisco_time.strftime("%Y"))
		sanfrancisco_month	=int(sanfrancisco_time.strftime("%m"))
		sanfrancisco_day	= int(sanfrancisco_time.strftime("%d")) 
		presentTime = datetime.datetime(sanfrancisco_year,sanfrancisco_month,sanfrancisco_day,sanfrancisco_hour,sanfrancisco_minute,sanfrancisco_second)
				
		sixhrLimit = presentTime-datetime.timedelta(hours=6)
		logging.info("sf six hours back time %s"%(str(sixhrLimit)))

		highleveldelCursor = newttobackground.ttoresultcoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL","time" :{ "$gt":presentTime}})
		lowleveldelCursor = newttobackground.ttoresultcoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL","time" :{ "$lt":sixhrLimit}})
		
		for docid in highleveldelCursor:
			highleveldelList.append(docid['_id'])
		for docid in lowleveldelCursor:
			lowleveldelList.append(docid['_id'])

		logging.info("sf docs before sixhourslimit %d"%(len(lowleveldelList)))
		logging.info("sf regular update doc length %d"%(len(highleveldelList)))	

		combinedDelList = []
		combinedDelList.extend(lowleveldelList)
		combinedDelList.extend(highleveldelList)
		
		newttobackground.ttoresultcoll.remove({'_id':{"$in":combinedDelList}}) # Dangerous line
			

		for i in range(len(time)):
			doc = {
					"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL",

					"time":time[i],
					"predictioninsecs":prediction[i],
					"predictioninmins":predictioninmins[i]
							}
			docid = newttobackground.ttoresultcoll.insert_one(doc)
			del doc

		docCount = newttobackground.ttoresultcoll.find({"route":"MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"}).count()	
		logging.info('SF -> after adding new results docCount%d'%(docCount))
		
			
		return True		

	except Exception as e:
		logging.error("The exception for sf_scikit %s,%s"(e,type(e)))
		return False









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



'''****************************************************************************************
Function Name 	:	bd_scikitalgo  (Algorithm operation)
Description		:	Function which does the scikit algorithm operation and gives the result
Parameters      :   bd_df (test data generated in testprep function)
****************************************************************************************'''
def bd_scikitalgo(bd_df):
	try:
		uri ='mongodb://rajeevtto:radiostud@ds035315-a0.mongolab.com:35315,ds035315-a1.mongolab.com:35315/newttobackground?replicaSet=rs-ds035315'
		client = MongoClient(uri)
		
		newttobackground = client.newttobackground
		
		logging.info('connected')
	
		bd_cursor = newttobackground.ttoopvalcoll.find({"route":"BROOKLYN-DENVILLE"})
		bdtestData = []
		bdtrainData = []
		bdrealTime = []
		time = []

		
		for doc in bd_cursor:
			bdtrainData.append([float(doc['Zone']),float(doc['Temparature'][0]),float(doc['Temparature'][1]),float(doc['CodedWeather'][0]),float(doc['CodedWeather'][1]),float(doc['CodedDay'])])
			bdrealTime.append(doc['realTime'])
	
		for z,t1,t2,w1,w2,c,d in zip(bd_df['Zone'],bd_df['Temparature1'],bd_df['Temparature2'],bd_df['CodedWeather1'],bd_df['CodedWeather2'],bd_df['CodedDay'],bd_df['Date']):
			bdtestData.append([float(z),float(t1),float(t2),float(w1),float(w2),c])
			time.append(d)
	 	
		logging.info("bdtrainData length %d"%(len(bdtrainData)))
		logging.info("bdtestData length %d"%(len(bdtestData)))

		neigh = nn(n_neighbors = 5)
		neigh.fit(bdtrainData)
		nn(algorithm = 'auto',metric = 'euclidean')


		distances = []
		indexs = []
		data = []

		for i in bdtestData:
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
			predicted_val.append(bdrealTime[k])  # bdrealTime is the list where training set realTime values stored



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

		
		
		docCount = newttobackground.ttoresultcoll.find({"route":"BROOKLYN-DENVILLE"}).count()
		logging.info('BD -> before adding new results docCount %d'%(docCount))

		
		lowleveldelList = [] # for the below 6hrs range
		highleveldelList = [] # for the regular update delete pupose
		brooklyndenville_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
			
		brooklyndenville_dayname = brooklyndenville_time.strftime("%A")
		brooklyndenville_hour = int(brooklyndenville_time.strftime("%H"))	
		brooklyndenville_minute = int(brooklyndenville_time.strftime("%M"))
		brooklyndenville_second = int(brooklyndenville_time.strftime("%S"))
		brooklyndenville_year = int(brooklyndenville_time.strftime("%Y"))
		brooklyndenville_month	= int(brooklyndenville_time.strftime("%m"))
		brooklyndenville_day	= int(brooklyndenville_time.strftime("%d")) 
		presentTime = datetime.datetime(brooklyndenville_year,brooklyndenville_month,brooklyndenville_day,brooklyndenville_hour,brooklyndenville_minute,brooklyndenville_second)
				
		sixhrLimit = presentTime-datetime.timedelta(hours=6)
		logging.info("bd six hours back time %s"%(str(sixhrLimit)))

		highleveldelCursor = newttobackground.ttoresultcoll.find({"route":"BROOKLYN-DENVILLE","time" :{ "$gt":presentTime}})
		lowleveldelCursor = newttobackground.ttoresultcoll.find({"route":"BROOKLYN-DENVILLE","time" :{ "$lt":sixhrLimit}})
		
		for docid in highleveldelCursor:
			highleveldelList.append(docid['_id'])
		for docid in lowleveldelCursor:
			lowleveldelList.append(docid['_id'])
		combinedDelList = []
		combinedDelList.extend(lowleveldelList)
		combinedDelList.extend(highleveldelList)
		
		logging.info("bd docs before sixhourslimit %d"%(len(lowleveldelList)))
		logging.info("bd regular update doc length %d"%(len(highleveldelList)))	
		

		
		newttobackground.ttoresultcoll.remove({'_id':{"$in":combinedDelList}}) # Dangerous line
			




		for i in range(len(time)):
			doc = {
					"route":"BROOKLYN-DENVILLE",

					"time":time[i],
					"predictioninsecs":prediction[i],
					"predictioninmins":predictioninmins[i]
							}
			docid = newttobackground.ttoresultcoll.insert_one(doc)
			del doc

		docCount = newttobackground.ttoresultcoll.find({"route":"BROOKLYN-DENVILLE"}).count()
		logging.info('BD -> after adding new results docCount %d'%(docCount))			
			
		return True	
	except Exception as e:
		logging.error("The exception occured in bd_scikit %s,%s"%(e,type(e)))
		return False










	













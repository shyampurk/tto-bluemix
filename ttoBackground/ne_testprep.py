import datetime
import requests
import demjson
import pytz
import logging

LOG_FILENAME = 'TTOBackgroundLogs.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')



Day_List = ['','Sun','Mon','Tue','Wed','Thu','Fri','Sat']
mini = 10

# maxlimit = 72
maxlimit = 108 # 18 hrs buffer




'''****************************************************************************************
Function Name 	:	nealgo  (Algorithm operation)
Description		:	Function which generates the test data
Parameters      :   date              - Present Time(route specific)
					induceTime        - Time for which values need to be changed(Recommended Departure Time suggested for the client)
					induceWeather     - weather value of our choice(selected through induceScript)
					induceTemparature - temparature value of our choice(selected through induceScript)
****************************************************************************************'''
def nealgo(date,induceTime,induceWeather,induceTemparature):
	global mini,maxlimit
	try:
		neDates = []
		neDates.append(date)
		for i in range(0,maxlimit,1):
			neDates.append(neDates[i] + datetime.timedelta(minutes=mini))
		

		for j in range(len(neDates)):
			if neDates[j] == date:
				break
		del neDates[j]

		nezones = []
		for val in neDates:
			v1 = int(val.strftime("%H"))
			v2 = int(val.strftime("%M"))
			v1 = (v1)*6
			v2 = (v2+10)/10
			nezones.append(v1+v2)

		newarkweatherforecast_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid= 2459299&format=json&env=store")	
		newarkweatherforecast_data = newarkweatherforecast_api.text
		newark_weatherforecast = demjson.decode(newarkweatherforecast_data)

		edisonweatherforecast_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid= 56250394&format=json&env=store")	
		edisonweatherforecast_data = edisonweatherforecast_api.text
		edison_weatherforecast = demjson.decode(edisonweatherforecast_data)

		newarkedison_hour = int(date.strftime("%H"))
		newarkedison_day = int(date.strftime("%d"))

		ntemporary = []
		etemporary = []
		for i in range(0,2,1):
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
			
			ntemporary.append([nday,navg,ncode,ndate])
			etemporary.append([eday,eavg,ecode,edate])

		nTemparature = []
		nDay = []
		nWeather = []

		eTemparature = []
		eDay = []
		eWeather = []

		for i in range(len(ntemporary)):
			if (newarkedison_hour<12):
				if (int(newarkedison_day) == int(ntemporary[i][3][0:2])):
					nTemparature.append(ntemporary[i][1])
					nDay.append(ntemporary[i][0])
					nWeather.append(int(ntemporary[i][2]))
				else:
					
					nTemparature.append(ntemporary[i][1])
					nDay.append(ntemporary[i][0])
					nWeather.append(int(ntemporary[i][2]))	
			else:
				
				nTemparature.append(ntemporary[i][1])
				nDay.append(ntemporary[i][0])
				nWeather.append(int(ntemporary[i][2]))	


		for i in range(len(etemporary)):
			if (newarkedison_hour<12):
				if (int(newarkedison_day) == int(etemporary[i][3][0:2])):
					eTemparature.append(etemporary[i][1])
					eDay.append(etemporary[i][0])
					eWeather.append(int(etemporary[i][2]))
				else:
				
					eTemparature.append(etemporary[i][1])
					eDay.append(etemporary[i][0])
					eWeather.append(int(etemporary[i][2]))			
			else:
				
				eTemparature.append(etemporary[i][1])
				eDay.append(etemporary[i][0])
				eWeather.append(int(etemporary[i][2]))			


		nTemparature_List = []
		nDay_List = []
		nWeather_List = []
		
		eTemparature_List = []
		eDay_List = []
		eWeather_List = []

		for k in range(len(neDates)):
			if (int(neDates[k].strftime("%d")) == newarkedison_day):
				nTemparature_List.append(nTemparature[0])
				nDay_List.append(nDay[0])
				nWeather_List.append(nWeather[0])
			else:
				nTemparature_List.append(nTemparature[1])
				nDay_List.append(nDay[1])
				nWeather_List.append(nWeather[1])
		
		for l in range(len(neDates)):
			if (int(neDates[l].strftime("%d")) == newarkedison_day):
				eTemparature_List.append(eTemparature[0])
				eDay_List.append(eDay[0])
				eWeather_List.append(eWeather[0])
			else:
				eTemparature_List.append(eTemparature[1])
				eDay_List.append(eDay[1])
				eWeather_List.append(eWeather[1])
		
		if (len(induceTime) != 0):
			# induce method changes
			induceTimeIndex = []

			for i in range(len(induceTime)):
				for j in range(len(neDates)):
					if neDates[j] == induceTime[i]:
						induceTimeIndex.append(neDates.index(induceTime[i]))
						# break


			for i in range(len(induceTimeIndex)):			
				# inducing the values(changes for the induce method)
				nWeather_List[induceTimeIndex[i]] = induceWeather[i][0]		
				eWeather_List[induceTimeIndex[i]] = induceWeather[i][1]
				nTemparature_List[induceTimeIndex[i]] = induceTemparature[i][0]
				eTemparature_List[induceTimeIndex[i]] = induceTemparature[i][1]


		else:
			pass		

		neCoded_Day = []
		for i in range(len(eDay_List)):
			for day in Day_List:
				if eDay_List[i]== day:
					dind = Day_List.index(day)
					neCoded_Day.append(dind)


		
		necols = ['Date','Zone','Temparature1','Temparature2','CodedWeather1','CodedWeather2','CodedDay']
		data = {'Date':neDates,'Zone':nezones,'Temparature1':nTemparature_List,'Temparature2':eTemparature_List,'CodedWeather1':nWeather_List,'CodedWeather2':eWeather_List,'CodedDay':neCoded_Day}
				

		df = data
		# logging.info("ne_Testprep length %s"%(len(df)))
		return df,True
	except Exception as e:
		logging.error("The exception occured in ne_testprep %s,%s"%(e,type(e)))	
		df = {}
		return df,False



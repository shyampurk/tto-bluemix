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
Function Name 	:	sfalgo  (Algorithm operation)
Description		:	Function which generates the test data
Parameters      :   date              - Present Time(route specific)
					induceTime        - Time for which values need to be changed(Recommended Departure Time suggested for the client)
					induceWeather     - weather value of our choice(selected through induceScript)
					induceTemparature - temparature value of our choice(selected through induceScript)
****************************************************************************************'''
def sfalgo(date,induceTime,induceWeather,induceTemparature):
	
	global mini,maxlimit
	try:
		sfDates = []
		sfDates.append(date)
		for i in range(0,maxlimit,1):
			sfDates.append(sfDates[i] + datetime.timedelta(minutes=mini))

		for j in range(len(sfDates)):
			if sfDates[j] == date:
				break
		del sfDates[j]

		sfzones=[]
		for val in sfDates:
			v1 = int(val.strftime("%H"))
			v2 = int(val.strftime("%M"))
			v1 = (v1)*6
			v2 = (v2+10)/10
			sfzones.append(v1+v2)
			


		sanfranciscoweatherforecast_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid= 2487956&format=json&env=store")	
		sanfranciscoweatherforecast_data = sanfranciscoweatherforecast_api.text
		sanfrancisco_weatherforecast = demjson.decode(sanfranciscoweatherforecast_data)

		sanfrancisco_hour = int(date.strftime("%H"))
		sanfrancisco_day = int(date.strftime("%d"))

		sftemporary = []
		
		for i in range(0,2,1):
			sfday= sanfrancisco_weatherforecast['query']['results']['channel']['item']['forecast'][i]['day']
			sfhigh = int(sanfrancisco_weatherforecast['query']['results']['channel']['item']['forecast'][i]['high'])
			sflow = int(sanfrancisco_weatherforecast['query']['results']['channel']['item']['forecast'][i]['low'])
			sfavg =(sfhigh+sflow)/2
			
			sfcode = sanfrancisco_weatherforecast['query']['results']['channel']['item']['forecast'][i]['code']
			
			sfdate = sanfrancisco_weatherforecast['query']['results']['channel']['item']['forecast'][i]['date']
			
			
			sftemporary.append([sfday,sfavg,sfcode,sfdate])
		
		# '''For local testing without internet'''
		# sftemporary = ['Mon',53,24,]

		

		sfTemparature = []
		sfDay = []
		sfWeather = []

		
		for i in range(len(sftemporary)):
			if (sanfrancisco_hour<12):
				if (int(sanfrancisco_day) == int(sftemporary[i][3][0:2])):
					sfTemparature.append(sftemporary[i][1])
					sfDay.append(sftemporary[i][0])
					sfWeather.append(int(sftemporary[i][2]))
				else:
				
					sfTemparature.append(sftemporary[i][1])
					sfDay.append(sftemporary[i][0])
					sfWeather.append(int(sftemporary[i][2]))	
			else:
				
				sfTemparature.append(sftemporary[i][1])
				sfDay.append(sftemporary[i][0])
				sfWeather.append(int(sftemporary[i][2]))	


		

		sfTemparature_List = []
		sfDay_List = []
		sfWeather_List = []
		
		
		for k in range(len(sfDates)):
			if (int(sfDates[k].strftime("%d")) == sanfrancisco_day):
				sfTemparature_List.append(sfTemparature[0])
				sfDay_List.append(sfDay[0])
				sfWeather_List.append(sfWeather[0])
			else:
				sfTemparature_List.append(sfTemparature[1])
				sfDay_List.append(sfDay[1])
				sfWeather_List.append(sfWeather[1])
		if (len(induceTime)!=0):
			# induce method changes
			induceTimeIndex = []
			for i in range(len(induceTime)):	
				for j in range(len(sfDates)):
					if sfDates[j] == induceTime[i]:
						induceTimeIndex.append(sfDates.index(induceTime[i]))
						break
			for i in range(len(induceTimeIndex)):	
				# inducing the values(changes for the induce method)
				sfWeather_List[induceTimeIndex[i]] = induceWeather[i][0]		
				sfTemparature_List[induceTimeIndex[i]] = induceTemparature[i][0]
				
		
		else:
			pass

		sfCoded_Day = []
		for i in range(len(sfDay_List)):
			for day in Day_List:
				if sfDay_List[i]== day:
					dind = Day_List.index(day)
					sfCoded_Day.append(dind)

		
		sfcols = ['Date','Zone','Temparature1','CodedWeather1','CodedDay']
		
		data = {'Date':sfDates,'Zone':sfzones,'Temparature1':sfTemparature_List,'CodedWeather1':sfWeather_List,'CodedDay':sfCoded_Day}			

		df = data
		return df,True
	except Exception as e:
		logging.error("The sf_testprep exception %s,%s"%(e,type(e)))	
		df = {}
		return df,False
			
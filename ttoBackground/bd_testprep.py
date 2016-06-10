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

def bdalgo(date,induceTime,induceWeather,induceTemparature):
	global mini,maxlimit
	try:
		bdDates = []
		bdDates.append(date)
		for i in range(0,maxlimit,1):
			bdDates.append(bdDates[i] + datetime.timedelta(minutes=mini))

		for j in range(len(bdDates)):
			if bdDates[j] == date:
				break
		del bdDates[j]

		bdzones = []
		for val in bdDates:
			v1 = int(val.strftime("%H"))
			v2 = int(val.strftime("%M"))
			v1 = (v1)*6
			v2 = (v2+10)/10
			bdzones.append(v1+v2)

		brooklynweatherforecast_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid= 2459115&format=json&env=store")	
		brooklynweatherforecast_data = brooklynweatherforecast_api.text
		brooklyn_weatherforecast = demjson.decode(brooklynweatherforecast_data)

		denvilleweatherforecast_api = requests.get("https://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid= 2391338&format=json&env=store")	
		denvilleweatherforecast_data = denvilleweatherforecast_api.text
		denville_weatherforecast = demjson.decode(denvilleweatherforecast_data)

		brooklyndenville_hour = int(date.strftime("%H"))
		brooklyndenville_day = int(date.strftime("%d"))

		btemporary = []
		dtemporary = []
		for i in range(0,2,1):
			bday= brooklyn_weatherforecast['query']['results']['channel']['item']['forecast'][i]['day']
			bhigh = int(brooklyn_weatherforecast['query']['results']['channel']['item']['forecast'][i]['high'])
			blow = int(brooklyn_weatherforecast['query']['results']['channel']['item']['forecast'][i]['low'])
			bavg =(bhigh+blow)/2
			
			bcode = brooklyn_weatherforecast['query']['results']['channel']['item']['forecast'][i]['code']
			
			bdate = brooklyn_weatherforecast['query']['results']['channel']['item']['forecast'][i]['date']
			
			dday= denville_weatherforecast['query']['results']['channel']['item']['forecast'][i]['day']
			dhigh = int(denville_weatherforecast['query']['results']['channel']['item']['forecast'][i]['high'])
			dlow = int(denville_weatherforecast['query']['results']['channel']['item']['forecast'][i]['low'])
			davg =(dhigh+dlow)/2
			
			dcode = denville_weatherforecast['query']['results']['channel']['item']['forecast'][i]['code']
			
			ddate = denville_weatherforecast['query']['results']['channel']['item']['forecast'][i]['date']
			
			btemporary.append([bday,bavg,bcode,bdate])
			dtemporary.append([dday,davg,dcode,ddate])

		bTemparature = []
		bDay = []
		bWeather = []

		dTemparature = []
		dDay = []
		dWeather = []

		for i in range(len(btemporary)):
			if (brooklyndenville_hour<12):
				if (int(brooklyndenville_day) == int(btemporary[i][3][0:2])):
					bTemparature.append(btemporary[i][1])
					bDay.append(btemporary[i][0])
					bWeather.append(int(btemporary[i][2]))
			
				else:
				
					bTemparature.append(btemporary[i][1])
					bDay.append(btemporary[i][0])
					bWeather.append(int(btemporary[i][2]))	
			else:
				
				bTemparature.append(btemporary[i][1])
				bDay.append(btemporary[i][0])
				bWeather.append(int(btemporary[i][2]))	


		for i in range(len(dtemporary)):
			if (brooklyndenville_hour<12):
				if (int(brooklyndenville_day) == int(dtemporary[i][3][0:2])):
					dTemparature.append(dtemporary[i][1])
					dDay.append(dtemporary[i][0])
					dWeather.append(int(dtemporary[i][2]))
				else:
				
					dTemparature.append(dtemporary[i][1])
					dDay.append(dtemporary[i][0])
					dWeather.append(int(dtemporary[i][2]))		
			else:
				
				dTemparature.append(dtemporary[i][1])
				dDay.append(dtemporary[i][0])
				dWeather.append(int(dtemporary[i][2]))			

		
				
		bTemparature_List = []
		bDay_List = []
		bWeather_List = []
		
		dTemparature_List = []
		dDay_List = []
		dWeather_List = []

		for k in range(len(bdDates)):
			if (int(bdDates[k].strftime("%d")) == brooklyndenville_day):
				bTemparature_List.append(bTemparature[0])
				bDay_List.append(bDay[0])
				bWeather_List.append(bWeather[0])
			else:
				bTemparature_List.append(bTemparature[1])
				bDay_List.append(bDay[1])
				bWeather_List.append(bWeather[1])
		
		for l in range(len(bdDates)):
			if (int(bdDates[l].strftime("%d")) == brooklyndenville_day):
				dTemparature_List.append(dTemparature[0])
				dDay_List.append(dDay[0])
				dWeather_List.append(dWeather[0])
			else:
				dTemparature_List.append(dTemparature[1])
				dDay_List.append(dDay[1])
				dWeather_List.append(dWeather[1])
		
		if (len(induceTime)!=0):			

			# induce method changes
			induceTimeIndex = []
			for i in range(len(induceTime)):
				for j in range(len(bdDates)):
					if bdDates[j] == induceTime[i]:
						induceTimeIndex.append(bdDates.index(induceTime[i]))
						# break		
			for i in range(len(induceTimeIndex)):			
				# inducing the values(changes for the induce method)
				bWeather_List[induceTimeIndex[i]] = induceWeather[i][0]		
				dWeather_List[induceTimeIndex[i]] = induceWeather[i][1]
				bTemparature_List[induceTimeIndex[i]] = induceTemparature[i][0]
				dTemparature_List[induceTimeIndex[i]] = induceTemparature[i][1]
		else:
			pass

		bdCoded_Day = []
		for i in range(len(dDay_List)):
			for day in Day_List:
				if dDay_List[i]== day:
					dind = Day_List.index(day)
					bdCoded_Day.append(dind)

		bdcols = ['Date','Zone','Temparature1','Temparature2','CodedWeather1','CodedWeather2','CodedDay']
		data = {'Date':bdDates,'Zone':bdzones,'Temparature1':bTemparature_List,'Temparature2':dTemparature_List,'CodedWeather1':bWeather_List,'CodedWeather2':dWeather_List,'CodedDay':bdCoded_Day}			

		df = data
		return df,True
	except Exception as e:
		logging.error("The bd_testprep exception %s,%s"%(e,type(e)))	
		df = {}
		return df,False

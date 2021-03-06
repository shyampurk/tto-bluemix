# Travel Time Optimizer App
Travel Time Optimizer (TTO) App for providing real-time recommendations for travel duration based on historical traffic data, weather and day of the week. 

# Introduction
This is a demonstration app for showcasing how to harness the power of accumulated historical traffic data to provide real-time recommendations and traffic advisory alerts to users. This app is hosted on IBM Bluemix and uses PubNub for client-server interaction & sending real-time alerts.

# Components

This application has four main components.

1. ttoBackground: This is a background process which is responsible for capturing traffic data and other traffic affecting parameters. This process also executes a KNN algorithm to generate predictions for future. It supposed to run continuously in conjunction with a hosted MongoDB database for storing the captured and prediction data, every ten minutes.

2. ttoServer: This is the main server process which is responsible for handling user requests and generating recommendations. It is hosted on IBM Bluemix

3. ttoApp: This is a Cordova,Android-based mobile app used for availing the TTO service.

4. ttoTest: This is a test script for testing real-time recommendation alerts due to weather changes. 


# Setup and Deployment

## Prerequisites

1. A hosted MongoDB setup is required for storing all the data for this application. We have used [mLab](https://mlab.com/) ( MongoDB Database as a service) for this project. The MongoDB should have the following configuration

      - Database name as 'newttobackground'
      - Following collections should be created
        - ttobgcoll ( TTO Background Collection for storing the API data from MapQuest and Yahoo Weather API)
        - ttoopvalcoll ( TTO Operation Value collection so storing the necessary data from API which affect Traffic)
        - ttoresultcoll ( TTO Result Collection for storing predictions )
        - ttoinducecoll ( TTO Induce value collection used for testing by ttoTest scripts )
      
      Note :- Also make a note of the DB URI, DB User and DB Password of our hosted Database.
      
2. You must have IBM Bluemix Account

3. You must have an PubNub subscription
 
4. You must have a [MapQuest](https://developer.mapquest.com/) subscription

5. You must have a cloned working copy of this repository 


## Deployment of ttoBackground Process
The ttoBarkground process can be executed under any system which has python2 runtime available.

Follow the steps below for running ttoBackground process
1. Install the python runtime dependencies for ttoBackground

  - pymongo
  - requests
  - demjson
  - pytz
  - scikit-learn

2. Open the ttoBackground [source file](ttoBackground/ttoBackground.py) and perform the following modifications

  - Line 34 : For the value of variable "mq_directions_key", set it to your MapQuest subscription key.
  
  - Line 35 : For the value of variable "mq_traffic_key", set it to your MapQuest subscription key.
  
            Note : To avoid API call limits for a trial subscription, we have used separate subscription keys 
            for getting direction and traffic data from MapQuest. If you have a paid subscription, then the same key can
            be used for both purposes. 

  - Line 23 : For the value of variable "uri", change it to the following format
    
            mongodb://<dbuser>:<dbpassword>@<dburi>/newttobackground
    
            where
                  dbuser       : Your username for mLab
                  dbpassword   : Your password for mLab
                  dburi        : The URI assigned for your hosted MongnDB Database. 

3. Open the [bd_scikit.py](ttoBackground/bd_scikit.py) and perform the following modifications

  - Line 25 : For the value of variable "uri", change it to the following format
    
            mongodb://<dbuser>:<dbpassword>@<dburi>/newttobackground
    
            where
                  dbuser       : Your username for mLab
                  dbpassword   : Your password for mLab
                  dburi        : The URI assigned for your hosted MongnDB Database. 

  Repeat this modification for [ne_scikit.py](ttoBackground/ne_scikit.py), line no. 28 and [sf_scikit.py](ttoBackground/sf_scikit.py), line no. 28.
        
4. Run ttoBackground [source file](ttoBackground/ttoBackground.py) process

            python ttoBackground.py

  Check the log file created in the same path to see the program in action. You can also see data getting added to the MongpDB collections every 10 minutes.

Note: - To achieve reasonably good predictions, we should keep this program running continuously for at least three months or more.


## Deployment of ttoServer

Follow the steps below for hosting ttoServer on IBM Bluemix

1. Open the [ttoServer.py](ttoServer/ttoServer.py) file and modify the following

    In function mongoInit(), change the value of variable uri to
    
        mongodb://<dbuser>:<dbpassword>@<dburi>/newttobackground
        
        where
          dbuser       : Your username for mLab
          dbpassword   : Your password for mLab
          dburi        : The URI assigned for your hosted MongnDB Database.
      
      
      
2. Change the PubNub keys in Line 17,18 with your PubNub subscription keys.

3. Login to Bluemix console via cf tool and select the space.

4. Change directory to the ttoServer under the cloned Github repository.

5. Run the following command to push the application code to Bluemix

            cf push

Once successfully pushed, the server application will be automatically started. You can check its state in your Bluemix dashboard and see that its state is set to 'Running'.

## Build the ttoApp

Thw ttoApp source code is located under the [ttoApp](ttoApp) directory of this repository.

Follow the standard build procedures for building the APK package for this android App.

Before building , ensure that you type in the PubNub keys in the following lines and ensure that the keys used in ttoApp are same as the ones used in ttoServer.

1. Line 22: In [index.js](ttoApp/www/js/index.js), set the PubNub Publish Key in function pubnubInit() 

2. Line 23: In [index.js](ttoApp/www/js/index.js), set the PubNub Subscribe Key in function pubnubInit() 


# TTO App User Flow
Assuming that the ttoBackground and ttoServer processes ar deployed, the user can test the application as follows.

Step 1: Launch the ttoApp on your Android mobile and you will be presented with this screen
<img src="/ttoScreenShots/appscreen.png" align="center" width="250" >

Step 2: Select a Route and a Desired Arrival Time and tap on "Submit".  Make sure that the Desired Arrival Time is within 12 hour range of the current local time of the selected route.

<img src="/ttoScreenShots/selection.png" align="center" width="250" >

Step 3: The ttoApp sends  request to ttoServer with runs a TTO Recommendation Engine and returns travel recommendations based on the selected route and desired arrival time.

<img src="/ttoScreenShots/recommendation.png" align="center" width="250" >

Step 4: Tap on one out of the presented recommendations and the ttoApp starts a countdown till the start of journey ( as per the Predicted Departure Time in the selected Recommendation). This is the pre journey phase of ttoApp.

<img src="/ttoScreenShots/prejourneytracking.png" align="center" width="250" >

Step 5: During this time, the ttoServer may send realtime recommendation alerts , if there is a change in weather condition which alters the previous prediction, or if there is an incident reported along the route. The Yahoo Weather API provides a near constant forecast for the entire day and typically does not give enough data to indicate changes in weather during a day. Hence to simulate a recommendation alert for change in weather , we have used a induce script. The details of are under the "Inducing real-time recommendations" sections below. 

<img src="/ttoScreenShots/recommendationalert.png" align="center" width="250" >

Step 6: Tap on “Start Journey”. The ttoApp will enter the journey tracking phase. 

<img src="/ttoScreenShots/journeytracking.png" align="center" width="250" >

During this time, the ttoServer will send realtime recommendation alerts only if there is an incident reported along the route. 

<img src="/ttoScreenShots/accident.png" align="center" width="250" >

Step 7: Tap on End Journey to end the journey and then the ttoServer will stop sending any further alerts.



# Inducing real-time recommendations

Since the public Yahoo Weather API has a limitation of not providing hourly variations in weather, we have to induce a weather change in our ttoBackground captured data so that we can generate modified predictions for travel duration and issue real-time advisory alerts to the users. 

For this purpose we have written a induce script which can be used to change the weather and temperature of a selected route ( for both source and destination place of the route ) . This script should be run when the user is in pre-journey trackign stage (Step 4 under the Usage section above). 

The induce script is located under [ttoTest](ttoTest) 

Here is how the induce script is executed.

<img src="/ttoScreenShots/induceScript.gif" align="center" width="800" >

Make sure to point to the correct MongoDB instance before executing this script, by changing the variable uri at Line 17 as per the Step 2 of "Deployment of ttoBackground Process" section above.

# Feedback & Issues

If you have any feedback or issues in setting up and running this application as per the steps given above, please raise a issue under this repository.

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

3. You must have an PubNub Subscription

4. You must have a cloned working copy of this repository 


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

  - Line 23 : For the value of variable uri change it to the following format
    
    mongodb://<dbuser>:<dbpassword>@<dburi>/newttobackground
    
    where
      dbuser       : Your username for mLab
      dbpassword   : Your password for mLab
      dburi        : The URI assigned for your hosted MongnDB Database. 

3. Open the [bd_scikit.py](ttoBackground/bd_scikit.py) and perform the following modifications

  - Line 25 : For the value of variable uri change it to the following format
    
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
      
      
    Change the PubNub keys in Line 17,18 with your PubNub subscription keys.

2. Login to Bluemix console via cf tool and select the space.
3. Change directory to the ttoServer under the cloned Github repository.
4. Run the following command to push the application code to Bluemix
    cf push

Once successfully pushed, the server application will be automatically started. You can check its state in your Bluemix dashboard and see that its state is set to 'Running'.

## Build the ttoApp

Thw ttoApp source code is located under the [ttoApp](ttoApp) directory of this repository.

Follow the standard build procedures for building the APK package for this android App.

Before building , ensure that you select the PubNub keys as follows and ensure that the keys used in ttoApp are same as the ones used in ttoServer.

Set the PubNub Publish Key in function pubnubInit() Line 22 in [index.js](ttoApp/www/js/index.js)

Set the PubNub Subscribe Key in function pubnubInit() Line 23 in [index.js](ttoApp/www/js/index.js)


# Usage
Assuming that the ttoBackground and ttoServer processes ar deployed, the user can test the application as follows.

Step 1: Launch the ttoApp on your Android mobile and you will be presented with this screen
<img src="/ttoScreenShots/appscreen.png" align="center" width="250" >

Step 2: Select a Route and a Desired Arrival Time and tap on "Submit".  Make sure that the Desired Arrival Time is within 12 hour range of the current local time of the selected route.

<img src="/ttoScreenShots/selection.png" align="center" width="250" >

Step 3: The ttoApp sends  request to ttoServer with runs a TTO Recommendation Engine and returns travel recommendations based on the selected route and desired arrival time.

<img src="/ttoScreenShots/recommendation.png" align="center" width="250" >

Step 4: Tap on one out of the presented recommendations and the ttoApp starts a countdown till the start of journey ( as per the Predicted Departure Time in the selected Recommendation).

<img src="/ttoScreenShots/prejourneytracking.png" align="center" width="250" >

Step 5: During this time, the ttoServer may send realtime recommendation alerts , if there is a change in weather condition which alters the previous prediction, or if there is an incident reported along the route.

<img src="/ttoScreenShots/recommendationalert.png" align="center" width="250" >

Step 6: Tap on “Start Journey”. The ttoApp will enter the journey tracking phase. 

<img src="/ttoScreenShots/journeytracking.png" align="center" width="250" >

During this time, the ttoServer will send realtime recommendation alerts only if there is an incident reported along the route. 

<img src="/ttoScreenShots/accident.png" align="center" width="250" >

Step 7: Tap on End Journey to end the journey and then the ttoServer will stop sending any further alerts.






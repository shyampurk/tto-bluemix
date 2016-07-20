# Travel Time Optimizer App
Travel Time Optimizer (TTO) App for providing real time recommendations for travel duration based on historic traffic data, weather and day of the week. This app is hosted on IBM Bluemix and uses PubNub for client server interaction.

# Introduction
This is a demonstration app for showcasing how to harness the power of accumulated historic traffic data to provide real-time recommendations and traffic advisory alerts to users. This app is hosted on IBM Bluemix and uses PubNub for client server interaction & sending realtime alerts.

# Components

This application has four main components.

1. ttoBackground : This is a background process which is responsible for capturing traffic data and other traffic affecting parameters. This process also executes a KNN algorithm to generate predictions for future. It supposed to run continuously in conjunction with a hosted MongoDB database for storing the captured and prediction data, every ten minutes.

2. ttoServer : This is the main server process which is responsible for handling user requests and generating recommendations. It is hosted on IBM Bluemix

3. ttoApp : This is a Cordova,Android based mobile app used for availing the TTO service.

4. ttoTest : This is a test script for testing real-time recommendation alerts due to weather changes. 

# Setup and Deployment

## Prerequisites

1. A hosted MongoDB setup is required for storing all the data for this application. We have used [mLab](https://mlab.com/) ( MongoDB Database as a service) for this project. The MongoDB shoudl have the following configuration

      - Database name as 'newttobackground'
      - Following collections should be created
        - ttobgcoll ( TTO Background Collection for storing the API data from MapQuest and Yahoo Weather API)
        - ttoopvalcoll ( TTO Operation Value collection so storing the necessary data from API which affect Traffic)
        - ttoresultcoll ( TTO Result Collection for storing predictions )
        - ttoinducecoll ( TTO Induce value collection used for testing by ttoTest scripts )
      
      Note :- Also make a note of the DB URI, DB User and DB Password of our hosted Database.
      
2. You must have IBM Bluemix Account

3. You mush have an PubNub Subscription

4. You must have a cloned working copy this repository 


## Deployment of ttoBackground Process
ttoBarkground process can be executed under any system which has python2 runtime available.

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

Note : - In order to get reasonably good predictions , this program should be continuously running for atleast 3 months or more.

## Deployment of ttoServer

Follow the steps below for hosting ttoServer on IBM Bluemix

1. Open the [ttoServer.py](ttoServer/ttoServer.py) file and modify the following

    In function mongoInit(), change the value of varible uri to
    
        mongodb://<dbuser>:<dbpassword>@<dburi>/newttobackground
        
        where
          dbuser       : Your username for mLab
          dbpassword   : Your password for mLab
          dburi        : The URI assigned for your hosted MongnDB Database.
      
      
    Change the PubNub keys in Line 17,18 with your PubNub subscription keys.

2. Login to Bluemix console via cf tool and select the space.
3. Change directory to the ttoServer under the cloned github repository.
4. Run the following command to push the application code to bluemix
    cf push

Once successfully pushed, the server application will be automatically started. You can check its state in your bluemix dashboard and see that its state is set to 'Running'.


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






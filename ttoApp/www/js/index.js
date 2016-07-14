var g_message
var g_current_time
var g_selectedRoute
var g_routePoints
var CID = PUBNUB.uuid().toString();
var app = {

    initialize: function() {
        this.bindEvents();
        $(window).on("navigate", function (event, data) {          
            event.preventDefault();      
        })
    },

    bindEvents: function() {
        app.pubnubInit();
        app.subscribeStart();
    },

    pubnubInit: function() {
        pubnub = PUBNUB({                          
            publish_key   : 'pub-c-f2fc0469-ad0f-4756-be0c-e003d1392d43',
            subscribe_key : 'sub-c-4d48a9d8-1c1b-11e6-9327-02ee2ddab7fe'})
    },

    registerRoute: function() {
        $(document).ready(function(){   

            var routeID = document.getElementById("SelectRoute").value;
            var arrivalTime = document.getElementById("datetimepicker").value;
            
            if (routeID == "Select"){
            	alert("Please select valid Route");
             
         }
            
            else{
	        	$(':mobile-pagecontainer').pagecontainer('change', $('#emptypage'));
	           
            	app.showLoading("Waiting for recommendations..."); 
                
	            var getrouteMessage = {"CID":CID,"requestType":1,"routeName":routeID,"arrivalTime":arrivalTime};
	            
                app.publish(getrouteMessage);
	            
                 

        }
    })
    },


    recommendation: function (Server_message) {
        $(document).ready(function(){ 

            document.getElementById('selectedRoute').innerHTML = Server_message.route_name;

            if (Server_message.route_name == "NEWARK-EDISON"){
                document.getElementById('selectedRoute').innerHTML = "NEWARK To EDISON";
                 }
            else if(Server_message.route_name == "BROOKLYN-DENVILLE"){
                 document.getElementById('selectedRoute').innerHTML = "BROOKLYN To DENVILLE";
               
            }
            else if (Server_message.route_name =="MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"){
                document.getElementById('selectedRoute').innerHTML = "MOUNTZION RADIOLOGY CENTER To SF GENERAL HOSPITAL";
           
            }
            

            document.getElementById('arrTime').innerHTML =Server_message.arrival_time;
            var recommendation = Server_message.recommendation;
            console.log("The receommendation we got from the server",recommendation)
            var pred_minutesReal_0 = recommendation[0].pred_minutesReal
            // console.log(pred_minutesReal_0)
            if (recommendation.length <= 0){
                alert("No Recommendation for the selected time !!!");
                $("#backButton").click();
            }
            else{
                var recommLength = 0;
                for(var i = 0; i < recommendation.length; i++) {
                    recommDepnoteLength = recommendation[i].dep_note.split(" ").length;
                    console.log("The recommendation Depnote length",recommDepnoteLength);
                    if (recommendation[i].dep_note.split(" ")[recommDepnoteLength-1] == "ontime")
                    {
                      console.log('ontime');
                       

                    $("#journeyTrackRecommendList").append('<div id="recommendation_'+i+'" class="recommendation'+i+'" style="background-color:lightgreen;text-align:center;font-size:14px;padding:5px;width:95%;height:10%;border:2px solid #FFF;"><h5 id="recommendation_hTag_'+i+'">Predicted DepartureTime ::'+recommendation[i].predictedDepartureTime+'</h5><h5 id="predArrTime_'+i+'">Predicted ArrivalTime :: '+recommendation[i].predictedArrivalTime+'</h5><h5 id="recommendation_ptag'+i+'">'+recommendation[i].dep_note+'</h5></div>');
                   
                    }

                    if (recommendation[i].dep_note.split(" ")[recommDepnoteLength-1] == "early")
                    {
                        console.log('early');
                        
                    $("#journeyTrackRecommendList").append('<div id="recommendation_'+i+'" class="recommendation'+i+'" style="background-color:lightgreen;text-align:center;font-size:14px;padding:5px;width:95%;height:10%;border:2px solid #FFF;"><h5 id="recommendation_hTag_'+i+'">Predicted DepartureTime ::'+recommendation[i].predictedDepartureTime+'</h5><h5 id="predArrTime_'+i+'">Predicted ArrivalTime :: '+recommendation[i].predictedArrivalTime+'</h5><h5 id="recommendation_ptag'+i+'">'+recommendation[i].dep_note+'</h5></div>');
                   
                    }

                    if (recommendation[i].dep_note.split(" ")[recommDepnoteLength-1] == "late")
                    {
                        console.log('late');
                        
                    $("#journeyTrackRecommendList").append('<div id="recommendation_'+i+'" class="recommendation'+i+'" style="background-color:#ff6666;text-align:center;font-size:14px;padding:5px;width:95%;height:10%;border:2px solid #FFF;"><h5 id="recommendation_hTag_'+i+'">Predicted DepartureTime ::'+recommendation[i].predictedDepartureTime+'</h5><h5 id="predArrTime_'+i+'">Predicted ArrivalTime :: '+recommendation[i].predictedArrivalTime+'</h5><h5 id="recommendation_ptag'+i+'">'+recommendation[i].dep_note+'</h5></div>');
                       
                    }
                   

                    
                    }
              
            }
            var selectedRoute = document.getElementById('selectedRoute').innerHTML   
                $("#recommendation_0").click(function(e){
                      console.log(document.getElementById("recommendation_hTag_0").innerHTML);
                      var rec_depTime_0 = document.getElementById("recommendation_hTag_0").innerHTML
                      rec_depTime_0 = rec_depTime_0.split("::")[1] 
                      var predArrTime_0 = document.getElementById("predArrTime_0").innerHTML
                      
                      var pred_minutesReal = recommendation[0].pred_minutesReal
                      app.openpopup(rec_depTime_0,selectedRoute,pred_minutesReal);
                      return false;
                });
                $("#recommendation_1").click(function(e){
                      var rec_depTime_1 = document.getElementById("recommendation_hTag_1").innerHTML
                      rec_depTime_1 = rec_depTime_1.split("::")[1]
                      var predArrTime_1 = document.getElementById("predArrTime_1").innerHTML
                      var pred_minutesReal = recommendation[1].pred_minutesReal
                      app.openpopup(rec_depTime_1,selectedRoute,pred_minutesReal);
                      return false;
                });
                $("#recommendation_2").click(function(e){
                      var rec_depTime_2 = document.getElementById("recommendation_hTag_2").innerHTML
                      rec_depTime_2 = rec_depTime_2.split("::")[1]
                      var predArrTime_2 = document.getElementById("predArrTime_2").innerHTML
                      var pred_minutesReal = recommendation[2].pred_minutesReal
                      app.openpopup(rec_depTime_2,selectedRoute,pred_minutesReal);
                      return false;
                });
            });
        
    },

    openpopup: function(rec_depTime,selectedRoute,pred_minutesReal){
        console.log("recommended departure time",rec_depTime)
        var selectedRecommendaionMessage = {"CID":CID,"requestType":4,"recommendedDepTime":rec_depTime ,"pred_minutesReal":pred_minutesReal};
        console.log("The request for confirming the Departure time",selectedRecommendaionMessage)
        app.publish(selectedRecommendaionMessage);
        g_selectedRoute = selectedRoute
        g_routePoints = g_selectedRoute.split("To"); 
        
        console.log(g_selectedRoute)
            $(':mobile-pagecontainer').pagecontainer('change', $('#popuppage'));
            $("#journeytrackingCounter").fadeIn("fast").append(function(){app.timeCalculation(rec_depTime,selectedRoute)});
    },

    localTimeCalculation: function(selectedRoute){
        if (selectedRoute == "NEWARK To EDISON") {
            g_current_time = moment().tz("US/Eastern").format("YYYY-MM-DD HH:mm:ss");
            console.log("The route present time",g_current_time)
        }
        else if(selectedRoute == "BROOKLYN To DENVILLE"){
            g_current_time = moment().tz("US/Eastern").format("YYYY-MM-DD HH:mm:ss");
            console.log("The route present time",g_current_time)
        }
        else if(selectedRoute == "MOUNTZION RADIOLOGY CENTER To SF GENERAL HOSPITAL"){
            g_current_time = moment().tz("US/Pacific").format("YYYY-MM-DD HH:mm:ss");
            console.log("The route present time",g_current_time)
        }
        return g_current_time
    },
    timeCalculation: function(rec_depTime,selectedRoute){

        app.localTimeCalculation(selectedRoute);
        console.log("The selected route",selectedRoute)
        var ms = moment(rec_depTime,"YYYY-MM-DD HH:mm:ss").diff(moment(g_current_time,"YYYY-MM-DD HH:mm:ss"));
        var d = moment.duration(ms);
        var s = d.format("hh:mm:ss");
        var mm = d.format("mm");
        var ss = d.format("ss");
        app.flipclock(ss);

    },

    flipclock: function(ss){
        var clock;
       
        if (ss <= 0) {
            app.localTimeCalculation(g_selectedRoute);
            var startNowMessage1 = {"CID":CID,"requestType":2,"startTime":g_current_time };
            app.publish(startNowMessage1);
            console.log("The request message confirming to start the journey",startNowMessage1);
            document.getElementById('pointA').innerHTML = g_routePoints[0]
            document.getElementById('pointB').innerHTML = g_routePoints[1]
            $("#journeytrackingCounter").fadeOut("fast");
            $("#journeytrackingPhase").fadeIn("fast").append();
        }
        else{
            $(document).ready(function() {
                clock = $('.clock').FlipClock(ss, {
                    clockFace: 'HourlyCounter',
                    countdown: true,
                    callbacks: {
                        stop: function() {
                            app.localTimeCalculation(g_selectedRoute);
                            var startNowMessage2 = {"CID":CID,"requestType":2,"startTime":g_current_time};
                            app.publish(startNowMessage2);
                            console.log("The request message confirming to start the journey",startNowMessage2);
                            
                            document.getElementById('pointA').innerHTML = g_routePoints[0]
                            document.getElementById('pointB').innerHTML = g_routePoints[1]
                            $("#journeytrackingCounter").fadeOut("fast");
                            $("#journeytrackingPhase").fadeIn("fast").append();
                        }
                    }
                });

            });
        }
    },

    startNow: function(){
        app.localTimeCalculation(g_selectedRoute);
        var startNowMessage3 = {"CID":CID,"requestType":2,"startTime":g_current_time};
        console.log("The request message confirming to start the journey",startNowMessage3);
        app.publish(startNowMessage3);
        document.getElementById('pointA').innerHTML = g_routePoints[0]
        document.getElementById('pointB').innerHTML = g_routePoints[1]
        $("#journeytrackingCounter").fadeOut("fast");
        $("#journeytrackingPhase").fadeIn("fast").append();
    },

    resetRecommendation: function(){
        $("#journeyTrackRecommendList").remove(); 
        $(':mobile-pagecontainer').pagecontainer('change', $('#mainpage')); 
        location.reload(true);
    },

    endJourney: function() {
        $(document).ready(function(){
            var endJourneyMessage = {"CID":CID,"requestType":3};
            console.log("The request messag confirming to delete the client from the server",endJourneyMessage);
            app.publish(endJourneyMessage)
            $(':mobile-pagecontainer').pagecontainer('change', $('#mainpage'));
            $("#journeyTrackRecommendList").remove();
            location.reload(true);
        });
    },

    showLoading: function(text) {
        $.mobile.loading("show", {
            text: text,
            textVisible: true,
            textonly: true
        });
    },

    back: function() {
        $(document).ready(function(){
            $(':mobile-pagecontainer').pagecontainer('change', $('#secondpage'));
        });
    },

    backButton: function(){
        $("#journeyTrackRecommendList").remove();
        var stopJourneyMessage = {"CID":CID,"requestType":3};
        app.publish(stopJourneyMessage)
        $(':mobile-pagecontainer').pagecontainer('change', $('#mainpage'));
        location.reload(true);

    },

    subscribeStart: function(){  
      
        pubnub.subscribe({                                     
            channel : CID,
            message : function(g_message){
            
                if(g_message.responseType == 1){
                	$(':mobile-pagecontainer').pagecontainer('change', $('#secondpage'));        
           
                    console.log("The message from the server",g_message)
                    app.recommendation(g_message)
                }
                else if(g_message.responseType == 2){
                    console.log("The message from the server for accident alerts",g_message)
                        $(':mobile-pagecontainer').pagecontainer('change', $('#popuppage'));
                            $("#recommendationNotification").fadeOut("fast");
                            $("#accidentNotification").fadeOut("fast");
                            $("#accidentNotification").fadeIn("slow");
                            $("#accidentNotificationMessage").replaceWith('<p id="accidentNotificationMessage">'+g_message.message[0].shortDesc+'</p>');
                            $("#dismissAccidentNotification").click(function(e){
                                $("#accidentNotification").fadeOut("fast");
                            });
                    
                }
                else if(g_message.responseType == 3){
                    console.log("The message from the server for recommendation alerts",g_message)
                        $(':mobile-pagecontainer').pagecontainer('change', $('#popuppage'));
                            $("#recommendationNotification").fadeOut("fast");
                            $("#accidentNotification").fadeOut("fast");
                            $("#recommendationNotification").fadeIn("slow");                                             
                            $("#recommendationNotificationMessage").replaceWith('<p id="recommendationNotificationMessage">'+g_message.message+'</p>');
                            $("#dismissRecommendationNotification").click(function(e){
                            $("#recommendationNotification").fadeOut("fast");
                            });
                    
                }
                else if(g_message.responseType == 4){
                    console.log("The message from the server for time out of range alerts",g_message)
                       
                        $(':mobile-pagecontainer').pagecontainer('change', $('#popuppage'));
                          
                    
                            $("#recommendationNotification").fadeOut("fast");
                            $("#accidentNotification").fadeOut("fast");
                            $("#timeNotInRangeNotification").fadeIn("slow");
                            $("#timeNotInRangeNotificationMessage").replaceWith('<p id="timeNotInRangeNotificationMessage">'+g_message.message+'</p>');
                           
                            $("#dismissTimeNotInRangeNotification").click(function(e){
                           
                                $("#timeNotInRangeNotification").fadeOut("fast");
                                $(':mobile-pagecontainer').pagecontainer('change', $('#mainpage'));
                               
                                location.reload(true);
                            });
                    
                }     
            }
        })
    
    },

    publish: function(App_message) {
        pubnub.publish({                                    
            channel : "ttotest1",
            message : App_message,
            callback : function(m) {console.log("publish function message-->"+"Successfully Sent Message!")},
            error : function(m) {
                console.log("publish function message -->"+"Message send failed - [" 
                    +App_message+ "] - Retrying in 3 seconds!");
                setTimeout(app.publish(App_message), 3000);}
        })
        console.log("The request message to the server",App_message)
    },
};



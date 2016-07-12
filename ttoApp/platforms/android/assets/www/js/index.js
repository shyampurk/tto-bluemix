var g_message
var g_current_time
var g_selectedRoute
var g_routePoints
// var CID = PUBNUB.uuid().toString();
var CID = 'ciid';
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
            
            //EDITED THIS FUNCTION 
            // 1) Select has been selected instead of route name
            // 2) starting the secondpage in the else block 
            // refer the old programs if something goes wrong
 
           	
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

            //EDITED THESE LINES
            // BECAUSE WE CHANGED NEWARK-EDISON to  NEWARK To EDISON FOR THE UI PART
            if (Server_message.route_name == "NEWARK-EDISON"){
                document.getElementById('selectedRoute').innerHTML = "NEWARK To EDISON";
                 }
            else if(Server_message.route_name == "BROOKLYN-DENVILLE"){
                 document.getElementById('selectedRoute').innerHTML = "BROOKLYN To DENVILLE";
               
            }
            else if (Server_message.route_name =="MOUNTZION RADIOLOGY CENTER-SF GENERAL HOSPITAL"){
                document.getElementById('selectedRoute').innerHTML = "MOUNTZION RADIOLOGY CENTER To SF GENERAL HOSPITAL";
           
            }//TILL HERE
            

            document.getElementById('arrTime').innerHTML =Server_message.arrival_time;
            var recommendation = Server_message.recommendation;
            console.log(recommendation)
            var pred_minutesReal_0 = recommendation[0].pred_minutesReal
            console.log(pred_minutesReal_0)
            if (recommendation.length <= 0){
                alert("No Recommendation for the selected time !!!");
                $("#backButton").click();
            }
            else{
                for(var i = 0; i < recommendation.length; i++) {
                    //EDITED THIS LINE
                    // JUST TO ADDED THE MESSAGE INFRONT OF THE OF THE TIME AND MADE EVERY MESSAGE BOLD
                    $("#journeyTrackRecommendList").append('<div id="recommendation_'+i+'" class="recommendation'+i+'" style="background-color:lightgrey;text-align:center;font-size:14px;padding:5px;width:95%;height:10%;border:2px solid #FFF;"><h5 id="recommendation_hTag_'+i+'">Predicted DepartureTime ::'+recommendation[i].predictedDepartureTime+'</h5><h5 id="predArrTime_'+i+'">Predicted ArrivalTime :: '+recommendation[i].predictedArrivalTime+'</h5><h5 id="recommendation_ptag'+i+'">'+recommendation[i].dep_note+'</h5></div>');
                   
                    }
            }
            var selectedRoute = document.getElementById('selectedRoute').innerHTML   
                $("#recommendation_0").click(function(e){
                      console.log("mytesting");
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
        console.log(rec_depTime)
        var selectedRecommendaionMessage = {"CID":CID,"requestType":4,"recommendedDepTime":rec_depTime ,"pred_minutesReal":pred_minutesReal};
        console.log(selectedRecommendaionMessage)
        app.publish(selectedRecommendaionMessage);
        g_selectedRoute = selectedRoute
        // g_routePoints = g_selectedRoute.split("-");
        // EDITED THIS LINE
        // USED To TO SPLIT THE MESSAGE BECAUSE WE CHANGED THE ROUTE NAME
        g_routePoints = g_selectedRoute.split("To"); //NEWLINE
        
        console.log(g_selectedRoute)
            $(':mobile-pagecontainer').pagecontainer('change', $('#popuppage'));
            $("#journeytrackingCounter").fadeIn("fast").append(function(){app.timeCalculation(rec_depTime,selectedRoute)});
    },

    localTimeCalculation: function(selectedRoute){
        if (selectedRoute == "NEWARK To EDISON") {
            g_current_time = moment().tz("US/Eastern").format("YYYY-MM-DD HH:mm:ss");
            console.log(g_current_time)
        }
        else if(selectedRoute == "BROOKLYN To DENVILLE"){
            g_current_time = moment().tz("US/Eastern").format("YYYY-MM-DD HH:mm:ss");
            console.log(g_current_time)
        }
        else if(selectedRoute == "MOUNTZION RADIOLOGY CENTER To SF GENERAL HOSPITAL"){
            g_current_time = moment().tz("US/Pacific").format("YYYY-MM-DD HH:mm:ss");
            console.log(g_current_time)
        }
        return g_current_time
    },
    timeCalculation: function(rec_depTime,selectedRoute){

        app.localTimeCalculation(selectedRoute);
        console.log(selectedRoute)
        console.log(g_current_time)
        var ms = moment(rec_depTime,"YYYY-MM-DD HH:mm:ss").diff(moment(g_current_time,"YYYY-MM-DD HH:mm:ss"));
        var d = moment.duration(ms);
        var s = d.format("hh:mm:ss");
        var mm = d.format("mm");
        var ss = d.format("ss");
        console.log(ss)
        app.flipclock(ss);

    },

    flipclock: function(ss){
        var clock;
       
        if (ss <= 0) {
            app.localTimeCalculation(g_selectedRoute);
            var startNowMessage1 = {"CID":CID,"requestType":2,"startTime":g_current_time };
            app.publish(startNowMessage1);
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
        app.publish(startNowMessage3);
        document.getElementById('pointA').innerHTML = g_routePoints[0]
        document.getElementById('pointB').innerHTML = g_routePoints[1]
        $("#journeytrackingCounter").fadeOut("fast");
        $("#journeytrackingPhase").fadeIn("fast").append();
    },

    resetRecommendation: function(){
        $("#journeyTrackRecommendList").remove(); 
        $(':mobile-pagecontainer').pagecontainer('change', $('#mainpage')); 
        //EDITED LINES FOR RESET ADDED THE true AS ARGUMENT,WILL REMOVE THE CACHE
        location.reload(true);
    },

    endJourney: function() {
        $(document).ready(function(){
            var endJourneyMessage = {"CID":CID,"requestType":3};
            app.publish(endJourneyMessage)
            $(':mobile-pagecontainer').pagecontainer('change', $('#mainpage'));
            $("#journeyTrackRecommendList").remove();
            //EDITED LINES, ADDED THE true AS ARGUMENT, WILL REMOVE THE CACHE
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
        // setTimeout(location.reload(), 6000);
        //EDITED LINES, ADDED THE true AS ARGUMENT, WILL REMOVE THE CACHE
        location.reload(true);

    },

    subscribeStart: function(){  
      
        pubnub.subscribe({                                     
            channel : CID,
            message : function(g_message){
            // console.log(g_message);
                if(g_message.responseType == 1){
                	$(':mobile-pagecontainer').pagecontainer('change', $('#secondpage'));        
           
                    console.log(g_message)
                    app.recommendation(g_message)
                }
                else if(g_message.responseType == 2){
                    console.log(g_message)
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
                    console.log(g_message)
                        $(':mobile-pagecontainer').pagecontainer('change', $('#popuppage'));
                            $("#recommendationNotification").fadeOut("fast");
                            $("#accidentNotification").fadeOut("fast");
                            $("#recommendationNotification").fadeIn("slow");                                             //message : THIS IS THERE IN DOWN LINE
                            $("#recommendationNotificationMessage").replaceWith('<p id="recommendationNotificationMessage">'+g_message.message+'</p>');
                            $("#dismissRecommendationNotification").click(function(e){
                            $("#recommendationNotification").fadeOut("fast");
                            });
                    
                }
                else if(g_message.responseType == 4){
                    console.log(g_message)
                       
                        $(':mobile-pagecontainer').pagecontainer('change', $('#popuppage'));
                          
                    
                            $("#recommendationNotification").fadeOut("fast");
                            $("#accidentNotification").fadeOut("fast");
                            $("#timeNotInRangeNotification").fadeIn("slow");
                            $("#timeNotInRangeNotificationMessage").replaceWith('<p id="timeNotInRangeNotificationMessage">'+g_message.message+'</p>');
                           
                            $("#dismissTimeNotInRangeNotification").click(function(e){
                           
                                $("#timeNotInRangeNotification").fadeOut("fast");
                                $(':mobile-pagecontainer').pagecontainer('change', $('#mainpage'));
                                //EDITED LINES, ADDED THE true AS ARGUMENT, WILL REMOVE THE CACHE
                                // FOR THE ISSUE ABOVE OR BELOW 2nd ATTEMPT FAILURE
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
            callback : function(m) {console.log("Successfully Sent Message!")},
            error : function(m) {
                console.log("Message send failed - [" 
                    +App_message+ "] - Retrying in 3 seconds!");
                setTimeout(app.publish(App_message), 3000);}
        })
        console.log(App_message)
    },
};



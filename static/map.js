// JS specifically for the query page.

function capitaliseFirstLetter(string)
{
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function lowerFirstLetter(string)
{
    return string.charAt(0).toLowerCase() + string.slice(1);
}

sentimentalApp.controller('MapUIController', function MapUIController($scope, $location) {
	// Controller that manages linking the map and URL arguments to the
	// current query. It has no querying logic itself. That is left up to
	// QueryController which is also
	// instantiated in query.html.

	// (disabled) On first load, read in URL arguments and load those into the query.
	// angular.extend($scope.watched, $location.search());

	$scope.map = init_gmap(document.getElementById("map-canvas"));
    $scope.data = [];
    $scope.capitaliseFirstLetter = capitaliseFirstLetter;
    $scope.scores = [];

    $scope.topAxis = 'pleasantness';
    $scope.rightAxis = 'attention';

    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: 'test_data/sample_data.json',
        success: function (data) {
            $scope.$apply(function() {
                $scope.data = data;
            });
        }});

	// Setup map marker bindings.
	$scope.queryMarker = null;
	$scope.resultMarkers = [];
	$scope.$watch('watched', function(newVal, oldVal) {
		// var locationTokens = newVal.latLng.split(",");
		// $scope.replaceMarker(new google.maps.LatLng(locationTokens[0], locationTokens[1]));
	});

    $scope.options = [
        [80, 80, 50, 50, "optimism"],
        [20, 80, 50, 50, "frustration"],
        [20, 20, 50, 50, "disapproval"],
        [80, 20, 50, 50, "frivolity"],
        [50, 50, 80, 80, "rivalry"],
        [50, 50, 20, 80, "submission"],
        [50, 50, 20, 20, "coercion"],
        [50 ,50, 80, 20, "contempt"],
        [50, 80, 80, 50, "hostility"],
        [50, 20, 80, 50, "rejection"],
        [50, 20, 20, 50, "awe"],
        [50, 80, 20, 50, "anxiety"],
        [80, 50, 50, 80, "love"],
        [80, 50, 50, 20, "gloat"],
        [20, 50, 50, 20, "remorse"],
        [20, 50, 50, 80, "envy"]
    ];

    $scope.label1 = $scope.options[0][4];
    $scope.label2 = $scope.options[1][4];
    $scope.label3 = $scope.options[2][4];
    $scope.label4 = $scope.options[3][4];

    $scope.go = function (e1, e2, e3, e4, description){
        $( "#pleasantness" ).slider( "value", e1 );
        $( "#attention" ).slider( "value", e2 );
        $( "#sensitivity" ).slider( "value", e3 );
        $( "#aptitude" ).slider( "value", e4 );
    };

    $scope.change_city = function (city){

        var vegas = new google.maps.LatLng(36.1215, -115.1739);
        var phoenix = new google.maps.LatLng(33.4500, -112.0667);
        var madison = new google.maps.LatLng(43.0667, -89.4000);
        var waterloo = new google.maps.LatLng(43.4667, -80.5167);
        var edinburgh = new google.maps.LatLng(26.3042, -98.1639);
        var SF = new google.maps.LatLng(37.7833, -122.4167);

        if (city == "vegas") {
            $scope.map.map.setCenter(vegas);
        } else if (city == "phoenix") {
            $scope.map.map.setCenter(phoenix);
        } else if (city == "madison") {
            $scope.map.map.setCenter(madison);
        } else if (city == "waterloo") {
            $scope.map.map.setCenter(waterloo);
        } else if (city == "edinburgh") {
            $scope.map.map.setCenter(edinburgh);
        }
        else if (city == "SF") {
            $scope.map.map.setCenter(SF);
        }
        redrawMap();
    };

    $scope.switchAxes = function (i, topAxis, rightAxis) {
        console.log('switchaxes');
        $scope.topAxis = capitaliseFirstLetter(topAxis);
        $scope.rightAxis = capitaliseFirstLetter(rightAxis);

        $scope.label1 = $scope.options[i * 4][4];
        $scope.label2 = $scope.options[i * 4 + 1][4];
        $scope.label3 = $scope.options[i * 4 + 2][4];
        $scope.label4 = $scope.options[i * 4 + 3][4];
    }

    colorFader = function (elem, startColor, endColor) {
        return function (newValue, oldValue) {
            var sliderValue = (newValue / 100.0); //* 2 - 1;
            var sliderIntensity = Math.abs(sliderValue);
            var r, g, b;
            // if (sliderValue <= 0) {
            //     r = startColor[0];
            //     g = startColor[1];
            //     b = startColor[2];
            // } else {
            //     r = endColor[0];
            //     g = endColor[1];
            //     b = endColor[2];
            // }
            // r = Math.floor(sliderIntensity * r + (1 - sliderIntensity) * 255);
            // g = Math.floor(sliderIntensity * g + (1 - sliderIntensity) * 255);
            // b = Math.floor(sliderIntensity * b + (1 - sliderIntensity) * 255);
            r = Math.floor(sliderIntensity * endColor[0] +
               (1 - sliderIntensity) * startColor[0]);
            g = Math.floor(sliderIntensity * endColor[1] +
               (1 - sliderIntensity) * startColor[1]);
            b = Math.floor(sliderIntensity * endColor[2] +
               (1 - sliderIntensity) * startColor[2]);
            elem.css("background-color", "rgb(" + r + "," + g + "," + b + ")");
            recalcData();
        };
    };

    recalcData = function () {
        var scores = [];

        var pleasantness = ($scope.pleasantness / 100.0) * 2 - 1;
        var aptitude = ($scope.aptitude / 100.0) * 2 - 1;
        var attention = ($scope.attention / 100.0) * 2 - 1;
        var sensitivity = ($scope.sensitivity / 100.0) * 2 - 1;

        for (var i = 0; i < $scope.data.length; i++) {
            var review_emotion = $scope.data[i];
            var distance = $scope.compute_distance(review_emotion,
             {pleasantness: pleasantness,
                aptitude: aptitude,
                attention: attention,
                sensitivity: sensitivity});
            scores.push({
                location: new google.maps.LatLng(review_emotion['lat'], review_emotion['lng']),
                weight: Math.pow(3 * (Math.min(1e3, 1.0 / distance)), 4)
            });
        }
        $scope.scores = scores;
    };


    google.maps.event.addListener($scope.map.map, 'click', function(event) {
        if($scope.prev_infowindow) {
            $scope.prev_infowindow.close();
        };
    });

    markers = [];

    rePlot = function () {
        var scores = [];
        markers = [];

        function selectPolarity(element) {
            var epsilon = 0.3;
            var score_close_enough = Math.abs(element['rating'] - $scope.polarity/100) < epsilon;
            var right_food = $scope.food == element['food'];
            var manual_label = element['type'] == "manual_label";

            var select = right_food;

            if (!$scope.see_all) {
                select = select && score_close_enough;
            }
            if ($scope.gold_data) {
                select = select && manual_label
            }
            return select;
        }

        var filteredData = $scope.data.filter(selectPolarity);

        for (var i = 0; i < filteredData.length - 1; i++) {
            var review_emotion = filteredData[i];

            // if (i > 0) {
            var contentString = '<div id="content">'+
              '<div id="siteNotice">'+'</div>'+
              '<h1 id="firstHeading" class="firstHeading">'+review_emotion['sentence']+'</h1>'+
              '<h2>('+review_emotion['food']+')</h2>'+
              '<div id="bodyContent">'+
              '<p><b>sentence polarity: </b>'+review_emotion['rating']+'</p>'+
              '<p><b>review rating: </b>'+review_emotion['stars']+'</p>'+
              '<p><b>business name: </b>'+review_emotion['name']+'</p>'+
              '<p><b>filtered concepts: </b>'+review_emotion['filtered_concepts']+'</p>'+
              '<p><b>concepts: </b>'+review_emotion['concepts']+'</p>'+
              '<p><b>concept polarity: </b>'+review_emotion['concept_polarity']+'</p>'+
              '<p><b>dependency polarity: </b>'+review_emotion['dep_polarity']+'</p>'+
              '<p><b>adjective polarity: </b>'+review_emotion['adj_polarity']+'</p>'+
              '<p><b>votes: </b>'+JSON.stringify(review_emotion['votes'])+'</p>'+
              '</div>'+
              '</div>';

            var marker = new google.maps.Marker({
                position: new google.maps.LatLng(review_emotion['lat'], review_emotion['lng']),
                map: $scope.map.map,
                title: 'Review Sentiment'
            });

            markers[i] = marker;

            closure(marker, contentString);

            scores.push({
                location: new google.maps.LatLng(review_emotion['lat'], review_emotion['lng']),
                weight: (review_emotion['rating'] + 3) * 10
            });
        }
        $scope.scores = scores;
    }

    $scope.prev_infowindow = false; 

    function closure(marker, contentString) {
        var infowindow = new google.maps.InfoWindow({
            content: contentString
        });


        google.maps.event.addListener(marker, 'click', function(event) {
            if($scope.prev_infowindow) {
                $scope.prev_infowindow.close();
            }
            $scope.prev_infowindow = infowindow;
            infowindow.open($scope.map.map, marker);
        });
    }

    redrawMap = function () {
        for (var i = 0; i < markers.length; i++) {
            markers[i].setMap(null);
        }
        $scope.map.heatmap.setData($scope.scores);
        rePlot();
    };


    $scope.food_list = [
        'burger',
        'burrito',
        'lobster',
        'beer'
    ];
    $scope.food = "burger";

    $scope.pleasantness = 50;
    $scope.attention = 50;
    $scope.sensitivity = 50;
    $scope.aptitude = 50;
    $scope.polarity = 0;
    $scope.$watch('pleasantness', colorFader($('#pleasantness'), [143, 236, 106], [50, 150, 50]));
    $scope.$watch('attention', colorFader($('#attention'), [253, 255, 115], [240, 80, 0]));
    $scope.$watch('sensitivity', colorFader($('#sensitivity'), [153, 120, 215], [20, 53, 173]));
    $scope.$watch('aptitude', colorFader($('#aptitude'), [252, 0, 46], [189, 6, 39]));

    // $scope.$watch('polarity', colorFader($('#polarity'), [0, 0, 0], [255, 255, 255]));

    $scope.$watch('polarity', redrawMap);
    // $scope.$watch('polarity', rePlot);
    // $scope.$watch('polarity', rePlot);
    $scope.$watch('data', redrawMap);
    $scope.$watch('food', redrawMap);
    $scope.$watch('see_all', redrawMap);


	// Setup click behavior.
	google.maps.event.addListener($scope.map.map, 'click', function(event) {
		// Since this callback isn't fired from within angularjs, we have to
		// make changes in $apply so it knows to propigate changes.
		$scope.$apply(function() {
			$scope.watched.latLng = event.latLng.lat() + "," + event.latLng.lng();
			$scope.map.map.panTo(new google.maps.LatLng(event.latLng.lat(), event.latLng.lng()));
		});
	});

	$scope.refreshMap = function() {
		pleasantness = $( "#pleasantness" ).slider( "value" ),
		attention = $( "#attention" ).slider( "value" ),
		sensitivity = $( "#sensitivity" ).slider( "value" ),
		aptitude = $( "#aptitude" ).slider( "value" );
        polarity = $( "#polarity" ).slider( "value" );

		$scope.pleasantness = pleasantness;
		$scope.attention = attention;
		$scope.sensitivity = sensitivity;
		$scope.aptitude = aptitude;
        $scope.polarity = polarity;

	    $scope.score = 0; //$scope.compute_distance({'pleasantness': 50, 'attention': 50, 'sensitivity': 50, 'aptitude': 50});
	};

    $scope.compute_distance = function(input1, input2) {
      return Math.sqrt(
         Math.pow(input1.pleasantness - input2.pleasantness, 2) +
         Math.pow(input1.attention - input2.attention, 2) +
         Math.pow(input1.sensitivity - input2.sensitivity, 2) +
         Math.pow(input1.aptitude - input2.aptitude, 2)
         );
  };
});

$(document).ready(function () {
    if ($(window).width() < 1500)
        $('body').addClass('too-narrow');
});

$(function() {
    $( ".slider" ).slider({
       orientation: "horizontal",
       value: 50,
       max: 100,
       change: update
   });

    $( ".polarity_slider" ).slider({
       orientation: "horizontal",
       value: 0,
       min: -200,
       max: 200,
       change: update
   }).each(function() {
        // Add labels to slider whose values 
        // are specified by min, max

        // Get the options for this slider (specified above)
        var opt = $(this).data().uiSlider.options;

        // Get the number of possible values
        var vals = opt.max - opt.min;

        // Position the labels
        for (var i = 0; i <= vals; i++) {

            // Create a new element and position it with percentages
            var el = $('<label>' + (i + opt.min) + '</label>').css('left', (i/vals*100) + '%');

            // Add the element inside #slider
            $("#slider").append(el);

        }
    });

	function update() {
		$(".left-bar").click();
	};
});

$(document).ready(function() {
    context = $("#mainCanvas")[0].getContext("2d");
    context.fillStyle = "rgb(200,0,0)";  
    context.fillRect(5, 10, 50, 50);  

    context.fillStyle = "rgba(0, 0, 200, 0.5)";  
    context.fillRect(30, 35, 55, 55);
});


$(function($) {
    $('#control-expander').click(function () {
        if ($('#controls').css('display') == 'block')
            $('#show-hide').text('Show');
        else
            $('#show-hide').text('Hide');
        $('#controls').slideToggle(500);
    });
    $(".knob").knob({
        change : function (value) {
            //console.log("change : " + value);
        },
        release : function (value) {
            //console.log(this.$.attr('value'));

            goWheel = function (rightAxis, topAxis){
                $( topAxis ).slider( "value", 50 + 50 * Math.cos(value / 180.0 * Math.PI ));
                $( rightAxis ).slider( "value", 50 + 50 * Math.sin(value / 180.0 * Math.PI ));
            };

            var topAxis = '#' + lowerFirstLetter($('#top-axis').text());
            var rightAxis = '#' + lowerFirstLetter($('#right-axis').text());

            goWheel(rightAxis, topAxis);
            // goWheel("#aptitude", "#sensitivity");
            // goWheel("#sensitivity", "#attention");
            // goWheel("#pleasantness", "#aptitude");
            console.log("release : " + value);
        },
        cancel : function () {
            console.log("cancel : ", this);
        },
        draw : function () {
            // draw axis
            console.log(this.xy);

            // "tron" case
            if(this.$.data('skin') == 'tron') {

                var a = this.angle(this.cv)         // Angle
                    , sa = this.startAngle          // Previous start angle
                    , sat = this.startAngle         // Start angle
                    , ea                            // Previous end angle
                    , eat = sat + a                 // End angle
                    , r = 1;

                    this.g.lineWidth = this.lineWidth;

                    this.o.cursor
                    && (sat = eat - 0.3)
                    && (eat = eat + 0.3);

                    if (this.o.displayPrevious) {
                        ea = this.startAngle + this.angle(this.v);
                        this.o.cursor
                        && (sa = ea - 0.3)
                        && (ea = ea + 0.3);
                        this.g.beginPath();
                        this.g.strokeStyle = this.pColor;
                        this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, sa, ea, false);
                        this.g.stroke();
                    }

                    this.g.beginPath();
                    this.g.strokeStyle = r ? this.o.fgColor : this.fgColor ;
                    this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, sat, eat, false);
                    this.g.stroke();

                    this.g.lineWidth = 2;
                    this.g.beginPath();
                    this.g.strokeStyle = this.o.fgColor;
                    this.g.arc( this.xy, this.xy, this.radius - this.lineWidth + 1 + this.lineWidth * 2 / 3, 0, 2 * Math.PI, false);
                    this.g.stroke();
                }

            this.draw();

            // Draw axes... these go above the knob stuff, so are drawn last
            var x  = this.xy;
            var y = this.xy;
            this.g.lineWidth = 1;
            this.g.beginPath();
            this.g.strokeStyle = this.o.fgColor;
            this.g.moveTo(x - this.radius - 100, y);
            this.g.lineTo(x + this.radius + 100, y);
            this.g.strokeStyle = 'rgb(0, 0, 150)';
            this.g.stroke();
            this.g.font="12pt Arial";
            this.g.fillStyle = 'rgb(0, 0, 150)';
            this.g.fillText("1", x + this.radius, y - 5);
            this.g.fillText("-1", x - this.radius, y - 5);

            this.g.beginPath();
            this.g.strokeStyle = this.o.fgColor;
            this.g.moveTo(x, y - this.radius - 10);
            this.g.lineTo(x, y + this.radius + 10);
            this.g.strokeStyle = 'rgb(150, 0, 0)';
            this.g.stroke();
            this.g.font="12pt Arial";
            this.g.fillStyle = 'rgb(150, 0, 0)';
            this.g.fillText("1", x + 5, y - this.radius);
            this.g.fillText("-1", x + 5, y + this.radius);

            return false;
        }});

    // Example of infinite knob, iPod click wheel
    var v, up=0,down=0,i=0
    ,$idir = $("div.idir")
    ,$ival = $("div.ival")
    ,incr = function() { i++; $idir.show().html("+").fadeOut(); $ival.html(i); }
    ,decr = function() { i--; $idir.show().html("-").fadeOut(); $ival.html(i); };
    $("input.infinite").knob(
    {
        min : 0
        , max : 20
        , stopper : false
        , change : function () {
            if(v > this.cv){
                if(up){
                    decr();
                    up=0;
                }else{up=1;down=0;}
            } else {
                if(v < this.cv){
                    if(down){
                        incr();
                        down=0;
                    }else{down=1;up=0;}
                }
            }
            v = this.cv;
        }
    });
});

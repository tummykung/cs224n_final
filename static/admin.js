// General admin JS.


// This is the angularjs module that all things are added to. It's a namespace
// basically.
var sentimentalApp = angular.module('sentimental', [], function($locationProvider) {
	// Make angularjs accept standard URL arguments.
	$locationProvider.html5Mode(true).hashPrefix("!");
});

sentimentalApp.controller('MapController', function MapController($scope) {
	// Controller that manages the emotion map.

	// Values that are watched are stored in $scope.watch. Initilize here.
	$scope.watched = {};


	$scope.watched.latLng = "37.764073094986266,-122.41952431201935";
});


init_gmap = function(mapElement) {
    // Initalizes the Google Map.
    //
    // Args:
    // mapElement - DOM element to place the map in.
    // Returns: An object with the following properties:
    //     map - The resulting Google Map.
    //     heatmapData - The heatmap array

    var scottsHouse = new google.maps.LatLng(37.764073094986266, -122.41952431201935);

    // Inits the map and sets a default location.
    var mapOptions = {
        center: scottsHouse,
        zoom: 14,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(mapElement, mapOptions);

    var dataArray = new google.maps.MVCArray([
        {location: new google.maps.LatLng(37.7750, -122.4174), weight: 10},
        {location: new google.maps.LatLng(37.7752, -122.4181), weight: 10},
        {location: new google.maps.LatLng(37.7755, -122.4186), weight: 10},
        {location: new google.maps.LatLng(37.7751, -122.4183), weight: 10},
        {location: new google.maps.LatLng(37.7745, -122.4175), weight: 10},
        {location: new google.maps.LatLng(37.7748, -122.4177), weight: 10},
        {location: new google.maps.LatLng(37.7742, -122.4188), weight: 10},
        {location: new google.maps.LatLng(37.7747, -122.4181), weight: 10},
    ]);
    var heatmap = new google.maps.visualization.HeatmapLayer({
        data: dataArray,
        map: map,
        dissipating: false,
        radius: 0.004,
        gradient: ["rgba(255, 255, 255, 0)", "rgba(255, 0, 0, 0.5)", "rgba(200, 0, 0, 1)"]
    });

    return {map : map, heatmap : heatmap};
};


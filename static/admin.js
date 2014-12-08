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

    vegas = "36.1215, -115.1739";
    phoenix = "33.4500, -112.0667";
    Madison = "43.0667, -89.4000";
    waterloo = "43.4667, -80.5167";
    edinburgh = "26.3042, -98.1639";
    SF = "37.764073094986266,-122.41952431201935";

    $scope.watched.latLng = vegas;
});


init_gmap = function(mapElement) {
    // Initalizes the Google Map.
    //
    // Args:
    // mapElement - DOM element to place the map in.
    // Returns: An object with the following properties:
    //     map - The resulting Google Map.
    //     heatmapData - The heatmap array

    var vegas = new google.maps.LatLng(36.1215, -115.1739);
    var phoenix = new google.maps.LatLng(33.4500, -112.0667);
    var madison = new google.maps.LatLng(43.0667, -89.4000);
    var waterloo = new google.maps.LatLng(43.4667, -80.5167);
    var edinburgh = new google.maps.LatLng(26.3042, -98.1639);

    // Inits the map and sets a default location.
    var mapOptions = {
        center: madison,
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(mapElement, mapOptions);

    var dataArray = new google.maps.MVCArray([
        {location: new google.maps.LatLng(36.1212, -115.1742), weight: 10},
        {location: new google.maps.LatLng(36.1217, -115.1739), weight: 10},
        {location: new google.maps.LatLng(36.1215, -115.1744), weight: 10},
        {location: new google.maps.LatLng(36.1215, -115.1748), weight: 10},
        {location: new google.maps.LatLng(36.1212, -115.1732), weight: 10},
        {location: new google.maps.LatLng(36.1214, -115.1739), weight: 10},
        {location: new google.maps.LatLng(36.1215, -115.1739), weight: 10},
        {location: new google.maps.LatLng(36.1211, -115.1739), weight: 10},
    ]);
    var heatmap = new google.maps.visualization.HeatmapLayer({
        data: dataArray,
        map: map,
        dissipating: false,
        radius: 0.012,
        gradient: ["rgba(255, 255, 255, 0)", "rgba(255, 0, 0, 0.5)", "rgba(200, 0, 0, 1)"]
    });

    return {map : map, heatmap : heatmap};
};


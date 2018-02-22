$(document).ready(function () {
    $('#defaultModal').modal('show');

    var _loading_location = null;
    var _current_markers = {};

    var generate_markers = function (data) {
        var markers = [];
        for (var d in data) {
            if (data.hasOwnProperty(d)) {

                var lat = data[d].location.coordinates[1];
                var lng = data[d].location.coordinates[0];

                if ((lat + lng) in _current_markers) {
                    continue;
                }

                _current_markers[lat + lng] = true;
                markers.push({
                    lat: lat,
                    lng: lng,
                    title: 'GeoStrangers',
                    icon: "{{ url_for('static', filename='img/maps/24px-Green_Point.png') }}",
                    infoWindow: {
                        content: '<p><b>' + data[d].location_text + '</b></p>'
                    }
                });


            }
        }
        return markers;
    };

    var load_locations = function () {
        var bounce = map.getBounds();
        if (bounce) {

            $.getJSON(
                "{{ url_for('api.users_location',_external=True, _scheme='https') }}",
                bounce.toJSON()
                , function (data) {
                    var markers = generate_markers(data);
                    map.addMarkers(markers);

                });
        }
    };


    var map = new GMaps({
        el: '#googlemaps'
        , lat: 41.761473
        , lng: 10.6796017
        , zoom: 1
        , scrollwheel: false
        , panControl: false
        , zoomControl: false
        , mapTypeControl: false
        , scaleControl: false
        , streetViewControl: false
        , overviewMapControl: false
        , idle: function (e) {
            load_locations();
        }

    });

    map.addControl({
        position: 'top_right',
        content: 'Show Stranger near you...',
        style: {
            margin: '7px',
            padding: '3px 10px',
            border: 'solid 1px #7aa431',
            background: '#89b837',
            color: '#fff'
        },
        events: {
            click: function () {
                GMaps.geolocate({
                    success: function (position) {
                        map.setCenter(position.coords.latitude, position.coords.longitude);
                        map.setZoom(7);
                    },
                    error: function (error) {
                        alert('Geolocation failed: ' + error.message);
                    },
                    not_supported: function () {
                        alert("Your browser does not support geolocation");
                    }

                });
            }
        }
    });
});



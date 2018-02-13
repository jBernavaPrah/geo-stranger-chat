$("#startwebchat").click(function (event) {
    event.preventDefault();

    $(this).hide();
    $("#webchat").html("<iframe class='google-map' style='margin:auto;' frameBorder=0 frameborder=0 hspace=0 vspace=0 marginheight=0 marginwidth=0 src='{{url_for('index.webchat_page', _external=True,_scheme='https')}}'></iframe>");
});

var _loading_location = null;
var _current_markers = {};

var generate_markers = function (data) {
    var markers = [];
    for (var d in data) {
        if (data.hasOwnProperty(d)) {

            var lat = data[d].location.coordinates[1];
            var lng = data[d].location.coordinates[0];

            if (!((lat + lng) in _current_markers) && data[d].count === _current_markers[lat + lng]) {
                _current_markers[lat + lng] = data[d].count;
                markers.append({
                    lat: lat,
                    lng: lng,
                    title: 'GeoStrangers',
                    icon: "{{ url_for('static', filename='img/maps/24px-Green_Point.png') }}",
                    infoWindow: {
                        content: '<p>GeoStrangers registered here: </p> <b>' + data[d].count + '</b>'
                    }
                });
            }


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
    , zoom: 5
    , scrollwheel: true
    , panControl: false
    , zoomControl: false
    , mapTypeControl: false
    , scaleControl: false
    , streetViewControl: false
    , overviewMapControl: false
    , dragend: function (e) {
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


// gmap_ele.data('gMap.reference').addListener('bounds_changed', function () {
//     if (_loading_location) {
//         clearTimeout(_loading_location);
//     }
//
//     _loading_location = setTimeout(function () {
//         load_locations();
//     }, 500);
//
// });

//
// if (navigator.geolocation) {
//     navigator.geolocation.getCurrentPosition(function (position) {
//         gmap_ele.gMap('centerAt', {
//             latitude: position.coords.latitude,
//             longitude: position.coords.longitude,
//             zoom: 8
//         });
//
//     }, function () {
//
//     });
// }
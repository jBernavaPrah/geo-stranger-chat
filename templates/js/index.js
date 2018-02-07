$("#startwebchat").click(function () {
    $(this).hide();
    $("#webchat").html("{{ webchat_iframe()|safe }}");
});

var _loading_location = null;
var _loading_location_ajax = null;
var load_locations = function (gmap) {
    var bounce = gmap.data('gMap.reference').getBounds();
    if (bounce) {
        if (_loading_location_ajax) {
            _loading_location_ajax.abort();
        }

        _loading_location_ajax = $.getJSON(
            "{{ url_for('api.users_location',_external=True, _scheme='https') }}",
            bounce.toJSON()
            , function (data) {
                if (data) {
                    gmap.gMap('clearMarkers');
                }

                for (var d in data) {
                    if (data.hasOwnProperty(d)) {
                        gmap.gMap('addMarker', {
                            latitude: data[d].location.coordinates[1],
                            longitude: data[d].location.coordinates[0],
                            content: 'GeoStrangers registered here: ' + data[d].count,
                            popup: false,
                            icon: {
                                image: "{{ url_for('static', filename='img/maps/24px-Green_Point.png') }}",
                                iconsize: [24, 24],
                                iconanchor: [12, 12]
                            }
                        });
                    }
                }
            });
    }
};

var gmap_ele = $('#googlemaps').gMap({
    controls: false,
    scrollwheel: true,
});

gmap_ele.data('gMap.reference').addListener('bounds_changed', function () {

    if (_loading_location) {
        clearTimeout(_loading_location);
    }

    _loading_location = setTimeout(function () {
        load_locations(gmap_ele);
    }, 500);

});

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function (position) {
        gmap_ele.gMap('centerAt', {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            zoom: 8
        });

    }, function () {

    });
}
//======================= CONSTANTES GLOBAIS ================================//
//var MAP_POINTER = null;

var gmap_options = {
    generate_controls: true,
    styles: {
        // source: https://snazzymaps.com/style/132/light-gray
        'custom': [{
            "featureType": "water",
            "elementType": "geometry.fill",
            "stylers": [{"color": "#d3d3d3"}]
        }, {
            "featureType": "transit",
            "stylers": [{"color": "#808080"}, {"visibility": "off"}]
        }, {
            "featureType": "road.highway",
            "elementType": "geometry.stroke",
            "stylers": [{"visibility": "on"}, {"color": "#b3b3b3"}]
        }, {
            "featureType": "road.highway",
            "elementType": "geometry.fill",
            "stylers": [{"color": "#ffffff"}]
        }, {
            "featureType": "road.local",
            "elementType": "geometry.fill",
            "stylers": [{"visibility": "on"}, {"color": "#ffffff"}, {"weight": 1.8}]
        }, {
            "featureType": "road.local",
            "elementType": "geometry.stroke",
            "stylers": [{"color": "#d7d7d7"}]
        }, {
            "featureType": "poi",
            "elementType": "geometry.fill",
            "stylers": [{"visibility": "on"}, {"color": "#ebebeb"}]
        }, {
            "featureType": "administrative",
            "elementType": "geometry",
            "stylers": [{"color": "#a7a7a7"}]
        }, {
            "featureType": "road.arterial",
            "elementType": "geometry.fill",
            "stylers": [{"color": "#ffffff"}]
        }, {
            "featureType": "road.arterial",
            "elementType": "geometry.fill",
            "stylers": [{"color": "#ffffff"}]
        }, {
            "featureType": "landscape",
            "elementType": "geometry.fill",
            "stylers": [{"visibility": "on"}, {"color": "#efefef"}]
        }, {
            "featureType": "road",
            "elementType": "labels.text.fill",
            "stylers": [{"color": "#696969"}]
        }, {
            "featureType": "administrative",
            "elementType": "labels.text.fill",
            "stylers": [{"visibility": "on"}, {"color": "#737373"}]
        }, {
            "featureType": "poi",
            "elementType": "labels.icon",
            "stylers": [{"visibility": "off"}]
        }, {
            "featureType": "poi",
            "elementType": "labels",
            "stylers": [{"visibility": "off"}]
        }, {
            "featureType": "road.arterial",
            "elementType": "geometry.stroke",
            "stylers": [{"color": "#d6d6d6"}]
        }, {
            "featureType": "road",
            "elementType": "labels.icon",
            "stylers": [{"visibility": "off"}]
        }, {}, {
            "featureType": "poi",
            "elementType": "geometry.fill",
            "stylers": [{"color": "#dadada"}]
        }]
    }
};

var rmvMap;

//============================= SWITCHERS ===================================//
$(document).ready(function() {
    $('#id_show_location').on('change', function () {
        show_location($(this).prop('checked') === true);
    });

    $('#id_lat').on('blur', function() {
        show_map();
    });
    $('#id_long').on('blur', function() {
        show_map();
    });
});

function show_map() {
    var empty_location_field = $('.location-field.no-map');
    var map_field = $('.map-field');
    var lat = $('#id_lat');
    var long = $('#id_long');

    if (lat.val() && long.val()) {
        empty_location_field.hide();
        map_field.show();
        render_map(lat.val(), long.val());
    } else {
        empty_location_field.show();
        map_field.hide();
    }
}

function render_map(lat, long) {
    var location_options = {
        locations: [{
            lat: lat,
            lon: long,
            animation: google.maps.Animation.DROP,
            html: "Drew Headquarter",
            icon: MAP_POINTER,
            clickable: false
        }],
        map_options: {
            scrollwheel: false,
            mapTypeControl: true,
            streetViewControl: true,
            zoomControlOptions: {
                style: google.maps.ZoomControlStyle.SMALL
            },
            zoom: 16,
            set_center: [lat, long]
        }
    };

    /**
     * =======================================
     * Google Maps
     * =======================================
     */
    if ( !rmvMap && typeof Maplace === 'function' && $( '#gmap' ) ) {
        rmvMap = new Maplace(gmap_options);
    }

    if (rmvMap) {
        if (rmvMap.Loaded()) {
            console.log("map has been previously loaded");
            rmvMap.RemoveLocations(1);
            rmvMap.Load(location_options);
        } else {
            console.log("map not previously loaded");
            rmvMap.Load(location_options);
        }
    }
}

function show_location(show) {
    show = show === true;
    if (show) {
        $('.location-field').fadeIn();
    } else {
        $('.location-field').fadeOut();
    }

    show_map();
}

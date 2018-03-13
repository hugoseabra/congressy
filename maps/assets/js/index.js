function initAutocomplete() {
    var map1 = new google.maps.Map(document.getElementById('map1'), {
        center: {lat: -33.8688, lng: 151.2195},
        zoom: 13,
    });
    var map2 = new google.maps.Map(document.getElementById('map2'), {
        zoom: 8,
        center: {lat: 40.731, lng: -73.997}
    });
    var geocoder1 = new google.maps.Geocoder;
    var geocoder2 = new google.maps.Geocoder;
    var infowindow = new google.maps.InfoWindow;

    //Faz a geo decodificação de uma coordenada para o local no mapa 2
    document.getElementById('submit').addEventListener('click', function() {
        geocodeLatLng(geocoder1, map2, infowindow);
    });

    document.getElementById('submitEndereco').addEventListener('click', function() {
        geocodeAddress(geocoder2, map1);
    });
}

function geocodeLatLng(geocoder, map, infowindow) {
    var input = document.getElementById('latlng').value;
    var latlngStr = input.split(',', 2);
    var latlng = {lat: parseFloat(latlngStr[0]), lng: parseFloat(latlngStr[1])};
    geocoder.geocode({'location': latlng}, function(results, status) {
        if (status === 'OK') {
            if (results[1]) {
                map.setZoom(15);
                var marker = new google.maps.Marker({
                    position: latlng,
                    map: map
                });
                map.setCenter({
                    lat: marker.position.lat(),
                    lng: marker.position.lng()
                });
                infowindow.setContent(results[1].formatted_address);
                infowindow.open(map, marker);
            } else {
                window.alert('No results found');
            }
        } else {
            window.alert('Geocoder failed due to: ' + status);
        }
    });
}

function geocodeAddress(geocoder, resultsMap) {
    var address = document.getElementById('endereco').value;
    geocoder.geocode({'address': address}, function(results, status) {
        if (status === 'OK') {
            resultsMap.setCenter(results[0].geometry.location);
            var marker = new google.maps.Marker({
                map: resultsMap,
                position: results[0].geometry.location,
                draggable: true
            });
            document.getElementById('lat').value = marker.position.lat(); //latitude
            document.getElementById('lng').value = marker.position.lng();
            document.getElementById('zoom').value = resultsMap.getZoom();
            google.maps.event.addListener(marker, 'dragend', function () {
                document.getElementById('lat').value = marker.position.lat();
                document.getElementById('lng').value = marker.position.lng();
            });
            google.maps.event.addListener(resultsMap, 'zoom_changed', function () {
                document.getElementById('zoom').value = resultsMap.getZoom();
            });
        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}
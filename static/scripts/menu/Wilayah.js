var Wilayah = {};
Wilayah.show = function () {
        $('.main').css({
        'height':'100%'
    });
    $.get('/api/get_wilayah', function (list_wilayah) {
        var option_tmp = '<option value="{{region_polygon}}">{{region_polygon}}</option>';
        for (var i = 0; i < list_wilayah.length; i++) {
            $('#active-wilayah').append(option_tmp.replaceAll('{{region_polygon}}', list_wilayah[i]))
        }
        Wilayah.load_area(list_wilayah[0]);
    });
    Wilayah.map = L.map('map').setView([-6.010565, 106.853122], 7);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(Wilayah.map);
    $('#active-wilayah').change(function () {
        try {
            Wilayah.map.layers.removeFrom(Wilayah.map)
        } catch (e) {
        }
        Wilayah.load_area($(this).val());
    })
};

Wilayah.save_geojson = function () {
    var geojson = {json: JSON.stringify(Wilayah.map.layers.toGeoJSON())};
    var url = '/api/post_wilayah/' + $('#active-wilayah').val();
    $.post(url, geojson, function (response) {
        // Do something with the request
    }, 'json');
};

Wilayah.load_area = function (wilayah_name) {
    $.get('/api/get_area_geojson/' + wilayah_name, function (areas) {
        Wilayah.old_areas = areas;
        Wilayah.new_areas = areas;
        var side_list = $('.side-list');
        var list_tmp = '' +
            '<div class="area-list area{{order}}"><span class="no-area">{{order}}</span>.' +
            '                <input type="text" value="{{area_name}}" id="area{{order}}name">' +
            '                <select id="area{{order}}cat">' +
            '                    <option value="hs">hs</option>' +
            '                    <option value="hmax">hmax</option>' +
            '                </select><div class="trash-button" id="area{{order}}del"><i class="fa fa-trash" aria-hidden="true"></i></div>' +
            '            </div>';
        side_list.html('');
        for (var i = 0; i < areas.features.length; i++) {
            var area_name = areas.features[i].properties.name;
            var area_category = areas.features[i].properties.category;
            var order = i + 1;
            side_list.append(list_tmp.replaceAll('{{area_name}}', area_name).replaceAll('{{order}}', order));
            $('#area' + order + 'cat').val(area_category);
            Wilayah.load_events();
        }
        // define toolbar options
        var options = {
            position: 'topleft',
            drawMarker: false,
            drawPolyline: false,
            drawRectangle: false,
            drawPolygon: true,
            drawCircle: false,
            cutPolygon: false,
            editMode: true,
            removalMode: false,
        };
        Wilayah.map.pm.addControls(options);
        Wilayah.map.layers = L.geoJSON(Wilayah.new_areas).addTo(Wilayah.map);
        var bounds = Wilayah.map.layers.getBounds();
        Wilayah.map.fitBounds(bounds);
        var center = bounds.getCenter();
        Wilayah.map.panTo(center);
        Wilayah.map.off('pm:create').on('pm:create', function (e) {
            e.shape;
            var new_layer = e.layer;
            var order = $('.side-list .area-list').length + 1;
            var area_name = 'Area ' + order;
            new_layer.feature = {type: 'Feature', properties: {name: area_name, category: "hs"}};
            new_layer.properties = {name: area_name, category: "hs"};
            Wilayah.map.layers.addLayer(new_layer);
            Wilayah.new_areas = Wilayah.map.layers.toGeoJSON();
            $('.side-list').append(list_tmp.replaceAll('{{area_name}}', area_name).replaceAll('{{order}}', order));
            Wilayah.load_events();
            Wilayah.save_geojson();
        });
        Wilayah.map.on('pm:globaleditmodetoggled', function (e) {
            Wilayah.save_geojson();
        });
    });
};

Wilayah.load_events = function () {
    $('.trash-button').off('click').click(function () {
        var remove_cl = $(this).attr('id').replace('del', '');
        var remove_el = $('.' + remove_cl);
        var idx = $('.side-list .area-list').index($(this).parent());
        remove_el.remove();
        var list = $('.side-list .area-list');
        var total = list.length;
        Wilayah.map.layers.removeLayer(Wilayah.map.layers.getLayers()[idx]);
        if (total > 0) {
            for (var i = 0; i < total; i++) {
                list[i].firstChild.innerText = i + 1;
            }
        }
        Wilayah.save_geojson();
    });
    $('.area-list').off('hover').hover(
        function () {
            var hover_idx = $('.side-list .area-list').index(this);
            var layer = Wilayah.map.layers.getLayers()[hover_idx];
            layer.setStyle({fillColor: '#fafafa'});
            console.log(layer.feature.properties.name);

        },
        function () {
            var hover_idx = $('.side-list .area-list').index(this);
            var layer = Wilayah.map.layers.getLayers()[hover_idx];
            layer.setStyle({fillColor: 'rgb(51, 136, 255)'})
        });
    $('.area-list input').off().change(function () {
        var area_name = $(this).val();
        var order = $('.side-list .area-list').index($(this).parent());
        var layer = Wilayah.map.layers.getLayers()[order];
        layer.feature.properties.name = area_name;
        Wilayah.save_geojson();
    });
    $('.area-list select').off().change(function () {
        var val = $(this).val();
        var order = $('.side-list .area-list').index($(this).parent());
        var layer = Wilayah.map.layers.getLayers()[order];
        layer.feature.properties.category = val;
        Wilayah.save_geojson();
    });
};
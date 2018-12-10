var Infomet = {};
Infomet.show = function () {
    $('#infomet-group-slide').chosen();
    Infomet.data.slide_list();
    Infomet.data.table();
    Infomet.events();
};

Infomet.getval = function () {
    return {
        name: $('#infomet-name').val(),
        url: $('#infomet-url').val(),
        lat: $('#infomet-lat').val(),
        lon: $('#infomet-lon').val(),
        slide: $('#infomet-slide').val(),
    }
};

Infomet.setval = function (obj) {
    if (obj === null) {
        $('#infomet-name').val(null);
        $('#infomet-url').val(null);
        $('#infomet-lat').val(null);
        $('#infomet-lon').val(null);
        $('#infomet-slide').val(null);
    } else {
        $('#infomet-name').val(obj.name);
        $('#infomet-url').val(obj.url);
        $('#infomet-lat').val(obj.lat);
        $('#infomet-lon').val(obj.lon);
        $('#infomet-slide').val(obj.slide);
    }
};

Infomet.data = {
    add: function () {
        var url = '/api/infomet/add';
        var form = Infomet.getval();
        for (var key in form) {
            if (form.keys === '') {
                $.notify('Mohon untuk melengkapi ' + key, 'error');
                return false;
            }
        }
        $.post(url, {'json': JSON.stringify(form)}, function (msg) {
            $.notify(msg.message, msg.type);
            Infomet.setval(null);
            Infomet.data.table();
        });
    },
    detail: function (name) {
        var url = '/api/infomet/detail/' + name;
        $.get(url, function (data) {
            Infomet.setval(data);
        })
    },
    table: function () {
        var url = '/api/infomet/table_list';
        $.get(url, function (datas) {
            var table = $('#table-infomet');
            table.html('');
            var head = '<tr><th>No.</th><th>Nama</th><th>URL</th><th>Latitude</th><th>Longitude</th><th>Slide</th></tr>';
            var row = '<tr><td>{no}</td><td><span class="hlink infomet-link">{name}</span></td><td><a href="/infomet/{url}">/infomet/{url}</a></td><td>{lat}</td><td>{lon}</td><td>{slide}</td></tr>';
            table.append(head);
            for (var i = 0; i < datas.length; i++) {
                var new_row = row
                    .replaceAll('{no}', i + 1)
                    .replaceAll('{name}', datas[i].name)
                    .replaceAll('{url}', datas[i].url)
                    .replaceAll('{lat}', datas[i].lat)
                    .replaceAll('{lon}', datas[i].lon)
                    .replaceAll('{slide}', datas[i].slide);
                table.append(new_row)
            }
            Infomet.events();
        })
    },
    remove: function (name) {
        var url = '/api/infomet/remove/' + name;
        $.get(url, function (msg) {
            $.notify(msg.message, msg.type);
            Infomet.data.table();
        })
    },
    slide_list: function () {
        var url = '/api/infomet/slide_name';
        var select = $('#infomet-slide');
        var option = '<option value="{name}">{name}</option>';
        $.get(url, function (slides) {
            for (var i = 0; i < slides.length; i++) {
                select.append(option.replaceAll('{name}', slides[i]['name']));
                select.trigger("chosen:updated");
            }
        })
    }
};

Infomet.events = function () {
    $('#open-infomet-dialog').click(function () {
        $("#infomet-name").prop('disabled', false);
        $('#update-infomet').hide();
        $('#add-infomet').show();
        $('#remove-infomet').hide();
        $('.infomet-dialog-warp').fadeIn(500);
    });
    $('#close-infomet-dialog').click(function () {
        $('.infomet-dialog-warp').fadeOut(500);
        Infomet.setval(null);
    });
    $('#add-infomet').off('click').click(function () {
        Infomet.data.add();
        $('.infomet-dialog-warp').fadeOut(300);
    });
    $('.infomet-link').off('click').click(function () {
        $("#infomet-name").prop('disabled', true);
        $('#update-infomet').show();
        $('#add-infomet').hide();
        $('#remove-infomet').show();
        var name = $(this).html();
        $('.infomet-dialog-warp').fadeIn(300);
        Infomet.data.detail(name);
    });
    $('#update-infomet').off('click').click(function () {
        Infomet.data.add();
        $('.infomet-dialog-warp').fadeOut(300);
    });
    $('#remove-infomet').off('click').click(function () {
        var name = $('#infomet-name').val();
        Infomet.data.remove(name);
        $('.infomet-dialog-warp').fadeOut(300);
    });
};
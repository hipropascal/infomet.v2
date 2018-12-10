var Slide = {};
Slide.show = function () {
    $('.main').css({
        'height': 'auto'
    });
    $.get('/api/get_wilayah', function (list_wilayah) {
        for (var i = 0; i < list_wilayah.length; i++) {
            $('#wilayah').append('<option value="' + list_wilayah[i] + '">' + list_wilayah[i] + '</option>')
        }
        $('#wilayah').chosen();
    });
    $.get('/api/get_list_cuaca_perairan/', function (list_cuaca_perairan) {
        for (var i = 0; i < list_cuaca_perairan.length; i++) {
            $('#cuaca_perairan').append('<option value="' + list_cuaca_perairan[i]['kode'] + '">' + list_cuaca_perairan[i]['wilayah'] + '</option>')
        }
        $('#cuaca_perairan').chosen();
    });
    $.get('/api/get_list_cuaca_kota/', function (list_kota) {
        for (var i = 0; i < list_kota.length; i++) {
            $('#cuaca_kota').append('<option value="' + list_kota[i] + '">' + list_kota[i] + '</option>')
        }
        $('#cuaca_kota').chosen();
    });
    $.get('/api/get_list_cuaca_pelabuhan/', function (list_pelabuhan) {
        for (var i = 0; i < list_pelabuhan.length; i++) {
            $('#cuaca_pelabuhan').append('<option value="' + list_pelabuhan[i]['id_pelabuhan'] + '">' + list_pelabuhan[i]['nama_pelabuhan'] + '</option>')
        }
        $('#cuaca_pelabuhan').chosen();
    });
    Slide.load_table();
};

Slide.events = function () {
    $('#add-slide').off('click').click(function () {
        Slide.add()
    });
    $('#remove-slide').off('click').click(function () {
        Slide.remove()
    });
    $('#update-slide').off('click').click(function () {
        Slide.update()
    });
    $('#open-slide-dialog').off('click').click(function () {
        $('#update-slide').hide();
        $('#remove-slide').hide();
        $('#add-slide').show();
        $('#name').prop('disabled', false);
        $('.slide-dialog-warp').fadeIn(300)
    });
    $('#close-slide-dialog').off('click').click(function () {
        $('.slide-dialog-warp').fadeOut(300);
        $('select').val(null);
        $('input').val(null);
        $('.input-slide').trigger("chosen:updated");
    });
    $('.slide-link').off('click').click(function () {
        var name = $(this).html();
        $('#update-slide').show();
        $('#remove-slide').show();
        $('#add-slide').hide();
        $('#name').prop('disabled', true);
        $.get('/api/slide/detail/' + name, function (detail) {
            console.log(detail);
            $('#cuaca_kota').val(detail.cuaca_kota);
            $('#cuaca_pelabuhan').val(detail.cuaca_pelabuhan);
            $('#cuaca_perairan').val(detail.cuaca_perairan);
            $('#wilayah').val(detail.wilayah);
            $('#name').val(detail.name);
            $('.input-slide').trigger("chosen:updated");
            $('.slide-dialog-warp').fadeIn(300)
        });
    })
};

Slide.add = function () {
    var name = $('#name').val();
    if(name === ''){
        $.notify('Silahkan isi nama slide','Error');
        return true
    }
    var wilayah = $('#wilayah').val();
    var cuaca_perairan = $('#cuaca_perairan').val();
    var cuaca_kota = $('#cuaca_kota').val();
    var cuaca_pelabuhan = $('#cuaca_pelabuhan').val();
    var new_slide_option = {
        'name': name,
        'wilayah': wilayah,
        'cuaca_perairan': cuaca_perairan,
        'cuaca_kota': cuaca_kota,
        'cuaca_pelabuhan': cuaca_pelabuhan
    };
    var json_post = {'json': JSON.stringify(new_slide_option)};
    console.log(json_post);
    var url = '/api/slide/add';
    $.post(url, json_post, function (response) {
        var msg = response.message;
        var type = response.type;
        $.notify(msg, type);
        $('.input-slide').val('').trigger("chosen:updated");
        $('.slide-dialog-warp').fadeOut(300);
        Slide.load_table();
    }, 'json');
};

Slide.remove = function () {
    var name = $('#name').val();
    $.get('/api/slide/remove/'+name,function (msg) {
        $.notify(msg.message,msg.type);
        $('.slide-dialog-warp').fadeOut(300);
        Slide.load_table();
    });
};

Slide.update = function () {
    Slide.add();
    Slide.load_table();
};

Slide.load_table = function () {
    $.get('/api/slide/list', function (list) {
        $('table').html('');
        var head = '' +
            '<tr>' +
            '   <th>No.</th>' +
            '   <th>Nama Grup Slide</th>' +
            '   <th>Gelombang,Arus & angin</th>' +
            '   <th>Cuaca Perairan</th>' +
            '   <th>Cuaca Pelabuhan</th>' +
            '   <th>Cuaca Kota</th>' +
            '   <th>Peta PDPI</th>' +
            '</tr>';
        $('table').append(head);
        var row_tmp = '' +
            '<tr><td>{no}</td>' +
            '<td><span class="hlink slide-link">{name}</a></td>' +
            '<td>{gelombang_arus_angin}</td>' +
            '<td>{cuaca_perairan}</td>' +
            '<td>{cuaca_pelabuhan}</td>' +
            '<td>{cuaca_kota}</td>' +
            '<td>-</td></tr>';
        for (var i = 0; i < list.length; i++) {
            var row = row_tmp.replace('{no}', i + 1)
                .replace('{name}', list[i]['name'])
                .replace('{gelombang_arus_angin}', list[i]['gelombang_arus_angin'])
                .replace('{cuaca_perairan}', list[i]['cuaca_perairan'])
                .replace('{cuaca_pelabuhan}', list[i]['cuaca_pelabuhan'])
                .replace('{cuaca_kota}', list[i]['cuaca_kota']);
            $('table').append(row);
        }
        Slide.events();
    });
};
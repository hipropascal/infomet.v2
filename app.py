from flask import Flask, render_template, jsonify, send_file, request
from src import misc, data_crawler, netcdf_mask
from pymongo import MongoClient
import threading
import schedule
import json
import time
import os

app = Flask(__name__)
db_connect = MongoClient('peta-maritim.bmkg.go.id', 27017)
db = db_connect['infomet']


# Dashboard utama
@app.route('/')
def menu_dashboard():
    return render_template('main.html')


# List menu
@app.route('/api/menu')
def get_menu_list():
    menu_files = misc.list_file('templates/menu/')
    menu_list = []
    for menu in menu_files:
        reformat = menu.split('_')[1].replace('.html', '')
        order = menu.split('_')[0]
        menu_list.append([order, reformat])
    return jsonify(menu_list)


@app.route('/page/<page>')
def get_page_menu(page):
    return send_file('templates/menu/' + page)


# API list geojson
@app.route('/api/get_wilayah/', methods=['GET', 'POST'])
def get_group_area():
    wilayah_dict = list(db['master_geojson_wilayah'].find({}, {"name": 1, "_id": 0}))
    wilayah_list = [str(arr['name']) for arr in wilayah_dict]
    return jsonify(wilayah_list)


@app.route('/api/get_list_cuaca_perairan/', methods=['GET', 'POST'])
def get_cuaca_perairan_list():
    cuaca_perairan = list(db['master_kode_perairan'].find({}, {"wilayah": 1, "kode": 1, "_id": 0}))
    return jsonify(cuaca_perairan)


@app.route('/api/get_list_cuaca_kota/', methods=['GET', 'POST'])
def get_cuaca_kota_list():
    cuaca_kota = list(db['data_cuaca_kota'].find({}, {"name": 1, "_id": 0}))
    list_kota = [str(arr['name']) for arr in cuaca_kota]
    return jsonify(list_kota)


@app.route('/api/get_list_cuaca_pelabuhan/', methods=['GET', 'POST'])
def get_cuaca_pelabuhan_list():
    cuaca_pelabuhan = list(db['master_kode_pelabuhan'].find({}, {"id_pelabuhan": 1, "nama_pelabuhan": 1, "_id": 0}))
    return jsonify(cuaca_pelabuhan)


# API list area dalam geojson
@app.route('/api/get_area_geojson/<wilayah>', methods=['GET', 'POST'])
def get_area(wilayah):
    geojson = db['master_geojson_wilayah'].find_one({'name': wilayah})['geojson']
    return jsonify(geojson)


# API untuk update area
# POST : Geojson baru yang telah di edit pada antarmuka
@app.route('/api/post_wilayah/<wilayah>', methods=['GET', 'POST'])
def post_group_area(wilayah):
    if request.method == 'POST':
        obj = request.form.to_dict()
        geojson = json.loads(obj['json'])
        db['master_geojson_wilayah'].update_one({'name': wilayah}, {'$set': {'geojson': geojson}})
        return jsonify({'messege': 'success'})


# API untuk hapus geojson
@app.route('/api/remove_wilayah/<wilayah>', methods=['GET', 'POST'])
def remove_group_area(wilayah):
    target_file = 'data/region_polygon/geojson/{}.json'.format(wilayah)
    os.remove(target_file)


# Triger to pull Inawave
@app.route('/trigger/inawave/')
def triger_inawave():
    threading.Thread(target=routine_handler).start()
    return jsonify({'messege': 'success'})


@app.route('/api/slide/list', methods=['GET', 'POST'])
def show_list_slide():
    datas = list(db['data_slide'].find({}, {'_id': 0}))
    table_list = []
    for idx, data in enumerate(datas):
        table_obj = {'name': data['name'], 'gelombang_arus_angin': data['wilayah'], 'cuaca_perairan': '',
                     'cuaca_pelabuhan': '', 'cuaca_kota': ''}
        table_obj['cuaca_kota'] = ' </br> '.join(data['cuaca_kota'])
        id_pelabuhan_list = data['cuaca_pelabuhan']
        id_perairan_list = data['cuaca_perairan']
        name_pelabuhan_col = []
        name_perairan_col = []
        for idy, id_pelabuhan in enumerate(id_pelabuhan_list):
            if id_pelabuhan != '':
                name_pelabuhan = db['master_kode_pelabuhan'].find({'id_pelabuhan': id_pelabuhan})[0]['nama_pelabuhan']
                name_pelabuhan_col.append(name_pelabuhan)
        for idy, id_perairan in enumerate(id_perairan_list):
            if id_perairan != '':
                name_perairan = db['master_kode_perairan'].find({'kode': id_perairan})[0]['wilayah']
                name_perairan_col.append(name_perairan)
        table_obj['cuaca_pelabuhan'] = ' </br> '.join(name_pelabuhan_col)
        table_obj['cuaca_perairan'] = ' </br> '.join(name_perairan_col)
        table_list.append(table_obj)
    return jsonify(table_list)


@app.route('/api/slide/detail/<name>', methods=['GET', 'POST'])
def detail_slide(name):
    data = db['data_slide'].find({'name': name}, {'_id': 0})[0]
    return jsonify(data)


@app.route('/api/slide/add', methods=['GET', 'POST'])
def add_slide():
    if request.method == 'POST':
        obj = request.form.to_dict()
        json_res = json.loads(obj['json'])
        check = list(db['data_slide'].find({'name': json_res['name']}))
        if len(check) == 0:
            db['data_slide'].insert_one(json_res)
            return jsonify({'message': 'Data "{}" ditambahkan'.format(json_res['name']), 'type': 'success'})
        else:
            db['data_slide'].update_one({'name': json_res['name']}, {'$set': json_res})
            return jsonify({'message': 'Data "{}" diperbaharui'.format(json_res['name']), 'type': 'info'})


@app.route('/api/slide/remove/<name>', methods=['GET', 'POST'])
def remove_slide(name):
    db['data_slide'].remove({'name': name})
    return jsonify({'message': 'Data "{}" dihapus'.format(name), 'type': 'info'})


@app.route('/api/infomet/add', methods=['GET', 'POST'])
def add_infomet():
    if request.method == 'POST':
        obj = request.form.to_dict()
        json_res = json.loads(obj['json'])
        check = list(db['data_infomet'].find({'name': json_res['name']}))
        if len(check) == 0:
            db['data_infomet'].insert_one(json_res)
            return jsonify({'message': 'Data "{}" ditambahkan'.format(json_res['name']), 'type': 'success'})
        else:
            db['data_infomet'].update_one({'name': json_res['name']}, {'$set': json_res})
            return jsonify({'message': 'Data "{}" diperbaharui'.format(json_res['name']), 'type': 'info'})


@app.route('/api/infomet/remove/<name>', methods=['GET', 'POST'])
def remove_infomet(name):
    db['data_infomet'].remove({'name': name})
    return jsonify({'message': 'Data "{}" dihapus'.format(name), 'type': 'info'})


@app.route('/api/infomet/table_list')
def show_table_infomet():
    datas = list(db['data_infomet'].find({}, {'_id': 0}))
    for idx, data in enumerate(datas):
        slide_name = db['data_slide'].find({'name': data['slide']})[0]['name']
        datas[idx]['slide_name'] = slide_name
    return jsonify(datas)


@app.route('/api/infomet/detail/<name>')
def show_detail_infomet(name):
    data = list(db['data_infomet'].find({'name': name}, {'_id': 0}))[0]
    return jsonify(data)


@app.route('/api/infomet/slide_name')
def show_list_name_slide():
    return jsonify(list(db['data_slide'].find({}, {'name': 1, '_id': 0})))


@app.route('/infomet/<infomet_path>')
def compile_data(infomet_path):
    infomet = db['data_infomet'].find_one({'url': infomet_path}, {'_id': 0})
    slide = db['data_slide'].find_one({'name': infomet['name']}, {'_id': 0})
    list_cuaca_perairan = []
    list_cuaca_pelabuhan = []
    list_cuaca_kota = []
    for cuaca_perairan in slide['cuaca_perairan']:
        item = db['data_cuaca_perairan'].find_one({'kode_perairan': cuaca_perairan}, {'_id': 0})
        list_cuaca_perairan.append(item)
    for cuaca_pelabuhan in slide['cuaca_pelabuhan']:
        item = db['data_cuaca_pelabuhan'].find_one({'id_pelabuhan': cuaca_pelabuhan}, {'_id': 0})
        list_cuaca_pelabuhan.append(item)
    for cuaca_kota in slide['cuaca_kota']:
        item = db['data_cuaca_kota'].find_one({'name': cuaca_kota}, {'_id': 0})
        list_cuaca_kota.append(item)
    cuaca_wilayah = db['data_cuaca_wilayah_level_model'].find_one({'name': slide['wilayah']}, {'_id': 0})
    obj = {}
    obj['infomet'] = infomet
    obj['cuaca_perairan'] = list_cuaca_perairan
    obj['cuaca_pelabuhan'] = list_cuaca_pelabuhan
    obj['cuaca_kota'] = list_cuaca_kota
    obj['cuaca_wilayah'] = cuaca_wilayah
    obj['geojson'] = db['master_geojson_wilayah'].find_one({'name': slide['wilayah']}, {'_id': 0})
    return jsonify(obj)


@app.route('/infomet/gempa')
def send_info_gempa():
    return jsonify(db['data_gempa_terkini'].find_one({}, {'_id': 0}))


def routine_handler():
    schedule.every().hour.do(routine_hourly)
    schedule.every(30).minutes.do(routine_every_30_minute)
    schedule.every(2).seconds.do(routine_every_30_seconds)
    while True:
        schedule.run_pending()
        time.sleep(1)


def routine_hourly():
    # Downloading Inawave
    # data_crawler.download_inawave()

    # Masking Inawave Data
    list_wilayah = db['master_geojson_wilayah'].find()
    netcdf_mask.inawave_mask_generator(list_wilayah)

    # Extracting value by mask area which is generated above
    list_wilayah = db['master_geojson_wilayah'].find()
    db_wilayah_inawave = db['data_cuaca_wilayah_level_model']
    db_wilayah_inawave.drop()
    netcdf_mask.extract_val_by_masking_area(list_wilayah, db_wilayah_inawave)


def routine_every_30_minute():
    # Downloading city weather
    obj_list_cuaca_kota = data_crawler.download_cuaca_kota()
    db['data_cuaca_kota'].drop()
    db['data_cuaca_kota'].insert_many(obj_list_cuaca_kota)

    # Downloading water area weather
    list_cuaca_perairan = db['master_kode_perairan'].find()
    obj_list_cuaca_perairan = data_crawler.download_cuaca_perairan(list(list_cuaca_perairan))
    db['data_cuaca_perairan'].drop()
    db['data_cuaca_perairan'].insert_many(obj_list_cuaca_perairan)

    # Downloading port weather
    list_pelabuhan = list(db['master_kode_pelabuhan'].find({}, {'_id': 0, 'data': 1}))[0]['data']
    obj_list_cuaca_pelabuhan = data_crawler.download_cuaca_pelabuhan(list_pelabuhan)
    db['data_cuaca_pelabuhan'].drop()
    db['data_cuaca_pelabuhan'].insert_many(obj_list_cuaca_pelabuhan)


def routine_every_30_seconds():
    # Downloading earthquake data
    data = data_crawler.download_gempa()
    db['data_gempa_terkini'].drop()
    db['data_gempa_terkini'].insert_one(data['Infogempa']['gempa'])


def broadcast_info():
    print 'broadcast'


if __name__ == '__main__':
    # test
    # routine_hourly()
    routine_every_30_seconds()
    # end test
    # threading.Thread(target=routine_handler).start()
    app.run(host='0.0.0.0', port=8182, debug=True)

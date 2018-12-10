from pymongo import MongoClient
from os import listdir
import json
from os.path import isfile, join
from pymongo import MongoClient
from collections import Counter
db_connect = MongoClient('peta-maritim.bmkg.go.id', 27017)
db = db_connect['infomet']

def list_file(path):
    return [f for f in listdir(path) if isfile(join(path, f))]


def put_wilayah_geojson():
    client = MongoClient('peta-maritim.bmkg.go.id', 27017)
    # client.admin.authenticate('infomet', 'infomet@bmkg', mechanism = 'SCRAM-SHA-1', source='source_database')
    db = client['infomet']
    wilayah = db['master_geojson_wilayah']
    path = '../../data/region_polygon/'
    for file in list_file(path):
        with open(path + file) as f:
            geos = json.load(f)
        name = file.replace('.json', '')
        total = wilayah.find({'name': name}).count()
        if total == 0:
            wilayah.insert({'name': name, 'geojson': geos})
    client.close()


def put_cuaca_perairan_kode():
    client = MongoClient('peta-maritim.bmkg.go.id', 27017)
    db = client['infomet']
    cuaca_perairan = db['master_kode_perairan']
    cuaca_perairan.drop()
    path = '../../doc/master_kode_perairan.json'
    with open(path) as f:
        datas = json.load(f)
        for data in datas:
            total = cuaca_perairan.find({'kode': data['kode']}).count()
            if total == 0:
                cuaca_perairan.insert(data)


def put_pelabuhan_kode():
    client = MongoClient('peta-maritim.bmkg.go.id', 27017)
    db = client['infomet']
    obj_list = []
    with open('../../doc/master_kode_pelabuhan.csv', 'r') as f:
        file = f.read().split('\n')
    for line in file:
        data = line.split(',')
        if len(data) > 1:
            if data[7] == '1':
                obj = {'id_pelabuhan': data[0], 'nama_pelabuhan': data[1]}
                obj['station'] = data[3]
                obj_list.append(obj)
    db['master_kode_pelabuhan'].drop()
    db['master_kode_pelabuhan'].insert_many(obj_list)


if __name__ == '__main__':
    # put_wilayah_geojson()
    # put_cuaca_perairan_kode()
    put_pelabuhan_kode()

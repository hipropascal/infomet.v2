import urllib2
import xmltodict
import json


def download(url):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'application/xml',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    req = urllib2.Request(url, headers=hdr)
    try:
        return urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        return e.fp.read()


def download_inawave():
    username = 'renderofs'
    password = 'render2303'
    baseurl = 'http://peta-maritim.bmkg.go.id'
    files = ['data/raster_netcdf/inawave/wib.nc', 'data/raster_netcdf/inawave/wita.nc',
             'data/raster_netcdf/inawave/wit.nc']
    urls = ['/render/netcdf/infomet/inawave_wib.nc', '/render/netcdf/infomet/inawave_wita.nc',
            '/render/netcdf/infomet/inawave_wit.nc']
    manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, baseurl, username, password)
    auth = urllib2.HTTPBasicAuthHandler(manager)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)
    for i, url in enumerate(urls):
        response = urllib2.urlopen(baseurl + url)
        with open(files[i], 'wb') as local:
            local.write(response.read())


def download_cuaca_perairan(list_cuaca_perairan):
    days = ['hari_ini', 'besok']
    cuaca_perairan_obj = []
    for cuaca_perairan in list_cuaca_perairan:
        for day in days:
            url = 'http://maritim.bmkg.go.id/xml/wilayah_pelayanan/prakiraan_by_kode?kode={}&kategori={}'.format(
                cuaca_perairan['kode'], day)
            print(url)
            try:
                xml_res = urllib2.urlopen(url)
            except urllib2.HTTPError, e:
                print e.fp.read()
                continue
            xml_load = xml_res.read()
            dict = json.dumps(xmltodict.parse(xml_load))
            json_obj = json.loads(dict)['xml']['item']
            cuaca_perairan_obj.append(json_obj)
    return cuaca_perairan_obj


def download_gempa():
    url = 'http://data.bmkg.go.id/autogempa.xml'
    path = 'data/earthquake/earthquake.json'
    xml_res = urllib2.urlopen(url)
    xml_load = xmltodict.parse(xml_res.read())
    dict_json = json.loads(json.dumps(xml_load))
    return dict_json


def download_cuaca_kota():
    list_cuaca_kota = ['http://data.bmkg.go.id/datamkg/MEWS/DigitalForecast/DigitalForecast-JawaBarat.xml',
                       'http://data.bmkg.go.id/datamkg/MEWS/DigitalForecast/DigitalForecast-JawaTengah.xml',
                       'http://data.bmkg.go.id/datamkg/MEWS/DigitalForecast/DigitalForecast-JawaTimur.xml',
                       'http://data.bmkg.go.id/datamkg/MEWS/DigitalForecast/DigitalForecast-SulawesiSelatan.xml',
                       'http://data.bmkg.go.id/datamkg/MEWS/DigitalForecast/DigitalForecast-Banten.xml',
                       'http://data.bmkg.go.id/datamkg/MEWS/DigitalForecast/DigitalForecast-DIYogyakarta.xml',
                       'http://data.bmkg.go.id/datamkg/MEWS/DigitalForecast/DigitalForecast-DKIJakarta.xml'
                       ]
    compile_cuaca_kota = []
    for cuaca_kota in list_cuaca_kota:
        print cuaca_kota
        xml_res = urllib2.urlopen(cuaca_kota)
        xml_load = xmltodict.parse(xml_res.read())
        dict_list = json.loads(json.dumps(xml_load))[u'data'][u'forecast'][u'area']
        for city in dict_list:
            cuaca_kota_obj = {'name': '', 'times': [], 'humidity': [], 'temperature': [], 'weather': [],
                              'wind_speed': [], 'wind_direction': []}
            cuaca_kota_obj['name'] = str(city[u'@description'])
            print city[u'@description']
            if city[u'@description'] == 'Pelabuhan Ratu':
                print 'debug'
            try:
                parameters = city[u'parameter']
            except:
                'Error : Parameter doesnt exsist'
                continue
            for parameter in parameters:
                if parameter[u'@description'] == u'Humidity':
                    for item in parameter[u'timerange']:
                        cuaca_kota_obj['humidity'].append(int(item[u'value'][u'#text']))
                        cuaca_kota_obj['times'].append(int(item[u'@datetime']))
                if parameter[u'@description'] == u'Temperature':
                    for item in parameter[u'timerange']:
                        cuaca_kota_obj['temperature'].append(int(item[u'value'][0][u'#text']))
                if parameter[u'@description'] == u'Weather':
                    for item in parameter[u'timerange']:
                        cuaca_kota_obj['weather'].append(int(item[u'value'][u'#text']))
                if parameter[u'@description'] == u'Wind direction':
                    for item in parameter[u'timerange']:
                        cuaca_kota_obj['wind_direction'].append(float(item[u'value'][0][u'#text']))
                if parameter[u'@description'] == u'Wind speed':
                    for item in parameter[u'timerange']:
                        cuaca_kota_obj['wind_speed'].append(float(item[u'value'][0][u'#text']))
            compile_cuaca_kota.append(cuaca_kota_obj)
    return compile_cuaca_kota


def download_cuaca_pelabuhan(list_pelabuhan):
    cuaca_pelabuhan = []
    url_pel_utama = 'http://maritim.bmkg.go.id/xml/pelabuhan_utama?stasiun={}&format=json'
    url_pel_laut = 'http://maritim.bmkg.go.id/xml/pelabuhan_laut?stasiun={}&format=json'
    for stasiun in list_pelabuhan:
        pel_laut_is_exsist = 0
        json_load_laut = []
        try:
            json_res_laut = urllib2.urlopen(url_pel_laut.format(stasiun))
            json_str_laut = json_res_laut.read()
            json_load_laut = json.loads(json_str_laut)
            pel_laut_is_exsist = 1
            print len(json_load_laut)
        except:
            print 'Error'
            pel_laut_is_exsist = 0
        try:
            json_res_utama = urllib2.urlopen(url_pel_utama.format(stasiun))
            json_str_utama = json_res_utama.read()
            json_load_utama = json.loads(json_str_utama)
            if pel_laut_is_exsist == 0:
                json_load_laut = [json_load_utama]
            else:
                json_load_laut.append(json_load_utama)
        except:
            print 'Error'
            continue
        if len(json_load_laut) != 0:
            cuaca_pelabuhan = cuaca_pelabuhan + json_load_laut
        print 'done'
    return cuaca_pelabuhan

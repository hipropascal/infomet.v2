from netCDF4 import Dataset, num2date
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from src import misc
import numpy as np
import datetime
import geojson
import math
import json
from datetime import datetime
import os


def get_wave_range(wave_arr):
    new_arr = np.copy(wave_arr).flatten()
    new_arr = new_arr[(new_arr >= 0) & (new_arr <= 14)]
    gradients = [0.1, 0.5, 1.25, 2.5, 4.0, 6.0, 9.0, 14]
    desc = ['Tenang', 'Rendah', 'Sedang', 'Tinggi', 'Sangat Tinggi', 'Ekstrem', 'Sangat Ekstrem']
    count = []
    for idx, gradient in enumerate(gradients):
        if idx + 1 == len(gradients):
            break
        freq = new_arr[(new_arr >= gradient) & (new_arr <= gradients[idx + 1])].shape[0]
        count.append(int(freq))
    range_from = gradients[count.index(max(count))]
    range_to = gradients[count.index(max(count)) + 1]
    condition = desc[count.index(max(count))]
    return [range_from, range_to, condition]


def get_wind_range(wind_arr):
    new_arr = np.copy(wind_arr).flatten()
    new_arr = new_arr[(new_arr >= 0) & (new_arr <= 60)]
    gradients = [0, 2, 4, 6, 8, 10, 15, 20, 25, 30, 35, 40, 50, 60]  # knot
    count = []
    for idx, gradient in enumerate(gradients):
        if idx + 1 == len(gradients):
            break
        freq = new_arr[(new_arr >= gradient) & (new_arr <= gradients[idx + 1])].shape[0]
        count.append(int(freq))
    range_from = gradients[count.index(max(count))]
    range_to = gradients[count.index(max(count)) + 1]
    return [range_from, range_to]


def get_dir(dir_arr):
    new_arr = np.copy(dir_arr).flatten()
    new_arr = new_arr[(new_arr >= -360) & (new_arr <= 360)]
    gradients = [-360, -337.5, -292.5, -247.5, -202.5, -157.5, -112.5, -67.5, -22.5, 0, 22.5, 67.5, 112.5, 157.5, 202.5,
                 247.5,
                 292.5, 337.5, 360]
    desc = ['Utara', 'Timur laut', 'Timur', 'Tenggara', 'Selatan', 'Barat daya', 'Barat', 'Barat Laut', 'Utara',
            'Timur laut', 'Timur', 'Tenggara', 'Selatan', 'Barat daya', 'Barat', 'Barat Laut', 'Utara']
    count = []
    for idx, gradient in enumerate(gradients):
        if idx + 1 == len(gradients):
            break
        freq = new_arr[(new_arr >= gradient) & (new_arr <= gradients[idx + 1])].shape[0]
        count.append(int(freq))
    dir_desc = desc[count.index(max(count))]
    # dir_val = int(np.nanmean(dir_arr))
    dir_val = gradients[count.index(max(count))]
    return [dir_desc, dir_val]


def inawave_mask_generator(list_wilayah):
    target_folder = 'data/raster_netcdf/masks/inawave/'
    # Boundingbox of file (In NETCDF File)
    lat_0, lat_1, lon_0, lon_1 = 15.0, -15.0, 90, 145
    # Height an width of dataset
    w, h = 881, 481
    interval = 0.0625
    for wilayah in list_wilayah:
        im = Image.new('RGBA', (w, h))
        draw = ImageDraw.Draw(im)
        lats = np.arange(lat_0, lat_1, -interval)
        lons = np.arange(lon_0, lon_1, interval)
        for idx, feature in enumerate(wilayah['geojson']['features']):
            poly = []
            coor_poly = feature['geometry']['coordinates'][0]
            for coor in coor_poly:
                x = find_nearest(lons[:], coor[0])
                y = find_nearest(lats[:], coor[1])
                poly.append((x, y))
            draw.polygon(poly, (idx + 1, idx + 1, idx + 1, 255), (idx + 1, idx + 1, idx + 1, 255))
        im.save(target_folder + '/' + wilayah['name'] + '.png', 'PNG')


def masktoarr(path):
    im = Image.open(path)
    im2arr = np.array(im)
    arrseg = im2arr[:, :, 0]
    return arrseg


def find_nearest(array, value):
    array = np.asarray(array)
    armin = np.abs(array - value)
    idx = armin.argmin()
    return idx


def plot2d(H):
    plt.imshow(H)
    plt.colorbar(orientation='vertical')
    plt.show()


def get_dataset_from_inawave_nc():
    dset_collection = {}
    datas = ['wib', 'wit', 'wita']
    for data in datas:
        path = os.path.abspath('data/raster_netcdf/inawave/{}.nc'.format(data))
        dset = Dataset(path, 'r', format='NETCDF4')
        times = num2date(dset['time'][:-1], units=dset['time'].units).tolist()
        time_str = [time.strftime('%m-%d-%Y-%H') for time in times]
        hs = dset['hs'][:-1].filled()
        hmax = dset['hmax'][:-1].filled()
        uwnd = dset['uwnd'][:-1].filled()
        vwnd = dset['vwnd'][:-1].filled()
        spdwnd = np.sqrt((uwnd * uwnd) + (vwnd * vwnd))
        dirwnd = np.arctan2(uwnd, vwnd) * 180 / math.pi
        dirwave = dset['dir'][:-1].filled()
        dset_collection[data] = {'times': time_str, 'hs': hs, 'hmax': hmax, 'uwnd': uwnd, 'vwnd': vwnd,
                                 'spdwnd': spdwnd,
                                 'dirwnd': dirwnd, 'dirwave': dirwave}
        dset.close()
    return dset_collection


def extract_val_by_masking_area(list_wilayah, db_wilayah_inawave):
    mask_folder = 'data/raster_netcdf/masks/inawave/'
    dset = get_dataset_from_inawave_nc()
    for wilayah in list_wilayah:
        name_wilayah = wilayah['name']
        times = dset['wib']['times']
        obj_wilayah = {'name': name_wilayah, 'time_zone': 'wib', 'times': [], 'areas': [], 'baserun': times[0]}
        mask = mask_folder + wilayah['name'] + '.png'
        arr = masktoarr(mask)
        obj_wilayah['times'] = times
        for idx, area in enumerate(wilayah['geojson']['features']):
            obj_area = {'wvh_range': [], 'spdwnd_range': [], 'dirwnd': [], 'dirwave': []}
            masker = arr != int(idx + 1)
            if area['properties']['category'] == 'hs':
                hs_over_time = dset['wib']['hs']
                for hs in hs_over_time:
                    hs_masked = np.ma.array(hs, mask=masker)
                    obj_area['wvh_range'].append(get_wave_range(hs_masked))
            elif area['properties']['category'] == 'hmax':
                hmax_over_time = dset['wib']['hs']
                for hmax in hmax_over_time:
                    hmax_masked = np.ma.array(hmax, mask=masker)
                    obj_area['wvh_range'].append(get_wave_range(hmax_masked))
            # extract wind speed
            spdwnd_over_time = dset['wib']['spdwnd']
            for spdwnd in spdwnd_over_time:
                spdwnd_masked = np.ma.array(spdwnd, mask=masker)
                obj_area['spdwnd_range'].append(get_wind_range(spdwnd_masked))
            # extract wind direction
            dirwnd_over_time = dset['wib']['dirwnd']
            for dirwnd in dirwnd_over_time:
                dirwnd_masked = np.ma.array(dirwnd, mask=masker)
                obj_area['dirwnd'].append(get_dir(dirwnd_masked))
            dirwave_over_time = dset['wib']['dirwave']
            for dirwave in dirwave_over_time:
                dirwave_masked = np.ma.array(dirwave, mask=masker)
                obj_area['dirwave'].append(get_dir(dirwave_masked))
            obj_wilayah['areas'].append({'name': area['properties']['name'], 'values': obj_area})
        with open('confirm/inawave/{}'.format(wilayah['name'] + '.json'), 'w') as fp:
            json.dump(obj_wilayah, fp, indent=4)
        db_wilayah_inawave.insert(obj_wilayah)


if __name__ == '__main__':
    extract_val_by_masking_area()
#     # generate()

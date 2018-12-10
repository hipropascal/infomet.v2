from netCDF4 import Dataset, date2num, num2date
import numpy as np
import urllib2
from datetime import timedelta


def get_local(path_src, target_folder):
    nc = Dataset(path_src, 'r')
    to_local(nc, 'wib', target_folder)
    to_local(nc, 'wita', target_folder)
    to_local(nc, 'wit', target_folder)


def to_local(nc, type, target_folder):
    local = {'wib': 7, 'wita': 8, 'wit': 9}
    gmt = local[type]
    timunit = nc['time'].units
    time = nc['time'][:]
    lat = nc['lat'][:]
    lon = nc['lon'][:]
    hs = nc['hs'][:]
    hmax = nc['hmax'][:]
    dir = nc['dir'][:]
    uwnd = nc['uwnd'][:]
    vwnd = nc['vwnd'][:]
    # Prepare container
    h1 = np.arange(time[0], time[-1], ((time[1] - time[0]) / 3))  # change from 3h into 1h
    h1_times = num2date(h1, timunit, 'standard')
    hs_h1 = interp_1h(hs, h1)
    hmax_h1 = interp_1h(hmax, h1)
    dir_h1 = interp_1h(dir, h1)
    uwnd_h1 = interp_1h(uwnd, h1)
    vwnd_h1 = interp_1h(vwnd, h1)
    hs_lcl, tgmt = to_gmt(gmt, h1_times, hs_h1)
    hmax_lcl, tgmt = to_gmt(gmt, h1_times, hmax_h1)
    dir_lcl, tgmt = to_gmt(gmt, h1_times, dir_h1)
    uwnd_lcl, tgmt = to_gmt(gmt, h1_times, uwnd_h1)
    vwnd_lcl, tgmt = to_gmt(gmt, h1_times, vwnd_h1)
    tgmt = date2num(tgmt, timunit, 'standard')
    nc_lcl = Dataset(target_folder + '{}.nc'.format(type), 'w')
    time_d_lcl = nc_lcl.createDimension("time", None)
    lat_d_lcl = nc_lcl.createDimension("lat", lat.shape[0])
    lon_d_lcl = nc_lcl.createDimension("lon", lon.shape[0])
    time_v_lcl = nc_lcl.createVariable("time", "f8", ("time",))
    lat_v_lcl = nc_lcl.createVariable("lat", "f4", ("lat",))
    lon_v_lcl = nc_lcl.createVariable("lon", "f4", ("lon",))
    lat_v_lcl[:] = lat
    lon_v_lcl[:] = lon
    time_v_lcl.units = timunit
    time_v_lcl[:] = tgmt
    hs_v_lcl = nc_lcl.createVariable("hs", "f4", ("time", "lat", "lon",), zlib=True, least_significant_digit=2)
    hmax_v_lcl = nc_lcl.createVariable("hmax", "f4", ("time", "lat", "lon",), zlib=True, least_significant_digit=2)
    dir_v_lcl = nc_lcl.createVariable("dir", "f4", ("time", "lat", "lon",), zlib=True, least_significant_digit=1)
    uwnd_v_lcl = nc_lcl.createVariable("uwnd", "f4", ("time", "lat", "lon",), zlib=True, least_significant_digit=2)
    vwnd_v_lcl = nc_lcl.createVariable("vwnd", "f4", ("time", "lat", "lon",), zlib=True, least_significant_digit=2)
    hs_v_lcl[:] = hs_lcl
    hmax_v_lcl[:] = hmax_lcl
    dir_v_lcl[:] = dir_lcl
    uwnd_v_lcl[:] = uwnd_lcl
    vwnd_v_lcl[:] = vwnd_lcl
    nc_lcl.close()


def interp_1h(data, time_after):
    new_data = []
    for i, t in enumerate(time_after):
        c = i % 3
        if c == 0:
            new_data.append(data[i / 3][:])
        elif c == 1:
            bottom = data[i // 3][:] * 2
            top = data[i // 3 + 1][:] * 1
            new_data.append((bottom + top) / 3)
        elif c == 2:
            bottom = data[i // 3][:] * 1
            top = data[i // 3 + 1][:] * 2
            new_data.append((bottom + top) / 3)
    return new_data

# TODO: Referensi times rubah pada posisi GMT
def to_gmt(gmt, times, dset):
    range_time = []
    t_gmt_li = []
    for time in times:
        t_gmt = (time + timedelta(hours=gmt))
        t_gmt_li.append(t_gmt)
        h_gmt = t_gmt.hour
        if h_gmt in range(0, 6):
            range_time.append(0)
        elif h_gmt in range(6, 12):
            range_time.append(6)
        elif h_gmt in range(12, 18):
            range_time.append(12)
        elif h_gmt in range(18, 24):
            range_time.append(18)
        time_group = []
    avg = []
    avth = []
    avh = []
    for i, rg in enumerate(range_time):
        if i == 0:
            avg.append(i)
            date_start = t_gmt_li[i].replace(hour=rg)
            avh.append(date_start)
            continue
        if rg == range_time[i - 1]:
            continue
        else:
            avg.append(i)
            avth.append(avg)
            date_start = t_gmt_li[i].replace(hour=rg)
            avh.append(date_start)
            avg = [i]
    dset_arr = []

    for ravg in avth:
        avg_dset = np.nanmean(dset[ravg[0]:ravg[1]], axis=0)
        dset_arr.append(avg_dset)
    return np.asarray(dset_arr), avh


if __name__ == '__main__':
    #get_local('C:\\Users\\Lenovo\\Desktop\\PROJECT\\infomet_nelayan2\\infomet_nelayan\\data\\raw_netcdf\\hires_20181208_0000.nc','C:\\Users\\Lenovo\\Desktop\\PROJECT\\infomet_nelayan2\\infomet_nelayan\\data\\raster_netcdf\\inawave\\')
    '''

    python <space> extract_netcdf_by_timezone.py <space> inawave_netcdf <space> target_folder
    
    path_src = '/Users/maritim/Project/BMKG/infomet_nelayan/data/raw_netcdf/inawave.nc'
    target_folder = '/Users/maritim/Project/BMKG/infomet_nelayan/data/raw_netcdf/'

    '''
    # import sys
    #
    # path_src = sys.argv[1]
    # target_folder = sys.argv[2]
    # get_local(path_src, target_folder)
    # #urllib2.urlopen('http://127.0.0.1:8182/trigger/inawave/')
    # urllib2.urlopen('http://peta-maritim.bmkg.go.id/infomet/trigger/inawave')

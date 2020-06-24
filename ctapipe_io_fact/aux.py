from astropy.table import Table
from astropy.time import Time
from fact.path import tree_path
from functools import lru_cache
from datetime import timedelta
import numpy as np
from sortedcontainers import SortedDict


class AUXService:

    def __init__(self, aux_path='/fact/aux'):
        self.aux_path = aux_path

    def get_aux_point(self, time):
        if time.datetime.hour < 12:
            dt = time.datetime - timedelta(days=1)
        else:
            dt = time.datetime

        night = int('{:%Y%m%d}'.format(dt))

        tracking = self.get_auxfile_data(night, 'DRIVE_CONTROL_TRACKING_POSITION')
        source = self.get_auxfile_data(night, 'DRIVE_CONTROL_SOURCE_POSITION')

        tracking_point = self.find_closest(time, tracking)
        source_point = self.find_earlier(time, source)

        return tracking_point, source_point

    @lru_cache()
    def get_auxfile_data(self, night, auxfile):
        data = Table.read(self.get_auxfile_path(night, auxfile))
        unix_time = np.array(data['Time']) * 24 * 3600
        data['Time'] = Time(unix_time, format='unix')
        sorted_dict = SortedDict(zip(data['Time'].unix, data))
        return sorted_dict

    @staticmethod
    def find_closest(time, data):
        unix_time = time.unix
        idx = data.bisect_left(unix_time)

        if idx == 0:
            return data[data.iloc[0]]

        if idx == len(data):
            return data[data.iloc[-1]]

        left = data.iloc[idx - 1]
        right = data.iloc[idx]

        left_diff = abs(unix_time - left)
        right_diff = abs(unix_time - right)

        if left_diff < right_diff:
            return data[left]

        return data[right]

    @staticmethod
    def find_earlier(time, data):
        idx = data.bisect_left(time.unix)
        if idx == 0:
            raise KeyError('Could not find an earlier timestamp in the aux file')
        return data[data.iloc[idx - 1]]

    def get_auxfile_path(self, night, auxfile):
        return tree_path(
            night,
            run=None,
            prefix=self.aux_path,
            suffix='.{}.fits'.format(auxfile)
        )

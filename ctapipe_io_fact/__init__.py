# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
EventSource for FACT fits-files.
"""

import numpy as np
import glob
from astropy import units as u
from ctapipe.instrument import (
    TelescopeDescription,
    SubarrayDescription,
    CameraGeometry,
    OpticsDescription,
)
from ctapipe.io import EventSource
from ctapipe.core import Provenance
from astropy.io import fits
from .containers import FACTDataContainer


__all__ = ['FACTEventSource']


class FACTEventSource(EventSource):
    """
    EventSource for FACT DL1 data
    """

    def __init__(self, config=None, tool=None, **kwargs):
        """
        Constructor
        Parameters
        ----------
        """

        if 'input_url' in kwargs.keys():
            self.file_list = glob.glob(kwargs['input_url'])
            self.file_list.sort()
            kwargs['input_url'] = self.file_list[0]
            super().__init__(config=config, tool=tool, **kwargs)
        else:
            super().__init__(config=config, tool=tool, **kwargs)
            self.file_list = [self.input_url]

        self.multi_file = MultiFiles(self.file_list)

        self.camera_config = self.multi_file.camera_config
        self.log.info(
            "Read {} input files".format(self.multi_file.num_inputs())
        )

    def rewind(self):
        self.multi_file.rewind()

    def _generator(self):
        something = True
        yield something

    @staticmethod
    def is_compatible(file_path):
        return True or False

    def fill_fact_service_container_from_fits_file(self):
        pass

    def fill_fact_event_container_from_fits_file(self, event):
        pass

    def fill_dl1_camera_container_from_fits_file(self, dl1_container, event):
        pass

    def fill_dl1_container_from_fits_file(self, event):
        pass

    def fill_mon_container_from_fits_file(self, event):
        pass


class MultiFiles:

    """
    This class open all the files in file_list and read the events following
    the event_id order
    """

    def __init__(self, file_list):

        self._file = {}
        self._events = {}
        self._events_table = {}
        self._camera_config = {}
        self.camera_config = None

        paths = []
        for file_name in file_list:
            paths.append(file_name)
            Provenance().add_input_file(file_name, role='r0.sub.evt')

        # open the files and get the first fits Tables
        from protozfits import File

        for path in paths:

            try:
                self._file[path] = File(path)
                self._events_table[path] = File(path).Events
                self._events[path] = next(self._file[path].Events)

                # verify where the CameraConfig is present
                if 'CameraConfig' in self._file[path].__dict__.keys():
                    self._camera_config[path] = next(
                        self._file[path].CameraConfig
                    )

                    # for the moment it takes the first CameraConfig it finds (to be changed)
                    if self.camera_config is None:
                        self.camera_config = self._camera_config[path]

            except StopIteration:
                pass

        # verify that somewhere the CameraConfing is present
        assert self.camera_config

    def __iter__(self):
        return self

    def __next__(self):
        return self.next_event()

    def next_event(self):
        # check for the minimal event id
        if not self._events:
            raise StopIteration

        min_path = min(
            self._events.items(), key=lambda item: item[1].event_id
        )[0]

        # return the minimal event id
        next_event = self._events[min_path]
        try:
            self._events[min_path] = next(self._file[min_path].Events)
        except StopIteration:
            del self._events[min_path]

        return next_event

    def __len__(self):
        total_length = sum(len(table) for table in self._events_table.values())
        return total_length

    def num_inputs(self):
        return len(self._file)

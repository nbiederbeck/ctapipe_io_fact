"""EventSource for FACT fits-files."""

import numpy as np
from astropy import units as u
from astropy.io import fits
from astropy.time import Time
from ctapipe.io import EventSource
from ctapipe.io.containers import (
    DataContainer,
    DL1CameraContainer,
    TelescopePointingContainer,
)


__all__ = ["FACTDL1EventSource"]


class FACTDL1EventSource(EventSource):

    """EventSource for FACT DL1 data."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.hdulist = fits.open(self.input_url)
        self.events = self.hdulist["Events"].data
        self.header = self.hdulist["Events"].header
        self.metadata["is_simulation"] = "timestamp" not in list(self.header.values())

    def __len__(self):
        return len(self.events)

    def _generator(self):
        for i in range(self.header["NAXIS2"]):
            event_data = self.events[i]
            event = DataContainer(count=i)
            yield self._fill_container(container=event, data=event_data)

    def __getitem__(self, idx):
        index, = np.where(self.events["event_num"] == idx)
        try:
            event_data = self.events[index[0]]
        except IndexError:
            raise IndexError(f"event_num {idx} not in data {self.input_url}")
        event = DataContainer(count=idx)
        return self._fill_container(container=event, data=event_data)

    def _fill_container(self, container, data):
        """Fill container with data from files. Used for both __getitem__ and _generator."""
        event = container
        event_data = data

        for level in ("r0", "r1", "dl0"):
            event[level].obs_id = self.header["NIGHT"] * 1000 + self.header["RUNID"]
            event[level].event_id = event_data["event_num"]
            event[level].tels_with_data = [1]

        if self.metadata["is_simulation"]:
            event.mc.energy = u.Quantity(
                event_data["corsika_event_header_total_energy"], u.GeV
            )
            event.mc.core_x = u.Quantity(event_data["corsika_event_header_x"], u.cm)
            event.mc.core_y = u.Quantity(event_data["corsika_event_header_y"], u.cm)
            event.mc.h_first_int = u.Quantity(
                event_data["corsika_event_header_first_interaction_height"]
            )
            # event.mc.xmax = u.Quantity(, u.g / u.cm ** 2)
            event.mc.shower_primary_id = 0
            event.mc.alt = u.Quantity(90 - event_data["source_position_zd"], u.deg)
            event.mc.az = u.Quantity(event_data["source_position_az"], u.deg)
            event.mc.tel[1] = DL1CameraContainer(
                image=event_data["photoncharge"], pulse_time=event_data["arrival_time"]
            )
        else:
            event.trig.gps_time = Time(event_data["timestamp"], scale="utc")
            event.dl0.tel[1].trigger_time = Time(event_data["timestamp"], scale="utc")

            event.dl1.tel[1] = DL1CameraContainer(
                image=event_data["photoncharge"], pulse_time=event_data["arrival_time"]
            )

        event.pointing = TelescopePointingContainer(
            azimuth=u.Quantity(event_data["pointing_position_az"], u.deg),
            altitude=u.Quantity(90 - event_data["pointing_position_zd"], u.deg),
        )

        return event

    @classmethod
    def is_compatible(cls, input_url):
        try:
            f = fits.open(input_url)
        except IOError:
            return False

        if f[0].header["ORIGIN"] != "FACT":
            return False

        if "Events" not in f:
            return False

        columns = f["Events"].data.dtype.names
        return "photoncharge" in columns and "arrival_time" in columns

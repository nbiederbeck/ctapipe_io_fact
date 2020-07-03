"""EventSource for FACT fits-files."""

import numpy as np
from astropy import units as u
from astropy.io import fits
from astropy.time import Time
from ctapipe.io import EventSource
from ctapipe.containers import (
    DataContainer,
    EventIndexContainer,
    MCHeaderContainer,
    PointingContainer,
    DL1CameraContainer,
    TelescopePointingContainer,
)
from ctapipe.io.datalevels import DataLevel
from ctapipe.instrument import SubarrayDescription, TelescopeDescription


__all__ = ["FACTDL1EventSource", "FACTDL2EventSource"]

SUBARRAY = SubarrayDescription(
    name='FACT',
    tel_positions={1: u.Quantity([-60.32, -45.08, 50.00], unit=u.m)},
    tel_descriptions={
        1: TelescopeDescription.from_name(
            camera_name="FACT",
            optics_name="SST-FACT",
        ),
    },
)


class FACTDL1EventSource(EventSource):

    """EventSource for FACT DL1 data."""

    def __init__(self, input_url, config=None, parent=None, gain_selector=None, **kwargs):
        super().__init__(input_url=input_url, config=config, parent=parent, **kwargs)

        self.hdulist = fits.open(self.input_url)
        self.events = self.hdulist["Events"].data
        self.header = self.hdulist["Events"].header
        if self.is_simulation:
            self.mc_header = self._parse_mc_header()

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

    def _parse_mc_header(self):
        return MCHeaderContainer(
            # run_array_direction=,
            # corsika_version=,
            # simtel_version=,
            # energy_range_min=,
            # energy_range_max=,
            # prod_site_B_total=,
            # prod_site_B_declination=,
            # prod_site_B_inclination=,
            # prod_site_alt=,
            # spectral_index=,
            # shower_prog_start=,
            # shower_prog_id=,
            # detector_prog_start=,
            # detector_prog_id=,
            # num_showers=,
            # shower_reuse=,
            # max_alt=,
            # min_alt=,
            # max_az=,
            # min_az=,
            # diffuse=,
            # max_viewcone_radius=,
            # min_viewcone_radius=,
            # max_scatter_range=,
            # min_scatter_range=,
            # core_pos_mode=,
            # injection_height=,
            # atmosphere=,
            # corsika_iact_options=,
            # corsika_low_E_model=,
            # corsika_high_E_model=,
            # corsika_bunchsize=,
            # corsika_wlen_min=,
            # corsika_wlen_max=,
            # corsika_low_E_detail=,
            # corsika_high_E_detail=,
        )

    def _fill_container(self, container, data):
        """Fill container with data from files. Used for both __getitem__ and _generator."""
        event = container
        event_data = data

        event.index = EventIndexContainer(obs_id=self.obs_id, event_id=event_data["eventNum"])
        # no event.r0
        # no event.r1
        # no event.dl0

        if self.is_simulation:
            event.mcheader = self.mc_header
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

        az = u.Quantity(event_data["pointing_position_az"], u.deg)
        alt = u.Quantity(90 - event_data["pointing_position_zd"], u.deg)

        event.pointing.tel[1].azimuth = az
        event.pointing.tel[1].altitude = alt
        event.pointing.array_azimuth = az
        event.pointing.array_altitude = alt

        return event

    @classmethod
    def is_compatible(cls, input_url):
        try:
            f = fits.open(input_url)
        except IOError:
            return False

        if f[1].header["ORIGIN"] != "FACT":
            return False

        if "Events" not in f:
            return False

        columns = f["Events"].data.dtype.names
        return "photoncharge" in columns and "arrival_time" in columns

    @property
    def datalevels(self):
        return (DataLevel.DL1)

    @property
    def is_simulation(self):
        return "timestamp" not in list(self.header.values())

    @property
    def obs_id(self):
        return self.header["NIGHT"] * 1000 + self.header["RUNID"]

    @property
    def subarray(self):
        return SUBARRAY

    @property
    def is_stream(self):
        return False


class FACTDL2EventSource(EventSource):

    """EventSource for FACT DL2 data."""

    def __init__(self, input_url, config=None, parent=None, gain_selector=None, **kwargs):
        super().__init__(input_url=input_url, config=config, parent=parent, **kwargs)

        self.hdulist = fits.open(self.input_url)
        self.events = self.hdulist["Events"].data
        self.header = self.hdulist["Events"].header
        if self.is_simulation:
            self.mc_header = self._parse_mc_header()

    def __len__(self):
        return len(self.events)

    def _generator(self):
        for i in range(self.header["NAXIS2"]):
            data = self.events[i]
            event = DataContainer(count=i)
            yield self._fill_container(event, data)

    def __getitem__(self, idx):
        index, = np.where(self.events["event_num"] == idx)
        try:
            data = self.events[index[0]]
        except IndexError:
            raise IndexError(f"event_num {idx} not in data {self.input_url}")
        event = DataContainer(count=idx)
        return self._fill_container(event, data)

    def _parse_mc_header(self):
        return MCHeaderContainer(
            # run_array_direction=,
            # corsika_version=,
            # simtel_version=,
            # energy_range_min=,
            # energy_range_max=,
            # prod_site_B_total=,
            # prod_site_B_declination=,
            # prod_site_B_inclination=,
            # prod_site_alt=,
            # spectral_index=,
            # shower_prog_start=,
            # shower_prog_id=,
            # detector_prog_start=,
            # detector_prog_id=,
            # num_showers=,
            # shower_reuse=,
            # max_alt=,
            # min_alt=,
            # max_az=,
            # min_az=,
            # diffuse=,
            # max_viewcone_radius=,
            # min_viewcone_radius=,
            # max_scatter_range=,
            # min_scatter_range=,
            # core_pos_mode=,
            # injection_height=,
            # atmosphere=,
            # corsika_iact_options=,
            # corsika_low_E_model=,
            # corsika_high_E_model=,
            # corsika_bunchsize=,
            # corsika_wlen_min=,
            # corsika_wlen_max=,
            # corsika_low_E_detail=,
            # corsika_high_E_detail=,
        )

    def _fill_container(self, event, data):
        """Fill container with data from files. Used for both __getitem__ and _generator."""

        event.index.obs_id = self.obs_id
        event.index.event_id = data["eventNum"]

        if self.is_simulation:
            event.mcheader = self.mc_header
            event.index.event_id = data["MCorsikaEvtHeader.fEvtNumber"]

        event.dl1.tel[1].image = np.float32(data["photoncharge"])
        event.dl1.tel[1].peak_time = np.float32(data["arrivalTime"])

        return event

    @classmethod
    def is_compatible(cls, input_url):
        try:
            f = fits.open(input_url)
        except IOError:
            return False

        if f[1].header["ORIGIN"] != "FACT":
            return False

        if f[1].header["CREATOR"] != "Ceres":
            return False

        if "Events" not in f:
            return False

        columns = f["Events"].data.dtype.names
        return "photoncharge" in columns and "arrivalTime" in columns

    @property
    def datalevels(self):
        return (DataLevel.DL1)

    @property
    def is_simulation(self):
        return "timestamp" not in list(self.header.values())

    @property
    def obs_id(self):
        return self.header["RUNID"]

    @property
    def subarray(self):
        return SUBARRAY

    @property
    def is_stream(self):
        return False

"""
EventSource for FACT fits-files.
"""

from astropy.io import fits
from ctapipe.io import EventSource
from ctapipe.containers import DataContainer, DL1CameraContainer


__all__ = ["FACTDL1EventSource"]


class FACTDL1EventSource(EventSource):
    """
    EventSource for FACT DL1 data.
    """

    def __init__(self, config=None, tool=None, **kwargs):
        super().__init__(config=config, tool=tool, **kwargs)

        self.hdulist = fits.open(self.input_url)
        self.events = self.hdulist["Events"].data
        self.header = self.hdulist["Events"].header

    def _generator(self):
        for i in range(self.header["NAXIS2"]):
            event_data = self.events[i]
            event = DataContainer(count=i)
            event.r0.obs_id = (
                self.header["NIGHT"] * 1000 + self.header["RUNID"]
            )
            event.r0.event_id = event_data["event_num"]
            event.dl1.tel[1] = DL1CameraContainer(
                image=event_data["photoncharge"],
                peakpos=event_data["arrival_time"],
            )

            yield event

    @classmethod
    def is_compatible(cls, input_url):
        try:
            f = fits.open(input_url)
            if f[0].header["ORIGIN"] != "FACT":
                return False
            if "Events" not in f:
                return False

            columns = f["Events"].data.dtype.names
            return "photoncharge" in columns and "arrival_time" in columns
        except IOError:
            return False

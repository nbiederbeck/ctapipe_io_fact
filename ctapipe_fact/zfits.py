from zfits import FactFits, ZFits
from ctapipe.io.containers import DataContainer
from ctapipe.io.eventfilereader import EventFileReader
from traitlets import Unicode
from astropy.io import fits


def fact_event_generator(inputfile, drsfile):
    fact_fits = FactFits(inputfile, drsfile)

    header = fact_fits.data_file['Events'].read_header()

    for i in range(fact_fits.data_file['Events'].get_nrows()):
        time_series = fact_fits.get_data_calibrated(i)

        event_id = fact_fits.get('EventNum', i)
        night = header['NIGHT']
        run_id = header['RUNID']

        data = DataContainer()
        data.meta['origin'] = 'FACT'

        for c in (data.r0, data.r1, data.dl0):
            c.event_id = event_id
            c.run_id = '{}_{:03d}'.format(night, run_id)
            c.tels_with_data = [0]

        data.r0.tel[0] = time_series

        yield data


class FACTEventFileReader(EventFileReader):
    drs_file_path = Unicode(
        allow_none=False, help='Path to the DRS calibration file'
    )
    origin = 'FACT'

    def __init__(self, config, tool, **kwargs):
        super().__init__(config=config, tool=tool, **kwargs)

    @staticmethod
    def check_file_compatibility(file_path):
        try:
            f = ZFits(file_path)
            return f['Events'].read_header.get('TELESCOP') == 'FACT'
        except Exception as e:
            return False

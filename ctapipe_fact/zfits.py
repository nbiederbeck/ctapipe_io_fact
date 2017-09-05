from zfits import FactFitsCalib, FactFits
from ctapipe.io.containers import DataContainer
from ctapipe.io.eventfilereader import EventFileReader
from traitlets import Unicode
from astropy.time import Time

from .instrument import FACT


def fact_event_generator(inputfile, drsfile):
    fact_fits_calib = FactFitsCalib(inputfile, drsfile)

    header = fact_fits_calib.data_file.header()

    for event in fact_fits_calib:

        event_id = event['EventNum'][0]
        night = header['NIGHT']
        run_id = header['RUNID']

        data = DataContainer()
        data.meta['origin'] = 'FACT'

        data.trig.gps_time = Time(
            event['UnixTimeUTC'][0] + event['UnixTimeUTC'][1] * 1e-6,
            scale='utc',
            format='unix',
        )
        data.trig.tels_with_trigger = [0]

        data.inst = FACT

        for c in (data.r0, data.r1, data.dl0):
            c.event_id = event_id
            c.run_id = '{}_{:03d}'.format(night, run_id)
            c.tels_with_data = [0]

        event['CalibData'][8::9, 240:300] = 0

        data.r0.tel[0].adc_samples = event['Data'].reshape(1, 1440, -1)
        data.r0.tel[0].num_samples = event['Data'].shape[1]
        data.r1.tel[0].pe_samples = event['CalibData'].reshape(1, 1440, -1) / 230
        data.dl0.tel[0].pe_samples = event['CalibData'].reshape(1, 1440, -1) / 230


        yield data


class FACTEventFileReader(EventFileReader):
    drs_file_path = Unicode(
        allow_none=False,
        help='Path to the DRS calibration file'
    )
    origin = 'FACT'

    def __init__(self, config, tool, **kwargs):
        super().__init__(config=config, tool=tool, **kwargs)

    @staticmethod
    def check_file_compatibility(file_path):
        try:
            f = FactFits(file_path)
            return f.header().get('TELESCOP') == 'FACT'
        except Exception as e:
            return False

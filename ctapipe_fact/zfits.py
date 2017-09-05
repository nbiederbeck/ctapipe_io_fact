from zfits import FactFitsCalib
from ctapipe.io.containers import DataContainer
from astropy.time import Time

from .instrument import FACT


def fact_event_generator(inputfile, drsfile, allowed_triggers=None):
    fact_fits_calib = FactFitsCalib(inputfile, drsfile)

    header = fact_fits_calib.data_file.header()

    for event in fact_fits_calib:
        print(event['EventNum'][0])
        trigger_type = event['TriggerType'][0]

        if allowed_triggers is not None:
            if trigger_type not in allowed_triggers:
                continue

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

        event['CalibData'][:, 150:300] = 0
        event['CalibData'][:, :10] = 0

        data.r0.tel[0].adc_samples = event['Data'].reshape(1, 1440, -1)
        data.r0.tel[0].num_samples = event['Data'].shape[1]
        data.r1.tel[0].pe_samples = event['CalibData'].reshape(1, 1440, -1) / 230
        data.dl0.tel[0].pe_samples = event['CalibData'].reshape(1, 1440, -1) / 230

        yield data

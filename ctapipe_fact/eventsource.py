from zfits import FactFitsCalib
from ctapipe.io.containers import DataContainer
from astropy.time import Time
import astropy.units as u
from fact.instrument.camera import reorder_softid2chid

from .instrument import FACT
from .aux import AUXService


def fact_event_generator(inputfile, drsfile, auxpath='/fact/aux', allowed_triggers=None):
    fact_fits_calib = FactFitsCalib(inputfile, drsfile)
    auxservice = AUXService(auxpath)

    header = fact_fits_calib.data_file.header()

    for event in fact_fits_calib:
        trigger_type = event['TriggerType']

        if allowed_triggers is not None:
            if trigger_type not in allowed_triggers:
                continue

        event_id = event['EventNum']

        night = header['NIGHT']
        run_id = header['RUNID']

        data = DataContainer()
        data.meta['origin'] = 'FACT'

        if 'UnixTimeUTC' in event:
            mc = False
            data.trig.gps_time = Time(
                event['UnixTimeUTC'][0] + event['UnixTimeUTC'][1] * 1e-6,
                scale='utc',
                format='unix',
            )
        else:
            mc = True
            data.trig.gps_time = Time.now()

        if mc:
            event['CalibData'] = reorder_softid2chid(event['CalibData'])
            event['McCherPhotWeight'] = reorder_softid2chid(event['McCherPhotWeight'])
            add_mc_data(event, data)
        else:
            add_aux_data(auxservice, data)

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
        data.r1.tel[0].pe_samples = event['CalibData'].reshape(1, 1440, -1) / 242
        data.dl0.tel[0].pe_samples = event['CalibData'].reshape(1, 1440, -1) / 242

        yield data


def add_mc_data(event, data):
    data.mc.energy = event['MCorsikaEvtHeader.fTotalEnergy'] * u.GeV
    data.mc.az = (180 + event['MCorsikaEvtHeader.fAz']) * u.deg
    data.mc.alt = (90 - event['MCorsikaEvtHeader.fZd']) * u.deg
    data.mc.core_x = event['MCorsikaEvtHeader.fX'] * u.cm
    data.mc.core_y = event['MCorsikaEvtHeader.fY'] * u.cm
    data.mc.h_first_int = event['CorsikaEvtHeader.fFirstInteractionHeight']
    data.mc.tel[0].photo_electron_image = event['McCherPhotWeight']

    data.pointing[0].azimuth = event['MPointingPos.fAz'] * u.deg
    data.pointing[0].altitude = (90 - event['MPointingPos.fZd']) * u.deg


def add_aux_data(auxservice, data):
    pointing, source = auxservice.get_aux_point(data.trig.gps_time)
    data.pointing[0].azimuth = (180 + pointing['Az']) * u.deg
    data.pointing[0].altitude = (90 - pointing['Zd']) * u.deg
    data.source.name = source['Name']
    data.source.ra = source['Ra_src'] * u.ha
    data.source.dec = source['Dec_src'] * u.deg

from zfits import FactFits
from ctapipe.io.containers import DataContainer


def fact_event_generator(inputfile, drsfile):
    fact_fits = FactFits(inputfile, drsfile)

    header = fact_fits.data_file['Events'].read_header()

    for i in range(fact_fits.data_file['Events'].get_nrows()):
        time_series = fact_fits.get_data_calibrated(i)

        event_id = fact_fits.get('EventNum', i)
        night = header['NIGHT']
        run_id = header['RUNID']

        data = DataContainer()

        for c in (data.r0, data.r1, data.dl0):
            c.event_id = event_id
            c.run_id = '{}_{:03d}'.format(night, run_id)
            c.tels_with_data = [0]

        data.r0.tel[0] = time_series

        yield data

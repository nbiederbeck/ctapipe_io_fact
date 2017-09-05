from argparse import ArgumentParser
from ctapipe_fact import fact_event_generator

from ctapipe.visualization import CameraDisplay
from ctapipe.instrument import CameraGeometry
from ctapipe.calib.camera import CameraDL1Calibrator
from ctapipe.image.charge_extractors import LocalPeakIntegrator

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

integrator = LocalPeakIntegrator(config=None, tool=None)
integrator.window_shift = 5
integrator.window_width = 30
integrator.sig_amp_cut_HG = 0.1 / 230
integrator.sig_amp_cut_LG = 0.1 / 230

dl1_calibrator = CameraDL1Calibrator(
    config=None,
    tool=None,
    extractor=integrator,
)

parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('drsfile')


def main():
    args = parser.parse_args()
    event_generator = fact_event_generator(args.inputfile, args.drsfile)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_axes([0, 0, 0.9, 1])
    ax.set_axis_off()
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size="5%", pad=0.05)

    geom = CameraGeometry.from_name('FACT')
    disp = CameraDisplay(geom, ax=ax)
    disp.add_colorbar(cax=cax, label='Photons')

    for e in event_generator:

        dl1_calibrator.calibrate(e)

        print(e.dl1.tel[0])
        disp.image = e.dl1.tel[0].image[0]

        ax.set_title('FACT Event {}'.format(e.trig.gps_time.iso))

        plt.pause(0.01)
        input('Press enter for next event')


if __name__ == '__main__':
    main()

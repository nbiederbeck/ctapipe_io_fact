from argparse import ArgumentParser
from ctapipe_fact import fact_event_generator

from ctapipe.visualization import CameraDisplay
from ctapipe.instrument import CameraGeometry
from ctapipe.calib.camera import CameraDL1Calibrator
from ctapipe.image.charge_extractors import LocalPeakIntegrator
from ctapipe.image.hillas import hillas_parameters_5 as hillas_parameters
from ctapipe.image.cleaning import tailcuts_clean

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

integrator = LocalPeakIntegrator(config=None, tool=None)
integrator.window_shift = 5
integrator.window_width = 30

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
    event_generator = fact_event_generator(
        args.inputfile, args.drsfile,
        allowed_triggers={4},
    )

    fig = plt.figure(figsize=(12, 6))
    ax1 = fig.add_axes([0, 0, 0.4, 1])
    ax1.set_axis_off()
    divider = make_axes_locatable(ax1)
    cax1 = divider.append_axes('right', size="5%", pad=0.05)

    ax2 = fig.add_axes([0.5, 0.0, 0.4, 1])
    ax2.set_axis_off()
    divider = make_axes_locatable(ax2)
    cax2 = divider.append_axes('right', size="5%", pad=0.05)

    geom = CameraGeometry.from_name('FACT')

    disp1 = CameraDisplay(geom, ax=ax1)
    disp1.add_colorbar(cax=cax1, label='Photons')
    disp2 = CameraDisplay(geom, ax=ax2)
    disp2.add_colorbar(cax=cax2, label='ArrivalTime')

    ax1.set_title('Photons')
    ax2.set_title('Peak Position')

    for e in event_generator:

        dl1_calibrator.calibrate(e)

        image = e.dl1.tel[0].image[0]
        cleaning_mask = tailcuts_clean(geom, image, 5, 3.5)

        if sum(cleaning_mask) < 15:
            continue

        hillas_container = hillas_parameters(
            geom.pix_x[cleaning_mask],
            geom.pix_y[cleaning_mask],
            image[cleaning_mask],
        )

        disp1.overlay_moments(hillas_container, linewidth=1.5, color='c', with_label=False)
        disp1.highlight_pixels(cleaning_mask)

        disp1.image = e.dl1.tel[0].image[0]
        disp2.image = e.dl1.tel[0].peakpos[0]

        for disp in (disp1, disp2):
            disp.highlight_pixels(cleaning_mask, color='r', linewidth=1.5)

        fig.suptitle('FACT Event {}'.format(e.trig.gps_time.iso))

        plt.pause(0.01)
        input('Press enter for next event')


if __name__ == '__main__':
    main()

from ctapipe.io.containers import InstrumentContainer
from fact.instrument.constants import FOCAL_LENGTH_MM
import astropy.units as u
import numpy as np


FACT = InstrumentContainer()
FACT.telescope_ids = [0]
FACT.optical_foclen[0] = FOCAL_LENGTH_MM * u.mm
FACT.mirror_dish_area[0] = 9.5 * u.m**2
FACT.mirror_numtiles[0] = 30
FACT.tel_pos[0] = np.array([0, 0])
FACT.num_pixels[0] = 1440
FACT.num_channels[0] = 1

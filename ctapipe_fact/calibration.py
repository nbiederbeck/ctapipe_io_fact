from ctapipe.calib.camera import CameraR1Calibrator


class FACTR1Calibrator(CameraR1Calibrator):
    origin = 'FACT'
    origin = 'FACTR1Calibrator'

    def calibrate(self, event):
        assert event.meta['origin'] == self.origin, 'Wrong camera type'

        for tel_id in event.r0.tels:

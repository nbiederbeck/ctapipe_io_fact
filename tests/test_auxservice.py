from ctapipe_io_fact.aux import AUXService
from astropy.time import Time


def test_auxservice():
    auxservice = AUXService('tests/resources/aux')
    t, s = auxservice.get_aux_point(Time('2014-06-23 23:30'))

    assert s['Name'] == 'Mrk 501'


if __name__ == '__main__':
    test_auxservice()

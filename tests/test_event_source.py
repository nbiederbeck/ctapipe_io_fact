

def test_event_source():
    from ctapipe_fact.zfits import fact_event_generator
    gen = fact_event_generator(
        'tests/resources/testDataFile.fits.fz',
        'tests/resources/testDrsFile.drs.fits.gz'
    )
    events = [e for e in gen]

    assert len(events) == 5
    assert events[0].r0.run_id == '20160817_016'


if __name__ == '__main__':
    test_event_source()

def test_dl1_event_source():
    raise NotImplementedError


# def test_event_source():
#     from ctapipe_io_fact.zfits import fact_event_generator

#     gen = fact_event_generator(
#         "tests/resources/20160817_016.fits.fz",
#         "tests/resources/20160817_030.drs.fits.gz",
#     )
#     print("start looping")
#     events = [e for e in gen]
#     print(events)

#     assert len(events) == 5
#     assert events[0].r0.run_id == "20160817_016"

from setuptools import setup, find_packages


setup(
    name="ctapipe_io_fact",
    version="0.0.1",
    description="ctapipe plugin for reading FACT files",
    author="Maximilian Noethe",
    author_email="maximilian.noethe@tu-dortmund.de",
    license="MIT",
    packages=find_packages(),
    tests_require=["pytest>=3.0.0", "pyfact"],
    setup_requires=["pytest-runner"],
    install_requires=["ctapipe", "sortedcontainers", "sortedcollections"],
    zip_safe=False,
)

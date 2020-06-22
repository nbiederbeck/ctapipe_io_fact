from setuptools import setup, find_packages


setup(
    name="ctapipe_io_fact",
    version="0.1.0",
    description="ctapipe plugin for reading FACT files",
    author="Maximilian Noethe",
    author_email="maximilian.noethe@tu-dortmund.de",
    license="MIT",
    packages=find_packages(),
    tests_require=["pytest>=3.0.0", "pyfact"],
    setup_requires=["pytest-runner"],
    install_requires=["ctapipe>=0.8", "sortedcontainers", "sortedcollections"],
    zip_safe=False,
)

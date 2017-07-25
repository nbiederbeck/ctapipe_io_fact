from setuptools import setup, find_packages


setup(
    name='ctapipe_fact',
    version='0.0.1',
    description='Some classes to make FACT data work with ctapipe',
    url='http://github.com/fact-project/ctapipe-fact',
    author='Maximilian Noethe',
    author_email='maximilian.noethe@tu-dortmund.de',
    license='MIT',
    packages=find_packages(),
    tests_require=['pytest>=3.0.0'],
    setup_requires=['pytest-runner'],
    install_requires=[
        'ctapipe',
        'zfits',
    ],
    zip_safe=False,
)

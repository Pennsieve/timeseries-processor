
from distutils.core import setup, Extension

pymeflib = Extension(
            'pymeflib',
             sources = [ 'mef/pymeflib.c' ]
)

setup (
    name        =   'mef2_processor',
    version     =   '1.0',
    description =   'mef2 timeseries processor',
    ext_modules =   [ pymeflib ]
)

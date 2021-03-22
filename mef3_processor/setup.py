
from distutils.core import setup, Extension

pymeflib = Extension(
            'pymeflib',
             sources = [ 'mef/pymeflib.c' ]
)

setup (
    name        =   'mef3_processor',
    version     =   '1.0',
    description =   'mef3 timeseries processor',
    ext_modules =   [ pymeflib ]
)

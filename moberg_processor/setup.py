from distutils.core import setup, Extension
import numpy
import sys

tsutils  = Extension('tsutils',
                sources      = ['tsutils/tsutils.c'],
                include_dirs = [numpy.get_include()])

setup (
		name              = 'tsutils',
		version           = '1.0',
		description       = 'timeseries utilities',
		setup_requires    = ['setuptools_cython'],
		ext_modules       = [tsutils])

# -*- coding: utf-8 -*-
"""
Modified:
 S. Lopez de Diego (20180423)

Created on Mon Jan  2 12:49:21 2017

setup.py file for pymef3 library

Ing.,Mgr. (MSc.) Jan Cimbálník
Biomedical engineering
International Clinical Research Center
St. Anne's University Hospital in Brno
Czech Republic
&
Mayo systems electrophysiology lab
Mayo Clinic
200 1st St SW
Rochester, MN
United States
"""

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext

class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())

# the c extension module
mef_file_ext = Extension("pymef.mef_file.pymef3_file", ["pymef/mef_file/pymef3_file.c"])

setup(name = "pymef",
      version="0.2.0",
      packages = ["pymef","pymef.mef_file"],
      cmdclass={'build_ext':build_ext},
      ext_modules=[mef_file_ext],
) # This line needed for MSEL (+ the import at the beginning)
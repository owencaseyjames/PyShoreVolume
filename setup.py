#!/usr/bin/env python
import os

from setuptools import setup
from setuptools import find_packages

import sys

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(name='PyShoreVolume',
      version ='1.0.2',
      description ='Python Based Shoreline Change and Beach Volume Analysis Tool',
      author ='Owen Casey James',
      author_email = 'owen.james@kcl.ac.uk',
      licence ='MIT',
      keywords = 'Shoreline Erosion SCA Volume Digital Elevation Model EPR SCA NSM LRR',
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires = ['basemap_data>=1.3.2',
                         'contextily>=1.3.0',
                         'Fiona>=1.9.1',
                         'geopandas>=0.9.0',
                         'geopy>=2.3.0',
                         'matplotlib>=3.7.1',
                         'numpy>=1.23.5',
                         'pandas>=1.5.3',
                         'Pillow>=9.4.0',
                         'pyproj<=3.5.0',
                         'rasterio>=1.3.6',
                         'scikit_learn>=1.2.2',
                         'scipy>=1.10.0',
                         'seaborn>=0.12.2',
                         'shapely>=2.0.1',
                         'statsmodels>=0.13.5'] ,
      url = 'https://github.com/owencaseyjames/PyShoreVolume',
      python_requires = '>=3',
      package_dir = {"":"src"},
      packages =  find_packages(where = 'src', include = ['PyShoreVolume', 'PyShoreVolume.ShorelineChange', 'PyShoreVolume.VolumeChanges', 'PyShoreVolume.CleanandTransectLocator', 'PyShoreVolume.Extra',]),
      classifiers = ['Development Status :: 4 - Beta',
                     'License :: OSI Approved :: MIT License',
                     'Programming Language :: Python :: 3',
                     'Intended Audience :: Science/Research',
                     'Topic :: Scientific/Engineering :: GIS',
                     'Operating System :: OS Independent'],
      py_modules = ['QGISMergedShoreline', 'File_Organisation_Script'],
      package_data = {'PyShoreVolume.Extra':['Transect1.*'], 'PyShoreVolume.Extra':['Intersections2.*', 'Transect1.*', 'End Point Rate.jpg', 'netshorelinemovement.jpg', 'shorleinechangeenvelope.jpg', 'NetShorelineMovementErosionandAccretion.jpg' ,'nsm.pkl',
      					'nsmerrandacc.pkl','scedic.pkl','lrrdictionary.pkl' ,'eprresults.pkl','File_Organisation_Script.py', 'QGISMergedShoreline.py']},
      include_package_data = True,
      )
    
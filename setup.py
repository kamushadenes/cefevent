import os
from distutils.core import setup

long_description = 'ArcSight\'s Common Event Format library',
if os.path.exists('README.rst'):
    long_description = open('README.rst', 'r').read()


setup(
  name = 'cefevent',
  packages = ['cefevent'], # this must be the same as the name above
  version = '0.3.2',
  description = 'ArcSight\'s Common Event Format library',
  long_description = long_description,
  author = 'Kamus Hadenes',
  author_email = 'kamushadenes@hyadesinc.com',
  url = 'https://github.com/kamushadenes/cefevent', # use the URL to the github repo
  download_url = 'https://github.com/kamushadenes/cefevent/tarball/0.1', # I'll explain this in a second
  keywords = ['logging', 'cef', 'arcsight', 'event', 'security'], # arbitrary keywords
  classifiers = [],
)

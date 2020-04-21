#! /usr/bin/env python
"""LiveTrackBot setup file."""
import pathlib
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import versioneer

# The directory containing this file
HERE = pathlib.Path(__file__).parent

DESCRIPTION = 'Telegram bot for paragliding livetrack.'
LONG_DESCRIPTION = HERE.joinpath('README.md').read_text()

DISTNAME = 'LiveTrackBot'
LICENSE = 'MIT'
AUTHOR = 'Axel Fahy'
EMAIL = 'axel@fahy.net'
URL = 'https://github.com/axelfahy/LiveTrackBot'
DOWNLOAD_URL = ''
PROJECT_URLS = {
    'Bug Tracker': 'https://github.com/axelfahy/LiveTrackBot/issues',
    #'Documentation': 'https://LiveTrackBot.readthedocs.io/en/latest/',
    'Source Code': 'https://github.com/axelfahy/LiveTrackBot'
}
REQUIRES = [
    'Click',
    'python-dotenv',
    'python-telegram-bot',
    'requests',
    'typing'
]
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Topic :: Utilities']

class NoopTestCommand(TestCommand):
    def __init__(self, dist):
        print('LiveTrackBot does not support running tests with '
              '`python setup.py test`. Please run `make all`.')

cmdclass = versioneer.get_cmdclass()
cmdclass.update({"test": NoopTestCommand})

setup(name=DISTNAME,
      maintainer=AUTHOR,
      version=versioneer.get_version(),
      packages=find_packages(exclude=('tests',)),
      maintainer_email=EMAIL,
      description=DESCRIPTION,
      license=LICENSE,
      cmdclass=cmdclass,
      url=URL,
      download_url=DOWNLOAD_URL,
      project_urls=PROJECT_URLS,
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      classifiers=CLASSIFIERS,
      python_requires='>=3.6',
      install_requires=REQUIRES,
      entry_points = {
        'console_scripts': [
            'livetrackbot = livetrackbot.__main__:main'
        ]
      },
      zip_safe=False)

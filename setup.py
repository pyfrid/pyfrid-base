try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

import sys

import pyfrid.version

LONG_DESCRIPTION = '''
PyFRID is a Python Framework for an instrument development. If you have a bunch of motors,
sensors, detectors and other hardware, if you can communicate with them and would like to organize them 
under an application with GUI or command line tool, if you want to control and manipulate them with an
easy macro language or to visualize data from detectors and sensors and so on, PyFRID is your tool.
'''

DESCRIPTION="Python Framework for an Instrument Development"

PACKAGE_NAME="PyFRID"

VERSION=pyfrid.version.__version__

URL="http://escape-app.net/"

NAMESPACE_PACKAGES=['pyfrid']

LICENSE="Apache"

AUTHOR= 'Denis Korolkov'

AUTHOR_EMAIL= 'pyfrid@gmail.com'

requires = ['lepl', 'pyyaml']


if sys.version_info < (2, 6):
    print('ERROR: PyFRID requires at least Python 2.6 to run.')
    sys.exit(1)


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    namespace_packages = NAMESPACE_PACKAGES,
    url=URL,
    #download_url='http://pypi.python.org/pypi/Sphinx',
    license=LICENSE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(exclude=['scripts']),
    entry_points={
        'console_scripts': [
            'pyfrid-admin = scripts:main'
        ]
    },
    install_requires=requires,
    include_package_data = True
)



from setuptools import setup

version = '0.1.1'

setup(
    name='python-wellrested',
    version=version,
    description='A REST client providing a convenience wrapper over httplib2',
    author='Nowell Strite',
    author_email='nowell@strite.org',
    url='http://github.com/nowells/python-wellrested/',
    packages=['wellrested', 'wellrested.connections'],
    install_requires=['httplib2'],
    )

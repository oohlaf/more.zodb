import os
from setuptools import setup, find_packages

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CHANGES.txt').read())

setup(name='more.zodb',
      version='0.1.dev0',
      description="ZODB integration for Morepath",
      long_description=long_description,
      author="Olaf Conradi",
      author_email="olaf@conradi.org",
      keywords='morepath zodb',
      license="BSD",
      #url="http://pypi.python.org/pypi/more.zodb",
      namespace_packages=['more'],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'morepath',
        'zodburi',
        ],
      extras_require = dict(
        test=['pytest >= 2.0',
              'pytest-cov'],
        ),
      )

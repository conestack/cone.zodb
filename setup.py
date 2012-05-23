from setuptools import setup, find_packages
import sys, os

version = '0.9pre3'
shortdesc = 'cone ZODB integration'
longdesc = ''

setup(name='cone.zodb',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'https://github.com/bluedynamics/cone.zodb',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['cone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'cone.app',
          'node',
          'node.ext.zodb',
          'repoze.catalog',
      ],
      extras_require=dict(
          test=[
                'interlude',
                'plone.testing',
                'unittest2',
          ]
      ),
      tests_require=[
          'interlude',
      ],
      test_suite = "cone.zodb.tests.test_suite",
      )

from setuptools import find_packages
from setuptools import setup
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '1.0a4.dev0'
shortdesc = 'ZODB integration for cone.app'
longdesc = '\n\n'.join([read_file(name) for name in [
    'README.rst',
    'CHANGES.rst',
    'LICENSE.rst'
]])


setup(
    name='cone.zodb',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='node pyramid cone web',
    author='Cone Contributors',
    author_email='dev@conestack.org',
    url='http://github.com/conestack/cone.zodb',
    license='Simplified BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['cone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'node.ext.zodb',
        'repoze.catalog',
        'pyramid_tm',
        'pyramid_zodbconn',
        'cone.app[lxml]>=1.0.3',
    ],
    extras_require=dict(
    test=[
        'pytest',
        'zope.pytestlayer'
    ])
)

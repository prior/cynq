from distutils.core import setup

VERSION='2.3.10'
setup(
    name='cynq',
    version=VERSION,
    description='A data synchronizer',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='https://github.com/prior/cynq',
    download_url='https://github.com/prior/cynq/tarball/v%s'%VERSION,
    packages=['cynq'],
    install_requires=[ 'nose==1.1.2' ]
)


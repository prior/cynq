from distutils.core import setup

setup(
    name='cynq',
    version='2.3.9',
    description='A data synchronizer',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='https://github.com/prior/cynq',
    download_url='https://github.com/prior/cynq/tarball/v2.3.9',
    packages=['cynq'],
    install_requires=[ 'nose==1.1.2' ]
)


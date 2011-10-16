from distutils.core import setup

setup(
    name='sync_core',
    version='1.0',
    description='SyncCore HubSpot Package',
    author='Michael Prior',
    author_email='mprior@hubspot.com',
    url=' http://hubspot.com/',
    packages=['sync'],
    install_requires=[
        'nose',
        'unittest2',
        'sanetime==1.0.0'],
    dependency_links = [
        'http://github.com/prior/sanetime/tarball/v1.0.0#egg=sanetime-1.0.0'],
    platforms=["any"] )


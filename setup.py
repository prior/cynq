from distutils.core import setup

setup(
    name='cynq',
    version='2.3.7',
    description='A data synchronizer',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='https://github.com/prior/cynq',
    download_url='https://github.com/prior/cynq/tarball/v2.3.7',
    packages=['cynq'],
    install_requires=[
        'nose==1.1.2',
        'sanetime==3.2'],
    dependency_links = ['https://github.com/prior/sanetime/tarball/v3.2'],
)


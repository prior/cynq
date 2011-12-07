from distutils.core import setup

setup(
    name='cynq',
    version='2.3',
    description='A data synchronizer',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='https://github.com/prior/cynq',
    packages=['cynq'],
    install_requires=[
        'nose==1.1.2',
        'unittest2==0.5.1',
        'sanetime==3.0.4'],
    dependency_links = ['https://github.com/prior/sanetime/tarball/v3.0.4'],
)


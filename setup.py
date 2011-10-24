from distutils.core import setup

setup(
    name='cynq',
    version='1.0.1',
    description='A data synchronizer',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='',
    packages=['cynq'],
    install_requires=[
        'nose',
        'unittest2',
        'sanetime==2.0.1'],
    dependency_links = [
        'http://github.com/prior/sanetime/tarball/v2.0.1#egg=sanetime-2.0.1'],
    platforms=["any"] )


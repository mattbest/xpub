from setuptools import setup

setup(
    name='xpub',
    version='0.1',
    description='A CLI for `xromm.uchicago.edu` data portal',
    url='https://github.com/rcc-uchicago/xpub',
    author='J. Voigt',
    author_email='jvoigt@uchicago.edu',
    license='MIT',
    packages=['xpub'],
    package_data = {
        '': ['*.md', '*.json'],
        'xpub': [
            'config/*.json', 
            'config/mediatypes/*.json'
        ]
    }
    zip_safe=False
    )

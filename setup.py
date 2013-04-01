import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-kishore',
    version = '0.1',
    packages = ['kishore'],
    include_package_data = True,
    license = 'MIT License', # example license
    description = 'A django app to help bands and labels share and sell their music.',
    long_description = README,
    url = 'http://github.com/udbhav/kishore',
    author = 'Udbhav Gupta',
    author_email = 'gupta.udbhav@gmail.com',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

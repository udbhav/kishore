import ez_setup
ez_setup.use_setuptools()

import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-kishore',
    version = '0.1.1',
    packages = ['kishore'],
    install_requires = ['Django>=1.5','boto>=2.10.0','django-imagekit>=3.0.3',
                        'django-less>=0.7.2','django-storages>=1.1.8','easypost>=2.0.4',
                        'soundcloud>=0.3.6','stripe>=1.9.4'],
    include_package_data = True,
    license = 'MIT License',
    description = 'A django app to help bands and labels share and sell their music.',
    long_description = README,
    url = 'http://github.com/udbhav/kishore',
    author = 'Udbhav Gupta',
    author_email = 'dev@udbhavgupta.com',
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

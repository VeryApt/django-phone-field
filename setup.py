from os import path
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='django-phone-field',
    version='1.5.3',
    url=r'https://github.com/VeryApt/django-phone-field/',
    license='GPL',
    platforms=['OS Independent'],
    description='Lightweight model and form field for phone numbers in Django',
    install_requires=['Django>=1.10'],
    long_description=long_description,
    author='Andrew Mackowski',
    author_email='andrew@veryapt.com',
    maintainer='Andrew Mackowski',
    maintainer_email='andrew@veryapt.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='django phonenumber phone number model field',
    packages=find_packages(exclude=['test_proj', 'test_app']),
    include_package_data=True
)

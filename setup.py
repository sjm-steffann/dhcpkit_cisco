"""
Setup script for dhcpkit_cisco
"""
import os

from setuptools import find_packages, setup

import dhcpkit_cisco


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(filename):
    """
    Read the contents of a file

    :param filename: the file name relative to this file
    :return: The contents of the file
    """
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='dhcpkit_cisco',
    version=dhcpkit_cisco.__version__,

    description='Cisco-specific extensions to DHCPKit',
    long_description=read('README.rst'),
    keywords='dhcp server ipv6 cisco',
    url='https://github.com/sjm-steffann/dhcpkit_cisco',
    license='GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
    ],

    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    entry_points={
        'dhcpkit_cisco.ipv6.remote_ids': [
            '2 = dhcpkit_cisco.ipv6.cisco_remote_id:CiscoEthernetRemoteId',
        ],
        'dhcpkit.ipv6.option_handlers': [
            ('rewrite-cisco-remote-id = '
             'dhcpkit_cisco.ipv6.option_handlers.rewrite_remote_id:RewriteRemoteIdOptionHandler'),
        ],
    },

    install_requires=[
        'dhcpkit >= 0.8.0',
    ],

    test_suite='tests',

    author='Sander Steffann',
    author_email='sander@steffann.nl',

    zip_safe=False,
)

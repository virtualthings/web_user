#!/usr/bin/env python
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from setuptools import setup
import re
import os
import ConfigParser

MODULE = 'web_user'
PREFIX = 'virtualthings'
MODULE2PREFIX = {}


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
version_info = info.get('version', '0.0.1')
branch, _ = version_info.rsplit('.', 1)
dev_branch = float(branch) * 10
# Warning: Check, after version 3.9 must follow 4.0. This calculation only
# works if the Tryton project follows a strict sequence version number policy.
if not (dev_branch % 2):  # dev_branch is a release branch
    dev_branch -= 1
next_branch = dev_branch + 2
branch_range = str(dev_branch / 10), str(next_branch / 10)
requires = []

for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        prefix = MODULE2PREFIX.get(dep, 'trytond')
        requires += ['%s_%s >= %s, < %s' % ((prefix, dep,) + branch_range)]
requires += ['trytond >= %s, < %s' % branch_range]
tests_require = ['proteus >= %s, < %s' % branch_range]

setup(
    name='%s_%s' % (PREFIX, MODULE),
    version=version_info,
    description='Tryton module with web user from %s' % PREFIX,
    long_description=read('README'),
    author='virtual things',
    author_email='info@virtual-things.biz',
    url='https://github.com/virtualthings/web_user',
    download_url='https://github.com/%s/'
        '%s/archive/%s.zip' % (PREFIX, MODULE, dev_branch + 1),
    package_dir={'trytond.modules.%s' % MODULE: '.'},
    packages=[
        'trytond.modules.%s' % MODULE,
        'trytond.modules.%s.tests' % MODULE,
    ],
    package_data={
        'trytond.modules.%s' % MODULE: (
            info.get('xml', []) + [
                '*.odt', '*.ods', 'icons/*.svg', 'tryton.cfg', 'view/*.xml',
                'locale/*.po', 'tests/*.rst']),
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Legal Industry',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Natural Language :: German',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business',
    ],
    license='GPL-3',
    install_requires=requires,
    extras_require={
        'BCrypt': ['bcrypt'],
    },
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    %s = trytond.modules.%s
    """ % (MODULE, MODULE),
    test_suite='tests',
    test_loader='trytond.test_loader:Loader',
    tests_require=tests_require,
)


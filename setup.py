# -*- encoding: utf-8 -*-
import os
import pwd
import grp

import getpass

from distutils.core import setup

cfg_name = '.pyred.cfg'
open(cfg_name, 'w').write('[server]')

setup(
    name='pyred',
    version='0.1.0',
    description='redmine wrapper with mechanize',
    long_description=open('README').read(),
    author=u'Nyirő Gergő',
    author_email='gergo.nyiro@gmail.com',
    url='https://github.com/nyirog/pyred',
    package_dir={'': 'src'},
    py_modules=['redmine'],
    scripts=['scripts/pyred'],
    requires=['mechanize'],
    license=open('COPYING').read(),
    data_files=[
        (os.path.expanduser('~'), [cfg_name]),
    ],
)

user = os.path.basename( os.path.expanduser('~') )
os.chown(os.path.expanduser(os.path.join('~', cfg_name)),
         pwd.getpwnam(user).pw_uid, grp.getgrnam(user).gr_gid)
os.remove(cfg_name)

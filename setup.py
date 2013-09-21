# -*- encoding: utf-8 -*-
from distutils.core import setup

setup(
    name='pyred',
    version='0.1.0',
    description='redmine wrapper with mechanize',
    long_description='''
    pyred offers redmine module to run automatic action on redmine project
    hosting server
    ''',
    author=u'Nyirő Gergő',
    author_email='gergo.nyiro@gmail.com',
    package_dir={'': 'src'},
    py_modules=['redmine'],
    requires=['mechanize'],
    license=open('COPYING').read(),
)


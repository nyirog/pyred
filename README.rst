pyred offers a wrapper for redmine project hosting server with mechanize.
The wrapper can be used from python with redmine.Redmine class or with the pyred
cli script

Initalize pyred
===============

Login
-----

>>> from redmine import Redmine
>>> redmine = Redmine('http://127.0.0.1/redmine')
>>> redmine.login('master.foo', 'secret')

$ pyred --url http://127.0.0.1/redmine --username master.foo --password secret

The pyred script remebers the url address of the server, the last login and its
password. Those data are stored in ~/.pyred.cfg.


Register users
--------------

The redmine server often has to be customized for the local needs.
User names should be tell to pyred, so they can be used as names instead of ids.

$ pyred --user-id master.foo 3 --user-id script.kiddy 7

>>> class Purplemine(Redmine):
...     users = {'master.foo': 3, 'script.kiddy': 7}
>>> redmine = Purplemine('http://127.0.0.1/redmine')


Special trackers
----------------

The local redmine server can have special tracker over the defaults one, that
should be known by pyred.

$ pyred --tracker-id Report 4

The Redmine class should store all the available tracker option in trackers
attribute, not just the special ones:

>>> class Bluemine(Redmine):
...     trackers = {'Bug': 1, 'Feature': 2, 'Support': 3, 'Report': 4}

_Remark_ user-id and tracker-id are stored in ~/.pyred.cfg under users and
trackers section.

Actions
=======

After the configuration of pyred we can run some action on it.

_Remark_ atomsk will be the project name at the actions, and 42 will be the issue
id

Upload file to a project
------------------------

$ pyred upload atomsk egg.py --file-desc 'all python need an egg' 

>>> redmine.upload_project_file('atomsk', 'egg.py', 'all python need an egg')

Upload a file to an issue
-------------------------

$ pyred upload-issue 42 egg.py --file-desc 'all python need an egg'

>>> redmine.upload_issue_file(42, 'egg.py', 'all python need an egg')

Create an issue
---------------

$ pyred issue atomsk Feature 'paint the eggs' --description 'please' --parent 42\
>       --file-name egg.png --watcher master.foo
43

>>> issue_id = redmine.create_issue('atomsk', 'Feature', 'paint the eggs',
...                                 'please', 42, ['master.foo'])
>>> redmine.upload_issue_file(issue_id, 'egg.png')

Parent issue and watchers are optionals.

List issue
----------

$ pyred list-issue 42
Subtasks of 42 issue
paint the eggs /redmine/issues/43

Have fun!

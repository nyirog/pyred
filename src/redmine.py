import re
from argparse import ArgumentParser, RawTextHelpFormatter

from mechanize import Browser, urlopen

class Redmine(Browser):
    trackers = {'Bug': 1, 'Feature': 2, 'Support': 3}
    def __init__(self, url, trackers=None):
        Browser.__init__(self)
        self.addheaders = [('User-agent', 'Firefox')]

        self._url = url
        self.trackers = trackers or Redmine.trackers
        return

    def login(self, login, password):
        resp = self.open('%s/login' % self._url)
        self.form = list(self.forms())[1]
        self['username'] = login
        self['password'] = password
        self.submit()
        return

    def upload_project_file(self, project, filename, file_desc=''):
        url = '%s/projects/%s/files/new' % (self._url, project)
        self._upload_file(url, filename, file_desc)
        return

    def upload_issue_file(self, issue, filename, file_desc=''):
        url = '%s/issues/%d' % (self._url, issue)
        self._upload_file(url, filename, file_desc)
        return

    def _upload_file(self, url, filename, file_desc):
        resp = self.open(url)
        self.form = self._find_form_by_control_names({'attachments[1][file]'})
        self.form.add_file(open(filename), 'text/plain', filename,
                         name='attachments[1][file]')
        self['attachments[1][description]'] = file_desc
        self.submit()
        return

    def _find_form_by_control_names(self, control_names):
        for form in self.forms():
            names = control_names - set(ctrl.name for ctrl in form.controls)
            if not names: return form
        raise ValueError('Invaliad forms no %s action' % control_name)

    def create_issue(self, project, subject, description, tracker,
                     parent_issue):
        url = '%s/projects/%s/issues/new' % (self._url, project)
        resp = self.open(url)
        self.form = self._find_form_by_control_names({'issue[tracker_id]'})
        self['issue[subject]'] = subject
        self['issue[description]'] = description
        self.form['issue[tracker_id]'] = [str(self.trackers[tracker])]
        if isinstance(parent_issue, int):
            self['issue[parent_issue_id]'] = str(parent_issue)

        resp = self.submit()
        match = re.search('<title>%s\\s+#(\\d+):.+</title>' % tracker,
                          resp.read())
        issue = int(match.group(1))
        return issue

    @classmethod
    def create_parser(cls):
        parser = ArgumentParser(formatter_class=RawTextHelpFormatter,
                                description="""
        redmine wrapper written in python with mechanize
        """)
        parser.add_argument('url', help='url of the redmine server')
        parser.add_argument('command', 
                            choices={'upload', 'upload-issue', 'issue'},
                            help=\
       'redmine actions:\n'\
       '  * upload: upload a file to the project\n'\
       '  ** required arguments:\n'\
       '  *** --file-name\n'\
       '  ** optional arguments:\n'\
       '  *** --file-desc\n'\
       '  * upload-issue: upload a file to the issue\n'\
       '  ** required arguments:\n'\
       '  *** --file-name\n'\
       '  ** optional arguments:\n'\
       '  *** --file-desc\n'\
       '  * issue: create redmine issue\n'\
       '  ** required arguments:\n'\
       '  *** --description\n'\
       '  *** --subject\n'\
       '  *** --tracker\n'\
       '  ** optional arguments:\n'\
       '  *** --parent-issue\n'\
       '  *** --file-name\n'\
       '  *** --file-desc\n')
        parser.add_argument('-p', '--project',
                            help='name of the redmine project')
        parser.add_argument('--login')
        parser.add_argument('--password')
        parser.add_argument('--file-name', action='append', default=[])
        parser.add_argument('--file-desc', action='append', default=[])
        parser.add_argument('--issue', type=int)
        parser.add_argument('--description')
        parser.add_argument('--subject')
        parser.add_argument('--tracker', choices=cls.trackers.keys())
        parser.add_argument('--parent-issue', type=int)
        return parser

    @staticmethod
    def fit_file_desc(file_descs, file_names):
        return file_descs or ['' for name in file_names]


if __name__ == '__main__':
    import getpass

    parser = Redmine.create_parser()
    args = parser.parse_args()

    if args.login is None:
        login = getpass.getuser()
        args.login = raw_input('login: [%s]' % login)
        if not args.login:
            args.login = login
    if args.password is None:
        args.password = getpass.getpass('password: ')


    redmine = Redmine(args.url)
    redmine.login(args.login, args.password)
    if args.command == 'upload':
        assert args.project is not None, 'project has to be set'
        assert args.file_name, 'file-name has to be set'

        file_descs = Redmine.fit_file_desc(args.file_desc, args.file_name)
        for file_name, file_desc in zip(args.file_name, file_descs):
            redmine.upload_project_file(args.project, file_name, file_desc)
    elif args.command == 'upload-issue':
        assert args.issue is not None, 'issue has to be set'
        assert args.file_name, 'file-name has to be set'

        file_descs = Redmine.fit_file_desc(args.file_desc, args.file_name)
        for file_name, file_desc in zip(args.file_name, file_descs):
            redmine.upload_issue_file(args.issue, file_name, file_desc)
    elif args.command == 'issue':
        assert args.project is not None, 'project has to be set'
        assert args.subject is not None, 'subject has to be set'
        assert args.description is not None, 'description has to be set'
        assert args.tracker is not None, 'tracker has to be set'

        issue = redmine.create_issue(args.project, args.subject,
                                     args.description, args.tracker,
                                     args.parent_issue)
        file_descs = Redmine.fit_file_desc(args.file_desc, args.file_name)
        for file_name, file_desc in zip(args.file_name, file_descs):
            redmine.upload_issue_file(issue, file_name, file_desc)
        print issue
    else:
        pass


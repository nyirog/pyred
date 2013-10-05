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
        parser.add_argument('--url', help='url of the redmine server')
        parser.add_argument('--username')
        parser.add_argument('--password')

        subparsers = parser.add_subparsers(dest='command')
        subparser = subparsers.add_parser('upload',
                                  description='upload a file to redmine project')
        subparser.add_argument('project',
                               help='name of the redmine project')
        subparser.add_argument('file_name', nargs='+')
        subparser.add_argument('--file-desc', nargs='+')

        subparser = subparsers.add_parser('upload-issue',
                                  description='upload a file to redmine issue')
        subparser.add_argument('issue', type=int)
        subparser.add_argument('file_name', nargs='+')
        subparser.add_argument('--file-desc', nargs='+')

        subparser = subparsers.add_parser('issue',
                                  description='create redmine issue')
        subparser.add_argument('project',
                               help='name of the redmine project')
        subparser.add_argument('tracker', choices=cls.trackers.keys())
        subparser.add_argument('subject')
        subparser.add_argument('description')
        subparser.add_argument('--parent-issue', type=int)
        subparser.add_argument('--file-name', nargs='+')
        subparser.add_argument('--file-desc', nargs='+')
        return parser

    @staticmethod
    def fit_file_desc(file_descs, file_names):
        return file_descs or ['' for name in file_names]


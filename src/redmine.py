
from mechanize import Browser

class Redmine(Browser):
    def __init__(self, url):
        Browser.__init__(self)
        self.addheaders = [('User-agent', 'Firefox')]

        self._url = url
        return

    def login(self, login, password):
        resp = self.open('%s/login' % self._url)
        self.form = list(self.forms())[1]
        self['username'] = login
        self['password'] = password
        self.submit()
        return

    def upload_project_file(self, project, filename, description=''):
        resp = self.open('%s/projects/%s/files/new' % (self._url, project))
        self.form = list(self.forms())[1]
        self.form.add_file(open(filename), 'text/plain', filename,
                         name='attachments[1][file]')
        self['attachments[1][description]'] = description
        self.submit()
        return

if __name__ == '__main__':
    import getpass
    import argparse

    parser = argparse.ArgumentParser(description="""
    redmine wrapper written in python with mechanize
    """)
    parser.add_argument('url', help='url of the redmine server')
    parser.add_argument('project', help='name of the redmine project')
    parser.add_argument('--login')
    parser.add_argument('--password')
    parser.add_argument('--file-name')
    parser.add_argument('--file-desc', default='')
    parser.add_argument('--issue', type=int)

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
    if args.file_name is not None and args.issue is None:
        redmine.upload_project_file(args.project, args.file_name,
                                    args.file_desc)


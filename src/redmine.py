import re
from HTMLParser import HTMLParser

from mechanize import Browser, urlopen

class Redmine(Browser):
    trackers = {'Bug': 1, 'Feature': 2, 'Support': 3}
    users = {}
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
        form_controls = []
        for form in self.forms():
            names = control_names - set(ctrl.name for ctrl in form.controls)
            if not names: return form
            form_controls.append(form.controls)
        raise ValueError(  'Invaliad forms no %s action in\n%s'
                         % (', '.join(control_names),
                            '\n'.join('%s' % (ctrl)
                                      for controls in form_controls
                                      for ctrl in controls)))

    def create_issue(self, project, tracker, subject, description,
                     parent_issue=None, watchers=None):
        watchers = watchers or []
        url = '%s/projects/%s/issues/new' % (self._url, project)
        resp = self.open(url)
        self.form = self._find_form_by_control_names({'issue[tracker_id]', 'issue[watcher_user_ids][]'})
        self['issue[subject]'] = subject
        self['issue[description]'] = description
        self.form['issue[tracker_id]'] = [str(self.trackers[tracker])]
        if isinstance(parent_issue, int):
            self['issue[parent_issue_id]'] = str(parent_issue)
        self.form['issue[watcher_user_ids][]'] = [str(self.users[user])
                                                  for user in watchers]

        resp = self.submit()
        match = re.search('<title>%s\\s+#(\\d+):.+</title>' % tracker,
                          resp.read())
        issue = int(match.group(1))
        return issue

    def create_wiki(self, project, title, description, parent_wiki):
        title = title.title()
        title_url = title.replace(' ', '_')
        url =  '%s/projects/%s/wiki/%s?parent=%s'\
             % (self._url, project, title_url, parent_wiki)
        resp = self.open(url)
        try:
            self.form = self._find_form_by_control_names({'content[text]'})
        except ValueError: # wiki page was already existed
            url = '%s/projects/%s/wiki/%s/edit' % (self._url, project, title_url)
            resp = self.open(url)
            self.form = self._find_form_by_control_names({'content[text]'})
        self['content[text]'] = "h1. %s\n\n%s" % (title, description)
        resp = self.submit()
        return

    def get_subtasks(self, issue):
        url = '%s/issues/%d' % (self._url, issue)
        page = self.open(url).read()
        parser = self.SubtaskParser()
        parser.feed(page)
        return parser.links

    class SubtaskParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)

            self.in_strong = False
            self.in_subtasks = False
            self.in_a = False
            self.attrs = {}
            self.link = ''
            self.links = {}
            return

        def handle_starttag(self, tag, attrs):
            self.in_strong = tag == 'strong'
            self.in_a = tag == 'a'
            self.tag = tag
            self.attrs = dict(attrs)
            return

        def handle_data(self, data):
            if self.in_strong and data == 'Subtasks': self.in_subtasks = True
            if self.in_subtasks and self.tag == 'a' and not self.in_a:
                self.links[self.attrs['href']] = data.lstrip(':').lstrip()
            return

        def handle_endtag(self, tag):
            if tag == 'strong': self.in_strong = False
            if tag == 'a': self.in_a = False
            if self.in_subtasks and tag == 'form': self.in_subtasks = False
            return

    @staticmethod
    def fit_file_desc(file_descs, file_names):
        return file_descs or ['' for name in file_names]


import re

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
        form_controls = []
        for form in self.forms():
            names = control_names - set(ctrl.name for ctrl in form.controls)
            if not names: return form
            form_controls.append(form.controls)
        raise ValueError(  'Invaliad forms no %s action in\n%s'
                         % (', '.join(control_names),
                            '\n'.join('%s<%s>' % (ctrl.name, ctrl.type)
                                      for controls in form_controls
                                      for ctrl in controls)))

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

    @staticmethod
    def fit_file_desc(file_descs, file_names):
        return file_descs or ['' for name in file_names]


import os

class Config:

    def __init__(self):
        self._sonar_url = os.environ['SONAR_URL']
        self._sonar_user = os.environ['SONAR_USER']
        self._sonar_password = os.environ['SONAR_PASSWORD']
        self._sonar_branch_list = os.environ['SONAR_BRANCH_LIST']

    @property
    def sonar_url(self):
        return self._sonar_url

    @property
    def sonar_user(self):
        return self._sonar_user

    @property
    def sonar_password(self):
        return self._sonar_password

    @property
    def sonar_branch_list(self):
        return self._sonar_branch_list
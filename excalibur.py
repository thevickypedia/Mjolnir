import logging
import os
from getpass import getpass

import requests
from requests.auth import HTTPBasicAuth

from storm_breaker import Client

handler = logging.StreamHandler()
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(hdlr=handler)
LOGGER.setLevel(level=logging.DEBUG)


class GitHub:
    """Initiates the GitHub object.

    >>> GitHub

    """

    def __init__(self, username: str = os.environ.get('username'), password: str = os.environ.get('password')):
        """Initiates with a username and password to be passed.

        Args:
            username: Takes the GitHub username as an argument. Checks for env var ``username`` if not passed.
            password: Takes the GitHub password as an argument. Checks for env var ``password`` if not passed.
        """
        self.username = username or input('Enter the GitHub username:\n')
        self.password = password or getpass('Enter your github password:\n')
        self.auth = HTTPBasicAuth(username=self.username, password=self.password)
        self.BASE_URL = "https://api.github.com/"

    def list_repos(self):
        """Lists all public repositories within a user profile without needing an auth token."""
        request = requests.get(f'{self.BASE_URL}users/{self.username}/repos')
        response = request.json()
        for i in range(len(response)):
            LOGGER.info(f"{response[i]['name']}:\t{response[i]['svn_url']}")

    def list_private_repos(self) -> None:
        """Lists all private repositories within a user profile using an auth token."""
        response = requests.get(f'{self.BASE_URL}user/repos', auth=self.auth)

        if not response.ok:
            LOGGER.error(f'{response.status_code}: {response.json().get("message")}')
            return

        response = response.json()
        for i in range(len(response)):
            if response[i]['private']:
                LOGGER.info(response[i]['name'])

    def renamer(self, repository: str, new_author_email: str, new_author: str = None) -> None:
        """Changes author info and committer info of a particular repository.

        Args:
            repository: Takes the name of the repository as an argument.
            new_author_email: Email address to which the commits have to be changed to.
            new_author: Name to which the commits have be changed to. Defaults to the same username.
        """
        LOGGER.info(f'Cloning repo {repository} locally.')
        os.system(f"git clone --bare https://github.com/{self.username}/{repository}.git &> /dev/null")

        if not os.path.isdir(f'{repository}.git'):
            LOGGER.error(f' {repository} - No such repo found.')
            return

        LOGGER.info('Initiating rename process')
        os.system(f"""cd {repository}.git
                    git filter-branch --env-filter '
                    export GIT_COMMITTER_NAME="{new_author or self.username}"
                    export GIT_COMMITTER_EMAIL="{new_author_email}"
                    export GIT_AUTHOR_NAME="{new_author or self.username}"
                    export GIT_AUTHOR_EMAIL="{new_author_email}"
                    '
                    git push --force --tags origin 'refs/heads/*'
                    cd ../
                    rm -rf {repository}.git
                    """)
        LOGGER.info(f'{repository} has been removed.')

    def get_user_profile(self, profile: str):
        """Calls the Client from storm breaker to get the profile information of a particular user.

        Args:
            profile: Takes the target username as an argument.
        """
        client = Client(username=self.username, password=self.password, target=profile, auth=self.auth)
        LOGGER.info(client.fetch())


if __name__ == '__main__':
    GitHub().get_user_profile(profile='thevickypedia')

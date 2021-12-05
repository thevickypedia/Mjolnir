import json
import logging
from string import punctuation

import requests
from requests.auth import HTTPBasicAuth

handler = logging.StreamHandler()
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(hdlr=handler)
LOGGER.setLevel(level=logging.DEBUG)


class Client:
    """Initiates the client object and creates the HTTP basic authentication object.

    >>> Client

    """

    def __init__(self, target: str, username: str = None, password: str = None, auth: HTTPBasicAuth = None):
        """Initiates with username and password or the HTTP basic auth object.

        Args:
            target: Username for which the profile information has to be retrieved.
            username: GitHub username of the requesting account.
            password: GitHub password or token of the requesting account.
            auth: Optional HTTPBasicAuth object.
        """
        self.target = target
        self.punctuations = [punc for punc in punctuation if punc != '-']
        self.variable = {"login": target}
        if auth:
            self.auth = auth
        else:
            self.auth = HTTPBasicAuth(username=username, password=password)

    def _check_format(self):
        """Checks the format of the target username."""
        if any([char in self.punctuations for char in self.target]) or '--' in self.target:
            exit("Username may only contain alphanumeric characters or single hyphens, and cannot begin or end with a "
                 "hyphen.")

    def _get_status(self) -> requests.Response:
        """Checks if the username is available or not.

        Returns:
            Response:
            Returns the response object.
        """
        self._check_format()
        return requests.get(f'https://github.com/{self.target}')

    def fetch(self) -> dict or int:
        """Uses GraphQL to query the github api endpoint and retrieve the profile information.

        Returns:
            dict or int:
            Returns the information as a dictionary or the status code if failed.
        """
        status = self._get_status()
        if not status.ok:
            return status.status_code

        query = """
        query userInfo($login: String!) {
          user(login: $login) {
            name
            login
            createdAt
            starredRepositories {
              totalCount
            }
            repositories {
              totalCount
            }
            following {
              totalCount
            }
            contributionsCollection {
              totalCommitContributions
              restrictedContributionsCount
              hasAnyContributions
            }
          }
        }
        """
        res = requests.post(
            url="https://api.github.com/graphql",
            json={
                "query": query,
                "variables": self.variable
            },
            auth=self.auth
        )
        if res.status_code == 200:
            return json.dumps(res.json().get('data', {}).get('user', {}), indent=4)
        else:
            return res.status_code

import logging
import os

import requests
from requests.auth import HTTPBasicAuth


def list_repos():
    # lists all public repositories within a user profile (does not require github token)
    logger.info(' Public repos:')
    request = requests.get(f'https://api.github.com/users/{username}/repos')
    response = request.json()
    for i in range(len(response)):
        print(response[i]['name'])
        # print(response[i]['svn_url'])


def list_private_repos():
    password = input('Enter your github password:\n')
    logger.info(' Private repos:')
    auth = HTTPBasicAuth(username=username, password=password)
    request = requests.get(f'https://api.github.com/user/repos', auth=auth)
    response = request.json()
    for i in range(len(response)):
        if response[i]['private']:
            print(response[i]['name'])


def renamer():
    # changes author info and committer info (requires github token)
    repo = input('Enter a repository you would like to change the author information:\n')
    new_name = username  # input('Enter the new author name (You can also enter the username):\n')
    new_email = input('Enter the new email address:\n')

    logger.info(' Cloning repo locally..')
    os.system(f"git clone --bare https://github.com/{username}/{repo}.git &> /dev/null")

    if not os.path.isdir(f'{repo}.git'):
        exit(logger.error(f' {repo} - No such repo found.'))

    logger.info(' Initiating rename process')
    os.system(f"""cd {repo}.git
                git filter-branch --env-filter '
                export GIT_COMMITTER_NAME="{new_name}"
                export GIT_COMMITTER_EMAIL="{new_email}"
                export GIT_AUTHOR_NAME="{new_name}"
                export GIT_AUTHOR_EMAIL="{new_email}"
                '
                git push --force --tags origin 'refs/heads/*'
                cd ../
                rm -rf {repo}.git
                """)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(':')
    username = input('Enter your GitHub username:\n')
    renamer()

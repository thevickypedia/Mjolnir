import requests


def list_repos():
    request = requests.get(f'https://api.github.com/users/{username}/repos')
    response = request.json()

    for i in range(len(response)):
        print(response[i]['name'])
        # print(response[i]['svn_url'])


if __name__ == '__main__':
    username = input('Enter your GitHub username:\n')
    list_repos()

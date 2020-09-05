import requests

username = 'thevickypedia'
request = requests.get(f'https://api.github.com/users/{username}/repos')
response = request.json()

for i in range(len(response)):
    print(response[i]['name'])
    print(response[i]['svn_url'])
    print()

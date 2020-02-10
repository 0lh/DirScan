import requests
from requests import RequestException
url='http://113.96.208.186:80'
try:
    r=requests.get(url)
    print(r)
except RequestException:
    print('Error')
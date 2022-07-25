import requests
from requests.adapters import HTTPAdapter, Retry

requester = requests.Session()

retries = Retry(total=50,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ])

def getHTMLDocument(url):
    try:
        requester.mount('http://',HTTPAdapter(max_retries=retries))
        response = requester.get(url)
        return response.text
    except:
        getHTMLDocument(url)
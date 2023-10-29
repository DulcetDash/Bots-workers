import requests
import json
from requests.adapters import HTTPAdapter, Retry
import re
from bs4 import BeautifulSoup

requester = requests.Session()

retries = Retry(total=50,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504])


def getHTMLDocument(url):
    try:
        requester.mount('http://', HTTPAdapter(max_retries=retries))
        response = requester.get(url)
        return response.text
    except:
        getHTMLDocument(url)


def getHTMLPageFrom(url):
    scrapingWaspEndpoint = "http://localhost:9000/api/v1/scraping"
    payload = json.dumps({
        "url": url
    })
    headers = {
        'Authorization': 'Bearer SW_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.wmHxDlKGW9g1mUz2UXilej2i5qPNhM2g2wSO2L23ud4',
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", scrapingWaspEndpoint, headers=headers, data=payload, timeout=240)

    cleaned_data = re.sub(r'\\(["\'])', r'\1', response.text)
    return cleaned_data


def getHTMLSOUPEDDocument(url):
    scrapingWaspEndpoint = "http://localhost:9000/api/v1/scraping"
    payload = json.dumps({
        "url": url
    })
    headers = {
        'Authorization': 'Bearer SW_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.wmHxDlKGW9g1mUz2UXilej2i5qPNhM2g2wSO2L23ud4',
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", scrapingWaspEndpoint, headers=headers, data=payload, timeout=240)

    soup = BeautifulSoup(response.json()['page'], 'html.parser')

    return soup

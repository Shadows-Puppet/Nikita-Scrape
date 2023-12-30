from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
import pandas as pd

url = 'https://scholar.google.ca/scholar?hl=en&as_sdt=0%2C5&q=Machine+learning&btnG='

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

req = Request(url, headers=headers)
webpage = urlopen(req).read()

with requests.Session() as sesh:
    soup = BeautifulSoup(webpage, 'html5lib')
    result = []
    pdf_links = []
    for item in soup.find_all('div', class_='gs_r gs_or gs_scl'):
        result.append(item.find('div', class_='gs_or_ggsm'))
    for i in result:
        if i != None:
            pdf_links.append(i.find('a').get('href'))
        else:
            pdf_links.append(i)
    for i in pdf_links:
        print(i)
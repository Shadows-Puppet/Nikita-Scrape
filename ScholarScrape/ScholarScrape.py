from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from urllib.error import HTTPError
import requests
import numpy as np
import pandas as pd
import time


def update_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params['start'] = [str(start + 10)]
    parsed_url = parsed_url._replace(query=urlencode(query_params, doseq=True))
    return urlunparse(parsed_url)


url = 'https://scholar.google.ca/scholar?start=0&q=machine+learning&hl=en&as_sdt=0,5'

current_url = url

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
}

start = 10
runs = 0
titles = []
links = []
authors = []
descriptions = []
pdf_links_raw = []
pdf_links = []
source_year = []
host_publisher = []
webpage = ''
for i in range(10):
    try:
        req = Request(current_url, headers=headers)
        webpage = urlopen(req).read()
    except HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")

        # Access the headers of the error response
        error_headers = e.headers

        # Check if the 'Retry-After' header is present
        if 'Retry-After' in error_headers:
            retry_after_value = error_headers['Retry-After']
            print(f"Retry-After: {retry_after_value} seconds")
        else:
            print("Retry-After header not found.")
    #req = Request(current_url, headers=headers)



    with requests.Session() as sesh:
        soup = BeautifulSoup(webpage, 'html5lib')
        for item in soup.find_all('div', class_='gs_r gs_or gs_scl'):
            # raw pdf link html to be parsed later
            pdf_links_raw.append(item.find('div', class_='gs_or_ggsm'))
            # title text
            titles.append(item.find('h3', class_='gs_rt').find('a').text)
            # title hyperlink
            links.append(item.find('h3', class_='gs_rt').find('a').get('href'))
            # description
            descriptions.append(item.find('div', class_='gs_rs').text)
            item_authors = []
            for sub_title in item.find_all('div', class_='gs_a'):
                s_text = sub_title.text
                # removes the non-breaking space sometimes placed into the text
                s_text = s_text.replace('\xa0', ' ')
                # if this is the last author then publication date and publisher follow after the '-' symbol
                if '-' in s_text:
                    sub_title_split = s_text.split('-')
                    while len(sub_title_split) < 3:
                        sub_title_split.append('')
                    item_authors.append(sub_title_split[0].strip())
                    source_year.append(sub_title_split[1].strip())
                    host_publisher.append(sub_title_split[2].strip())
                else:
                    item_authors.append(s_text)
            # add the authors for this item to the list of all authors
            authors.append(item_authors)

        # raw pdf parsed
        for i in pdf_links_raw:
            if i is not None:
                pdf_links.append(i.find('a').get('href'))
            else:
                pdf_links.append('')
        authors_str = [', '.join(authors_list) for authors_list in authors]

        current_url = update_url(current_url)
        runs += 1
        time.sleep(15)

print(runs)
data = {'Title': titles,
        'Description': descriptions,
        'Authors': authors_str,
        'Hyperlink': links,
        'Document': pdf_links,
        'Source and/or Year': source_year,
        'Host/Publisher': host_publisher}

df = pd.DataFrame(data)

df.to_csv('testing.csv')


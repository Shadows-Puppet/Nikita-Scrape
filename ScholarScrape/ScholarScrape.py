from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
import numpy as np
import pandas as pd

url = 'https://scholar.google.ca/scholar?hl=en&as_sdt=0%2C5&q=machine+learning&btnG='

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 '
                  'Safari/537.36 '
}

req = Request(url, headers=headers)
webpage = urlopen(req).read()


with requests.Session() as sesh:
    soup = BeautifulSoup(webpage, 'html5lib')
    titles = []
    links = []
    authors = []
    descriptions = []
    pdf_links_raw = []
    pdf_links = []
    source_year = []
    host_publisher = []
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
    for i in authors:
        print(i)

    print(len(titles), len(descriptions),len(authors), len(links), len(pdf_links), len(source_year), len(host_publisher))
    data = {'Title': titles,
            'Description': descriptions,
            'Authors': authors_str,
            'Hyperlink': links,
            'Document': pdf_links,
            'Source and/or Year': source_year,
            'Host/Publisher': host_publisher}

    df = pd.DataFrame(data)

    df.to_csv('testing.csv')

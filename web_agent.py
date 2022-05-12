import random
import re
import json
import time

from bs4 import BeautifulSoup, Comment
import requests


def extract_information(address, html):
    '''Extract contact information from html, returning a list of (url, category, content) pairs,
    where category is one of PHONE, ADDRESS, EMAIL'''

    # TODO: implement
    results = []
    for match in re.findall('\d\d\d-\d\d\d-\d\d\d\d', str(html)):
        results.append((address, 'PHONE', match))

    for match in re.findall('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', str(html)):
        results.append((address, 'EMAIL', match))

    for match in re.findall('(?:[A-Z][a-zA-Z_.+-]+\s)*[A-Z][a-zA-Z_.+-]+,\s[A-Z][a-zA-Z_.+-]+\s\d{5}', str(html)):
        results.append((address, 'ADDRESS', match.strip()))

    return results


def writelines(filename, data):
    with open(filename, 'w') as fout:
        for d in data:
            print(d, file=fout)


def read_shopping_site():
    my_file = open("sites.json")
    data = json.load(my_file)
    my_file.close()
    return data


def read_search_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36',
        'Accept-Language': 'en'
    }
    time.sleep(0.5 * random.random())
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')

    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)

    res = []
    for i in visible_texts:
        if not i == '\n':
            res.append(i)
    return res


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def search(keyword):
    return []

    # search_query = keyword.replace(' ', '+')
    # sites = read_shopping_site()
    #
    # for site, search_url in sites.items():
    #     # need more cases
    #     pagination = '&page='
    #     if site == 'bestbuy':
    #         pagination = '&cp='
    #     if site == 'ebay':
    #         pagination = '&_pgn='
    #
    #     text = []
    #     base_url = search_url + search_query
    #     for i in range(1, 11):
    #         url = base_url + pagination + str(i)
    #         print("processing " + url)
    #         text.append(read_search_page(url))
    #     writelines(site + "_text", text)


def main():
    search("microwave")


if __name__ == "__main__":
    main()

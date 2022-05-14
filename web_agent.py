import random
import re
import json
import time

from bs4 import BeautifulSoup, Comment
import requests

from urllib import parse 

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

NUM_PAGES = 2

def writelines(filename, data):
    with open(filename, 'w') as fout:
        for d in data:
            print(d, file=fout)


def read_shopping_site():
    my_file = open("sites.json")
    data = json.load(my_file)
    my_file.close()
    return data


def crawl_amazon(url, soup):
    title = []
    price = []
    product_url = []
    try:
        temps = soup.find_all('div', class_="a-section a-spacing-small a-spacing-top-small s-padding-right-small")
        for temp in temps:
            if temp.find('h2'):
                title.append(temp.find('h2').text.strip())

                href = temp.find('a').get('href')
                product_url.append(parse.urljoin(url, href))

                price.append(temp.find('span', class_='a-price').span.text.strip())
    except:
        title = None
        product_url = None
        price = None
    return title, price, product_url


def crawl_walmart(url, soup):
    title = []
    price = []
    product_url = []
    try:
        temps = soup.find_all('div', class_='sans-serif mid-gray relative flex flex-column w-100')
        # ('a', class_='absolute w-100 h-100 z-1')
        for temp in temps:
            title.append(temp.a.find('span', class_='w_EA').text.strip())

            href = temp.a.get('href')
            product_url.append(parse.urljoin(url, href))

            price.append(temp.find('div', class_='b black f5 mr1 mr2-xl lh-copy f4-l').text.strip())
    except:
        title = None
        product_url = None
        price = None
    return title, price, product_url

def crawl_bestbuy(url, soup):
    title = []
    price = []
    product_url = []
    try:
        temps = soup.find_all('div', class_='list-item')
        for temp in temps:
            title.append(temp.h4.a.text.strip())

            href = temp.h4.a.get('href')
            product_url.append(parse.urljoin(url, href))

            price.append(temp.find('div', class_='priceView-hero-price priceView-customer-price').find('span').text.strip())
    except:
        title = None
        product_url = None
        price = None
    return title, price, product_url

def crawl_ebay(url, soup):
    title = []
    price = []
    product_url = []
    try:
        temps = soup.find_all('a', _sp="p2351460.m1686.l7400")
        for temp in temps:
            title.append(temp.find('h3').text.strip())

            href = temp.get('href')
            product_url.append(parse.urljoin(url, href))

            price.append(temp.find('span', class_='s-item__price').find('span', class_='BOLD').text.strip())
    except:
        title = None
        product_url = None
        price = None
    return title, price, product_url

crawl_func = {
    'amazon': crawl_amazon,
    'walmart': crawl_walmart,
    'bestbuy': crawl_bestbuy,
    'ebay': crawl_ebay
}

def read_search_page(site, base_url, num_pages=2):

    title = []
    price = []
    product_url = []
    for i in range(1,num_pages+1):
        # e.g. url = 'https://www.walmart.com/search?q=toothpaste&page=' + str(i)
        url = base_url + str(i)
        print("processing " + url)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36',
            'Accept-Language': 'en'
        }
        time.sleep(0.5 * random.random())
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.content, 'html.parser') # : utf-8?
        # soup = BeautifulSoup(url, 'lxml') # 'html.parser'

        t, p, u = crawl_func[site](url, soup)
        if t and p and u: # results are not empty
            title += t
            price += p
            product_url += u

    # print(title)
    # print(product_url[0])
    # print(price)

    assert len(title) == len(product_url)
    assert len(title) == len(price)

    data = []
    data_dict = {}
    for t,p,u in zip(title, price, product_url):
        ### data.append({'title': t, 'price': p, 'url': u})
        if (t,p) not in data_dict:
            data_dict[(t,p)] = u
            data.append([t,p,u])
        # else is duplicate, ignore

    return data


# def tag_visible(element):
#     if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
#         return False
#     if isinstance(element, Comment):
#         return False
#     return True


def process_search_result(keyword, data, option):
    df = pd.DataFrame(data, columns=['title', 'price', 'url'])

    # compute title-query similarity scores
    tfidf_vectorizer = TfidfVectorizer(analyzer='char') # tfidf_vectorizer.fit()
    titles = df['title'].tolist()
    mat_titles = tfidf_vectorizer.fit_transform(titles)
    vec_keyword = tfidf_vectorizer.transform(keyword.split())
    vals = cosine_similarity(vec_keyword, mat_titles)[0]
    df['sim_score'] = vals

    # extract price values
    temp = [p.strip('$').replace(',','') for p in df['price'].tolist()] 
    df['price_vals'] = [float(p) if p.replace('.','').isdigit() else pd.NA for p in temp]

    # sort result
    if option == "price":
        sorted_df = df.sort_values(by = ['price_vals', 'sim_score'], ascending = [True, False], na_position = 'last')
    elif option == "relevance":
        sorted_df = df.sort_values(by = ['sim_score', 'price_vals'], ascending = [False, True], na_position = 'last')
    else: # by source (shopping site)
        sorted_df = df
    return sorted_df[['title','price','url']] # exclude vals and scores in table returned to .html


def search(keyword, option):
    # return []

    search_query = keyword.replace(' ', '+')
    sites = read_shopping_site()

    data = []

    for site, search_url in sites.items():
        # need more cases
        pagination = '&page='
        if site == 'bestbuy':
            pagination = '&cp='
        if site == 'ebay':
            pagination = '&_pgn='

        print(site)
        
        base_url = search_url + search_query + pagination
        data += read_search_page(site, base_url, num_pages=NUM_PAGES)
    
    # writelines("data_txt", data)

    # process search result: dataframe of info, ranked by price and similarity scores 
    return process_search_result(keyword, data, option)


def main():
    search("microwave", "price")


if __name__ == "__main__":
    main()

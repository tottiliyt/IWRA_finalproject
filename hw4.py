import logging
import re
import sys
import json
from bs4 import BeautifulSoup
from queue import Queue
from urllib import parse, request
from difflib import SequenceMatcher


logging.basicConfig(level=logging.DEBUG, filename='output.log', filemode='w')
visitlog = logging.getLogger('visited')
extractlog = logging.getLogger('extracted')


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def parse_links(root, html):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string
            if not text:
                text = ''
            text = re.sub('\s+', ' ', text).strip()
            yield (parse.urljoin(root, link.get('href')), text)


def parse_links_sorted(root, html):
    soup = BeautifulSoup(html, 'html.parser')
    result = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string
            if not text:
                text = ''
            text = re.sub('\s+', ' ', text).strip()
            result.append((similar(root, parse.urljoin(root, link.get('href'))), parse.urljoin(root, link.get('href')), text))

    result.sort(key=lambda y: y[0], reverse=True)
    return [(x[1], x[2]) for x in result]


def get_links(url):
    res = request.urlopen(url)

    return list(parse_links(url, res.read()))


def get_nonlocal_links(url):
    '''Get a list of links on the page specificed by the url,
    but only keep non-local links and non self-references.
    Return a list of (link, title) pairs, just like get_links()'''

    res = request.urlopen(url)
    html = res.read()

    soup = BeautifulSoup(html, 'html.parser')

    filtered = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string
            if not text:
                text = ''
            text = re.sub('\s+', ' ', text).strip()

            new_url = parse.urljoin(url, link.get('href'))
            domain = parse.urlparse(url). netloc
            if domain not in new_url:
                filtered.append((new_url, text))

    return filtered


def get_local_links(url):
    res = request.urlopen(url)
    html = res.read()

    soup = BeautifulSoup(html, 'html.parser')

    filtered = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string
            if not text:
                text = ''
            text = re.sub('\s+', ' ', text).strip()

            new_url = parse.urljoin(url, link.get('href'))
            domain = parse.urlparse(url). netloc
            if domain in new_url:
                filtered.append((new_url, text))

    return filtered


def crawl(root, wanted_content=[], within_domain=True):
    '''Crawl the url specified by `root`.
    `wanted_content` is a list of content types to crawl
    `within_domain` specifies whether the crawler should limit itself to the domain of `root`
    '''
    # TODO: implement

    queue = Queue()
    queue.put(root)

    visited = []
    extracted = []

    get_links_function = get_local_links if within_domain else get_nonlocal_links

    while not queue.empty() and len(visited) < 100:
        print("visited: ", len(visited), "queue: ", queue.qsize())
        url = queue.get()
        try:
            req = request.urlopen(url)
            content_type = req.info().get_content_type()
            if len(wanted_content) > 0 and content_type not in wanted_content:
                continue

            html = req.read()

            visited.append(url)
            visitlog.debug(url)

            for ex in extract_information(url, html):
                extracted.append(ex)
                extractlog.debug(ex)

            for link, title in get_links_function(url):
                if link not in visited:
                    queue.put(link)

        except Exception as e:
            print(e, url)

    return visited, extracted


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

def load_personal_info():
    f = open('personal_info.json')

    data = json.load(f)

    f.close()

    return data

def main():
    # site = sys.argv[1]

    personal_info = load_personal_info()



    #
    # links = get_links(site)
    # writelines('links.txt', links)
    #
    # nonlocal_links = get_nonlocal_links(site)
    # writelines('nonlocal.txt', nonlocal_links)
    #
    # local_links = get_local_links(site)
    # writelines('local.txt', local_links)
    #
    # visited, extracted = crawl(site, [], True)
    # writelines('visited.txt', visited)
    # writelines('extracted.txt', extracted)

    # for match in re.findall('(?:[A-Z][a-zA-Z_.+-]+\s)*[A-Z][a-zA-Z_.+-]+,\s(?:[A-Z][a-zA-Z_.+-]+\s)?[A-Z][a-zA-Z_.+-]+\s\d{5}', "I like ny byc New Jersey, New York 20202"):
    #     print(match)

if __name__ == '__main__':
    main()

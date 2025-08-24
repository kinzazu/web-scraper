import os

import requests
import re
from bs4 import BeautifulSoup
import string


def check_article(soup):
    if soup.article:
        return True
    else:
        return False


def check_website(url):
    if "nature.com" not in url:
        return False
    return True


def get_resp(session,url):
    headers = {'Accept-Language': 'en-US,en;q=0.5'}
    response = session.get(url, headers=headers)
    return response


def parse_main_page(soup, session, article_type):
    # articles = soup.find_all('article', attrs={'class': 'u-full-height c-card c-card--flush'})
    news_articles = soup.find_all('span', attrs={"class": "c-meta__type"}, string=article_type)
    collected_articles = []
    for article_span in news_articles:
        article =  article_span.find_parent('article')

        name = article.a.text
        name = name.replace(' ', '_')
        # name = name.replace('’', '')
        name = re.sub(f'[{re.escape(string.punctuation)}]', '_', name)
        name = name.strip("_")


        prefix = "https://www.nature.com"
        link = article.find('a', attrs={'data-track-action':"view article"})['href']

        page_content = get_resp(session, prefix + link)
        soup = prepare_soup(page_content)
        content = soup.find('p', attrs={"class": "article__teaser"})

        if content is not None:
            collected_articles.append({'name': name, 'link': link, 'content': content.text})
        else:
            collected_articles.append({'name': name, 'link': link, 'content': None})

    return collected_articles


def prepare_soup(http_response):
    if http_response.status_code == requests.codes.ok:
        soup = BeautifulSoup(http_response.content, 'html.parser')
    else:
        soup = None
    return soup

def write_to_file(collected_articles, page):
    for article in collected_articles:
        if article['content'] is not None:
            with open(f'Page_{page}/{article["name"]}.txt', 'wb', ) as f:
                f.write(bytes(article['content'], 'utf-8'))

    titles = [article['name'] for article in collected_articles]
    print(f'Saved articles: {titles}')

def create_dirs(pages):
    for page in range(1, pages+1):
        try:
            os.mkdir(f'Page_{page}')
        except FileExistsError:
            pass


def main():
    with requests.Session() as session:
        count_pages = int(input('Enter number of pages to scrape: '))
        article_type = input('Enter article type: ')
        url = "https://www.nature.com/nature/articles?sort=PubDate&year=2020&page="
        create_dirs(count_pages)
        for page in range(1, count_pages + 1):
            resp = get_resp(session,url + str(page))
            soup = prepare_soup(resp)
            get_articles = parse_main_page(soup, session, article_type)
            write_to_file(get_articles, page)


if __name__ == '__main__':
    main()
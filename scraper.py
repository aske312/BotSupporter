# -*- coding: utf-8 -*-

import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
from lib.config import *
from lib.exception import *

db = config(filename='lib/config.ini', section='pg3')
date_now = datetime.now()
base, pool = {}, {}


class ScraperNews:
    def __int__(self, headers):
        self.headers = headers
        self.news_pool = {}

    def _parser_url(self, url):
        s = requests.Session()
        print('REQUEST')
        response = s.get(url=url, headers=self.headers)
        if response.ok:
            html_raw = bs(response.text, 'lxml')
        else:
            raise ResponseNotOk('Response not ok, maybe time out.')
        return html_raw

    def kp_ru(self, url):
        news_pool = {}
        raw_html = self._parser_url(url)
        pool_html = raw_html.find_all('div', class_='sc-1tputnk-0 bbyOTY')
        news = pool_html[0].find_all('a', class_='sc-1tputnk-2 drlShK')
        news_pool['href'] = url + news[0]['href'].replace('/online/', '')
        news_pool['area'] = pool_html[0].a.text
        news_pool['title'] = news[0].text
        sql = f'''SELECT href FROM news WHERE href = '{news_pool['href']}' '''
        if not SqlDataBase(db, sql).raw():
            for link in self._parser_url(news_pool['href']).select("img[src^=http]"):
                lnk = link["src"]
                news_pool['img'] = lnk
                # with open(basename(lnk), "wb") as f:
                #     f.write(requests.get(lnk).content)
                # lnk = re.findall('[\w\-\_]+\.\w{2,5}$', lnk)
                # news_pool['img'] = lnk[0]   # os.path.dirname(os.path.abspath(__file__)) + '\\' +
                # print(news_pool)
        return news_pool

    def insert_to_base(self, news):
        if len(news) > 3:
            pool['date'] = f"'{str(date_now)}'"
            pool['href'] = f"'{str(news['href'])}'"
            pool['area'] = f"'{str(news['area'])}'"
            pool['title'] = f"'{str(news['title'])}'"
            pool['img'] = f"'{'' + str(news['img'])}'"
            base['news'] = pool
            SqlDataBase(base=db, request=base).insert()
        else:
            print('News exists')

    def run(self, url):
        if 'kp.ru' in url:
            self.insert_to_base(self.kp_ru(url))


if __name__ == "__main__":
    parser = ScraperNews()
    parser.headers = config(filename='lib/config.ini', section='header_request')
    parser.run(url='https://www.kp.ru/online/')


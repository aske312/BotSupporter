# -*- coding: utf-8 -*-
import hashlib
import requests
from datetime import datetime
from lib.config import config, SqlDataBase


date_now = datetime.now()
db = config(filename='lib/config.ini', section='pg3')
url = f'https://s02.api.yc.kpcdn.net/content/api/1/pages/get.json?' \
      f'pages.age.month={date_now.month}&pages.age.year={date_now.year}&' \
      f'pages.direction=page&pages.number=999&pages.target.class=100&pages.target.id=0'


def body_hash(data):
    body = data
    bh = hashlib.md5()
    bh.update(str(body).encode())
    return str(bh.hexdigest())


def kp_news(json):
    result = {}
    for state in json['childs']:
        sql = f'''SELECT bh FROM news WHERE bh = 
        '{body_hash(f"URL:{state['image']['url']} TITLE:{state['ru']['title']}")}' '''
        if not SqlDataBase(db, sql).raw():
            result['source'] = 'kp.ru'
            result['bh'] = body_hash(f"URL:{state['image']['url']} TITLE:{state['ru']['title']}")
            result['img_url'] = f"https://s10.stc.yc.kpcdn.net{state['image']['url']}"
            result['title'] = state['ru']['title']
            result['description'] = state['ru']['description']
        break   # stop 1 news
    return result


def request_json():
    s = requests.Session()
    json_response = {}
    response = s.get(url=url, headers=config(filename='lib/config.ini', section='header_request'))
    try:
        if response.ok:
            json_response = response.json()
    except Exception as error:
        print(f'WARN: {error}')
    finally:
        _insert_db(kp_news(json_response))


def _insert_db(news):
    if len(news) != 0:
        pool, base = {}, {}
        pool['date'] = f"'{str(date_now)}'"
        pool['source'] = f"'{news['source']}'"
        pool['bh'] = f"'{str(news['bh'])}'"
        pool['title'] = f"'{news['title']}'"
        pool['description'] = f"'{news['description']}'"
        pool['img_url'] = f"'{news['img_url']}'"
        base['news'] = pool
        SqlDataBase(base=db, request=base).insert()


request_json()

# -*- coding: utf-8 -*-

import time
import hashlib
import requests
import threading
from tqdm import tqdm
from multiprocessing import Process
from datetime import datetime
from lib.config import config, SqlDataBase

date_now = datetime.now()


def threaded(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs).start()
    return wrapper


class _ParserNews:
    def __int__(self, db, headers):
        self.db = db
        self.headers = headers

    @threaded
    def json_response(self, url):
        s = requests.Session()
        json_response = {}
        response = s.get(url=url, headers=self.headers)
        try:
            if response.ok:
                json_response = response.json()
        except Exception as error:
            print(f'WARN: {error}')
        finally:
            return self._insert(self.kp_json(json_response))

    def _insert(self, news):
        if news:
            pool, base = {}, {}
            pool['date'] = f"'{str(datetime.now())}'"
            pool['source'] = f"'{news['source']}'"
            pool['bh'] = f"'{str(news['bh'])}'"
            pool['title'] = f"'{news['title']}'"
            pool['description'] = f"'{news['description']}'"
            pool['img_url'] = f"'{news['img_url']}'"
            base['news'] = pool
            SqlDataBase(base=self.db, request=base).insert()
            return 'source update'
        return 'no new source'

    def _body_hash(self, data):
        body = data
        bh = hashlib.md5()
        bh.update(str(body).encode())
        return str(bh.hexdigest())

    def kp_json(self, json):
        result, poll = {}, []
        for state in json['childs']:
            now = datetime.now()
            then = datetime.strptime(str(state['meta'][1]['value']).replace('T', ' '), '%Y-%m-%d %H:%M:%S')
            duration_in_s = (now - then).total_seconds()
            if divmod(duration_in_s, 60)[0] > 5:
                break
            bh = self._body_hash(f"URL:https://www.kp.ru/online/{state['@type'][0]}/{state['@id']}/ TITLE:{state['ru']['title']}")
            sql = f'''SELECT bh FROM news WHERE bh = '{bh}' '''
            if len(SqlDataBase(self.db, sql).raw()) == 0:
                result['source'] = f"https://www.kp.ru/online/{state['@type'][0]}/{state['@id']}/"
                result['bh'] = bh
                result['img_url'] = f"https://s10.stc.yc.kpcdn.net{state['image']['url']}"
                result['title'] = state['ru']['title']
                result['description'] = state['ru']['description']
                poll.append(result)
            break   # stop 1 news
        for new in poll:
            return new


def runner():
    start_time = time.time()
    start = _ParserNews()
    start.db = config(filename='lib/config.ini', section='pg3')
    start.headers = config(filename='lib/config.ini', section='header_request')
    # url_list = ['https://tass.ru/tgap/api/v1/messages/?lang=ru&limit=50']
    url_list, jobs = [], []
    for num in [999, 1000]:
        url = f'https://s02.api.yc.kpcdn.net/content/api/1/pages/get.json?' \
              f'pages.age.month={date_now.month}&pages.age.year={date_now.year}&' \
              f'pages.direction=page&pages.number={num}&pages.target.class=100&pages.target.id=0'
        url_list.append(url)
    for url in tqdm(url_list, ncols=100, desc=f'check url in', colour='red'):
        process = Process(target=start.json_response(url=url))
        process.start()
        jobs.append(process)
    for job in tqdm(jobs, ncols=100, desc=f'start parsing url', colour='green'):
        job.join()
    print(f"***** Start:{date_now} - {round(float(time.time() - start_time), 5)} seconds check *****")


if __name__ == "__main__":
    while True:
        runner()
        time.sleep(15)

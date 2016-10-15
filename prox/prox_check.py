#!/usr/bin/env python
from urllib3.contrib.socks import SOCKSProxyManager
import urllib3
from urllib.request import urlopen
from threading import Thread
from collections import defaultdict
from argparse import ArgumentParser
import os
import time
import logging
import json
from random import shuffle
import gzip

from .database import Check, init_database

THREADS = 50 
# http://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#module-urllib3.util.timeout
CONNECT_TIMEOUT = 1
READ_TIMEOUT = 3 # this is not TOTAL READ TIME timeout


def download_plist(url):
    res = urlopen(url)
    lines = res.read().decode('ascii').splitlines()
    return lines


def check_worker(task_iter, proxy_type, stat):
    while True:
        try:
            proxy = next(task_iter)
        except StopIteration:
            break
        else:
            if proxy_type == 'socks':
                pool = SOCKSProxyManager('socks5://%s' % proxy)
            else:
                pool = urllib3.ProxyManager('http://%s' % proxy)
            retries = urllib3.Retry(connect=False, read=False, redirect=10)
            timeout = urllib3.Timeout(connect=CONNECT_TIMEOUT,
                                      read=READ_TIMEOUT)
            op = {
                'status': None,
                'connect_time': None,
                'read_time': None,
                'error': None,
            }
            try:
                start_time = time.time()
                res = pool.request('GET', 'http://yandex.ru/robots.txt',
                                   retries=retries, timeout=timeout,
                                   preload_content=False)
                connected_time = time.time()
                op['connect_time'] = round(connected_time - start_time, 2)
                data = res.read()
                op['read_time'] = round(time.time() - connected_time, 2)
            except Exception as ex:
                error = type(ex).__name__
                op['error'] = error
                if error in ('NewConnectionError', 'ConnectTimeoutError'):
                    op['status'] = 'connect_fail' 
                elif error in ('ProtocolError', 'ReadTimeoutError',):
                    op['status'] = 'read_fail'
                else:
                    raise Exception('Unexpected error: %s' % error)
            else:
                if b'Disallow: /adresa-segmentator' in data:
                    op['status'] = 'ok'
                else:
                    op['status'] = 'data_fail'
            stat['count'][op['status']] += 1
            stat['ops'][proxy].append(op)
            if op['status'] == 'ok':
                stat['count']['ok_connect_time'] += op['connect_time']
                stat['count']['ok_read_time'] += op['read_time']


def get_stat_fails(stat):
    return sum(stat['count'][x] for x in ['connect_fail', 'read_fail',
                                          'data_fail'])


def render_stat_counts(name, stat):
    fail = get_stat_fails(stat)
    return ('[%s] OK: %d, FAIL: %d (CONNECT: %d, READ: %d, DATA: %d)' % (
            name,
            stat['count']['ok'],
            fail,
            stat['count']['connect_fail'],
            stat['count']['read_fail'],
            stat['count']['data_fail']))


def stat_worker(name, stat):
    while True:
        time.sleep(3)
        print(render_stat_counts(name, stat))


def normalize_plist_url(url):
    if not url.startswith(('http://', 'https://', 'file://')):
        url = os.path.join(os.path.abspath(os.getcwd()), url)
        url = 'file://localhost' + url
    return url


def check_plist(plist_url, proxy_type, threads=THREADS,
                limit=None, name=None, save=False):
    if not name:
        name = plist_url.split('/')[-1]

    if save:
        init_database()
    plist_url = normalize_plist_url(plist_url)
    plist = download_plist(plist_url)
    shuffle(plist)

    def task_iter_func(plist, limit=None):
        for count, proxy in enumerate(plist):
            yield proxy
            if limit and (count + 1) >= limit:
                break

    task_iter = task_iter_func(plist, limit)
    stat = {
        'count': {
            'ok': 0,
            'connect_fail': 0,
            'read_fail': 0,
            'data_fail': 0,
            'ok_connect_time': 0,
            'ok_read_time': 0,
        },
        'ops': defaultdict(list),
    }
    
    th = Thread(target=stat_worker, args=[name, stat])
    th.daemon = True
    th.start()
    start = time.time()

    pool = []
    for x in range(threads):
        th = Thread(target=check_worker, args=[task_iter, proxy_type, stat])
        th.start()
        pool.append(th)
    for th in pool:
        th.join()
    session_time = time.time() - start
    print(render_stat_counts(name, stat))
    
    ops_blob = gzip.compress(json.dumps(stat['ops']).encode('utf-8'))

    if save:
        Check.create(
            name=name,
            count_ok=stat['count']['ok'],
            count_fail=get_stat_fails(stat),
            count_connect_fail=stat['count']['connect_fail'],
            count_read_fail=stat['count']['read_fail'],
            count_data_fail=stat['count']['data_fail'],
            avg_connect_time=round(stat['count']['ok_connect_time']
                                   / (stat['count']['ok'] or 1), 2),
            avg_read_time=round(stat['count']['ok_read_time']
                                / (stat['count']['ok'] or 1), 2),
            session_time=round(session_time, 2),
            ops=ops_blob,
        )


def main():
    parser = ArgumentParser()
    parser.add_argument('proxy_type')
    parser.add_argument('plist_url')
    parser.add_argument('-l', '--limit', type=int)
    parser.add_argument('-t', '--threads', default=THREADS, type=int)
    parser.add_argument('-n', '--name')
    parser.add_argument('-s', '--save', action='store_true', default=False)
    opts = parser.parse_args()
    check_plist(opts.plist_url, limit=opts.limit, proxy_type=opts.proxy_type)


if __name__ == '__main__':
    main()

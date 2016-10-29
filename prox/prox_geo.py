#!/usr/bin/env python
from urllib.request import urlopen
from collections import defaultdict, Counter
from argparse import ArgumentParser
import os
from geoip import open_database

from .database import Check, init_database
from prox.prox_check import normalize_plist_url, download_plist
from prox import country_database_file

def download_plist(url):
    res = urlopen(url)
    lines = res.read().decode('ascii').splitlines()
    return lines


def normalize_plist_url(url):
    if not url.startswith(('http://', 'https://', 'file://')):
        url = os.path.join(os.path.abspath(os.getcwd()), url)
        url = 'file://localhost' + url
    return url


def parse_geo(plist_url, stat=False, include=None, exclude=None,
              exclude_list=None):
    include = [x.strip() for x in include.split(',')] if include else []
    exclude = [x.strip() for x in exclude.split(',')] if exclude else []
    if exclude_list:
        ex_plist = download_plist(normalize_plist_url(exclude_list))
        ex_ips = set([x.split(':')[0] for x in ex_plist])
    else:
        ex_ips = set()
    geo = open_database(country_database_file)
    plist_url = normalize_plist_url(plist_url)
    plist = download_plist(plist_url)
    reg = defaultdict(int)
    for addr in plist:
        ip = addr.split(':')[0]
        match = geo.lookup(ip)
        code = (match.country or '--').lower()
        if include and code not in include:
            continue
        elif exclude and code in exclude:
            continue
        elif ip in ex_ips:
            continue
        else:
            reg[code] += 1
            if not stat:
                print(addr)
    if stat:
        for code, count in sorted(reg.items(), key=lambda x: x[1]):
            print('%s:%d' % (code, count))
        print('total:%d' % sum(x for x in reg.values()))


def main():
    parser = ArgumentParser()
    parser.add_argument('plist_url')
    parser.add_argument('-s', '--stat', action='store_true', default=False)
    parser.add_argument('-i', '--include')
    parser.add_argument('-x', '--exclude')
    parser.add_argument('--exclude-list')
    opts = parser.parse_args()
    parse_geo(opts.plist_url,
              stat=opts.stat,
              include=opts.include,
              exclude=opts.exclude,
              exclude_list=opts.exclude_list)


if __name__ == '__main__':
    main()

#!/usr/bin/env python
from argparse import ArgumentParser
import yaml
from check_plist import check_plist

def main():
    parser = ArgumentParser()
    parser.add_argument('task_file')
    opts = parser.parse_args()
    task_list = yaml.load(open(opts.task_file))
    for task in task_list:
        print('Checking %s' % (task['plist_url']))
        check_plist(**task)



if __name__ == '__main__':
    main()

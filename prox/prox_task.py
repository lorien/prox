#!/usr/bin/env python
from argparse import ArgumentParser
import yaml
from multiprocessing import Process, Queue
from queue import Empty
from copy import deepcopy

from .prox_check import check_plist


def worker(global_config, taskq):
    while True:
        try:
            task = taskq.get_nowait()
        except Empty:
            break
        else:
            print('Checking %s' % (task['plist_url']))
            opts = deepcopy(global_config)
            opts.update(task)
            check_plist(**opts)


def main():
    parser = ArgumentParser()
    parser.add_argument('task_file')
    parser.add_argument('-w', '--workers', type=int, default=1)
    opts = parser.parse_args()

    config = yaml.load(open(opts.task_file))
    taskq = Queue()
    for task in config['task']:
        taskq.put(task)
    global_config = (config.get('config', {}) or {})

    pool = []
    for x in range(opts.workers):
        pr = Process(target=worker, args=[global_config, taskq])
        pr.start()
        pool.append(pr)
    for pr in pool:
        pr.join()


if __name__ == '__main__':
    main()

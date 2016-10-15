#!/usr/bin/env python
from argparse import ArgumentParser
import yaml
from multiprocessing import Process, Queue
from queue import Empty

from .prox_check import check_plist


def worker(taskq):
    while True:
        try:
            task = taskq.get_nowait()
        except Empty:
            break
        else:
            print('Checking %s' % (task['plist_url']))
            check_plist(**task)


def load_task_queue(task_file):
    taskq = Queue()
    for task in yaml.load(open(task_file)):
        taskq.put(task)
    return taskq


def main():
    parser = ArgumentParser()
    parser.add_argument('task_file')
    parser.add_argument('-w', '--workers', type=int, default=1)
    opts = parser.parse_args()
    taskq = load_task_queue(opts.task_file)
    pool = []
    for x in range(opts.workers):
        pr = Process(target=worker, args=[taskq])
        pr.start()
        pool.append(pr)
    for pr in pool:
        pr.join()


if __name__ == '__main__':
    main()

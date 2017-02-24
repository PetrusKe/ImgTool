#!/usr/bin/env python
# -*- coding: utf-8 -*
# Written by - CSDN:Mars Loo的博客

import threading, time, signal
import multiprocessing
import sys
import os
import subprocess
import ctypes


def printA():
    signal.signal(signal.SIGINT, quit)
    id = os.getpid()
    print('A' + str(id))
    i = 0
    while i < 100000000:
        # print(i)
        i += 1
    print('sdadsad')


def printB():
    signal.signal(signal.SIGINT, quit)
    id = os.getpid()
    print('2' + str(id))
    i = 0
    while i < 20000000000000000:
        # print(i)
        i += 1
    print('sdadsad')


def quit(signum, frame):
    id1 = os.getpid()
    os.kill(id1, signal.CTRL_BREAK_EVENT)
    # os.popen('TASKKILL /F /PID ' + str(id1))


if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit)
    print('1' + str(os.getpid()))
    pool = multiprocessing.Pool(8)
    pool.apply_async(printA)
    pool.apply_async(printB)
    pool.apply_async(printA)
    pool.apply_async(printB)
    pool.apply_async(printA)
    pool.apply_async(printB)
    pool.apply_async(printA)
    pool.apply_async(printB)
    pool.close()

    pool.join()


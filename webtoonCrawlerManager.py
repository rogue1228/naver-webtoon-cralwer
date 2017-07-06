# -*- coding: utf-8 -*-
import os
import sys
import time
import json

import signal
import subprocess

from configparser import ConfigParser

import webtoonCrawler as WC

processList = set()
processCnt = 1
processName = 'webtoonCrawler'
processFileName = processName + '.py'

configPath = './config.ini'
config = ConfigParser()
config.read(configPath)

DEFAULT = 'default'
CRAWL_LIST = 'crawl_list'
LAST_NO = 'last_no'


def subprocess_setup():
    # Python installs a SIGPIPE handler by default. This is usually not what
    # non-Python subprocesses expect.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def timePrint():
    now = time.localtime()
    text = "%02d/%02d %02d:%02d:%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    return text
    
def excuteProcess(fileName, toonId):
    cmd = ['python3', fileName, toonId]
    p = subprocess.Popen(cmd, preexec_fn=subprocess_setup)
    print(p.pid)
    processList.add(p.pid)

def terminateProcess(pid):
    cmd = ['kill', '-9', pid]
    subprocess.Popen(cmd, preexec_fn=subprocess_setup)

def printToonList():
    for toonId in getToonList():
        toonName = WC.getToonName(toonId)
        print('{toonName} : {toonId}'.format(toonId=toonId, toonName=toonName))

def getToonList():
    if DEFAULT in config.sections():
        strToonList = config[DEFAULT][CRAWL_LIST]
        return json.loads(strToonList)
    return list()

def setToonList(toonId):
    toonList = list()
    if checkDefaultConfig():
        toonList = getToonList()
    if toonId not in toonList:
        toonList.append(toonId)
        print('added toonId')
    strToonList = json.dumps(toonList)

    config[DEFAULT].update({CRAWL_LIST:strToonList})
    saveConfig()

def checkDefaultConfig():
    if DEFAULT not in config.sections():
        config.add_section(DEFAULT)
        with open(configPath, 'w') as f:
            config.write(f)
        return False
    return True

def saveConfig():
    with open(configPath, 'w') as f:
        config.write(f)

def removeToonList(toonId):
    toonList = list()
    if checkDefaultConfig():
        toonList = getToonList()
    toonList.remove(toonId)
    print('remove toonId')
    strToonList = json.dumps(toonList)

    config[DEFAULT].update({CRAWL_LIST:strToonList})
    saveConfig()
    

def crawlToon():
    print('#############################')
    print('#  crawler start')
    print('#', timePrint())
    print('#############################')
    sys.stdout.flush()
    toonList = getToonList()
    print(toonList)
    while True:
        if len(toonList) < 1:
            break
        toonId = toonList.pop()
        print('start toon crawl toonid : {}'.format(toonId))
        print(toonList)
        excuteProcess(processFileName, toonId)
        time.sleep(5)
        sys.stdout.flush()

    print('#############################')
    print('#  crawler end')
    print('#', timePrint())
    print('#############################')
    sys.stdout.flush()

def test(toonId=119874):
    excuteProcess(processFileName, toonId)
        
if __name__ == '__main__':

    order = sys.argv[1]    
    if order == "crawl":
        crawlToon()
    elif order == "add":
        toonId = sys.argv[2]
        if toonId:
            setToonList(toonId)
        printToonList()
    elif order == "remove":
        toonId = sys.argv[2]
        if toonId:
            removeToonList(toonId)
        printToonList()
    elif order == "list":
        printToonList()
    else:
        print("사용 할 수 없는 명령입니다.")

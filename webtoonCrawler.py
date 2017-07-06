# -*- coding: utf-8 -*-
import sys
import os

from urllib.request import urlopen
from urllib.parse import urljoin
from io import BytesIO
from configparser import ConfigParser

from bs4 import BeautifulSoup
# sudo apt-get install python3-bs4

from PIL import Image
# sudo apt-get install python3-image
# sudo apt-get install python3-pil
# from cStringIO import StringIO

toonListURL = "http://m.comic.naver.com/webtoon/list.nhn?titleId={titleId}&page={page}"
toonDetailURL = "http://m.comic.naver.com/webtoon/detail.nhn?titleId={titleId}&no={no}"

configPath = './config.ini'
config = ConfigParser()
config.read(configPath)

def getLastNo(toonId):
    toonId = str(toonId)
    if toonId in config.sections():
        return config[toonId]['last_no']
    return 0

def setLastNo(toonId, lastNo):
    toonId = str(toonId)
    lastNo = str(lastNo)
    if toonId not in config.sections():
        config.add_section(toonId)
    config[toonId].update({'last_no':lastNo})
    with open(configPath, 'w') as f:
        config.write(f)

def getToonList(toonId):
    url = toonListURL.format(titleId=toonId, page=1)
    conn = urlopen(url)
    soup = BeautifulSoup(conn.read(), 'lxml')
    toonPage = soup.find('ul', class_='toon_lst lst2 lst_episode')
    toonList = toonPage.find_all('li')
    for toonItem in toonList:
        toonURL = toonItem.a.get('href')
        toonTitle = toonItem.a.find('div', class_="toon_info").find('span', class_="toon_name").find('span').string.strip()
        print('{toonTitle} : {toonURL}'.format(toonTitle=toonTitle, toonURL=toonURL))
        yield toonURL, toonTitle

def getToonImg(toonId, page):
    url = toonDetailURL.format(titleId=toonId, no=page)
    conn = urlopen(url)
    print('url : {}'.format(url))
    soup = BeautifulSoup(conn.read(), 'lxml')
    # toonPage = soup.find('div', class_='wt_viewer')
    toonPage = soup.find('div', class_='toon_view_lst')
    toonList = toonPage.find_all('img')
    for toonItem in toonList:
        imgUrl = toonItem.get('src')
        if 'transparency' in imgUrl:
            imgUrl = toonItem.get('data-original')
        yield imgUrl

def getToonTitle(toonId, page):
    url = toonDetailURL.format(titleId=toonId, no=page)
    conn = urlopen(url)
    print('url : {}'.format(url))
    soup = BeautifulSoup(conn.read(), 'lxml')
    toonTitleBar = soup.find('div', class_='viewer_fixed viewerGnb hide')
    if toonTitleBar:
        toonTitle = toonTitleBar.h1.string
        return toonTitle
    return None

def checkMaxCount(toonId):
    toonList = getToonList(toonId)
    for detailURL, detailTitle in toonList:
        toonURLSplit = detailURL.split('?')
        toonParams = toonURLSplit[1].split('&')
        for toonParam in toonParams:
            tParamSplit = toonParam.split('=')
            tParamKey = tParamSplit[0]
            tParamValue = tParamSplit[1]
            if tParamKey == 'no':
                return tParamValue

def getToonName(toonId):
    url = toonListURL.format(titleId=toonId, page=1)
    conn = urlopen(url)
    soup = BeautifulSoup(conn.read(), 'lxml')
    toonName = soup.find('span', class_='title')
    return toonName.string

def imagePaste(imgURLList):
    maxHeight = 0
    tmpImgList = list()
    maxWidth = 0
    for imgURL in imgURLList:
        print('imgURL : {}'.format(imgURL))
        if imgURL == "" or imgURL is None:
            continue
        tmpImgFile = BytesIO(urlopen(imgURL).read())
        tmpImg = Image.open(tmpImgFile)
        tmpImgList.append(tmpImg)
        width, height = tmpImg.size
        if maxWidth < width :
            maxWidth = width
        maxHeight += height
    img = Image.new("RGB", (maxWidth, maxHeight))
    lastHeight = 0
    for tmpImg in tmpImgList:
        img.paste(tmpImg, (0, lastHeight))
        width, height = tmpImg.size
        lastHeight += height
    return img

def main(toonId):
    maxCount = checkMaxCount(toonId)
    maxCount = int(maxCount) + 1
    minCount = int(getLastNo(toonId)) + 1
    toonName = getToonName(toonId)
    toonPath = './{}/'.format(toonName)
    print('minCount : {}'.format(minCount))
    print('maxCount : {}'.format(maxCount))
    print('toonName : {}'.format(toonName))
    print('toonPath : {}'.format(toonPath))
    if not os.path.exists(toonPath):
        print('toonPath is not exists')
        os.makedirs(toonPath)
    i = minCount
    for i in range(minCount, maxCount):
        toonTitle = getToonTitle(toonId, i)
        if toonTitle is None:
            continue
        imgURLList = getToonImg(toonId, i)
        img = imagePaste(imgURLList)
        fileName = '{}{}_{}.png'.format(toonPath, '%04d' % i, toonTitle)
        img.save(fileName)
        print("Download Complete.. {}".format(fileName))
        setLastNo(toonId, i)

if __name__ == '__main__':
    toonID = sys.argv[1]
    if toonID:
        main(toonID)
    else:
        print("invalid argument")
        pass

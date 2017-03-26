# coding=utf-8
import sys
import os
import urllib
import Queue
import requests
from bs4 import BeautifulSoup

website_url_prefix="http://linux.linuxidc.com/"
local_filepth_prefix="E:\\spider\\linuxidc\\"

initUrl = "http://linux.linuxidc.com/"

#爬取的目录列表页面信息
urlQueue = Queue.Queue()
#爬取的目录对应的文件目录信息
urlToFilePathDict = dict()

#爬取的文件信息
fileQueue = Queue.Queue()
#爬取的文件地址对应的文件名信息
fileUrlAndNameDict = dict()


#初始化url信息
def init():
    urlToFilePathDict[initUrl] = ""
    urlQueue.put(initUrl)


#添加待爬取url信息
def addDirUrl(url, filePrefix):
    urlToFilePathDict[website_url_prefix + url] = filePrefix
    urlQueue.put(website_url_prefix + url)


#添加待爬取url信息
def addFileUrl(url, fileName):
    fileUrlAndNameDict[website_url_prefix + url] = fileName
    fileQueue.put(website_url_prefix + url)
    

#获取目录地址并添加到待爬取队列
def getDirUrlFromHtml(beautifulSoup4, oldFilePrefix):
    folderDict = getInfoFromHtmlByClassType(beautifulSoup4, 'folder_bg')
    for folderUrl, folderPath in folderDict.items():
        addDirUrl(folderUrl, oldFilePrefix + folderPath + '\\')


#获取文件地址并添加到文件队列
def getFilePathFromHtml(beautifulSoup4, oldFilePrefix):
    i = 1
    while True:
        fileDict = getInfoFromHtmlByClassType(beautifulSoup4, 'file_bg' + str(i))
        if len(fileDict) <= 0:
            break
        for fileUrl, fileName in fileDict.items():
            addFileUrl(fileUrl, oldFilePrefix + fileName)
        i += 1


#根据标签获取结果列表    
def getInfoFromHtmlByClassType(beautifulSoup4, classType):
    resultDict = dict()
    targetTags = beautifulSoup4.find_all(class_=classType)
    if targetTags is not None:
        for targetTag in targetTags:
            fileParent = targetTag.td
            if fileParent is not None:
               name = fileParent.div.a.string
               url = fileParent.div.a['href']
               resultDict[url] = name
    return resultDict


#爬取目标页面
def spiderPage(url):
    print '++++++++++++++++++++++++++'
    print '开始爬取页面，地址为' + url
    oldFilePrefix = urlToFilePathDict.get(url)
    print '目录为' + oldFilePrefix
    print '...........'

    response = requests.get(url)
    beautifulSoup4 = BeautifulSoup(response.text, 'html.parser')

    getDirUrlFromHtml(beautifulSoup4, oldFilePrefix)
    getFilePathFromHtml(beautifulSoup4, oldFilePrefix)

    print '爬取当前页面结束'
    print '++++++++++++++++++++++++++'


#下载并保存文件
def downloadFile(url):
    print '++++++++++++++++++++++++++'
    print '开始下载文件，地址为' + url
    fileName = local_filepth_prefix + fileUrlAndNameDict.get(url)
    print '文件名为' + fileName

    checkFile(fileName)
    urllib.urlretrieve(url, fileName)

    print '下载文件结束'
    print '++++++++++++++++++++++++++'


#检查文件的目录，不存在则创建
def checkFile(fileName):
    parentPath = os.path.dirname(fileName)
    if not os.path.isdir(parentPath):
        os.makedirs(parentPath)


#爬取所有页面信息,并下载文件
def spider():
    init()

    while not urlQueue.empty():
        unspiderUrl = urlQueue.get()
        spiderPage(unspiderUrl)

    while not fileQueue.empty():
        fileUrl = fileQueue.get()
        downloadFile(fileUrl)

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    spider()




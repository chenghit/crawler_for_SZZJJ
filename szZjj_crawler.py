#!/usr/bin/env python3
# -*- codeing = utf-8 -*-
from bs4 import BeautifulSoup
import re
import urllib.request, urllib.error
import xlwt
import itertools as it
import pysnooper   #debug tool


findLink = re.compile(r'href="(.+?)"')
findBldLink = re.compile(r'href="(building.+?)"')


findTower = re.compile(r'项目楼栋情况.*?(\S+?栋)', re.S)
findUnit = re.compile(r'座号.*?(\S+?单元)', re.S)
findPrice = re.compile(r'拟售价格.*?(\S+?)元/平方米', re.S)
findFloor = re.compile(r'楼层.*?(\d{1,2})', re.S)
findRoom = re.compile(r'房号.*?(\d{3,4})', re.S)
findGrossArea = re.compile(r'建筑面积.*?(\S+?\d)平方米', re.S)
findNetArea = re.compile(r'户内面积.*?(\S+?\d)平方米', re.S)


base_url = "http://zjj.sz.gov.cn/ris/bol/szfdc/"
project_url = "http://zjj.sz.gov.cn/ris/bol/szfdc/projectdetail.aspx?id=51413"


@pysnooper.snoop()
def main():
    tower_url_list = getTowerUrl(project_url)
    unit_url_list = getUnitLinks(tower_url_list)
    room_url_list = getRoomLinks(unit_url_list)
    room_details = getDetails(room_url_list)
    savepath = "project.xls"
    saveData(room_details, savepath)


# 爬取所有套房的详细信息，返回一个3级嵌套的list
#@pysnooper.snoop()
def getDetails(datalist):
    details = []
    for x in datalist:
        for y in x:
            for z in y:
                url = base_url + z
                details.append(getRoomData(url))
    return details


# 爬取所有楼栋，所有单元，所有套房的URL，返回一个2级嵌套的List
def getRoomLinks(datalist):
    unit_list = []
    for x in datalist:
        room_list = []
        for y in x:
            url = base_url + y
            room_list.append(getRoomUrl(url))
        unit_list.append(room_list)
    return unit_list



# 爬取所有楼栋所有单元的URL，返回一个1级嵌套的list
def getUnitLinks(datalist):

    link_list = []
    for i in datalist:
        url = base_url + i
        link_list.append(getUnitUrl(url))

    return link_list


# 爬取所有楼栋的URL
def getTowerUrl(url):
    html = askURL(url)
    soup = BeautifulSoup(html, "html.parser")    
    item = str(soup.find_all('div', class_="wrap"))
    link_list = re.findall(findBldLink, item)

    i = 0
    for x in link_list:
        link_list[i] = x.replace('&amp;', '&')
        i += 1

    return link_list


# 爬取一栋楼所有单元的URL
def getUnitUrl(url):
    html = askURL(url)
    soup = BeautifulSoup(html, "html.parser")    
    item = str(soup.find_all('div', id="divShowBranch"))
    link_list = re.findall(findLink, item)

    i = 0
    for x in link_list:
        link_list[i] = x.replace('&amp;', '&')
        i += 1

    return link_list


# 爬取套房URL
def getRoomUrl(url):
    html = askURL(url)
    soup = BeautifulSoup(html, "html.parser")    
    item = str(soup.find_all('div', class_="tablebox"))
    link_list = re.findall(findLink, item)
    return link_list


# 爬取套房详细信息
def getRoomData(url):
    datalist = []
    html = askURL(url)
    soup = str(BeautifulSoup(html, "html.parser"))
        
    tower = re.findall(findTower, soup)
    datalist.append(tower)
    unit = re.findall(findUnit, soup)
    datalist.append(unit)
    floor = re.findall(findFloor, soup)
    datalist.append(floor)
    room = re.findall(findRoom, soup)
    datalist.append(room)
    price = re.findall(findPrice, soup)
    datalist.append(price)
    gross_area = re.findall(findGrossArea, soup)
    datalist.append(gross_area)
    net_area = re.findall(findNetArea, soup)
    datalist.append(net_area)

    return datalist


# 得到指定一个URL的网页内容
def askURL(url):
    head = {  # 模拟浏览器头部信息，向服务器发送消息
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"
    }
    # 用户代理，表示告诉服务器，我们是什么类型的机器、浏览器（本质上是告诉浏览器，我们可以接收什么水平的文件内容）

    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


# 保存数据到表格
def saveData(datalist, savepath):
    print("save.......")
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)
    sheet = book.add_sheet('预售项目', cell_overwrite_ok=True)
    col = ("楼栋","单元","楼层","房号","预售单价","建筑面积","户内面积")
    for i in range(7):
        sheet.write(0,i,col[i])
    for i in range(len(datalist)):
        row = datalist[i]
        for j in range(7):
            if len(row[j]) != 0:
                sheet.write(i+1,j,row[j][0])
            else:
                sheet.write(i+1,j,row[j])
    book.save(savepath)




if __name__ == "__main__":
    print()
    print('-' * 80)
    print()
    print("正在爬取数据，请稍后...")
    print()
    main()
    print("爬取完毕！")
    print()
    print('-' * 80)
    print()

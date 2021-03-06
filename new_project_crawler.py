#!/usr/bin/env python3
# -*- codeing = utf-8 -*-
from bs4 import BeautifulSoup
import re
import urllib.request, urllib.error
import xlwt
import pandas as pd
import numpy as np
from openpyxl import Workbook
import xlrd
import os
import datetime
import pysnooper   #debug tool


findProjectIds = re.compile(r'<a href="projectdetail\.aspx\?id=(\d+)"')
findProjectDates = re.compile(r'20\d\d-\d\d-\d\d')
findProjectNames = re.compile(r'<a href="projectdetail.*?>\s*?(\S+?)<\/a>', re.S)
findLink = re.compile(r'href="(.+?)"')
findBldLink = re.compile(r'href="(building.+?)"')

findTower = re.compile(r'项目楼栋情况.*?(\S+?栋)', re.S)
findUnit = re.compile(r'座号.*?<td.*?>\s*?(\S+)\s*?</td>', re.S)
findPrice = re.compile(r'拟售价格.*?(\S+?)元/平方米', re.S)
findFloor = re.compile(r'楼层.*?<td.*?>\s*?(\S+)\s*?</td>', re.S)
findRoom = re.compile(r'房号.*?<td.*?>\s*?(\S+)\s*?</td>', re.S)
findGrossArea = re.compile(r'建筑面积.*?(\S+?\d)平方米', re.S)
findNetArea = re.compile(r'户内面积.*?(\S+?\d)平方米', re.S)

base_url = "http://zjj.sz.gov.cn/ris/bol/szfdc/"
project_base_url = "http://zjj.sz.gov.cn/ris/bol/szfdc/projectdetail.aspx?id="


#@pysnooper.snoop()
def main():
    project_names, project_urls = getNewProjectUrls(base_url)
    print()
    print('-' * 80)
    print()
    if len(project_urls) == 0:
        print('今日没有公布新房预售项目')
    else:
        print('今日公布了 ' + str(len(project_urls)) + ' 个新房预售项目，正在爬取信息...')
        getAllData(name_list=project_names, project_list=project_urls)
        print('信息爬取完毕')
    print()
    print('-' * 80)
    print()
    

def getAllData(name_list, project_list):
    for i in range(len(project_list)):
        print()
        print('正在爬取第 ' + str(i+1) + ' 个项目')
        print()
        tower_url_list = getTowerUrl(project_list[i])
        unit_url_list = getUnitLinks(tower_url_list)
        room_url_list = getRoomLinks(unit_url_list)
        room_details = getDetails(room_url_list)
        interim_path = "project_" + name_list[i] + ".xlsx"
        result_path = "result_" + name_list[i] + ".xlsx"
        saveData(room_details, interim_path)
        saveParsedData(interim_path, result_path)
        print()
        print('第 ' + str(i+1) + ' 个项目爬取完成，剩余 ' + \
            str(len(project_list)-i-1) + ' 个项目')
        print()


#获取当天公布的项目URL
#@pysnooper.snoop()
def getNewProjectUrls(url):
    urls = []
    name_list = []    
    ids, names, dates = getProjectIds_Names_Dates(url)
    for i in range(len(ids)):
        if dates[i] == str(datetime.date.today()):
#        if dates[i] == '2020-12-30':
            name_list.append(names[i])
            urls.append(project_base_url + ids[i])
    return name_list, urls
    

#获取首页所有项目的ID，项目名称和公布日期
#@pysnooper.snoop()
def getProjectIds_Names_Dates(url):
    html = askURL(url)
    soup = BeautifulSoup(html, "html.parser")    
    id_list = re.findall(findProjectIds, str(soup))
    name_list = re.findall(findProjectNames, str(soup))
    date_list = re.findall(findProjectDates, str(soup))
    return id_list, name_list, date_list


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
#@pysnooper.snoop()
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
    if is_contains_chinese(room[0]):
        datalist.append(room)
    else:
        r = list(room[0])
        if r[-1].isalpha():
            r = [r[-1]]
        else:
            r = [''.join(r[-2:])]
        datalist.append(r)

    price = re.findall(findPrice, soup)
    if price == ['--']:
        datalist.append([0])
    else:
        datalist.append(price)

    gross_area = re.findall(findGrossArea, soup)
    datalist.append(gross_area)
    net_area = re.findall(findNetArea, soup)
    datalist.append(net_area)

    return datalist



#检验是否含有中文字符
def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


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


# 保存数据到表格，得到 @咚咚找房 格式
def saveData(datalist, path):
    if os.path.exists(path) is True:
        os.remove(path)
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
    book.save(path)



# 升级 @咚咚找房 格式到 @唐老师傅 格式
#@pysnooper.snoop()
def saveParsedData(path1, path2):
    df = pd.read_excel(path1)
    total = df['建筑面积'] * df['预售单价']
    df['总价'] = total
    df['总价'] = df['总价'].map(lambda x:('%d') % x)
    df.fillna('--', inplace=True)

    if df['单元'].dtypes == 'int64':
        df['单元'] = df['单元'].map(lambda x:('%d') % x)

    df["楼栋"] = df["楼栋"] + df["单元"]
    
    df_sum = df.drop(["单元","预售单价","建筑面积","户内面积"], axis=1)
    df_price = df.drop(["单元","总价","建筑面积","户内面积"], axis=1)

    df_sum = df_sum.pivot_table(values='总价', index=['楼栋','楼层'], columns='房号', aggfunc=np.sum)
    df_sum.replace("0", "", inplace=True)
    df_price = df_price.pivot_table(values='预售单价', index=['楼栋','楼层'], columns='房号', aggfunc=np.sum)
    df_price.replace(0, "", inplace=True)
    
    if os.path.exists(path2) is True:
        os.remove(path2)
    with pd.ExcelWriter(path2) as writer:
        df_sum.to_excel(writer, sheet_name="总价分布")
        df_price.to_excel(writer, sheet_name="单价分布")



if __name__ == "__main__":
    main()

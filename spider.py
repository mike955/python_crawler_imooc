#/bin/env python3
# -*- coding: UTF-8 -*-

import urllib
from urllib import request
import ssl
import re
import csv
import time

class Spider():
    url = 'https://coding.imooc.com/?sort=2'
    page_url = 'https://coding.imooc.com/?sort=2&unlearn=0&page='

    page_pattern = 'page=\d">(\d)</a>'
    course_pattern = '<div class="shizhan-intro-box">([\s\S]*?)加购物车</span>'
    name_pattern = ' class="shizan-name" title="([\s\S]*?)">'
    grade_pattern = '<span class="grade">([\s\S]*?)</span>'
    price_pattern = '<div class=\'course-card-price\'>([\s\S]*?)</div>'
    discount_price_pattern = '<span class=\'discount-price\'>([\s\S]*?)</span>'
    learn_number_pattern = 'class="imv2-set-sns"></i>([\s\S]*?)</span>'
    desc_pattern = '<p class="shizan-desc" title="([\s\S]*?)">'

    def __fetch_content(self, url):
        try:
            context = ssl._create_unverified_context()
            r = urllib.request.urlopen(url, context=context)
            html = str(r.read(), encoding='utf-8')
        except urllib.error.HTTPError as error:
            print('HTTP 请求错误: ', error)
        except urllib.error.URLError as error:
            print('url 错误: ', error)
        return html

    def __analysis(self, html):
        courses_html = re.findall(Spider.course_pattern, html)
        page_numbers = re.findall(Spider.page_pattern, html)
        try:
            if len(page_numbers) > 0:
                for number in page_numbers:
                    page_html = self.__fetch_content(Spider.page_url + number)
                    course_html = re.findall(Spider.course_pattern, page_html)
                    courses_html = courses_html + course_html
        except urllib.error.HTTPError as error:
            print('HTTP 请求错误: ', error)
        except urllib.error.URLError as error:
            print('url 错误: ', error)
        return courses_html

    def __refine(self, anchors):
        courses_data = []
        i = 1
        for anchor in anchors:
            name = re.findall(Spider.name_pattern, anchor)
            grade = re.findall(Spider.grade_pattern, anchor)
            price = re.findall(Spider.price_pattern, anchor)
            if len(price) == 0:
                price = re.findall(Spider.discount_price_pattern, anchor)
            learn_number = re.findall(Spider.learn_number_pattern, anchor)
            desc = re.findall(Spider.desc_pattern, anchor)
            course_dict = [i, name[0], grade[0], price[0], learn_number[0], desc[0]]
            courses_data.append(course_dict)
            i += 1

        file_name = 'Course_' + time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()) + '.csv'
        try:
            with open(file_name, 'w', newline='' ,encoding='utf-8-sig') as fr:
                writer = csv.writer(fr, dialect='excel')
                writer.writerow(['序号','课程名称', '难度', '价格', '学习人数', '介绍'])
                for course in  courses_data:
                    writer.writerow(course)
        except IOError as error:
            print('CSV 文件操作错误：', error)
        else:
            print('数据获取成功')

    def go(self):
        root_html = self.__fetch_content(Spider.url)
        courses_html = self.__analysis(root_html)
        self.__refine(courses_html)

spider = Spider()
spider.go()
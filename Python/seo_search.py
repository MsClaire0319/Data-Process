import requests     
import pandas as pd
from lxml import etree
import re
import openpyxl

class Search():
    def __init__(self):
        self.mobile_headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}
        self.pc_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'}

        self.search_engine = {
            '百度PC引擎': ['http://www.baidu.com/s?wd=', self.pc_headers, self.baidu_pc],
            '百度moblie引擎': ['http://m.baidu.com/s?word=', self.mobile_headers, self.baidu_moblie]
        }

        for k, i in zip(self.search_engine.keys(), range(1, len(self.search_engine.keys())+1)): print('{}、{}'.format(i, k))
        self.choose = self.search_engine[list(self.search_engine.keys())[int(input("请选择搜索引擎:"))-1]]

        self.file_path = input("请拖入需要搜索的excle表，并保证数据在excel的第一列，且有列名  ")
        self.data = self.read_file()

        self.result = []

    def read_file(self): 
        return list(pd.read_excel(self.file_path).iloc[:, 0])

    def parse_result(self):
        for word in self.data:
            try:
                print('parsing.....{}'.format(word))
                time = 5
                url = self.choose[0] + word
                result = [word]
                while time:
                    url = self.choose[2](word, result, time, url)
                    if not url: break
                    time -= 1
                self.result.append(result)
                
            except:
                print(word, '出错啦！！！')
                continue

        self.save()

    def save(self):
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.append(['搜索关键词', '标题名称1', '对应网址1', '排名1'])
        for i in self.result: sheet.append(i)
        wb.save('result.xlsx')

    def baidu_moblie(self, word, result, time, url=None):
        name_list = []
        url_list = []

        content = requests.get(url, headers=self.choose[1]).text
        x = etree.HTML(content)
        extract_text = re.findall('<div class="c-result result".*?order=".*?</article>', content)

        for text in extract_text:
            url = re.findall("'mu':'(.*?)'", text)
            if 'recommend_list' in url: continue
            url = url[0] if url != [] else ''

            title = re.findall('<h3 [a-z"=]{,15} class="c-title.*?</h3>', text)
            title = title[0] if title != [] else ''
            title = re.sub('<.*?>', '', title)
            title = re.sub('[\n\r\t ]', '', title)
            name_list.append(title)
            url_list.append(url)

        for name, url, num in zip(name_list, url_list, range(1, len(name_list)+1)):
            if '申请方' in name: result.extend([name, url, num+(5-time)*10])

        page_url = x.xpath('//a[@class="new-nextpage-only"]/@href')
        if page_url == []: 
            page_url = x.xpath('//a[@class="new-nextpage"]/@href')
            if page_url == []:
                print('下一页网址错误，需要检查')
                print(result)
                return False

        return page_url[0]

    def baidu_pc(self, word, result, time, url=None):
        name_list = []
        url_list = []

        content = requests.get(url, headers=self.choose[1]).text
        content = re.sub('[\n\r\t]', '', content)
        x = etree.HTML(content)
        extract_text = re.findall('<div class="result c-container " id=".*?".*?</a>', content)

        for text in extract_text:
            url = re.findall('href = "(.*?)"', text)
            url = url[0] if url != [] else ''
            url = re.sub('[\n\r\t ]', '', url)

            title = re.findall('<h3 class="t.*?<a .*?>(.*?)</a>', text)
            title = title[0] if title != [] else ''
            title = re.sub('<.*?>', '', title)
            title = re.sub('[\n\r\t ]', '', title)
            
            name_list.append(title)
            url_list.append(url)

        for name, url, num in zip(name_list, url_list, range(1, len(name_list)+1)):
            if '申请方' in name: 
                content = requests.get(url, headers=self.choose[1])
                url = content.url
                result.extend([name, url, num+(5-time)*10])

        page_url = x.xpath('//div[@id="page"]/a/@href')
        if page_url == []: 
            print('下一页网址错误，需要检查')
            print(result)
            return False
        page_url = 'https://www.baidu.com' + page_url[-1]

        return page_url

a = Search()
a.parse_result()

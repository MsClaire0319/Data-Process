# coding: utf-8
# Created by FeiFei Liu on 2018-12-11

import csv
import glob
import os.path
import random
import re
import pandas as pd
import time

from datetime import datetime

import requests
import hashlib


def main():
    
    path = input('请输入待验证的URL文件 (可分工作表, 但需要url字段):')
    outdir = os.path.basename(path).split('.')[0]       # output directory
    
    engine = BaiduIncluded(outdir=outdir)
    engine.execute(path)
    
    

class BaiduIncluded:
    
    def __init__(self, **kwargs): 
        self.url = 'https://www.baidu.com/'
        self.resp = requests.Session()
        self.resp.headers['User-Agent'] = ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                                           'Chrome/56.0.2924.87 Safari/537.36')
        self.resp.head(self.url)
        self.ROOT = kwargs.get('outdir', 'data')
        
        if not os.path.isdir(self.ROOT):
            os.mkdir(self.ROOT)
        
    def execute(self, path):
        
        count = 0
        sheets = pd.read_excel(path, sheetname=None)
        for catalog, df in sheets.items():
            for idx, row in df.iterrows():
                url = row['url']
                outfile = '{}/{}.csv'.format(self.ROOT, self.get_md5(url))
                if os.path.exists(outfile): 
                    flag = pd.read_csv(outfile)['flag'].tolist()[0]
                    if flag: continue
                
                count += 1
                flag = self.is_included(url)
                df_out = pd.DataFrame({'catalog': [catalog], 'url': [url], 'flag': [flag]}, index=[0])
                df_out.to_csv(outfile, index=False, encoding='utf8')
                print('***[Done]***', idx, flag, url)
                
                if count % 77 == 0:
                    time.sleep(30)
                    
        hcol = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')
        df = self.merge_csv().rename(columns={'flag': hcol})
        if df is not None:
            df_count = df.groupby(['catalog', hcol]).count().reset_index().rename(columns={'url': 'count'})
            print('\n各工作表中网址被收录情况:\n', df_count)
            
            outfile = 'baidu_included_result.xlsx'
            if os.path.exists(outfile):
                df_final = pd.read_excel(outfile).merge(df, how='outer')
            else:
                df_final = df
                
            df_final.to_excel(outfile, index=False)
            print('\n***[FILE SAVED]***', outfile)
    
    def is_included(self, site):
        
        url = self.url + 's'
        query ={ 'wd': site}
        
        html = self.get_html(url, **query)
    
        if html.status_code < 400:
            return '没有找到' not in html.text
        
        time.sleep(random.randint(1, 20)/2)
        return self.is_included(site)
            
    def get_html(self, url, **kwargs):
        return self.resp.get(url, params=kwargs)
    
    def merge_csv(self):
     
        paths = glob.glob('{}/*.csv'.format(self.ROOT))
        
        if paths:
            dfs = [pd.read_csv(path) for path in paths]
            return pd.concat(dfs).drop_duplicates()
        
    def get_md5(self, url):
        
        m = hashlib.md5()
        m.update(url.encode())
        return m.hexdigest()
    
    
if __name__ == '__main__': main()
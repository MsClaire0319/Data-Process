import os
import random
import string
import re
import shutil
import pandas as pd
import sys

def all_path(path, namelist):
    for file in os.listdir(path):
        if '.py' in file: continue
        path_ = path + '/{}'.format(file)
        if os.path.isdir(path_): all_path(path_, namelist)
        else:  namelist.append(path_)

def random_name():
    Ofnum = random.randint(1,5)
    Ofletter = 22 - Ofnum
    slcNum = [random.choice(string.digits) for i in range(Ofnum)]
    slcLetter = [random.choice(string.ascii_letters) for i in range(Ofletter)]
    slcChar = slcLetter + slcNum
    random.shuffle(slcChar)
    getPwd = ''.join([i for i in slcChar])
    return getPwd

def content_generate(folder, team, project, date):
    namelist = []
    all_path(folder, namelist)
    mark = ''
    content = ''
    for file in namelist:
        mark_now = "/".join(file.split('/')[:-1])
        name = '{}.{}'.format(random_name(), file.split('.')[-1])
        os.rename(file, name)
        if mark == '': mark = mark_now
        if mark_now != mark:
            with open ('{}.html'.format(mark), 'w', encoding='utf-8') as f:
                print(mark_now)
                f.write(content)
            mark = mark_now
            content = ''
            content += '<figure class="image"><img src="https://cdn.applysquare.net/storage/datum/teams/team:X33cZQKEBc/projects/prj:XKEvrmprXA/images/2019-08/misc/{}"></figure>'.format(name)
        
        content += '<figure class="image"><img src="https://cdn.applysquare.net/storage/datum/teams/team:X33cZQKEBc/projects/prj:XKEvrmprXA/images/2019-08/misc/{}"></figure>'.format(name)

def data_qc(folder, excel_path):
    file_list = list(pd.read_excel(excel_path)['知拾名称'])
    namelist = []
    all_path(folder, namelist)
    result = False
    for file in namelist:
        if '.' in file:
            name = file.split('/')[-2]
            if name not in file_list: 
                result = True
                print(name)
    if result: sys.exit(0)

def tag_generate(folder, excel_path):
    namelist = []
    match = {}
    data = pd.read_excel(excel_path)
    d = list(data['知拾名称'])
    for i in data.values: match[i[0]] = list(i[1:])
    all_path(folder, namelist)
    for file in namelist:
        print(file)
        name = file.split('/')[-1].split('.')[0]
        temp = match[name]
        tag = ''
        for _ in temp:
            if pd.notnull(_):
                tag += '{},'.format(_)
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(file, 'w', encoding='utf-8') as f:
            content = '<html><head><meta name="keywords" content="{}" /></head><body>'.format(tag[:-1]) + content
            content += '</body></html>'
            f.write(content)

def image_uplaod(team, project, date):
    for file in os.listdir('.'):
        if '.jpg'in file or '.JPG' in file or 'png' in file:            
            os.system('aws s3 cp {} s3://applysquare-storage/datum/teams/{}/projects/{}/images/{}/misc/'.format(file, team, project, date))

def delete_folder(folder):
    namelist = []
    all_path(folder, namelist)
    for path in namelist:
        if os.path.isdir(path):
            os.remove(path)

def main():
    # 先运行QC 有错误的话，就不会往下运行了
    data_qc('资料库', '【国内组】坚果云文档架构.xlsx')
    # 生成html
    content_generate('资料库', 'team:X33cZQKEBc', 'prj:XKEvrmprXA', '2019-08')
    # 补充tag
    tag_generate('资料库', '【国内组】坚果云文档架构.xlsx')
    # 删除无用的空文件夹
    delete_folder('资料库')
    # 上传图片
    image_uplaod('team:X33cZQKEBc', 'prj:XKEvrmprXA', '2019-08')

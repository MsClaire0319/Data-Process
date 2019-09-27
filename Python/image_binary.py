# coding: utf-8
# Created by FeiFei Liu on 2019-08-13

import glob
import os
import os.path
from PIL import Image
import numpy as np
import cv2 as cv


def main():
    
    infolder = input('请输入图片文件夹所在顶级目录: ')
    infolder = os.path.abspath(infolder)
    
    tmpfile = 'tmp.png'
    kernel = np.ones((2,2), np.uint8)
    
    err = []
    paths = walk_dir(infolder)
    for path in paths:
        
        segs = path.replace(infolder, '').split('\\')
        if len(segs) == 2:
            outdir = 'output'
            outfile = os.path.join(outdir, os.path.basename(path))
        else:
            outdir = 'output\\' + segs[1]
            outfile = os.path.join(outdir, '_'.join(segs[2:]))
        
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        
        print('***[Process Image]***', path)
        try:
            imgNew = remove_noise_short(path)
        except:
            err.append(path)
            continue
        
        imgNew.save(tmpfile)
        
        img = cv.imread(tmpfile, cv.IMREAD_GRAYSCALE)
        imgScale = cv.resize(img, None, fx=3, fy=3, interpolation=cv.INTER_CUBIC)
        imgBlack = (imgScale > 210) * 255
        Image.fromarray(np.uint8(imgBlack), 'L').save(outfile)
        
    if err:
        with open('error_image.txt', 'w', encoding='utf8') as file:
            file.write('\n\r'.join(err))
        print('***[ERROR FILE]***', 'error_image.txt')
        
    print('ok')
    
    
def walk_dir(folder, extensions=['.png','.jpg','.gif','.bmp','.jpeg']):
    '''Recursively walk through folder directory and get all filenames.'''
    
    for subdir, dirs, files in os.walk(folder, topdown=True):
        for file in files:
            if file.startswith('~$'): continue
            fullname = os.path.join(subdir, file)
            _, ext = os.path.splitext(file)
            if ext.lower() in extensions: 
                yield fullname
                
def remove_noise_short(imgfile):
    
    img = Image.open(imgfile).convert('L')
    pixel = np.asarray(img)
    pixelNew = np.uint8((pixel > 210) * 255)
    
    return Image.fromarray(pixelNew, 'L')
    
    
def remove_noise(imgfile):
    
    img = Image.open(imgfile).convert('L')
    pixel = img.load()
    
    imgNew = Image.new('L', img.size)
    pixnew = imgNew.load()
    
    width, height = img.size
    for i in range(width):
        for j in range(height):
            pixnew[i,j] = 255
            
            k = pixel[i, j]
            if k <= 60:
                pixnew[i,j] = 0
            elif k <= 210:
                pixnew[i,j] = 0
            else:
                pixnew[i,j] = 255
            
    return imgNew
    
if __name__ == '__main__': main()
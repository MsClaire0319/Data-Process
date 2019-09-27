# coding: utf-8
# Created by FeiFei Liu on 2017-11-15

import argparse
import os
import os.path
import shutil
import sys
from PIL import Image

# 图片批量缩放至同样大小
def main():
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if len(sys.argv) == 1:
        infolder = input('Enter the input directory: ').strip()
        outfolder = input('Enter the output directory (default output): ').strip() or 'output'        
        height = input('Enter the result height (None means remain original): ').strip()
        try:
            height = int(height)
        except:
            height = None
        types = input('Enter the input image types (default .jpg .jpeg .png .bmp):').strip()
        images = ['.jpg','.jpeg','.png','.bmp'] if len(types) == 0 else types.split()
        format = input('Enter the output image type (default the same as origin):').strip()
    else:
        param = argparse.ArgumentParser()
        param.add_argument('-i', '--input-directory', required=True, dest='infolder', help='the input directory') 
        param.add_argument('-o', '--output-directory', required=True, dest='outfolder', help='the output directory')
        param.add_argument('-height', '--resized-height', default=200, dest='height', help='the result image height')
        param.add_argument('-images', '--image-types', nargs='+', default=['.jpg','.jpeg','.png'], dest='images', help='the input image types')
        param.add_argument('-format', '--output-format', default='', dest='format', help='the output image format')
        
        args = param.parse_args()
        infolder = args.infolder
        outfolder = args.outfolder
        height = args.height
        images = args.images
        format = args.format
        
    engine = ImageToolkit()
    engine.do_resize(infolder, outfolder, height, images, format)
    input('Done')


class ImageToolkit():
    
    def __init__(self):
        pass
    
    def do_resize(self, infolder, outfolder, height=200, exts=['.png'], extB='.png'):
        '''Resize the images to 200px height and remain the aspect ratio.'''
        
        rootA = os.path.abspath(infolder)
        rootB = os.path.abspath(outfolder)
        
        self.clean_folder(rootB)
        
        for extA, pathA in self.walk_dir(rootA, exts):
            pathB = pathA.replace(rootA, rootB)
            if len(extB) > 0: pathB = pathB.rstrip(extA) + extB
            pfolder = os.path.dirname(pathB)
            if not os.path.exists(pfolder): os.makedirs(pfolder)
            
            with Image.open(pathA) as imgA:
                nheight = height or imgA.size[1]
                nwidth = int(nheight * imgA.size[0]/imgA.size[1]) # new width
                imgB = imgA.resize((nwidth, nheight), resample=Image.ANTIALIAS) 
                
            if imgB.mode != 'RGB': imgB = imgB.convert('RGB')
            imgB.save(pathB)
            print('**[RESIZED]** {}'.format(pathB.replace(rootB + '\\', '')))
        
    def clean_folder(self, folder):
        '''Remove all content in the folder.'''
        
        if os.path.exists(folder): shutil.rmtree(folder)
        os.makedirs(folder)
    
    def walk_dir(self, folder, targets):
        '''Recursively walk through the folder to get all the target files.'''

        for subdir, dirs, files in os.walk(folder, topdown=True):
            for file in files:
                fullname = os.path.join(subdir, file)
                _, ext = os.path.splitext(file)
                if ext.lower() in targets: yield ext, fullname
    
    
    
if __name__ == '__main__': main()
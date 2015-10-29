#!/usr/bin/env python
# -*- coding: utf-8 -*-

import winprint
from PIL import Image,ImageDraw,ImageFont,ImageWin
import winstruct as wst

def createImg():
    img=Image.new('RGB',(512,512), 'white')
    draw=ImageDraw.Draw(img)
    fnt = ImageFont.truetype('msyh.ttf', 40)
    print(fnt)
    draw.text((10,10),'test',font=fnt,fill=(0,0,255,255))
    draw.text((100,100),'測試',font=fnt,fill=(0,0,255,255))
    #img.show()
    return ImageWin.Dib(img)

'''
    pt   磅或点数，是point简称 1磅=0.03527厘米=1/72英寸
    inch 英寸，1英寸=2.54厘米=96像素（分辨率为96dpi）
    px   像素，pixel的简称（本表参照显示器96dbi显示进行换算。像素不能出现小数点，一般是取小显示)
    绘制内容默认使用的单位
        字体单位使用point（磅）
        长度单位使用cm（厘米）
        需要使用像素作为单位时，需要特别声明
'''

def printtest():
    wp=winprint.WinPrinter()
    wp.selectByPrintDlg()
    print('print dc',wp.PrinterDC)
    pg=wp.newPage()
    print('page',pg)
    #fnt = ImageFont.truetype
    pg.line((0,0,10,0),5)
    pg.line((0,0,0,10),5)
    fnt=('msyh.ttf', 20)
    pg.text((10,10),'test',font=fnt,fill=(0,0,255,255))
    fnt=('msyh.ttf', 72)    
    pg.text((50,100),'測試',font=fnt,fill=(0,0,255,255))
    wp.printOut('test print')
        
## pt=winprint.selectPrinter()
## if  pt:
    
printtest()

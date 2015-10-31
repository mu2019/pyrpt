#!/usr/bin/env python
# -*- coding: utf-8 -*-

import winprint
from defusedxml.ElementTree  import parse
from __init__ import AttrDict
from getfontname import get_font_file
import re
from base64 import b64decode
from io import BytesIO

        

class Paper(AttrDict):
    def __init__(self,xmlpaper=None):
        super(Paper,self).__init__()
        if xmlpaper:
            pg=AttrDict(dict(xmlpaper.items()))
            self.MarginsRight=int(pg.marginsRight)/4
            self.MarginsLeft=int(pg.marginsLeft)/4
            self.MarginsTop=int(pg.marginsTop)/4
            self.MarginsBottom=int(pg.marginsBottom)/4
            self.PageHeight=int(pg.pageHeight)/4
            self.PageWidth=int(pg.pageWidth)/4
            self.Orientation=int(pg.orientation)
            self.PageNo=int(pg.pageNo)

class Label(AttrDict):
    def __init__(self,label):
        '''
        label: dict/Ordered object
        '''
        super(Label,self).__init__()
        self.update(label)

    def draw(self,canvas,margins=(0,0),unit=None):
        '''
        draw label to printer canvas
        canvas: PrinterCanvas
        margins: label left,top margins in unit
        '''
        lcan=canvas.clone((self.Width,self.Height))
        pxw,pxh = lcan.size()
        #print('label font file',self.Name,self.FontFile)
        
        font=lcan.createFont((self.FontFile,self.FontSize))
        lcan.rectangle(((0,0,pxw,pxh)),fill=self.BackgroudColor)
        bd=int(self.BorderWidth[:-2])
        bdunit=self.BorderWidth[-2:]
        bdpx = lcan.unitToPixel(bd,bdunit)
        if self.TextWrap == '1':
            wtext = lcan.wrapText(self.Value,font,(bd,bd,bdunit))
        else:
            wtext = self.Value
        
        #print('--text',self.Value,'--wrap text',wtext)
        fsz=lcan.multiline_textsize(wtext,font)
        halign = self.AligmentH.lower()[1:]

        l = bdpx
        if self.AligmentH  == 'hCenter':
            l = int((pxw - bdpx*2 - fsz[0]) / 2) + bdpx
        elif self.AligmentH  == 'hRight':
            l = pxw - fsz[0] - bdpx + bdpx
        t = bdpx
        if self.AligmentV == 'vCenter':
            t = int((pxh - bdpx*2 - fsz[1]) / 2) + bdpx

        elif self.AligmentV == 'vBottom':
            t = pxh - bdpx -fsz[1] + bdpx
        lcan.multiline_text((l,t),wtext,self.FontColor,font,align=halign)
        if bd and self.BorderTop:
            lcan.line((0,0,pxw,0),self.BorderTop,bd,bdunit)
        if bd and self.BorderRight:
            lcan.line((pxw-bd,0,pxw-bd,pxh-bd),self.BorderRight,bd,bdunit)
        if bd and self.BorderBottom:            
            lcan.line((0,pxh-bd,pxw-bd,pxh-bd),self.BorderTop,bd,bdunit)
        if bd and self.BorderLeft:
            lcan.line((0,0,0,pxh),self.BorderLeft,bd,bdunit)
            
        canvas.paste(lcan,(self.Left+margins[0],self.Top+margins[1]),unit=unit)

class Image(AttrDict):
    def __init__(self,label):
        super(Image,self).__init__()
        self.update(label)
        
    def draw(self,canvas,margins=(0,0),unit=None):
        lcan=canvas.clone((self.Width,self.Height))
        pxw,pxh = lcan.size()
        lcan.rectangle(((0,0,pxw,pxh)),fill=self.BackgroudColor)
        bd=int(self.BorderWidth[:-2])
        bdunit=self.BorderWidth[-2:]
        imgb=b64decode(self.Picture)
        img=winprint.Image.open(BytesIO(imgb))
        img2=img.resize((pxw-bd,pxh-bd))
        
        #lcan.paste(img2,(bd,bd,pxw-bd,pxh-bd),unit='px')

        if bd and self.BorderTop:
            lcan.line((0,0,pxw,0),self.BorderTop,bd,bdunit)
        if bd and self.BorderRight:
            lcan.line((pxw-bd,0,pxw-bd,pxh-bd),self.BorderRight,bd,bdunit)
        if bd and self.BorderBottom:            
            lcan.line((0,pxh-bd,pxw-bd,pxh-bd),self.BorderTop,bd,bdunit)
        if bd and self.BorderLeft:
            lcan.line((0,0,0,pxh),self.BorderLeft,bd,bdunit)
            
        lcan.paste(img2,(bd,bd),unit='px')
        canvas.paste(lcan,(self.Left+margins[0],self.Top+margins[1]),unit=unit)        

class ContainerField(AttrDict):
    '''
      <TContainerField borderTop="rgba(0,0,0,255)" name="field3" autoHeight="0" left="65" borderColor="rgba(0,0,0,255)" borderStyle="solid" backgroundColor="rgba(255,255,255,255)" fontSize="10" width="140" textWrap="1" aligmentH="hLeft" fontUnderline="0" fontStrikeout="0" top="-1" fontItalic="0" printing="1" value="master footer" fontColor="rgba(0,0,0,255)" fontBold="0" fontFamily="SimSun" borderLeft="rgba(0,0,0,255)" aligmentV="vCenter" highlighting="" groupName="" borderWidth="1px" borderBottom="rgba(0,0,0,255)" height="30" type="label" format="" borderRight="rgba(0,0,0,255)"/>

      self.FontFile,get_font_name将字体名字转换为字体文件名
    '''
    def __init__(self,xmlfield=None):
        super(ContainerField,self).__init__()
        for i,v in xmlfield.items():
            n=i[0].upper()+i[1:]
            if v.startswith('rgba(') and n != 'Value':
                self[n]=tuple([int(c) for c in re.findall('\d+',v)])
            else:
                self[n]=v
        self.Width=int(self.Width)/4
        self.Height=int(self.Height)/4
        self.Left=int(self.Left)/4
        self.Top=int(self.Top)/4
        self.FontSize=int(self.FontSize)
        fstyle='Bold' if self.FontBold == '1' else 'Regular'
        fn=get_font_file(self.FontFamily,fstyle)
        self.FontFile= fn if fn else 'arial.ttf'
        
        
def createField(xmlfield):
    field=AttrDict()
    for i,v in xmlfield.items():
        n=i[0].upper()+i[1:]
        if v.startswith('rgba(') and n != 'Value':
            field[n]=tuple([int(c) for c in re.findall('\d+',v)])
        else:
            field[n]=v
    field.Width=int(field.Width)/4
    field.Height=int(field.Height)/4
    field.Left=int(field.Left)/4
    field.Top=int(field.Top)/4
    if field.FontSize:
        field.FontSize=int(field.FontSize)
    fstyle='Bold' if field.FontBold == '1' else 'Regular'
    fn = get_font_file(field.FontFamily,fstyle)
    field.FontFile = fn if fn else 'arial.ttf'
    if field.Type == 'label':
        return Label(field)
    elif field.Type == 'image':
        return Image(field)
    else:
        return field
    

class ReportBand(AttrDict):
    def __init__(self,xmlband=None):
        super(ReportBand,self).__init__()
        self.Fields=[]
        if xmlband:
            bd=AttrDict(dict(xmlband.items()))

            self.__dict__['data'].update(bd)            
            self.Top=int(bd.top)/4
            self.Left=int(bd.left)/4
            self.Width=int(bd.width)/4
            self.Height=int(bd.height)/4 if bd.height else 0
            self.Name=bd.name
            self.Type=bd.type
            if bd.type=='DataGroupHeader':
                self.StartNewNumeration=int(bd.startNewNumeration)
                self.StartNewPage=int(bd.startNewPage)
            self.Fields=[createField(fld) for fld in xmlband]

class ReportPage():
    def __init__(self,xmlreport):
        self.Paper=Paper(xmlreport)
        self.Bands=[ReportBand(bnd) for bnd in xmlreport]


class QTRPT():
    '''
    QTRP file  compatible
    '''
    def __init__(self,filename=''):
        self.Pages=[]
        self.Printer=winprint.WinPrinter()
        self.ReportFile=filename
        if filename:
            self.loadFromFile(filename)

    def loadFromFile(self,filename):
        xmlf=parse(filename)
        reports=xmlf.getroot()
        if reports.get('lib').upper()=='QTRPT':
            self.Pages=[ReportPage(pg) for pg in reports]
        else:
            self.Pages=[]

    def drawReport(self):
        if not self.Printer.isReady():
            return
        for p in self.Pages:
            if p.Paper.Orientation == 1:
                sz=(p.Paper.PageHeight,p.Paper.PageWidth)
            else:
                sz=(p.Paper.PageWidth,p.Paper.PageHeight)
            self.CurrentCanvas=pg=self.Printer.newPage(sz)
            boffset=0
            for bnd in p.Bands:
                for fld in bnd.Fields:
                    #print('file',fld.Name)
                    if fld.Printing == '1' and fld.draw:
                        fld.draw(pg,(bnd.Left,boffset))
                boffset += (bnd.Height or 0)
        return True
            

    def printOut(self,docname,printerName='',silent=True,setting={}):
        '''
        docname:打印任務名稱
        printName:選擇打印機名稱
        silent:靜默打印
        setting:其它打印設置選項
        '''
        if printerName:
            self.Printer.selectByName(printerName)
        if not silent:
            self.Printer.selectByPrintDlg()
        
        if self.drawReport():
            self.Printer.printOut(docname)

    def printPreview(self,setting={}):
        pass
            


        
if __name__ == '__main__':
    
    #rp=QTRPT('../test/1.xml')
    rp=QTRPT('../test/label.yu-city.xml')
    
    #rp.Printer.selectByPrintDlg()
    #rp.drawReport()
    rp.printOut('打印测试',silent=False)
    
    
    


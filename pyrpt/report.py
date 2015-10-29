#!/usr/bin/env python
# -*- coding: utf-8 -*-

import winprint
from defusedxml.ElementTree  import parse
from ..utilitis import AttrDict
from getfontname import get_font_file
import re


    

class Paper(AttrDict):
    def __init__(self,xmlpaper=None):
        super(Paper,self).__init__()
        if xmlpaper:
            pg=AttrDict(dict(xmlpaper.items()))
            self.MarginsRight=int(pg.marginsRight)/4
            self.MarginsLeft=int(pg.marginsLeft)/4
            self.MarginsTop=int(pg.marginsTop)/4
            self.MarginsBottom=int(pg.marginsBottom)/4
            self.PageHight=int(pg.pageHeight)/4
            self.PageWidth=int(pg.pageWidth)/4
            self.Orientation=int(pg.orientation)
            self.PageNo=int(pg.pageNo)

class ContainerField(AttrDict):
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
        self.FontSize=int(FontSize)
        fstyle='Bold' if self.FontBold == '1' else 'Regular'
        self.FontFile=get_font_file(self.FontFamily,fstyle)
        
        

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
            self.Height=int(bd.height)/4
            self.Name=bd.name
            self.Type=bd.type
            if bd.type=='DataGroupHeader':
                self.StartNewNumeration=int(bd.startNewNumeration)
                self.StartNewPage=int(bd.startNewPage)
            self.Fields=[ContainerField(fld) for fld in xmlband]

class ReportPage():
    def __init__(self,xmlreport):
        self.Paper=Paper(xmlreport)
        self.Bands=[ReportBand(bnd for bnd in xmlreport)]

class QTRPT():
    '''
    QTRP file  compatible
    '''
    def __init__(self,filename=''):
        self.Pages=[]
        self.Printer=winprint.WinPrinter()

    def loadFromFile(self,filename):
        xmlf=parse(filename)
        reports=xmlf.getroot()
        if reports.get('lib').upper()=='QTRPT':
            self.Pages=[ReportPage(pg) for pg in reports]
        else:
            self.Pages=[]

    def drawLabel(self,label):
        pass

    def drawReport(self):
        if not self.Printer.isReady():
            return
        
        for p in self.Pages:
            if p.Paper.Orientation == 1:
                sz=(p.Paper.PageHeight,p.Paper.PageWidth)
            else:
                sz=(p.Paper.PageWidth,p.Paper.PageHeight)
            pg=self.Printer.newPage(sz)
            for bnd in self.Bands:
                for fld in bnd.Fields:
                    print(fild.Type)
            

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

        

    def printPreview(self,setting={}):
        pass
            


        
if __name__ == '__main__':
    rp=QTRP('1.xml')
    rp.drawReport()
    
    
    


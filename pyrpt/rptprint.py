#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .uicore import winprint
#from getfontname import get_font_file
#import re
from base64 import b64decode
from io import BytesIO
from . import barcode


class RptPrint():
    def __init__(self):
        self.Printer = winprint.WinPrinter()
        self.Report = None


    def getDetailBandHeight(self,page):
        h = 0
        for b in page.Bands:
            if b.tag not in ( 'TprtDetailDataBand','TprtChildBand') and b.Printing != 'False':
                h += b.Height
        return  page.PageHeight - page.MarginBottom - page.MarginTop - h

    def getPageCount(self):
        pass


    def drawField(self,field,band):
        '''
        '''
        canv = self.CurrentCanvas.clone((field.Width,field.Height))
        bd=int(field.BorderWidth[:-2])
        bdunit=field.BorderWidth[-2:]
        bdpx = canv.unitToPixel(bd,bdunit)
        if field.tag == 'TprtLabelField':
            self.drawLabel(canv,field)
        elif field.tag == 'TprtImageField':
            self.drawImage(canv,field)
        elif field.tag == 'TprtBarCodeField':
            field.Value = self.Report.parseValue(field)
            barcode.drawBarcode(canv,field)

        bds = field.BorderStyle.split(',')
        bds.extend([bds[-1]]*4)
        pxw,pxh = canv.size()
            
        if bds[0] == 'solid':
            canv.line((0,0,pxw,0),field.BorderColor,bd,bdunit)
        if bds[1] == 'solid' :
            canv.line((pxw-bd,0,pxw-bd,pxh-bd),field.BorderColor,bd,bdunit)
        if bds[2] == 'solid' : 
            canv.line((0,pxh-bd,pxw-bd,pxh-bd),field.BorderColor,bd,bdunit)
        if bds[2] == 'solid' : 
            canv.line((0,0,0,pxh),field.BorderColor,bd,bdunit)
        return canv

    def drawImage(self,canvas,field):
        '''
        '''
        pxw,pxh = canvas.size()
        canvas.rectangle(((0,0,pxw,pxh)),fill=field.BackgroudColor)

        bd=int(field.BorderWidth[:-2])
        bdunit=field.BorderWidth[-2:]
        try:
            imgb=b64decode(field.Image)
            img=winprint.Image.open(BytesIO(imgb))
            img2=img.resize((pxw-bd,pxh-bd))
            canvas.paste(img2,(bd,bd),unit=bdunit)
        except Exception as e:
            print(e)

    def drawBand(self,page,band):
        '''
        绘制一个Band内的内容
        '''
        if band.tag == 'TprtDetailDataBand':
            band_height = self.getDetailBandHeight(page,band)
            band_canv = self.CurrentCanvas.clone(band.Width,band_height)

            dataset = self.Report.Local._DataSet[band.DataSet]
            line_total_height = 0
            for i in range(1,len(datset)+1):
                self.Report.Local.LineNo = dataset.CurrentPos() + 1
                line_canv = self.CurrentCanvas.clone(band.Width,band.Height)
                for field in band.Fields:
                    fim = self.drawField(field,band)
                    line_canv.paste(fim,(field.Left,field.Top))
                band_canv.paste(line_canv,(0,line_total_height))
                
                line_total_height += band.Height
                dataset.next()
                if line_total_height > band_height:
                    self.drawPage(page)
                    break
        else:
            band_canv = self.CurrentCanvas.clone((band.Width,band.Height))
            for field in band._Fields:
                fim = self.drawField(field,band)
                band_canv.paste(fim,(field.Left,field.Top))
        return band_canv

    def drawLabel(self,canvas,field):
        '''
        '''
        pxw,pxh = canvas.size()
        font=canvas.createFont((field.FontFile,field.FontSize))
        canvas.rectangle(((0,0,pxw,pxh)),fill=field.BackgroudColor)
        bd=int(field.BorderWidth[:-2])
        bdunit=field.BorderWidth[-2:]
        bdpx = canvas.unitToPixel(bd,bdunit)
        wtext = self.Report.parseValue(field)
        if field.TextWrap == 'True':
            wtext = canvas.wrapText(wtext,font,(bd,bd,bdunit))
        fsz=canvas.multiline_textsize(wtext,font)
        halign = field.HAlign and field.HAlign.lower() or 'left'

        l = bdpx
        if field.HAlign  == 'Center':
            l = int((pxw - bdpx*2 - fsz[0]) / 2) + bdpx
        elif field.HAlign  == 'Right':
            l = pxw - fsz[0] - bdpx + bdpx
        t = bdpx
        if field.VAlign == 'Center':
            t = int((pxh - bdpx*2 - fsz[1]) / 2) + bdpx

        elif field.VAlign == 'Bottom':
            t = pxh - bdpx -fsz[1] + bdpx
        canvas.multiline_text((l,t),wtext,field.FontColor,font,align=halign)
        

    def drawPage(self,page):
        '''
        新增一页
        '''
        p = page
        if page.Orientation == 'Lanscape':
            sz=(page.PageHeight,page.PageWidth)
        else:
            sz=(page.PageWidth,page.PageHeight)
        self.CurrentCanvas=pg=self.Printer.newPage(sz,p.Unit)
        for bnd in p._Bands:
            img = self.drawBand(p,bnd)
            #img._Image.show()
            pg.paste(img,(p.MarginLeft,(bnd.top or 0)+p.MarginTop))
            
    def printOut(self,report,printerName='',silent=True,setting={}):
        '''
        打印报表
        report: PyRpt实例
        '''
        if printerName:
            self.Printer.selectByName(printerName)
        if not silent or not printerName:
            self.Printer.selectByPrintDlg()
        if not self.Printer.isReady():
            return
        self.Report = report
        for pg in report.Pages:
            self.drawPage(pg)
        self.Printer.printOut('PyRpt PrintOut %s ' % (report.ReportName or ''))
        self.Report = None

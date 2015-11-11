#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .uicore import winprint
from defusedxml.ElementTree  import parse
from . import AttrDict
from getfontname import get_font_file
import re
from base64 import b64decode
from io import BytesIO
from . import barcode
import html
from datetime import datetime


_PyRptBarCodeMap = {
    '20' : 'CODE128', #Code128 / Code128A
    '58' : 'QRCODE', #QRCode
    '60' : 'CODE128B'  #Code128B    
    }

_PyRptBandMap = {
    'ReportTitle' : 'TprtReportTitleBand'
    
    }

def tag_to_pyrtp(field):

    d = AttrDict()
    d.tag = 'TprtLabelField'
    d.Name = field.Name
    d.Left = field.Left
    d.Top = field.Top
    d.Width = field.Width
    d.Height = field.Height
    d.FontColor = field.FontColor
    d.FontSize = field.FontSize
    d.FontName = field.FontFamily
    d.FontFile = field.FontFile
    d.FontStyle = ','.join([
        'Underline' if field.FontUnderline == '1' else '',
        'Strikeout' if field.FontStrikeout == '1' else '',
        'Italic' if field.FontItalic == '1' else '',
        'Bold' if field.FontBold == '1' else 'Normal'
        ]).replace(',,,',',').replace(',,',',')
    d.HAlign = field.AligmentH[1:]
    d.VAlign = field.AligmentV[1:]
    d.Text = field.Value
    d.Printing = 'True' if field.Printing == '1' else 'False'
    d.BackgroudColor = field.BackgroudColor
    d.TextWrap = 'True' if field.TextWrap == '1' else 'False'
    d.BorderColor = field.BorderColor
    bs = ['None' if field.BorderTop[:3] == (255,255,255) else field.BorderStyle,
          'None' if field.BorderRight[:3] == (255,255,255) else field.BorderStyle,
          'None' if field.BorderBottom[:3] == (255,255,255) else field.BorderStyle,
          'None' if field.BorderLeft[:3] == (255,255,255) else field.BorderStyle]
    d.BorderStyle = ','.join(bs)
    d.BorderWidth = field.BorderWidth
    d.DisplayFormat = field.DisplayFormat
    return d
    

class Page(AttrDict):
    def __init__(self,xmlpaper=None):
        super(Page,self).__init__()
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

    def pyrpt(self):
        d = AttrDict()
        d.MarginRight = self.MarginsRight
        d.MarginLeft = self.MarginsLeft
        d.MarginTop = self.MarginsTop
        d.MarginBottom = self.MarginsBottom
        d.Orientation = 'Portrait'  if self.Orientation == '0' else 'Landscape'
        d.PageHeight = self.PageHeight
        d.PageWidth = self.PageWidth
        
        d.Name = 'Page%s' % self.PageNo
        d.tag = 'TprtReportPage'
        d.Unit = d.Unit or 'mm'
        return d

class Label(AttrDict):
    def __init__(self,label):
        '''
        label: dict/Ordered object
        '''
        super(Label,self).__init__()
        self.update(label)

    def pyrpt(self):
        return tag_to_pyrtp(self)

    def draw(self,canvas,margins=(0,0),unit=None,local={}):
        '''
        draw label to printer canvas
        canvas: PrinterCanvas
        margins: label left,top margins in unit
        '''
        lcan=canvas.clone((self.Width,self.Height))
        pxw,pxh = lcan.size()
        
        font=lcan.createFont((self.FontFile,self.FontSize))
        lcan.rectangle(((0,0,pxw,pxh)),fill=self.BackgroudColor)
        bd=int(self.BorderWidth[:-2])
        bdunit=self.BorderWidth[-2:]
        bdpx = lcan.unitToPixel(bd,bdunit)
        if self.TextWrap == '1':
            wtext = lcan.wrapText(self.Value,font,(bd,bd,bdunit))
        else:
            wtext = self.Value
        
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

    def pyrpt(self):
        d = tag_to_pyrtp(self)
        d.tag = 'TprtImageField'
        d.Image = self.Picture
        d.Transparent = self.Transparent or 'False'
        d.TransparentColor = self.TransparentColor
        return d
        
    def draw(self,canvas,margins=(0,0),unit=None,local={}):
        lcan=canvas.clone((self.Width,self.Height))
        pxw,pxh = lcan.size()
        lcan.rectangle(((0,0,pxw,pxh)),fill=self.BackgroudColor)

        bd=int(self.BorderWidth[:-2])
        bdunit=self.BorderWidth[-2:]
        imgb=b64decode(self.Picture)
        img=winprint.Image.open(BytesIO(imgb))
        img2=img.resize((pxw-bd,pxh-bd))
        
        #lcan.paste(img2,(bd,bd,pxw-bd,pxh-bd),unit='px')
        lcan.paste(img2,(bd,bd),unit='px')
        
        if bd and self.BorderTop:
            lcan.line((0,0,pxw,0),self.BorderTop,bd,bdunit)
        if bd and self.BorderRight:
            lcan.line((pxw-bd,0,pxw-bd,pxh-bd),self.BorderRight,bd,bdunit)
        if bd and self.BorderBottom:            
            lcan.line((0,pxh-bd,pxw-bd,pxh-bd),self.BorderTop,bd,bdunit)
        if bd and self.BorderLeft:
            lcan.line((0,0,0,pxh),self.BorderLeft,bd,bdunit)
            
        canvas.paste(lcan,(self.Left+margins[0],self.Top+margins[1]),unit=unit)

class Barcode(AttrDict):
    def __init__(self,label):
        super(Barcode,self).__init__()
        self.update(label)

    def pyrpt(self):
        d = tag_to_pyrtp(self)
        d.tag = 'TprtBarCodeField'
        d.BarType = _PyRptBarCodeMap[self.BarcodeType]
        return d
        
    def draw(self,canvas,margins=(0,0),unit=None,local={}):
        lcan=canvas.clone((self.Width,self.Height))
        pxw,pxh = lcan.size()
        lcan.rectangle(((0,0,pxw,pxh)),fill=self.BackgroudColor)
        bd=int(self.BorderWidth[:-2])
        bdunit=self.BorderWidth[-2:]

        #im = self._drawCode(canvas)
        barcode.drawBarcode(lcan,self)
        
        #img2=img.resize((pxw-bd,pxh-bd))
        
        #lcan.paste(img,(bd,bd),unit='px')
        
        if bd and self.BorderTop:
            lcan.line((0,0,pxw,0),self.BorderTop,bd,bdunit)
        if bd and self.BorderRight:
            lcan.line((pxw-bd,0,pxw-bd,pxh-bd),self.BorderRight,bd,bdunit)
        if bd and self.BorderBottom:            
            lcan.line((0,pxh-bd,pxw-bd,pxh-bd),self.BorderTop,bd,bdunit)
        if bd and self.BorderLeft:
            lcan.line((0,0,0,pxh),self.BorderLeft,bd,bdunit)
            
        canvas.paste(lcan,(self.Left+margins[0],self.Top+margins[1]),unit=unit)

class Circle(AttrDict):
    def __init__(self,label):
        super(Circle,self).__init__()
        self.update(label)

    def pyrpt(self):
        d = tag_to_pyrtp(self)
        d.tag = 'TprtShapeField'
        d.ShapeType = 'Circle'
        return d


class Rectangle(AttrDict):
    def __init__(self,label):
        super(Rectangle,self).__init__()
        self.update(label)

    def pyrpt(self):
        d = tag_to_pyrtp(self)
        d.tag = 'TprtShapeField'
        d.ShapeType = 'Rectangle'
        return d
        
    def draw(self,canvas,margins=(0,0),unit=None,local={}):
        lcan=canvas.clone((self.Width,self.Height))
        pxw,pxh = lcan.size()
        bd=int(self.BorderWidth[:-2])
        bdunit=field.BorderWidth[-2:]
        bdpx = lcan.unitToPixel(bd,bdunit)
        
        lcan.rectangle(((0,0,pxw,pxh)),fill=self.BackgroudColor)
        bdunit = 'px'
        lcan.line((0,0,pxw,0),self.BorderTop,bd,bdunit)
        lcan.line((pxw-bdpx,0,pxw-bdpx,pxh-bdpx),self.BorderRight,bd,bdunit)
        lcan.line((0,pxh-bdpx,pxw-bdpx,pxh-bdpx),self.BorderTop,bd,bdunit)
        lcan.line((0,0,0,pxh),self.BorderLeft,bd,bdunit)
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
        elif n == 'Value':
            field[n] = html.unescape(v)
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
    elif field.Type == 'barcode':
        return Barcode(field)
    elif field.Type == 'reactangle':
        return Rectangle(field)
    elif field.Type == 'circle':
        return Circle(field)
    
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

    def pyrpt(self):
        d = AttrDict()
        d.tag = _PyRptBandMap[self.Type]
        d.Top = self.Top
        d.Left = self.Left
        d.Width = self.Width
        d.Height = self.Height
        d.Name = self.Name
        d._Fields = []
        d._Fields = [ f.pyrpt and f.pyrpt() or AttrDict() for f in self.Fields]
        return d

class DataSource(AttrDict):
    def __init__(self,xmlfield=None):
        super(DataSource,self).__init__()
        for i,v in xmlfield.items():
            n=i[0].upper()+i[1:]
            if v.startswith('rgba(') and n != 'Value':
                self[n]=tuple([int(c) for c in re.findall('\d+',v)])
            else:
                self[n]=v

    def pyrpt(self):
        return AttrDict()
    
class ReportPage():
    def __init__(self,xmlreport):
        self.Page=Page(xmlreport)
        self.Bands = []
        self.DataSource = None
        for bnd in xmlreport:
            if bnd.tag == 'DataSource':
                self.DataSource=DataSource(bnd)
            elif bnd.tag == 'ReportBand':
                self.Bands.append(ReportBand(bnd))

    def pyrpt(self):
        d = self.Page.pyrpt()
        d._Bands =[b.pyrpt() for b in self.Bands]
        if self.DataSource :
            d._DataSource = self.DataSource.pyrpt  and self.DataSource.pyrpt()  or AttrDict() 
        else:
            d._DataSource = AttrDict() 

        return d

class QTRPT():
    '''
    QTRP file  compatible
    '''
    def __init__(self,filename='',):
        self.Pages=[]
        #self.Printer=winprint.WinPrinter()
        self.ReportFile=filename
        if filename:
            self.loadFromFile(filename)
        self.DataSource=AttrDict()

    def pyrpt(self):
        d = AttrDict()
        d.Version = '0.1'
        d.Lib = 'PyRpt'
        d.tag = 'TprtReports'
        pgs=[p.pyrpt() for p in self.Pages]
        dts=[]
        for p in pgs:
            dts.append(p._DataSource)
            del p._DataSource
        d._Pages = pgs
        d._DataSource = dts
        return d

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
            if p.Page.Orientation == '1':
                sz=(p.Page.PageHeight,p.Page.PageWidth)
            else:
                sz=(p.Page.PageWidth,p.Page.PageHeight)
            self.CurrentCanvas=pg=self.Printer.newPage(sz)
            boffset=0
            for bnd in p.Bands:
                for fld in bnd.Fields:
                    if fld.Printing == '1' and fld.draw:
                        fld.draw(pg,(bnd.Left,boffset),local=local)
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
    
    
    


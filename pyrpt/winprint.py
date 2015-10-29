#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
from ctypes import windll # gdi32
from wintypes import * #BYTE, DWORD, LPCWSTR
import wincons as wcs
import winstruct as wst
from PIL import ImageWin,Image,ImageDraw,ImageFont

gdi32=windll.gdi32
comdlg32 = windll.comdlg32
kernel32=windll.kernel32
winspool = ctypes.WinDLL('winspool.drv')  # for EnumPrintersW
msvcrt = ctypes.cdll.msvcrt  # for malloc, free

'''
打印需要支持的功能

获取所有安装的打印机
获取默认打印机
选择打印机
获取打印机信息
获取打印机打印设置
修改打印机打印设置

高级功能
获取打印队列状态

'''

FontParaName=('font', 'size', 'index', 'encoding')

class PrinterError(Exception):
    pass



def getPrintersName():
    '''
    获取所有安装的打印机
    '''

    # Parameters: modify as you need. See MSDN for detail.
    PRINTER_ENUM_LOCAL = 2
    Name = None  # ignored for PRINTER_ENUM_LOCAL
    Level = 1  # or 2, 4, 5

    # Invoke once with a NULL pointer to get buffer size.
    info = ctypes.POINTER(BYTE)()
    pcbNeeded = DWORD(0)
    pcReturned = DWORD(0)  # the number of PRINTER_INFO_1 structures retrieved
    winspool.EnumPrintersW(PRINTER_ENUM_LOCAL, Name, Level, ctypes.byref(info), 0,
            ctypes.byref(pcbNeeded), ctypes.byref(pcReturned))

    bufsize = pcbNeeded.value
    buffer = msvcrt.malloc(bufsize)
    winspool.EnumPrintersW(PRINTER_ENUM_LOCAL, Name, Level, buffer, bufsize,
            ctypes.byref(pcbNeeded), ctypes.byref(pcReturned))
    info = ctypes.cast(buffer, ctypes.POINTER(wst.PRINTER_INFO_1))
    ps=[info[i].pName for i in range(pcReturned.value)]
    msvcrt.free(buffer)
    return ps


def getPrinterInfoByDC(pdc):
    info={}
    if not pdc:
        return info
    try:
        scr=gdi32.CreateDCW('DISPLAY',NULL,NULL,NULL)
        info['DisplayDPI']=gdi32.GetDeviceCaps(scr,wcs.LOGPIXELSY)
        gdi32.DeleteDC(scr)
        
        info['MilimeterWidth']=mw=gdi32.GetDeviceCaps(pdc,wcs.HORZSIZE)
        info['MillimeterHeight']=mh=gdi32.GetDeviceCaps(pdc,wcs.VERTSIZE)

        info['PixelWidth']=pxw=gdi32.GetDeviceCaps(pdc,wcs.HORZRES)
        info['PixelHeight']=pxh=gdi32.GetDeviceCaps(pdc,wcs.VERTRES)

        info['PhysicalWidth']=phw=gdi32.GetDeviceCaps(pdc,wcs.PHYSICALWIDTH)
        info['PhysicalHeight']=phh=gdi32.GetDeviceCaps(pdc,wcs.PHYSICALHEIGHT)

        info['PhysicalOffsetX']=pox=gdi32.GetDeviceCaps(pdc,wcs.PHYSICALOFFSETX)
        info['PhysicalOffsetY']=poy=gdi32.GetDeviceCaps(pdc,wcs.PHYSICALOFFSETY)

        info['ScalingFactorX']=sfx=gdi32.GetDeviceCaps(pdc,wcs.SCALINGFACTORX)
        info['ScalingFactorY']=sfy=gdi32.GetDeviceCaps(pdc,wcs.SCALINGFACTORY)
        
        info['DPI']=dpi=gdi32.GetDeviceCaps(pdc,wcs.LOGPIXELSY)
        #int(pxw/mw*25.4)
        
        info['DPM']=dpi=pxw/mw #dot per millimeter
        #pdc=gdi32.DeleteDC(pdc)
    except Exception as e:
        print(e)
        pass
    return info

def getPrinterInfoByName(printer_name):
    '''
    获取打印机信息
    HDC CreateDC(
                 LPCTSTR lpszDriver,
      _In_       LPCTSTR lpszDevice,
                 LPCTSTR lpszOutput,
      _In_ const DEVMODE *lpInitData
    );    
    '''
    pptn=LPCWSTR(printer_name)
    pdc=gdi32.CreateDCW("WINSPOOL",pptn,None,None)
    info={}
    if not pdc:
        return info
    return getPrinterInfoByDC(pdc)



def getDefaultPrinterName():
    '''
    获取默认打印机
    BOOL GetDefaultPrinter(
      _In_    LPTSTR  pszBuffer,
      _Inout_ LPDWORD pcchBuffer
    );
    
    '''
    lPrinterNameLength=DWORD(0)
    winspool.GetDefaultPrinterW(None,ctypes.byref(lPrinterNameLength))
    printername=LPCWSTR('\x00'*lPrinterNameLength.value)
    winspool.GetDefaultPrinterW(printername,ctypes.byref(lPrinterNameLength))
    return printername.value

def selectPrinterByDlg(parent=None,setting={}):
    '''
    彈出對話框讓用戶選擇打印機及修改設置
    '''
    dlg = wst.PRINTDLGW()
    dlg.nMinPage=setting.get('MinPage',1)
    dlg.nMaxPage=setting.get('MaxPage',1)
    dlg.nToPage=setting.get('ToPage',1)
    dlg.Flags =  wcs.PD_RETURNDC
    if parent is not None:
        dlg.hwndOwner = parent._handle
    if comdlg32.PrintDlgW(byref(dlg)) and dlg.hDC:
        return dlg
    errcode = comdlg32.CommDlgExtendedError()
    if errcode:
        raise PrinterError( errcode)

def releasePrinter(PrinterDlg):
    '''
    釋放PrinterDlg創建的資源
    '''
    pt=PrinterDlg
    if pt:
        if pt.hDevMode:
            kernel32.GlobalFree(pt.hDevMode)
        if pt.hDevNames:
            kernel32.GlobalFree(pt.hDevNames)
        if pt.hDC:
            gdi32.DeleteDC(pt.hDC)

def drawImageToPrinter(img,printdlg):
    '''
    img:PIL ImageWin object
    printdlg:windows PrintDlg
    '''
    docinfo = wst.DOCINFO()
    docinfo.lpszDocName = 'test print'
    gdi32.StartDocW(printdlg.hDC, byref(docinfo))
    gdi32.StartPage(printdlg.hDC)
    gdi32.SaveDC(printdlg.hDC)
    w,h=img.size
    img.draw(printdlg.hDC,(0,0,w,h))
    gdi32.RestoreDC(printdlg.hDC,-1)
    gdi32.EndPage(printdlg.hDC)
    gdi32.EndDoc(printdlg.hDC)
    
    #hPrnDC, iWidthLP, iHeightLP);

class PrinterCanvas():
    def __init__(self,docinfo,size):#mode,size,color=0,dcinfo={}):
        '''
        dcinfo:打印机dc资料
        size:畫布大小,A 3-tuple, containing (width, height,unit),unit default in mm.
        
        '''
        size=list(size)
        size.append('mm')
        unit=size[2]
        size=size[:2]
        self._UnitMap={'mm':self.mmToPixel,
                       'pt':self.pointToPixel,
                       'in':self.inchToPixel}
        if size:
            size=self.unitToPixel(size,unit)
        else:
            size=(docinfo.get('PixelWidth'),docinfo.get('PixelHeight'))
        self._Image=Image.new('RGB',size,'white')
        self._Draw=ImageDraw.Draw(self._Image)
        self._DCInfo=docinfo

    def arc(self,xy, start, end, fill=None,unit='mm'):
        self._Draw.arc(xy,start,end,fill)

    def bitmap(self,xy, bitmap, fill=None,unit='mm'):
        self._Draw.bitmap(xy, bitmap, fill)

    def chord(xy, start, end, fill=None, outline=None,unit='mm'):
        self._Draw.chord(xy, start, end, fill, outline)

    def ellipse(xy, fill=None, outline=None,unit='mm'):
        self._Draw.ellipse(xy, fill, outline)

    def inchToPixel(self,inch):
        p=inch*self._DCInfo['DPI']
        return 1 if 0<p<1 else int(p) 

    def line(self,xy, fill=None, width=0,unit='mm'):
        xy=self.unitToPixel(xy)
        self._Draw.line(xy, fill, width)

    def label(self,label):
        '''
        draw label
        字體轉換
        計算顯示尺寸
        比較標籤大小寫
        是否換行,
        
        '''
        
        pass

    def mmToPixel(self,mm):
        p=mm*self._DCInfo['DPM']
        return 1 if 0<p<1 else int(p) 

      
    def pointToPixel(pt):
        p=pt*self._DCInfo['DPI']/72
        return 1 if 0<p<1 else int(p) 
    
    def pieslice(self,xy, start, end, fill=None, outline=None,unit='mm'):
        self._Draw.pieslice(xy, start, end, fill, outline)

    def point(self,xy, fill=None,unit='mm'):
        '''
        xy – Sequence of either 2-tuples like [(x, y), (x, y), ...] or numeric values like [x, y, x, y, ...].
        fill – Color to use for the point.
        '''
        self._Draw.point(xy, fill)

    def printOut(self,dc):
        ImageWin.Dib(self._Image).draw(dc,(0,0,self._Image.size[0],self._Image.size[1]))

    def polygon(self,xy, fill=None, outline=None,unit='mm'):
        self._Draw.polygon(xy, fill, outline)

    def rectangle(self,xy, fill=None, outline=None,unit='mm'):
        self._Draw.rectangle(xy, fill, outline)

    def size(self):
        return self._Image.size



    def text(self,xy, text, fill=None, font=('arial.ttf',10), anchor=None,unit='mm'):
        '''
        将字体尺寸转为打印尺寸
        打印机DPI/显示器DPI*字体尺寸*尺寸调整系数(24/18)
            (24/18)是經實際打印對比後量度後得到的比例,可能因為不同打印機係數不一樣
        font:(font, size, index, encoding)
        '''

        fnt=dict(zip(FontParaName[:len(font)],font))
        fsize=self._DCInfo['DPI']/self._DCInfo['DisplayDPI']*fnt.get('size',10)*(24/18)
        fnt['size']=int(fsize)
        font=ImageFont.truetype(**fnt)
        xy=self.unitToPixel(xy,unit)
        self._Draw.text(xy, text, fill, font, anchor)

    def multiline_text(self,xy, text, fill=None, font=('arial.ttf',10), anchor=None, spacing=0, align="left",unit='mm'):
        self._Draw.multiline_text(xy, text, fill, font, anchor, spacing, align)

    def textsize(self,text, font=('arial.ttf',10)):
        sz=self._Draw.textsize(text, font)
        return sz

    def multiline_textsize(self,text, font=('arial.ttf',10), spacing=0):
        sz=self._Draw.multiline_textsize(text, font, spacing)
        return sz

    def unitToPixel(self,xy,unit='mm'):
        '''
        xy:需转换单位的数字或数字列表
        '''
        if unit not in self._UnitMap:
            return xy
        if type(xy) in (int,float):
            return self._UnitMap[unit](xy)
        elif type(xy) in (list,tuple):
            return [self.unitToPixel(i,unit) for i in xy]
        else:
            raise Exception('paramater xy error,must be int or float or list/tuple.')
                
            
class WinPrinter:
    '''
    pt   磅或点数，是point简称 1磅=0.03527厘米=1/72英寸
    inch 英寸，1英寸=2.54厘米=96像素（分辨率为96dpi）
    px   像素，pixel的简称（本表参照显示器96dbi显示进行换算。像素不能出现小数点，一般是取小显示)
    绘制内容默认使用的单位
        字体单位使用point（磅）
        长度单位使用cm（厘米）
        需要使用像素作为单位时，需要特别声明
        

    使用步骤
    选择打印机
    绘制需打印的内容
    打印输出
    
    '''

    def  __init__(self):
        '''
        
        '''
        self.PrinterDlg=None
        self.PrinterDC=None
        self.PrinterInfo={}
        self.Pages=[]

    def __del__(self):
        print('__del__')

    def newPage(self,size=()):#page={}):
        '''
        新建画页
        在获取新打印DC或修改打印机设置后重新创建画页
        新页面将追加到Pages后面
        创建失败返回空
        size:畫布大小,A 3-tuple, containing (width, height,unit),unit default in mm.
        '''
        if not self.PrinterInfo:
            return
        if not size:
            size=(self.PrinterInfo['PixelWidth'],self.PrinterInfo['PixelHeight'],'px')
        pg=PrinterCanvas(self.PrinterInfo,size) #'RGB',(self.PrinterInfo['PixelWidth'],self.PrinterInfo['PixelHeight']),'white')
        self.Pages.append(pg)
        return pg

    def isReady(self):
        return self.PrinterDC!=None
        
    def selectByPrintDlg(self):
        if self.PrinterDlg:
            releasePrinter(self.PrinterDlg)
        self.PrinterDlg=selectPrinterByDlg()
        self.PrinterDC=self.PrinterDlg.hDC if self.PrinterDlg else None
        self.PrinterInfo=getPrinterInfoByDC(self.PrinterDC)

            
    def selectByName(self,printer_name):
        pptn=LPCWSTR(printer_name)
        self.PrinterDC=gdi32.CreateDCW("WINSPOOL",pptn,None,None)
        self.PrinterInfo=getPrinterInfoByDC(self.PrinterDC)        
        if self.PrinterDlg:
            releasePrinter(self.PrinterD)

    def printOut(self,docname):#,silent=True):
        '''
        打印已生成的内容
        docname:打印队列显示的任务名称
        silent:静默打印，不弹出打印对话框
        '''
        docinfo = wst.DOCINFO()
        docinfo.lpszDocName = docname
        gdi32.StartDocW(self.PrinterDC, byref(docinfo))
        for pg in self.Pages:
            gdi32.StartPage(self.PrinterDC)
            gdi32.SaveDC(self.PrinterDC)
            pg.printOut(self.PrinterDC)
            gdi32.RestoreDC(self.PrinterDC,-1)
            gdi32.EndPage(self.PrinterDC)
        gdi32.EndDoc(self.PrinterDC)
        

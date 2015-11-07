#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import code128
from . import pyqrnative

class QRCode(pyqrnative.QRCode):
    def __init__(self, typeNumber, errorCorrectLevel):
        super(QRCode,self).__init__(typeNumber,errorCorrectLevel)

    def makeImage(self):
        boxsize = 10 #pixels per box
        offset = 4 #boxes as border
        pixelsize = (self.getModuleCount() + offset + offset) * boxsize

        im = Image.new("RGB", (pixelsize, pixelsize), "white")
        d = ImageDraw.Draw(im)

        for r in range(self.getModuleCount()):
            for c in range(self.getModuleCount()):
                if (self.isDark(r, c) ):
                    x = (c + offset) * boxsize
                    y = (r + offset) * boxsize
                    b = [(x,y),(x+boxsize,y+boxsize)]
                    d.rectangle(b,fill="black")
        del d
        return im

    def drawImage(self,canvas,field):
        '''
        在canvas上绘制field的QRCode
        canvas: PrinterCanvas实例
        field: Report QRCode 实例
        '''
        cw,ch = canvas.size()
        bd = int(field.BorderWidth[:-2])
        bdunit = field.BorderWidth[-2:]
        bdx = canvas.unitToPixel(bd,bdunit)
        bcsize = min(cw,ch)
        moduleCount = self.getModuleCount()
        boxsize = int(bcsize / (moduleCount +bdx*2))

        for r in range(moduleCount):
            for c in range(moduleCount):
                if (self.isDark(r,c)):
                    x = (c + bdx) * boxsize
                    y = (r + bdx) * boxsize
                    b = (x,y,x+boxsize,y+boxsize)
                    canvas.rectangle(b,fill='black',unit='px')
        

def _drawCode128B(canvas,field):
    '''
    返回Image实例
    canvas: PrinterCanvas实例
    
    '''
    bitstr = code128.codeBFromString(field.Value)
    bd = int(field.BorderWidth[:-2])
    bdunit = field.BorderWidth[-2:]
    bdx = canvas.unitToPixel(bd,bdunit)
    bcw=canvas.unitToPixel(field.Width)
    bch = canvas.unitToPixel(field.Height)

    if field.Scaling:
        scaling = int(canvas._DCInfo['DPI'] / canvas._DCInfo['DisplayDPI'] * field.Scaling) or 1
    else:
        scaling = int(canvas._DCInfo['DPI'] / canvas._DCInfo['DisplayDPI']) or 1
        #scaling = int((bcw - bdx*2) / (len(bitstr)+20))

    if field.ShowLabel == '1':
        font=canvas.createFont((field.FontFile,field.FontSize))
        labelw,labelh = canvas.textsize(field.Value,font=font)
        txtL = (bcw - bdx * 2) / 2
        canvas.text((txtL,bdx),field.Value,fill = 0,font = font)
        bch = bch - labelh
    x = bdx + scaling * 10
    y = bch - bdx*2

    for char in bitstr:
        fill = (0,0,0,255) if int(char)  else (255,255,255,0)
        canvas.rectangle((x,bdx,x+scaling,y),fill = fill,unit = 'px')
        x += scaling
    rotate = int(field.Rotate or 0)


def _drawCode128(canvas):
    pass


def _drawQRCode(canvas,field):
    '''
    '''
    qr=QRCode(1,pyqrnative.QRErrorCorrectLevel.M)
    qr.addData(field.Value)
    qr.make()
    qr.drawImage(canvas,field)

BarcodeDraw = {
    'CODE128' : _drawCode128,
    'QRCODE' : _drawQRCode, 
    'CODE128B' : _drawCode128B 
    }

  
def drawBarcode(canvas,barcode):
    
    '''
    返回条码Image实例
    canvas: PrinterCanvas实例
    barcode: report TprtBarCodeField实例
    '''
    draw = BarcodeDraw.get(barcode.BarType,None)
    if not draw:
        return
    draw(canvas,barcode)

    
    

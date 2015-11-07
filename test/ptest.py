#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyrpt import pyrpt
from pyrpt import qtrpt,rptprint

def main():
     rp = qtrpt.QTRPT('./test/label.xml')
     rp_prt = rp.pyrpt()
     prpt=pyrpt.PyRpt()
     prpt.load(rp)
     pnt = rptprint.RptPrint()
     pnt.printOut(prpt)

if __name__ == '__main__':
    main()
    


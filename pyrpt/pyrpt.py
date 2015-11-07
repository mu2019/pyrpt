#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .uicore import winprint
from pyrpt  import AttrDict,LOCAL
import re


def formatstr(somethin,):
    '''
    '''
    
class PyRpt():
    def __init__(self,rpt=None,local=AttrDict(),engine={}):
        self.Pages = []
        self.DataSource = AttrDict()
        self.Scripts = AttrDict()
        self.BuiltinEngine = engine
        self.ReportName = ''        
        lc = AttrDict(local)
        lc.update(LOCAL)
        self.Local = lc
        if rpt:
            self.load(rpt)
            self.createDataSource()

    def createDataset(self,dataset,engine):
        d = AttrDict()
        if dataset.tag == 'TprtPyObject':
            d = engine[dataset.Object]
        elif dataset.tag == 'TprtHttpRst':
            pass
        elif dataset.tag == 'TprtSqlQuery':
            pass
        return d

    def createDataSource(self):
        engs={}
        dst = AttrDict()
        dso = AttrDict()
        for k,ds in self.DataSource.items():
            if ds.Engine == 'Builtin':
                engs[k] = self.BuiltinEngine[ds.EngineName]
            for d in ds.DataSet:
                dt = self.createDataset(d,engs[k])
                dst[d.Name] = dt
            
        self.Local._DataSet=dst
        
    def parseValue(self,field): #,band=None):
        '''
        解释报表字段值
        field: 需要解释的报表字段
        '''
        txt = field.Text
        txt = txt.replace('%','%(pc)s')
        vs = {'pc':'%'}
        for v in set(re.findall('<[\w.]+>',txt)):
            nv = v
            for fv in set(re.findall('\[[\w.]+\]',v)):
                nv = nv.replace(fv,'_DataSet.%s' % fv[1:-1])
            if nv != v:
                txt = txt.replace(v,nv)
            
        for v in set(re.findall('<[\w.]+>',txt)): 
            txt = txt.replace(v,'%('+v+')s')
            ev=eval(v[1:-1],{},self.Local)
            try:
                fmtstr=('{:'+field.DisplayFormat+"}").format(ev)
            except:
                fmtstr=str(ev)
            vs[v]=fmtstr
            
        for v in set(re.findall('\[[\w.]+\]',txt)): #field.Text)):
            txt = txt.replace(v,'%('+v+')s')
            ev=eval(v[1:-1],{},self.Local._DataSet)
            try:
                fmtstr=('{:'+field.DisplayFormat or ''+"}").format(ev)
            except:
                fmtstr=str(ev)
            vs[v]=fmtstr

        txt = txt % vs
        return txt


    def load(self,rpt):
        '''
        载入报表
        rpt: pyrpt/qtrpt/frrpt文件名称或实例
            文件名称时,只能为pyrtp格式
        '''
        if isinstance(rpt,str):
            self.loadFromFile(rpt)
        elif hasattr(rpt,'pyrpt'):
            rp=rpt.pyrpt()
            ds = AttrDict()
            for d in rp._DataSource:
                ds[d.Name] = d
            self.DataSource = ds
            self.Pages = rp._Pages
            
    def loadFromFile(self,pyrptfile):
        '''
        从报表文件载入报表
        '''
        

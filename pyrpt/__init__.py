#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime
from .uicore import winprint

class AttrDict(object):
    def __init__(self,dict_data={},read_only=False):
        self.__dict__['data']=OrderedDict(dict_data)
        #self.__dict__.update(dict_data)
        self.__dict__['ReadOnly']=read_only

    def __setitem__(self,item,value):
        self.__dict__['data'][item]=value

    def __getitem__(self,item):
        return self.__dict__['data'][item]

    def __getattr__(self,attr):
        return self.__dict__['data'].get(attr)

    def __setattr__(self,attr,value):
        assert not self.__dict__['ReadOnly'],'object just read only.'
        self.__dict__['data'][attr]=value

    def __delitem__(self,attr):
        self.__dict__['data'].pop(attr)

    def __delattr__(self,attr):
        self.__dict__['data'].pop(attr)        

    def keys(self):
        return self.__dict__['data'].keys()

    def values(self):
        return self.__dict__['data'].values()

    def items(self):
        return self.__dict__['data'].items()

    def update(self,adict):
        self.__dict__['data'].update(adict)

    
LOCAL = AttrDict()
LOCAL.Now = datetime.now()
LOCAL.Date = lambda : datetime.date(datetime.now())
LOCAL.Time = lambda : datetime.time(datetime.now())


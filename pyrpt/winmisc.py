#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform

def ErrorIfZero(handle):
    if handle == 0:
        raise WinError
    else:
        return handle


def get_win_ver():
    vs=platform.win32_ver()
    if vs:
        vs=vs[1].split('.')
        vs='0x'+('00'+vs[0])[-2:]+('00'+vs[1])[-2:]
        vs=int(vs,16)
        return vs
        
    
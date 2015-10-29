#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ctypes import * #POINTER,c_void_p,CFUNCTYPE,c_int,byref,pointer,c_wchar
from ctypes.wintypes import *
import sysinfo

LPPRINTHOOKPROC = c_void_p
LPSETUPHOOKPROC = c_void_p
ABORTPROC = CFUNCTYPE(c_int, HDC, c_int)
LPPRINTER_DEFAULTS = c_void_p
TCHAR=c_wchar
NULL = c_int(0)
#LPTTTOOLINFOW = POINTER(tagTOOLINFOW)
#PTOOLINFOW = POINTER(tagTOOLINFOW)
BOOL = c_int
BYTE = c_ubyte
CHAR = c_char
DWORD = c_ulong
HANDLE = c_void_p
HBITMAP = c_long
LONG = c_long
LPVOID = c_void_p
PVOID = c_void_p
UINT = c_uint
WCHAR = c_wchar
WORD = c_ushort
INT=c_int
LPCTSTR=c_wchar_p

WNDPROC = WINFUNCTYPE(c_long, c_int, c_uint, c_int, c_int)


HCURSOR=c_int
_REF=_R=R=REF_=byref
_PT=PT_=pointer



COLORREF = DWORD
LPBYTE = POINTER(BYTE)
LPWSTR = c_size_t #POINTER(WCHAR)
DWORD_PTR = UINT_PTR = ULONG_PTR = c_size_t
if sysinfo.is_x64_Python():
    INT_PTR = LONG_PTR = c_longlong
else:
    INT_PTR = LONG_PTR = c_long

HBITMAP = LONG_PTR #LONG
HINSTANCE = LONG_PTR #LONG
HMENU = LONG_PTR #LONG
HBRUSH = LONG_PTR #LONG
HTREEITEM = LONG_PTR #LONG
HWND = LONG_PTR #LONG

LPARAM = LONG_PTR
WPARAM = UINT_PTR

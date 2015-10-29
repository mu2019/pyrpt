import os, sys
import platform
import ctypes

def OS():
    architectureMap = {
        'x86':'x86',
        'i386':'x86',
        'i486':'x86',
        'i586':'x86',
        'i686':'x86',
        'x64':'x86_64',
        'amd64':'x86_64',
        'em64t':'x86_64',
        'x86_64':'x86_64',
        'ia64':'ia64'
    }
    if sys.platform == 'win32':
        architectureVar = os.environ.get('PROCESSOR_ARCHITEW6432', '')
        if architectureVar == '':
            architectureVar = os.environ.get('PROCESSOR_ARCHITECTURE', '')
        return architectureMap.get(architectureVar.lower(), 'Unknown')
    else:
        return architectureMap.get(platform.machine().lower(), '')

def PythonBitness():
    return ctypes.sizeof(ctypes.POINTER(ctypes.c_int)) * 8

def is_x64_Python():
    return PythonBitness() == 64

def is_x64_OS():
    return OS() in ['x86_64', 'ia64']

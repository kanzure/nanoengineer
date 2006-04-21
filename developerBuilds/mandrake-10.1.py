#!/usr/bin/python

import sys, os

def install(x):
    os.system("rpm -i " + x)

def uninstall(x):
    fields = x.strip().split('/')
    x = fields[-1]
    fields = x.split('-')
    x = '-'.join(fields[:-1])
    os.system("rpm -e " + x)

lst = [
    '/mnt/cdrom/media/main/libpython2.3-devel-2.3.4-6mdk.i586.rpm',
    '/mnt/cdrom/media/main/libMesaglut3-5.0.2-8mdk.i586.rpm',
    '/mnt/cdrom/media/main/libMesaglut3-devel-5.0.2-8mdk.i586.rpm',
    '/mnt/cdrom/media/contrib/sip-3.10.2-4mdk.i586.rpm',
    '/mnt/cdrom/media/contrib/libqscintilla5-1.4-2mdk.i586.rpm',
    '/mnt/cdrom/media/main/python-numeric-23.1-2mdk.i586.rpm',
    '/mnt/cdrom/media/contrib/PyQt-3.12-2mdk.i586.rpm',
    '/mnt/cdrom/media/contrib/PyQt-devel-3.12-2mdk.i586.rpm',
    ]

inst = ("uninstall" not in sys.argv[1:])

if inst:
    for x in lst:
        install(x)
else:
    lst.reverse()
    for x in lst:
        uninstall(x)

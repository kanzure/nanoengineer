# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
# $Id$
# modified from: Makefile for the simulator

UNAME := $(shell uname)
# dotted python version (2.3, 2.4)
PYDVER := $(shell python -c "import sys; print sys.version[:3]")
# un-dotted python version (23, 24)
PYVER := $(shell python -c "import sys; print sys.version[0]+sys.version[2]")

ifeq ($(OS),Windows_NT)
#---------------------------------------- Start Windows stuff
# One dollar sign for DOS and two for Cygwin
UNAME_A=$(shell ver)
# UNAME_A=$$(shell ver)   # Cygwin: but in this case use 'uname -a' anyway
CC = "C:/Dev-Cpp/bin/gcc.exe"
CFLAGS=-g -I"C:/Dev-Cpp/include" -I"C:/Python$(PYVER)/include" -Disnan=_isnan
LDFLAGS=-L"C:/Dev-Cpp/lib"
TARGET=foo.dll
STDC99=
SIMTARGET=simulator.exe
PYREXC=python c:/Python$(PYVER)/Scripts/pyrexc.py
#---------------------------------------- End of Windows stuff
else
#---------------------------------------- Start Unix/Mac stuff
UNAME_A=$$(uname -a)
CC=gcc
TARGET=foo.so
STDC99=-std=c99
SIMTARGET=simulator
CFLAGS:=$(shell python distutils_compile_options.py compiler_so)
ifeq ($(strip $(UNAME)),Darwin)
#---------------------------------------- Mac
CFLAGS+=-I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/lib/python$(PYDVER)/config \
    -I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/include/python$(PYDVER)/ \
   -DMACOSX -I/System/Library/Frameworks/OpenGL.framework/Headers
LDFLAGS=-Wl,-F. -framework Python
## LDFLAGS+=-L/usr/X11R6/lib -lGL
LDFLAGS+=-framework OpenGL
LDFLAGS+=-L/usr/lib -lm
LDSHARED=gcc -bundle
else
#---------------------------------------- Unix
PYBASE:=$(shell which python | sed "s%/bin/python%%")
CFLAGS+=-I$(PYBASE)/include/python$(PYDVER)
LDFLAGS=-L$(PYBASE)/lib/python$(PYDVER)/config -lm -lpython$(PYDVER)
LDFLAGS+=-L/usr/X11R6/lib -lGL
LDFLAGS+=-L/usr/lib -lm
LDSHARED=gcc -shared
#---------------------------------------- End of Unix
endif
PYREXC=$(shell python -c "import findpyrex; print findpyrex.find_pyrexc()")
CFLAGS+=-fno-strict-aliasing -DNDEBUG -g -Wall -Wmissing-prototypes \
  -Wstrict-prototypes -fPIC
# These CFLAGS and LDFLAGS are not used by distutils. If asked to
# compile or link, Pyrex uses distutils, and will therefore not
# use these CFLAGS and LDFLAGS.
#---------------------------------------- End of Unix/Mac stuff
endif


all: $(TARGET) CruftDialog.py

foo.o: foo.c

foo.so:  foo.o
	$(LDSHARED) foo.o -o foo.so $(LDFLAGS)

CruftDialog.py: CruftDialog.ui
	pyuic CruftDialog.ui > CruftDialog.py

clean:
	rm -f *.pyc *~ *.o *.so core.* CruftDialog.py

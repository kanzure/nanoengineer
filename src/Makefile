# Copyright (c) 2006 Nanorex, Inc. All rights reserved.

# $Id$

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
PYREXTARGET=atombase.dll
STDC99=
PYREXC=python c:/Python$(PYVER)/Scripts/pyrexc.py
#---------------------------------------- End of Windows stuff
else
#---------------------------------------- Start Unix/Mac stuff
UNAME_A=$$(uname -a)
CC=gcc
PYREXTARGET=atombase.so
STDC99=-std=c99
ifeq ($(strip $(UNAME)),Darwin)
#---------------------------------------- Mac
CFLAGS=-I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/lib/python$(PYDVER)/config \
   -I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/include/python$(PYDVER)/
LDFLAGS=-Wl,-F. -framework Python
LDSHARED=gcc -bundle
else
#---------------------------------------- Unix
CFLAGS=-pthread -I/usr/include/python$(PYDVER)
LDFLAGS=-L/usr/lib/python$(PYDVER)/config -lm -lpython$(PYDVER)
LDSHARED=gcc -shared
#---------------------------------------- End of Unix
endif
PYREXC=$(shell python -c "import platform; print platform.find_pyrexc()")
LDFLAGS+=-L/usr/lib -lm
CFLAGS+=-fno-strict-aliasing -DNDEBUG -g -Wall -Wmissing-prototypes \
  -Wstrict-prototypes -fPIC
# These CFLAGS and LDFLAGS are not used by distutils. If asked to
# compile or link, Pyrex uses distutils, and will therefore not
# use these CFLAGS and LDFLAGS.
#---------------------------------------- End of Unix/Mac stuff
endif

# CFLAGS=-g -Wall -I/usr/include/python2.4

UIFILES = $(wildcard *.ui)
##MANUAL_EDITED_FILES = ElementSelectorDialog.py
PYFILES0 = $(UIFILES:.ui=.py)

##PYFILES = $(filter-out $(MANUAL_EDITED_FILES), $(PYFILES0))

# bruce 051202 added this target
all : 
	echo "Nothing is remade by default -- use one of the explicit make targets."

# bruce 051202 added this target
extensions: 
	python setup.py build_ext --inplace

pyx: extensions

build : $(PYFILES0) 
$(PYFILES0) : %.py : %.ui
	pyuic $< -o $@ 

pyclean:
	rm -f $(PYFILES0) *.pyc *~

clean:
	rm -f *.pyc *~ *.o *.so *.a *.dll *.def atombase.c

abt: $(PYREXTARGET) atombasetests.py
	python atombasetests.py

atombase.c: atombasehelp.c atombase.pyx
	$(PYREXC) atombase.pyx

libpython$(PYVER).a: libpython$(PYVER).a.gz
	gunzip < libpython$(PYVER).a.gz > libpython$(PYVER).a

# On Windows, use "make atombase.dll"
atombase.dll: atombase.c $(PYREXOBJS) libpython$(PYVER).a version.h
	gcc -shared -I"C:/Python$(PYVER)/include" -o atombase.dll $(PYREXOBJS) \
		-Wl,--output-def,atombase.def -L. -lpython$(PYVER)

# On Mac and Linux, use "make atombase.so"
atombase.so: atombase.o
	$(LDSHARED) atombase.o -o atombase.so $(LDFLAGS)

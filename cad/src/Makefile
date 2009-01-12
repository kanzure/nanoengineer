# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.

# $Id$

UNAME := $(shell uname)
# dotted python version (2.3, 2.4)
PYDVER := $(shell python -c "import sys; print sys.version[:3]")
# un-dotted python version (23, 24)
PYVER := $(shell python -c "import sys; print sys.version[0]+sys.version[2]")

SHARED=atombase.lib samevals.lib

ifeq ($(OS),Windows_NT)
#---------------------------------------- Start Windows stuff
# One dollar sign for DOS and two for Cygwin
UNAME_A=$(shell ver)
# UNAME_A=$$(shell ver)   # Cygwin: but in this case use 'uname -a' anyway
CC = "C:/MinGW/bin/gcc.exe"
CFLAGS=-g -I"C:/MinGW/include" -I"C:/Python$(PYVER)/include" -Disnan=_isnan
LDFLAGS=-L"C:/MinGW/lib"
PYREXTARGET=atombase.dll
STDC99=
PYREXC=python c:/Python$(PYVER)/Scripts/pyrexc.py
SHARED_LIBRARIES = $(SHARED:.lib=.dll)
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
   -I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/include/python$(PYDVER)/ \
   -DMACOSX -I/System/Library/Frameworks/OpenGL.framework/Headers
LDFLAGS=-Wl,-F. -framework Python
LDFLAGS+=-L/usr/lib -lm
## LDFLAGS+=-L/usr/X11R6/lib -lGL
LDFLAGS+=-framework OpenGL
LDSHARED=gcc -bundle

# See if we can add Universal build flags
UNAME_M=$(shell uname -m)
ifeq ($(UNAME_M),i386)
CFLAGS+=-arch i386 -arch ppc
LDFLAGS+=-arch i386 -arch ppc
endif

else
#---------------------------------------- Unix
CFLAGS=-pthread -I/usr/include/python$(PYDVER)
LDFLAGS=-L/usr/lib/python$(PYDVER)/config -lm -lpython$(PYDVER)
LDFLAGS+=-L/usr/lib -lm
LDFLAGS+=-L/usr/X11R6/lib -lGL
LDSHARED=gcc -shared
#---------------------------------------- End of Unix
endif
SHARED_LIBRARIES = $(SHARED:.lib=.so)
PYREXC=$(shell python -c "import platform_dependent.PlatformDependent; print platform_dependent.PlatformDependent.find_pyrexc()")
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

DOC_MODULES = $(wildcard *.py) exprs/

# bruce 051202 added this target
all : 
	@echo "Nothing is remade by default -- use one of the explicit make targets."

build : $(PYFILES0) 
$(PYFILES0) : %.py : %.ui
	pyuic $< -o $@ 

doc:
	epydoc $(DOC_MODULES)

cleanpyc:
	find . -name \*.pyc -delete
	find . -name \*.pyo -delete

pyclean: cleanpyc
	rm -f $(PYFILES0) *~

clean: cleanpyc
	rm -f *~ *.o *.so *.a *.dll *.def core
	rm -f atombase.c samevals.c pyrex_test.c
	@echo
	@echo "Warning: make clean has removed C-coded shared libraries."
	@echo "To remake them, use 'make shared' ."

pyrex: $(PYREXTARGET)

abt: $(PYREXTARGET) atombasetests.py
	python atombasetests.py

atombase.c: atombasehelp.c atombase.pyx
	$(PYREXC) atombase.pyx

samevals.c: samevalshelp.c samevals.pyx
	$(PYREXC) samevals.pyx

libpython$(PYVER).a: libpython$(PYVER).a.gz
	gunzip < libpython$(PYVER).a.gz > libpython$(PYVER).a

shared: $(SHARED_LIBRARIES)

# On Windows, use "make atombase.dll"
atombase.dll: atombase.o libpython$(PYVER).a
	gcc -shared -I"C:/Python$(PYVER)/include" -o atombase.dll atombase.o \
		-Wl,--output-def,atombase.def -L. -lpython$(PYVER) -lopengl32

samevals.dll: samevals.o libpython$(PYVER).a
	gcc -shared -I"C:/Python$(PYVER)/include" -o samevals.dll samevals.o \
		-Wl,--output-def,samevals.def -L. -lpython$(PYVER)

# On Mac and Linux, use "make atombase.so"
atombase.so: atombase.o
	$(LDSHARED) atombase.o -o atombase.so $(LDFLAGS)

samevals.so: samevals.o
	$(LDSHARED) samevals.o -o samevals.so $(LDFLAGS)

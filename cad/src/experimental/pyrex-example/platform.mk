# Try to distill our platform-independence smarts into a separate file that can
# be used verbatim in other projects.

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
TARGET_SUFFIX=.dll
STDC99=
PYREXC=python c:/Python$(PYVER)/Scripts/pyrexc.py
#---------------------------------------- End of Windows stuff
else
#---------------------------------------- Start Unix/Mac stuff
UNAME_A=$$(uname -a)
CC=gcc
TARGET_SUFFIX=.so
STDC99=-std=c99
CFLAGS:=$(shell python makehelp.py compiler_so)
ifeq ($(strip $(UNAME)),Darwin)
#---------------------------------------- Mac
CFLAGS+=-I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/lib/python$(PYDVER)/config \
    -I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/include/python$(PYDVER)/
LDFLAGS=-Wl,-F. -framework Python
LDSHARED=gcc -bundle
else
#---------------------------------------- Unix
PYBASE:=$(shell which python | sed "s%/bin/python%%")
CFLAGS+=-I$(PYBASE)/include/python$(PYDVER)
LDFLAGS=-L$(PYBASE)/lib/python$(PYDVER)/config -lm -lpython$(PYDVER)
LDSHARED=gcc -shared
#---------------------------------------- End of Unix
endif
PYREXC=$(shell python makehelp.py findpyrex)
LDFLAGS+=-L/usr/X11R6/lib -lGL
LDFLAGS+=-L/usr/lib -lm
CFLAGS+=-fno-strict-aliasing -DNDEBUG -g -Wall -Wmissing-prototypes \
  -Wstrict-prototypes -fPIC
# These CFLAGS and LDFLAGS are not used by distutils. If asked to
# compile or link, Pyrex uses distutils, and will therefore not
# use these CFLAGS and LDFLAGS.
#---------------------------------------- End of Unix/Mac stuff
endif

PYREXTARGET=$(PYREXNAME)$(TARGET_SUFFIX)

all: $(PYREXTARGET)

libpython$(PYVER).a: libpython$(PYVER).a.gz
	gunzip < libpython$(PYVER).a.gz > libpython$(PYVER).a

clean:
	rm -f *~ *.o *.pyc $(PYREXNAME).c $(PYREXNAME).so 

$(PYREXNAME).c: $(PYREXNAME).pyx
	$(PYREXC) $(PYREXNAME).pyx

$(PYREXNAME).dll: $(PYREXNAME).c $(PYREXOBJS) libpython$(PYVER).a version.h
	gcc -shared -I"C:/Python$(PYVER)/include" -o $(PYREXNAME).dll $(PYREXOBJS) \
		-Wl,--output-def,$(PYREXNAME).def -L. -lpython$(PYVER)

$(PYREXNAME).so: $(PYREXNAME).o
	$(CC) -shared -o $(PYREXNAME).so $(PYREXNAME).o $(LDFLAGS)

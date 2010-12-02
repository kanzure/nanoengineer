# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

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
# CXXFLAGS = -O3 -W1 $(CFLAGS)     ### what is -W1 supposed to do???
CXXFLAGS = -O3 $(CFLAGS)
LDFLAGS=-L. -L"C:/Dev-Cpp/lib" -L"C:/Python$(PYVER)/libs"
TARGET=psurface.dll
PYREXC=python c:/Python$(PYVER)/Scripts/pyrexc.py
#---------------------------------------- End of Windows stuff
else
#---------------------------------------- Start Unix/Mac stuff
UNAME_A=$$(uname -a)
CC=gcc
CXX:=$(shell python distutils_compile_options.py compiler_cxx)
TARGET=psurface.so
CFLAGS:=$(shell python distutils_compile_options.py compiler_so)
CXXFLAGS:=$(CFLAGS)
ifeq ($(strip $(UNAME)),Darwin)
#---------------------------------------- Mac
CFLAGS+=-I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/lib/python$(PYDVER)/config \
    -I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/include/python$(PYDVER)/
LDFLAGS=-Wl,-F. -framework Python
LDSHARED=g++ -bundle
else
#---------------------------------------- Unix
PYBASE:=$(shell which python | sed "s%/bin/python%%")
CFLAGS+=-I$(PYBASE)/include/python$(PYDVER)
LDFLAGS=-L$(PYBASE)/lib/python$(PYDVER)/config -lm -lpython$(PYDVER)
LDSHARED=gcc -shared
#---------------------------------------- End of Unix
endif
PYREXC=$(shell python -c "import findpyrex; print findpyrex.find_pyrexc()")
LDFLAGS+=-L. -L/usr/lib -lm
CFLAGS+=-fno-strict-aliasing -DNDEBUG -g -Wall -Wmissing-prototypes \
  -Wstrict-prototypes -fPIC
# These CFLAGS and LDFLAGS are not used by distutils. If asked to
# compile or link, Pyrex uses distutils, and will therefore not
# use these CFLAGS and LDFLAGS.
#---------------------------------------- End of Unix/Mac stuff
endif

OBJS = cppsurface.o \
	rotationmatrix.o \
	intersection.o \
	hierarchy.o \
	collisiondetector.o \
	box.o \
	interval.o \
	boxtree.o \
	surface.o \
	container.o \
	bucket.o \
	distancetransform.o \
	triple.o \
	couple.o \
	psurface.o

all: $(TARGET)

install: $(TARGET)
	mkdir -p ../../../bin
	cp $(TARGET) ../../../bin

clean:
	rm -f *~ *.o *.pyc psurface.c *.so *.dll psurface.def

libpython$(PYVER).a: libpython$(PYVER).a.gz
	gunzip < libpython$(PYVER).a.gz > libpython$(PYVER).a

psurface.c: psurface.pyx
	$(PYREXC) psurface.pyx

psurface.o: psurface.c
	gcc -c psurface.c -o psurface.o $(CFLAGS)

cppsurface.o: cppsurface.cpp cppsurface.h
	g++ -c cppsurface.cpp -o cppsurface.o $(CXXFLAGS)

rotationmatrix.o: rotationmatrix.cpp rotationmatrix.h
	g++ -c rotationmatrix.cpp -o rotationmatrix.o $(CXXFLAGS)

intersection.o: intersection.cpp intersection.h
	g++ -c intersection.cpp -o intersection.o $(CXXFLAGS)

hierarchy.o: hierarchy.cpp hierarchy.h
	g++ -c hierarchy.cpp -o hierarchy.o $(CXXFLAGS)

collisiondetector.o: collisiondetector.cpp collisiondetector.h 
	g++ -c collisiondetector.cpp -o collisiondetector.o $(CXXFLAGS)

box.o: box.cpp box.h
	g++ -c box.cpp -o box.o $(CXXFLAGS)

interval.o: interval.cpp interval.h
	g++ -c interval.cpp -o interval.o $(CXXFLAGS)

boxtree.o: boxtree.cpp boxtree.h
	g++ -c boxtree.cpp -o boxtree.o $(CXXFLAGS)

surface.o: surface.cpp surface.h
	g++ -c surface.cpp -o surface.o $(CXXFLAGS)

container.o: container.cpp container.h
	g++ -c container.cpp -o container.o $(CXXFLAGS)

bucket.o: bucket.cpp bucket.h
	g++ -c bucket.cpp -o bucket.o $(CXXFLAGS)

distancetransform.o: distancetransform.cpp distancetransform.h
	g++ -c distancetransform.cpp -o distancetransform.o $(CXXFLAGS)

triple.o: triple.cpp triple.h
	g++ -c triple.cpp -o triple.o $(CXXFLAGS)

couple.o: couple.cpp couple.h
	g++ -c couple.cpp -o couple.o $(CXXFLAGS)

# Windows
psurface.dll: psurface.c $(OBJS) libpython$(PYVER).a
	g++ -shared -o psurface.dll $(OBJS) \
		-Wl,--output-def,psurface.def $(LDFLAGS) -lpython$(PYVER)

# Mac and Linux
psurface.so: $(OBJS)
	$(LDSHARED) $(OBJS) -o psurface.so $(LDFLAGS)

depend:
	head -`egrep -n "^# BEGIN" Makefile | sed 's/:.*//'` Makefile > tmp.mk
	makedepend -f tmp.mk -Y. *.[ch]
	mv -f tmp.mk Makefile
	rm tmp.mk.bak

# BEGIN DEPENDENCIES
# DO NOT DELETE

couple.o: triple.h
intersection.o: couple.h
rotationmatrix.o: triple.h
hierarchy.o: box.h boxtree.h container.h rotationmatrix.h
collisiondetector.o: boxtree.h triple.h hierarchy.h rotationmatrix.h
box.o: interval.h triple.h
boxtree.o: container.h box.h
bucket.o: container.h triple.h
distancetransform.o: container.h triple.h
csurface.o: cppsurface.h
psurface.o: csurface.h cppsurface.h
surface.o: container.h triple.h

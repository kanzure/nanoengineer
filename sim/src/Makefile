# Makefile for the simulator
# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
# $Id$

UNAME := $(shell uname)
# dotted python version (2.3, 2.4)
PYDVER := $(shell python -c "import sys; print sys.version[:3]")
# un-dotted python version (23, 24)
PYVER := $(shell python -c "import sys; print sys.version[0]+sys.version[2]")

LODE=
USEODE=
#LODE=-lode
#USEODE=-DUSE_ODE

ifeq ($(OS),Windows_NT)
#---------------------------------------- Start Windows stuff
# One dollar sign for DOS and two for Cygwin
UNAME_A=$(shell ver)
# UNAME_A=$$(shell ver)   # Cygwin: but in this case use 'uname -a' anyway
# Location of the MinGW compiler
CCDIR = C:/MinGW
#CCDIR = C:/Dev-Cpp
CC = "$(CCDIR)/bin/gcc.exe"
#CFLAGS=-g -I"$(CCDIR)/include" -I"C:/cygwin/usr/local/include" -I"C:/Python$(PYVER)/include" -Disnan=_isnan

CFLAGS=-g -I"$(CCDIR)/include" -I"C:/ode-win32-0.7/include" -I"C:/Python$(PYVER)/include" -Disnan=_isnan $(USEODE)

LDFLAGS=-L"$(CCDIR)/lib" -L"C:/ode-win32-0.7/lib/releasedll" $(LODE)
PYREXTARGET=sim.dll
STDC99=
SIMTARGET=simulator.exe
PYREXC=python c:/Python$(PYVER)/Scripts/pyrexc.py
#---------------------------------------- End of Windows stuff
else
#---------------------------------------- Start Unix/Mac stuff
UNAME_A=$$(uname -a)
CC=gcc
PYREXTARGET=sim.so
STDC99=-std=c99
SIMTARGET=simulator
CFLAGS=-pthread -fno-strict-aliasing -g -I/usr/include/python2.3 -fno-strict-aliasing -Wall -Wmissing-prototypes -Wstrict-prototypes -fPIC
#CFLAGS:=$(shell python distutils_compile_options.py compiler_so)
ifeq ($(strip $(UNAME)),Darwin)
#---------------------------------------- Mac
CFLAGS+=-I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/lib/python$(PYDVER)/config \
    -I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/include/python$(PYDVER)/
LDFLAGS=-Wl,-F. -framework Python
LDSHARED=gcc -bundle
else
#---------------------------------------- Unix
PYBASE:=$(shell which python | sed "s%/bin/python%%")
CFLAGS+=-I$(PYBASE)/include/python$(PYDVER) $(USEODE)
LDFLAGS=-L$(PYBASE)/lib/python$(PYDVER)/config $(LODE) -lm -lpython$(PYDVER)
LDSHARED=gcc -shared
#---------------------------------------- End of Unix
endif
PYREXC=$(shell python -c "import findpyrex; print findpyrex.find_pyrexc()")
LDFLAGS+=-L/usr/lib -lm
CFLAGS+=-fno-strict-aliasing -DNDEBUG -g -Wall -Wmissing-prototypes \
  -Wstrict-prototypes -fPIC
# These CFLAGS and LDFLAGS are not used by distutils. If asked to
# compile or link, Pyrex uses distutils, and will therefore not
# use these CFLAGS and LDFLAGS.
#---------------------------------------- End of Unix/Mac stuff
endif

COMMONOBJS=\
	allocate.o \
	amber_patterns.o \
	dynamics.o \
	globals.o \
	hashtable.o \
	interpolate.o \
	jigs.o \
	lin-alg.o \
	minimize.o \
	minstructure.o \
	newtables.o \
	part.o \
	pam5_patterns.o \
	pattern.o \
	potential.o \
	printers.o \
	printGromacsTopology.o \
	read_amber_itp.o \
	readmmp.o \
	readxyz.o \
	rigid.o \
	rigid-ode.o \
	structcompare.o \
	writemovie.o

ifeq ($(OS),Windows_NT)
	COMMONOBJS+= strtok_r.o
endif

PYREXSRCS=$(COMMONOBJS:.o=.c)

SIMOBJS=$(COMMONOBJS) simulator.o

PYREXOBJS=$(COMMONOBJS) sim.o

EXE_DIRECTORY=../../cad/bin
#EXE_DIRECTORY=~/bin

ifeq ($(PROFILING),1)
CFLAGS+=-pg
LDFLAGS+=-pg
endif

ifeq ($(WWDEBUG),1)
CFLAGS+=-DWWDEBUG
endif

# It's important not to change these two targets.
all: $(SIMTARGET)

help:
	echo $(DISTU)

# It's important not to change these two targets.
pyx: $(PYREXTARGET)

.PHONY: all lall noopt pyx install install-linux clean dist_clean depend depends

lall: all pyx glviewer

SUFFIXES: .c .h .o ;

.c.o:
	$(CC) -c $(CFLAGS) -o $@ $(@:.o=.c)

#bruce 051230 added dependency on Makefile to some rules (not all, and not as many are
# affected as I'd hoped);
# this is desirable since Makefile defines CFLAGS (and full remake doesn't take very long);
# feel free to do this in a cleaner way, or not at all if it causes problems.

# -std-c99 gets us isnormal()
structcompare.o: structcompare.c simulator.h
	$(CC) -c $(STDC99) $(CFLAGS) -o structcompare.o structcompare.c

ifeq ($(OS),Windows_NT)
# We need sim.c rule to build for Windows
sim.c: simhelp.c sim.pyx
	$(PYREXC) sim.pyx

libpython$(PYVER).a: libpython$(PYVER).a.gz
	gunzip < libpython$(PYVER).a.gz > libpython$(PYVER).a

sim.dll: sim.c $(PYREXOBJS) libpython$(PYVER).a version.h
	gcc -shared -I"C:/Python$(PYVER)/include" -o sim.dll $(PYREXOBJS) \
		-Wl,--output-def,sim.def -L. -lpython$(PYVER) -L"C:/ode-win32-0.7/lib/releasedll" $(LODE)
else
# here's the distutils version:
#sim.so: Makefile $(PYREXSRCS) version.h bends.gen bonds.gen sim.pyx simhelp.c
#	python setup.py build_ext --inplace

sim.c: sim.pyx simhelp.c
	$(PYREXC) sim.pyx

sim.so: $(PYREXOBJS)
	$(LDSHARED) $(PYREXOBJS) -o sim.so $(LDFLAGS)
endif

tables.c: gentab.py
	python gentab.py > tables.c

bonds.gen: stretch.py stretch.parms
	python stretch.py stretch.parms > bonds.gen

bends.gen: bend.py bending.parms
	python bend.py bending.parms > bends.gen

# There is something about bends.gen that the compiler doesn't want to
# optimize. It's getting tripped up by the bend names; if they are all
# the same it doesn't get stuck.
newtables.o: newtables.c
	$(CC) -o newtables.o -c -g newtables.c

version.h:
	python makehelp.py "$(CFLAGS)" "$(LDFLAGS)" "$(UNAME_A)" \
		| grep -v "^running " > version.h

noopt:
	make CFLAGS=-g $(SIMTARGET)

$(SIMTARGET): $(SIMOBJS) version.h
	$(CC) -o $(SIMTARGET) $(LDFLAGS) $(SIMOBJS) -lm

testminimize: minimize.c allocate.o
	$(CC) -o testminimize.o $(CFLAGS) -DTEST -c minimize.c
	$(CC) -o testminimize $(LDFLAGS) testminimize.o allocate.o
teststructcompare: structcompare.c minimize.o allocate.o lin-alg.o
	$(CC) -o teststructcompare.o $(CFLAGS) -DTEST -c structcompare.c
	$(CC) -o teststructcompare $(LDFLAGS) teststructcompare.o minimize.o allocate.o lin-alg.o

glviewer: glviewer.c allocate.o
	$(CC) -o glviewer.o $(CFLAGS) -c glviewer.c
	$(CC) -o glviewer $(LDFLAGS) -L/usr/X11R6/lib -lGL -lGLU glviewer.o allocate.o

install: $(SIMTARGET)
	if [ ! -d $$HOME/bin ] ; then \
		mkdir $$HOME/bin ;\
	fi
	cp -f $(SIMTARGET) $$HOME/bin
	if [ ! -d $(EXE_DIRECTORY) ] ; then \
		mkdir $(EXE_DIRECTORY) ;\
	fi
	cp $(SIMTARGET) $(EXE_DIRECTORY) 

install-linux: install $(PYREXTARGET)
	cp sim.so $(EXE_DIRECTORY)

clean:
	rm -f version.h bonds.gen bends.gen
	rm -f $(SIMTARGET) moldisp molsim physeng sim.so sim.c
	rm -f glviewer
	rm -f *.o *.a *.dll *.def sim.c *.so \.\#* *~ fmc.mmp dumpstruct.xyz *.pyc *.gcno
	rm -rf html gmon.out build obj
	rm -f tests/*/*.trcnew
	rm -f tests/*/*.altout
	rm -f tests/*/*.diff
	rm -f tests/*/*.xyz
	rm -f tests/*/*.dpb

dist_clean: clean
	rm -f TAGS

TAGS:
	etags *.c *.h


doxy:
	doxygen Doxyfile

depend: version.h
	head -`egrep -n "^# BEGIN" Makefile | sed 's/:.*//'` Makefile > tmp.mk
	makedepend -f tmp.mk -Y. *.[ch]
	mv -f tmp.mk Makefile
	rm tmp.mk.bak

depends: depend

# BEGIN DEPENDENCIES
# DO NOT DELETE

allocate.o: allocate.h
amber_patterns.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h
amber_patterns.o: minimize.h structcompare.h part.h newtables.h interpolate.h
amber_patterns.o: readmmp.h readxyz.h read_amber_itp.h printers.h dynamics.h
amber_patterns.o: jigs.h amber_patterns.h pam5_patterns.h pattern.h
amber_patterns.o: potential.h minstructure.h writemovie.h rigid.h
amber_patterns.o: printGromacsTopology.h globals.h
dynamics.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
dynamics.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
dynamics.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
dynamics.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
dynamics.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
dynamics.o: globals.h
globals.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
globals.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
globals.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
globals.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
globals.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
globals.o: globals.h
glviewer.o: allocate.h
hashtable.o: allocate.h hashtable.h
interpolate.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h
interpolate.o: minimize.h structcompare.h part.h newtables.h interpolate.h
interpolate.o: readmmp.h readxyz.h read_amber_itp.h printers.h dynamics.h
interpolate.o: jigs.h amber_patterns.h pam5_patterns.h pattern.h potential.h
interpolate.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
interpolate.o: globals.h
jigs.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
jigs.o: structcompare.h part.h newtables.h interpolate.h readmmp.h readxyz.h
jigs.o: read_amber_itp.h printers.h dynamics.h jigs.h amber_patterns.h
jigs.o: pam5_patterns.h pattern.h potential.h minstructure.h writemovie.h
jigs.o: rigid.h printGromacsTopology.h globals.h
lin-alg.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
lin-alg.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
lin-alg.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
lin-alg.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
lin-alg.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
lin-alg.o: globals.h
minimize.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
minimize.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
minimize.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
minimize.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
minimize.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
minimize.o: globals.h
minstructure.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h
minstructure.o: minimize.h structcompare.h part.h newtables.h interpolate.h
minstructure.o: readmmp.h readxyz.h read_amber_itp.h printers.h dynamics.h
minstructure.o: jigs.h amber_patterns.h pam5_patterns.h pattern.h potential.h
minstructure.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
minstructure.o: globals.h
newtables.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
newtables.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
newtables.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
newtables.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
newtables.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
newtables.o: globals.h bonds.gen bends.gen
pam5_patterns.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h
pam5_patterns.o: minimize.h structcompare.h part.h newtables.h interpolate.h
pam5_patterns.o: readmmp.h readxyz.h read_amber_itp.h printers.h dynamics.h
pam5_patterns.o: jigs.h amber_patterns.h pam5_patterns.h pattern.h
pam5_patterns.o: potential.h minstructure.h writemovie.h rigid.h
pam5_patterns.o: printGromacsTopology.h globals.h
part.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
part.o: structcompare.h part.h newtables.h interpolate.h readmmp.h readxyz.h
part.o: read_amber_itp.h printers.h dynamics.h jigs.h amber_patterns.h
part.o: pam5_patterns.h pattern.h potential.h minstructure.h writemovie.h
part.o: rigid.h printGromacsTopology.h globals.h
pattern.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
pattern.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
pattern.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
pattern.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
pattern.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
pattern.o: globals.h
potential.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
potential.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
potential.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
potential.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
potential.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
potential.o: globals.h
printers.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
printers.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
printers.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
printers.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
printers.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
printers.o: globals.h
printGromacsTopology.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h
printGromacsTopology.o: minimize.h structcompare.h part.h newtables.h
printGromacsTopology.o: interpolate.h readmmp.h readxyz.h read_amber_itp.h
printGromacsTopology.o: printers.h dynamics.h jigs.h amber_patterns.h
printGromacsTopology.o: pam5_patterns.h pattern.h potential.h minstructure.h
printGromacsTopology.o: writemovie.h rigid.h printGromacsTopology.h globals.h
read_amber_itp.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h
read_amber_itp.o: minimize.h structcompare.h part.h newtables.h interpolate.h
read_amber_itp.o: readmmp.h readxyz.h read_amber_itp.h printers.h dynamics.h
read_amber_itp.o: jigs.h amber_patterns.h pam5_patterns.h pattern.h
read_amber_itp.o: potential.h minstructure.h writemovie.h rigid.h
read_amber_itp.o: printGromacsTopology.h globals.h
readers.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
readers.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
readers.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
readers.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
readers.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
readers.o: globals.h
readmmp.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
readmmp.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
readmmp.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
readmmp.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
readmmp.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
readmmp.o: globals.h
readxyz.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
readxyz.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
readxyz.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
readxyz.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
readxyz.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
readxyz.o: globals.h
rigid.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
rigid.o: structcompare.h part.h newtables.h interpolate.h readmmp.h readxyz.h
rigid.o: read_amber_itp.h printers.h dynamics.h jigs.h amber_patterns.h
rigid.o: pam5_patterns.h pattern.h potential.h minstructure.h writemovie.h
rigid.o: rigid.h printGromacsTopology.h globals.h rigid-ode.h
rigid-ode.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
rigid-ode.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
rigid-ode.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
rigid-ode.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
rigid-ode.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
rigid-ode.o: globals.h rigid-ode.h
sim.o: simhelp.c simulator.h debug.h lin-alg.h allocate.h hashtable.h
sim.o: minimize.h structcompare.h part.h newtables.h interpolate.h readmmp.h
sim.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
sim.o: amber_patterns.h pam5_patterns.h pattern.h potential.h minstructure.h
sim.o: writemovie.h rigid.h printGromacsTopology.h globals.h version.h
simhelp.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
simhelp.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
simhelp.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
simhelp.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
simhelp.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
simhelp.o: globals.h version.h
simulator.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
simulator.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
simulator.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
simulator.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
simulator.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
simulator.o: globals.h version.h
simulator.o: debug.h lin-alg.h allocate.h hashtable.h minimize.h
simulator.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
simulator.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
simulator.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
simulator.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
simulator.o: globals.h
structcompare.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h
structcompare.o: minimize.h structcompare.h part.h newtables.h interpolate.h
structcompare.o: readmmp.h readxyz.h read_amber_itp.h printers.h dynamics.h
structcompare.o: jigs.h amber_patterns.h pam5_patterns.h pattern.h
structcompare.o: potential.h minstructure.h writemovie.h rigid.h
structcompare.o: printGromacsTopology.h globals.h
writemovie.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
writemovie.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
writemovie.o: readxyz.h read_amber_itp.h printers.h dynamics.h jigs.h
writemovie.o: amber_patterns.h pam5_patterns.h pattern.h potential.h
writemovie.o: minstructure.h writemovie.h rigid.h printGromacsTopology.h
writemovie.o: globals.h

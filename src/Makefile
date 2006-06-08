# Makefile for the simulator
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
PYREXTARGET=sim.dll
STDC99=
SIMTARGET=simulator.exe
PYREXC=python c:/Python$(PYVER)/Scripts/pyrexc.py sim.pyx
#---------------------------------------- End of Windows stuff
else
#---------------------------------------- Start Unix/Mac stuff
UNAME_A=$$(uname -a)
CC=gcc
PYREXTARGET=sim.so
STDC99=-std=c99
SIMTARGET=simulator
ifeq ($(strip $(UNAME)),Darwin)
#---------------------------------------- Mac
PYREXC=/Library/Python/$(PYDVER)/Pyrex-0.9.3.1/bin/pyrexc
CFLAGS=-I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/lib/python$(PYDVER)/config \
   -I/System/Library/Frameworks/Python.framework/Versions/$(PYDVER)/include/python$(PYDVER)/
LDFLAGS=-Wl,-F. -framework Python
LDSHARED=gcc -bundle
else
#---------------------------------------- Unix
PYREXC=pyrexc
CFLAGS=-pthread -I/usr/include/python$(PYDVER)
LDFLAGS=-L/usr/lib/python$(PYDVER)/config -lm -lpython$(PYDVER)
LDSHARED=gcc -shared
#---------------------------------------- End of Unix
endif
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
	potential.o \
	printers.o \
	readmmp.o \
	readxyz.o \
	structcompare.o \
	writemovie.o

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
		-Wl,--output-def,sim.def -L. -lpython$(PYVER)
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

version.h:
	python makehelp.py "$(CFLAGS)" "$(LDFLAGS)" "$(UNAME_A)" \
		| grep -v "^running " > version.h

noopt:
	make CFLAGS=-g $(SIMTARGET)

$(SIMTARGET): $(SIMOBJS) version.h
	$(CC) -o $(SIMTARGET) $(LDFLAGS) $(SIMOBJS)

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
dynamics.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
dynamics.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
dynamics.o: readxyz.h printers.h dynamics.h jigs.h potential.h minstructure.h
dynamics.o: writemovie.h globals.h
globals.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
globals.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
globals.o: readxyz.h printers.h dynamics.h jigs.h potential.h minstructure.h
globals.o: writemovie.h globals.h
glviewer.o: allocate.h
hashtable.o: allocate.h hashtable.h
interpolate.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h
interpolate.o: minimize.h structcompare.h part.h newtables.h interpolate.h
interpolate.o: readmmp.h readxyz.h printers.h dynamics.h jigs.h potential.h
interpolate.o: minstructure.h writemovie.h globals.h
jigs.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
jigs.o: structcompare.h part.h newtables.h interpolate.h readmmp.h readxyz.h
jigs.o: printers.h dynamics.h jigs.h potential.h minstructure.h writemovie.h
jigs.o: globals.h
lin-alg.o: lin-alg.h
minimize.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
minimize.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
minimize.o: readxyz.h printers.h dynamics.h jigs.h potential.h minstructure.h
minimize.o: writemovie.h globals.h
minstructure.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h
minstructure.o: minimize.h structcompare.h part.h newtables.h interpolate.h
minstructure.o: readmmp.h readxyz.h printers.h dynamics.h jigs.h potential.h
minstructure.o: minstructure.h writemovie.h globals.h
newtables.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
newtables.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
newtables.o: readxyz.h printers.h dynamics.h jigs.h potential.h
newtables.o: minstructure.h writemovie.h globals.h bonds.gen bends.gen
part.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
part.o: structcompare.h part.h newtables.h interpolate.h readmmp.h readxyz.h
part.o: printers.h dynamics.h jigs.h potential.h minstructure.h writemovie.h
part.o: globals.h
potential.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
potential.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
potential.o: readxyz.h printers.h dynamics.h jigs.h potential.h
potential.o: minstructure.h writemovie.h globals.h
printers.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
printers.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
printers.o: readxyz.h printers.h dynamics.h jigs.h potential.h minstructure.h
printers.o: writemovie.h globals.h
readers.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
readers.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
readers.o: readxyz.h printers.h dynamics.h jigs.h potential.h minstructure.h
readers.o: writemovie.h globals.h
readmmp.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
readmmp.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
readmmp.o: readxyz.h printers.h dynamics.h jigs.h potential.h minstructure.h
readmmp.o: writemovie.h globals.h
readxyz.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
readxyz.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
readxyz.o: readxyz.h printers.h dynamics.h jigs.h potential.h minstructure.h
readxyz.o: writemovie.h globals.h
sim.o: simhelp.c simulator.h debug.h lin-alg.h allocate.h hashtable.h
sim.o: minimize.h structcompare.h part.h newtables.h interpolate.h readmmp.h
sim.o: readxyz.h printers.h dynamics.h jigs.h potential.h minstructure.h
sim.o: writemovie.h globals.h version.h
simhelp.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
simhelp.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
simhelp.o: readxyz.h printers.h dynamics.h jigs.h potential.h minstructure.h
simhelp.o: writemovie.h globals.h version.h
simulator.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
simulator.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
simulator.o: readxyz.h printers.h dynamics.h jigs.h potential.h
simulator.o: minstructure.h writemovie.h globals.h version.h
simulator.o: debug.h lin-alg.h allocate.h hashtable.h minimize.h
simulator.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
simulator.o: readxyz.h printers.h dynamics.h jigs.h potential.h
simulator.o: minstructure.h writemovie.h globals.h
structcompare.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h
structcompare.o: minimize.h structcompare.h part.h newtables.h interpolate.h
structcompare.o: readmmp.h readxyz.h printers.h dynamics.h jigs.h potential.h
structcompare.o: minstructure.h writemovie.h globals.h
tables.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
tables.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
tables.o: readxyz.h printers.h dynamics.h jigs.h potential.h minstructure.h
tables.o: writemovie.h globals.h
writemovie.o: simulator.h debug.h lin-alg.h allocate.h hashtable.h minimize.h
writemovie.o: structcompare.h part.h newtables.h interpolate.h readmmp.h
writemovie.o: readxyz.h printers.h dynamics.h jigs.h potential.h
writemovie.o: minstructure.h writemovie.h globals.h

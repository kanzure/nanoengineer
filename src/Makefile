# Makefile for the simulator
# $Id$

ifeq ($(OS),Windows_NT)
CC = "C:/Dev-Cpp/bin/gcc.exe"
CFLAGS=-I"C:/Dev-Cpp/include"
LDFLAGS=-L"C:/Dev-Cpp/lib"
PYREXTARGET=sim.dll
STDC99=
SIMTARGET=simulator.exe
else
# non-Windows
CC=gcc
CFLAGS=-g -Wmissing-prototypes -Wall
# Note: these CFLAGS are probably not used to build the files for Pyrex, 
# only for the standalone simulator executable. [bruce 051230 guess]
LDFLAGS=-L/usr/lib -lm
PYREXTARGET=sim.so
STDC99=-std=c99
SIMTARGET=simulator
endif

UNAME_A=$$(uname -a)

PYREXOBJS=\
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

PYREXSRCS=$(PYREXOBJS:.o=.c)

SIMOBJS=$(PYREXOBJS) simulator.o

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

# We need sim.c rule to build for Windows
sim.c: simhelp.c sim.pyx
	python c:/Python23/Scripts/pyrexc.py sim.pyx

libpython23.a: libpython23.a.gz
	gunzip < libpython23.a.gz > libpython23.a

sim.dll: sim.c $(PYREXOBJS) libpython23.a version.h
	gcc -shared -I"C:/Python23/include" -o sim.dll sim.c $(PYREXOBJS) \
		-Wl,--output-def,sim.def -L. -lpython23

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
	$(CC) -o glviewer $(LDFLAGS) -lGL -lGLU glviewer.o allocate.o

# don't add dependencies here, add them to setup.py "depends" list
# unless they require independent rebuilding
sim.so: Makefile version.h bends.gen bonds.gen
	python setup.py build_ext --inplace

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
	rm -f version.h
	rm -f $(SIMTARGET) moldisp molsim physeng sim.so sim.c
	rm -f *.o *.a *.dll *.def sim.c *.so *~ fmc.mmp dumpstruct.xyz *.pyc
	rm -rf html gmon.out build
	rm -f tests/*/*.altout
	rm -f tests/*/*.diff
	rm -f tests/*/*.xyz
	rm -f tests/*/*.dpb

dist_clean: clean
	rm -f TAGS bonds.gen bends.gen

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

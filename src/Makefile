# Makefile for the simulator
# $Id$

ifeq ($(OS),Windows_NT)
CC = "C:/Dev-Cpp/bin/gcc.exe"
CFLAGS=-I"C:/Dev-Cpp/include"
LDFLAGS=-L"C:/Dev-Cpp/lib"
STDC99=
WARNWIN32="echo Please build this with Makefile.win32, not Makefile"
HALTWIN32="exit 1"
else
# non-Windows
CC=gcc
CFLAGS=-g -Wmissing-prototypes -Wall
# Note: these CFLAGS are probably not used to build the files for Pyrex, 
# only for the standalone simulator executable. [bruce 051230 guess]
LDFLAGS=-L/usr/lib -lm
STDC99=-std=c99
WARNWIN32=
HALTWIN32=
endif

EXE_DIRECTORY=../../cad/bin
#EXE_DIRECTORY=~/bin

ifeq ($(PROFILING),1)
CFLAGS+=-pg
LDFLAGS+=-pg
endif

ifeq ($(WWDEBUG),1)
CFLAGS+=-DWWDEBUG
endif

all:
	make clean
	make empty-trace-prefix
	make trace-prefix
	make simulator pyx

lall: all glviewer

SUFFIXES: .c .h .o ;

.c.o:
	$(CC) -c $(CFLAGS) -o $@ $(@:.o=.c)

SIMINCLUDES=\
	allocate.h \
	debug.h \
	dynamics.h \
	globals.h \
	hashtable.h \
	interpolate.h \
	jigs.h \
	lin-alg.h \
	minimize.h \
	minstructure.h \
	newtables.h \
	part.h \
	potential.h \
	printers.h \
	readmmp.h \
	readxyz.h \
	structcompare.h \
	writemovie.h

#bruce 051230 added dependency on Makefile to some rules (not all, and not as many are
# affected as I'd hoped);
# this is desirable since Makefile defines CFLAGS (and full remake doesn't take very long);
# feel free to do this in a cleaner way, or not at all if it causes problems.

simulator.h: $(SIMINCLUDES) Makefile

allocate.o: allocate.h Makefile
globals.o: simulator.h
hashtable.o: allocate.h hashtable.h Makefile
interpolate.o: simulator.h
jigs.o: simulator.h
lin-alg.o: lin-alg.h Makefile
minimize.o: allocate.h minimize.h debug.h Makefile
minstructure.o: simulator.h
newtables.o: simulator.h bonds.h bends.h
part.o: simulator.h
potential.o: simulator.h
printers.o: simulator.h
readmmp.o: simulator.h
readxyz.o: simulator.h
simulator.o: simulator.h
traceprefix.o: traceprefix.c
writemovie.o: simulator.h

# -std-c99 gets us isnormal()
structcompare.o: structcompare.c simulator.h
	$(CC) -c $(STDC99) $(CFLAGS) -o structcompare.o structcompare.c

# Rules for sim.o and sim.c are obsolete.  wware 060101 [rev 1.48]

tables.c: gentab.py
	python gentab.py > tables.c

bonds.h: parmlist.py stretch.parms
	python parmlist.py stretch.parms > bonds.h

bends.h: bend.perl bending.parms
	./bend.perl < bending.parms > bends.h

SIMOBJS=\
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
	traceprefix.o \
	writemovie.o \
	simulator.o

noopt:
	make CFLAGS=-g simulator

empty-trace-prefix:
	echo "char tracePrefix[] = \"\\" > traceprefix.c
	echo "# Simulator built:" `date` | sed 's#$$#\\n\\#' >>traceprefix.c
	echo "# Platform:" `uname -a` | sed 's#$$#\\n\\#' >>traceprefix.c
	echo "\";" >>traceprefix.c

trace-prefix:
	echo "char tracePrefix[] = \"\\" > _traceprefix.c
	echo "# Simulator built:" `date` | sed 's#$$#\\n\\#' >>_traceprefix.c
	echo "# Platform:" `uname -a` | sed 's#$$#\\n\\#' >>_traceprefix.c
	make simulator | sed 's/^/# /' | sed 's#$$#\\n\\#' >>_traceprefix.c
	make extensions | sed 's/^/# /' | sed 's#$$#\\n\\#' >>_traceprefix.c
	echo "\";" >>_traceprefix.c
	mv -f _traceprefix.c traceprefix.c

simulator: $(SIMOBJS)
	$(CC) -o simulator $(LDFLAGS) $(SIMOBJS)

testminimize: minimize.c allocate.o
	$(CC) -o testminimize.o $(CFLAGS) -DTEST -c minimize.c
	$(CC) -o testminimize $(LDFLAGS) testminimize.o allocate.o

teststructcompare: structcompare.c minimize.o allocate.o lin-alg.o
	$(CC) -o teststructcompare.o $(CFLAGS) -DTEST -c structcompare.c
	$(CC) -o teststructcompare $(LDFLAGS) teststructcompare.o minimize.o allocate.o lin-alg.o

glviewer: glviewer.c allocate.o
	$(CC) -o glviewer.o $(CFLAGS) -c glviewer.c
	$(CC) -o glviewer $(LDFLAGS) -lGL -lGLU glviewer.o allocate.o

# wware 060101  sim.c dependency no longer needed, simhelp.c dependency in setup.py
extensions: Makefile
	$(WARNWIN32)
	$(HALTWIN32)
	python setup.py build_ext --inplace

pyx: extensions

install: simulator
	if [ ! -d $(EXE_DIRECTORY) ] ; then \
		mkdir $(EXE_DIRECTORY) ;\
	fi
	cp simulator ~/bin/simulator
	cp simulator $(EXE_DIRECTORY) 

install-linux: install extensions
	cp sim.so $(EXE_DIRECTORY)

## should make clean also remove tables.c, bonds.h, bends.h?? [bruce 051230 question]
clean:
	rm -f simulator moldisp molsim physeng sim.so sim.c traceprefix.c _traceprefix.c
	rm -f *.o *.so *~ fmc.mmp dumpstruct.xyz *.pyc
	rm -rf html gmon.out build
	rm -f tests/*/*.altout
	rm -f tests/*/*.diff
	rm -f tests/*/*.xyz
	rm -f tests/*/*.dpb

dist_clean: clean
	rm -f TAGS bonds.h bends.h

TAGS:
	etags *.c *.h


doxy:
	doxygen Doxyfile

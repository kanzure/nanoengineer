# Makefile for the simulator
# $Id$

ifeq ($(OS),Windows_NT)
CC = "C:/Dev-Cpp/bin/gcc.exe"
CFLAGS=-I"C:/Dev-Cpp/include"
LDFLAGS=-L"C:/Dev-Cpp/lib"
STDC99=
else
# non-Windows
CC=gcc
CFLAGS=-g -Wmissing-prototypes -Wall
# Note: these CFLAGS are probably not used to build the files for Pyrex, 
# only for the standalone simulator executable. [bruce 051230 guess]
LDFLAGS=-L/usr/lib -lm
STDC99=-std=c99
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

all: simulator

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
newtables.o: simulator.h bonds.h
part.o: simulator.h
potential.o: simulator.h
printers.o: simulator.h
readmmp.o: simulator.h
readxyz.o: simulator.h
simulator.o: simulator.h
writemovie.o: simulator.h

# -std-c99 gets us isnormal()
structcompare.o: structcompare.c simulator.h
	$(CC) -c $(STDC99) $(CFLAGS) -o structcompare.o structcompare.c

# Is this rule obsolete too? [bruce 060101 question] 
# Partial answer: It is not used by make or make pyx.
# It is used if you type "make sim". I think that can't work correctly, 
# so I'll leave this rule in, with an error, to detect that mistake. [bruce 060101]
sim.o: sim.c simulator.h Makefile
	echo "using toplevel make rule for sim.o"
	cause an error on purpose if this is used
	gcc -c -g -fPIC -I/usr/include/python2.3 sim.c

# is this sim.c rule obsolete? Will it interfere with anything? [bruce 051230 question]
# Partial answers:
# - It is probably not used when you do "make pyx", since its echo does not happen then.
# - If you run it separately (e.g. by "make sim.c"), the sim.c it produces is identical
#   (except for date in comment) to what "make pyx" would silently produce itself;
#   and the sim.c this rule produces *is* used (not overwritten) by a subsequent
#   "make pyx" (proved by intervening manual edit to introduce syntax error).
# - This means it does not in itself create the needed dependency on simhelp.c,
#   but if "make extensions" is also given a dependency on sim.c, then it uses this rule
#   and does have the desired dependency on simhelp.c, so I've added that and left this 
#   rule in place. This only works if we also touch sim.pyx here so the setup.py knows it
#   has to do something. [Does it then overwrite sim.c? Not retested. ###] [bruce 060101]
sim.c: sim.pyx simhelp.c Makefile
	echo "using toplevel make rule for sim.c, which touches sim.pyx"
	touch sim.pyx
	pyrexc sim.pyx

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
	writemovie.o \
	simulator.o

noopt:
	make CFLAGS=-g simulator

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

# bruce 060101 added sim.c to help cause dependency of pyrex rebuild on simhelp.c
# (just adding simhelp.c here is not enough, since in that case distutils (setup.py)
#  doesn't realize it needs to do any work)
extensions: sim.c Makefile
	python setup.py build_ext --inplace

pyx: extensions

install: simulator
	if [ ! -d $(EXE_DIRECTORY) ] ; then \
		mkdir $(EXE_DIRECTORY) ;\
	fi
	cp simulator ~/bin/simulator
	cp simulator $(EXE_DIRECTORY) 

## should make clean also remove tables.c, bonds.h, bends.h?? [bruce 051230 question]
clean:
	rm -f simulator moldisp molsim physeng sim.so sim.c
	rm -f *.o *.so *~ fmc.mmp dumpstruct.xyz
	rm -rf html gmon.out build
	rm -f tests/minimize/*.altout
	rm -f tests/minimize/*.diff
	rm -f tests/dynamics/*.diff

dist_clean: clean
	rm -f TAGS

TAGS:
	etags *.c *.h


doxy:
	doxygen Doxyfile

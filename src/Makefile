# Makefile for the simulator

CC=gcc

#CFLAGS=-O2 -g
CFLAGS=-g

#LDFLAGS=-L/usr/X11R6/lib -lm -lX11 -lXi -lXmu
LDFLAGS=-L/usr/lib -lm

EXE_DIRECTORY=../../cad/bin
#EXE_DIRECTORY=~/bin

ifeq ($(PROFILING),1)
CFLAGS+=-pg
LDFLAGS+=-pg
endif

all: simulator

SUFFIXES: .c .h .o ;

.c.o:
	$(CC) -c $(CFLAGS) -o $@ $(@:.o=.c)


simulator.o: simulator.h
lin-alg.o: lin-alg.h
readers.o: simulator.h
printers.o: simulator.h
hashtable.o: allocate.h hashtable.h
allocate.o: allocate.h
newtables.o: simulator.h bonds.h
structcompare.o: simulator.h
interpolate.o: simulator.h
minimize.o: allocate.h minimize.h
readmmp.o: simulator.h

tables.c: gentab.py
	python gentab.py > tables.c

bonds.h: parmlist.py stretch.parms
	python parmlist.py stretch.parms > bonds.h

bends.h: bend.perl bending.parms
	./bend.perl < bending.parms > bends.h

SIMOBJS=\
	simulator.o \
	lin-alg.o \
	readers.o \
	printers.o \
	allocate.o \
	hashtable.o \
	minimize.o \
	newtables.o \
	structcompare.o \
	readmmp.o \
	interpolate.o

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


install: simulator
	if [ ! -d $(EXE_DIRECTORY) ] ; then \
		mkdir $(EXE_DIRECTORY) ;\
	fi
	cp simulator ~/bin
	mv simulator $(EXE_DIRECTORY) 

clean:
	rm -f simulator moldisp molsim physeng
	rm -f *.o *.so *~ fmc.mmp dumpstruct.xyz
	rm -rf html gmon.out

dist_clean: clean
	rm -f TAGS

TAGS:
	etags *.c *.h


doxy:
	doxygen Doxyfile

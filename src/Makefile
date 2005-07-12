# Makefile for the simulator

CC=gcc

CFLAGS=-O2 -g

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
newtables.o: simulator.h
structcompare.o: simulator.h
interpolate.o: simulator.h

tables.c: gentab.py
	python gentab.py > tables.c

SIMOBJS=\
	simulator.o \
	lin-alg.o \
	readers.o \
	printers.o \
	allocate.o \
	hashtable.o \
	newtables.o \
	structcompare.o \
	interpolate.o

all: simulator

noopt:
	make CFLAGS=-g all

simulator: $(SIMOBJS)
	$(CC) -o simulator $(LDFLAGS) $(SIMOBJS)

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

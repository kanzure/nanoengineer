# Makefile for the simulator

CC=gcc
CFLAGS=-O3 -g
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
tables.o: simulator.h
lin-alg.o: simulator.h lin-alg.c
readers.o: simulator.h
printers.o: simulator.h

tables.c: gentab.py
	python gentab.py > tables.c

SIMOBJS=simulator.o tables.o lin-alg.o readers.o printers.o
all: simulator 

simulator: $(SIMOBJS)
	$(CC) -o simulator $(LDFLAGS) $(SIMOBJS)
	if [ ! -d $(EXE_DIRECTORY) ] ; then \
		mkdir $(EXE_DIRECTORY) ;\
	fi
	cp simulator ~/bin
	mv simulator $(EXE_DIRECTORY) 

clean:
	rm -f simulator moldisp molsim physeng
	rm -f *.o *.so *~ TAGS fmc.mmp dumpstruct.xyz
	rm -rf html gmon.out

TAGS:
	etags *.c *.h


doxy:
	doxygen Doxyfile

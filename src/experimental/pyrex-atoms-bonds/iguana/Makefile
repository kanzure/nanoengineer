CC=gcc
#CFLAGS=-g -Wall -I/usr/include/python2.4
CFLAGS=-O3 -Wall -I/usr/include/python2.4

all: ighelp.so

clean:
	rm -f *.o *.so core* *~ ighelp2.* *.pyc

ighelp.so: ighelp.o ighelp2.o
	gcc -shared -o ighelp.so ighelp.o ighelp2.o

ighelp2.c: ops.b procops.py
	python procops.py > ighelp2.c

ighelp2.o: ighelp2.c ighelp.h
ighelp.o: ighelp.c ighelp.h

shar:
	shar ighelp.c ighelp.h iguana.py Makefile \
		ops.b procops.py > ../ig.shar

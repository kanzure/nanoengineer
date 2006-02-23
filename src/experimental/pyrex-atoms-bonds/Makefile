CC=gcc
#CFLAGS=-I/usr/include/python2.4 -Wall -g -O0
#CFLAGS=-I/usr/include/python2.4 -Wall -g -O3
CFLAGS=-I/usr/include/python2.4 -Wall -g
LDFLAGS=-L/usr/lib/python2.4/config -lm -lpython2.4

all: bases.so

clean:
	rm -f *~ *.o *.so *.pyc bases.c

bases.c: bases.pyx basehelp.c Makefile
	pyrexc bases.pyx

bases.o: bases.c

bases.so: bases.o
	$(CC) -shared -o bases.so bases.o $(LDFLAGS)

basehelp.o: basehelp.c
	$(CC) -c -o basehelp.o -D__TEST__ basehelp.c $(CFLAGS) -pg

proto.so: proto.o
	$(CC) -shared -o proto.so proto.o $(LDFLAGS)

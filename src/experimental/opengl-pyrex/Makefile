CC=gcc
CFLAGS=-Wall -g -I/usr/X11R6/include -I/usr/include/python2.3
LDFLAGS=-L/usr/X11R6/lib -L/usr/lib/python2.3/config -lGL -lGLU -lpython2.3

all: putz.so

clean:
	rm -f *~ *.o putz.c putz.so

putz.c: putz.pyx
	pyrexc putz.pyx

putz.so: putz.o
	$(CC) -shared $(LDFLAGS) -o putz.so putz.o

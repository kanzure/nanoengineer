CC=gcc
CFLAGS=-I/usr/include/python2.4 -Wall -g
#CFLAGS=-I/usr/include/python2.4 -O3
LDFLAGS=-L/usr/lib/python2.4/config -lm -lpython2.4

all: bases.so

clean:
	rm -f *~ *.o *.so bases.c

bases.c: bases.pyx basehelp.c
	pyrexc bases.pyx

bases.o: bases.c

bases.so: bases.o
	$(CC) -shared -o bases.so bases.o $(LDFLAGS)

test: bases.so
	python -c "import bases; bases.test()"

#gdb: bases.so
#	echo 'run -c "import bases; bases.test()"' | gdb python

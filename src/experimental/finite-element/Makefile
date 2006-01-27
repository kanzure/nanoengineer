UNAME := $(shell uname)

ifeq ($(OS),Windows_NT)
# Start Windows stuff
CC="C:/Dev-Cpp/bin/gcc.exe"
CFLAGS=-g -Wmissing-prototypes
CFLAGS+=-I"C:/Dev-Cpp/include" -I"C:/Python23/include"
LDFLAGS=-Wl,--output-def,comp.def -L. -L"C:/Dev-Cpp/lib" -lpython23
PYREXC=python c:/Python23/Scripts/pyrexc.py
TARGET=comp.dll
# End of Windows stuff
else
# Start Unix/Mac stuff
ifeq ($(strip $(UNAME)),Darwin)
# Mac
PYREXC=/Library/Python/2.3/Pyrex-0.9.3.1/bin/pyrexc
CFLAGS=-DMACOSX -I/usr/include/python2.3
LDFLAGS=-L/usr/lib/python2.3/config -lm -lpython2.3
else
# Unix
PYREXC=pyrexc
#CFLAGS=-g -Wall -I/usr/include/python2.3
CFLAGS=-O3 -Wall -I/usr/include/python2.3
LDFLAGS=-L/usr/lib/python2.3/config -lm -lpython2.3
endif
CC=gcc
TARGET=comp.so
# End of Unix/Mac stuff
endif

all: jelloGui.py comp.so

jelloGui.py: jelloGui.ui
	pyuic jelloGui.ui > jelloGui.py

comp.c: comp.pyx comphelp.c
	$(PYREXC) comp.pyx

comp.so: comp.o
	$(CC) -shared -o comp.so comp.o $(LDFLAGS)

clean:
	rm -f *.pyc *~ *.o jelloGui.py *.so comp.c

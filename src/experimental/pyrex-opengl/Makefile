ifeq ($(OS),Windows_NT)
CC="C:/Dev-Cpp/bin/gcc.exe"
CFLAGS=-g -Wmissing-prototypes
CFLAGS+=-I"C:/Dev-Cpp/include" -I"C:/Python23/include"
LDFLAGS=-Wl,--output-def,tryit.def -L. -L"C:/Dev-Cpp/lib" \
	-lpython23 -lopengl32
PYREXC=python c:/Python23/Scripts/pyrexc.py
TARGET=quux.dll
LIBPYTHONDEP=libpython23.a
else
# Unix, and maybe the Mac
# It turns out I need /usr/X11R6/(include,lib) to get the stuff for
# OpenGL. This is NOT a dependency on X11 proper.
CC=gcc
CFLAGS=-g -Wmissing-prototypes
CFLAGS+=-I/usr/X11R6/include -I/usr/include/python2.3
LDFLAGS=-L/usr/X11R6/lib -L/usr/lib/python2.3/config -lm -lGL -lpython2.3
PYREXC=pyrexc
TARGET=quux.so
LIBPYTHONDEP=
endif

all: $(TARGET)

clean:
	rm -rf *~ *.o quux.c $(TARGET) build

quux.c: quux.pyx quux_help.c
	$(PYREXC) quux.pyx

quux.o: quux.c

distutils:
	python setup.py build_ext --inplace

$(TARGET): quux.o $(LIBPYTHONDEP)
	$(CC) -shared -o $(TARGET) quux.o $(LDFLAGS)

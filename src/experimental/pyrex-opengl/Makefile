UNAME := $(shell uname)

ifeq ($(OS),Windows_NT)
# Start Windows stuff
CC="C:/Dev-Cpp/bin/gcc.exe"
CFLAGS=-g -Wmissing-prototypes
CFLAGS+=-I"C:/Dev-Cpp/include" -I"C:/Python23/include"
LDFLAGS=-Wl,--output-def,tryit.def -L. -L"C:/Dev-Cpp/lib" \
	-lpython23 -lopengl32
PYREXC=python c:/Python23/Scripts/pyrexc.py
TARGET=quux.dll
# End of Windows stuff
else
# Start Unix/Mac stuff
ifeq ($(strip $(UNAME)),Darwin)
# Mac
PYREXC=/Library/Python/2.3/Pyrex-0.9.3.1/bin/pyrexc
else
# Unix
PYREXC=pyrexc
endif
CC=gcc
# It turns out I need /usr/X11R6/(include,lib) to get the stuff for
# OpenGL. This is NOT a dependency on X11 proper.
CFLAGS=-I/usr/X11R6/include -I/usr/include/python2.3
LDFLAGS=-L/usr/X11R6/lib -L/usr/lib/python2.3/config -lm -lGL -lpython2.3
PYREXC=pyrexc
TARGET=quux.so
# End of Unix/Mac stuff
endif

all: $(TARGET)

clean:
	rm -rf *~ *.o quux.c $(TARGET) build

quux.c: quux.pyx quux_help.c
	$(PYREXC) quux.pyx

quux.o: quux.c

# Unix, Mac can use distutils
quux.so: quux.pyx quux_help.c
	python setup.py build_ext --inplace

# Windows can't use distutils (avoid MSVC, use Dev-Cpp)
quux.dll: quux.o libpython23.a
	$(CC) -shared -o quux.dll quux.o $(LDFLAGS)

rebuild:
	gcc -pthread -fno-strict-aliasing -DNDEBUG -O2 -fomit-frame-pointer -pipe -march=i586 -mtune=pentiumpro -g -fPIC -I/usr/include/python2.3 -c quux.c -o build/temp.linux-i686-2.3/quux.o
	gcc -pthread -shared build/temp.linux-i686-2.3/quux.o -o quux.so -L/usr/X11R6/lib -lGL

test: $(TARGET)
	python -c "import quux; quux.test()"

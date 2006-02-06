UNAME := $(shell uname)
# dotted python version (2.3, 2.4)
PYDVER := $(shell python -c "import sys; print sys.version[:3]")
# un-dotted python version (23, 24)
PYVER := $(shell python -c "import sys; print sys.version[0]+sys.version[2]")

ifeq (XX$(OS),XXWindows_NT)
#---------------------------------------- Start Windows stuff
CC="C:/Dev-Cpp/bin/gcc.exe"
CXX="C:/Dev-Cpp/bin/g++.exe"
CFLAGS=-g -Wmissing-prototypes
CFLAGS+=-I"C:/Dev-Cpp/include" -I"C:/Python$(PYVER)/include"
CXXFLAGS+=-I"C:/Dev-Cpp/include" -I"C:/Python$(PYVER)/include"
LDFLAGS=-Wl,--output-def,quux.def -L. -L"C:/Dev-Cpp/lib" \
	-lpython$(PYVER) -lopengl32
PYTHON=c:/Python$(PYVER)/python
PYREXC=c:/Python$(PYVER)/python c:/Python$(PYVER)/Scripts/pyrexc.py
TARGET=quux.dll
#---------------------------------------- End of Windows stuff
else
#---------------------------------------- Start Unix/Mac stuff
ifeq ($(strip $(UNAME)),Darwin)
#---------------------------------------- Mac
PYREXC=/Library/Python/$(PYDVER)/Pyrex-0.9.3.1/bin/pyrexc
CFLAGS=-DMACOSX -I/System/Library/Frameworks/AGL.Framework/Headers \
	-I/usr/include/python$(PYDVER)
LDFLAGS=-L/usr/X11R6/lib -L/usr/lib/python$(PYDVER)/config -lm -lGL \
	-lpython$(PYDVER)
else
#---------------------------------------- Unix
PYREXC=pyrexc
# It turns out I need /usr/X11R6/(include,lib) to get the stuff for
# OpenGL. This is NOT a dependency on X11 proper.
CFLAGS=-g -Wall -I/usr/X11R6/include -I/usr/include/python$(PYDVER)
CPPFLAGS=-g -Wall -I/usr/X11R6/include -I/usr/include/python$(PYDVER)
LDFLAGS=-L/usr/X11R6/lib -L/usr/lib/python$(PYDVER)/config -lm -lGL \
	-lpython$(PYDVER)
endif
PYTHON=python
CC=gcc
TARGET=quux.so
#---------------------------------------- End of Unix/Mac stuff
endif

# Should libpython23.a be replaced everywhere by libpython$(PYVER)??
# I think it should but it's an easy thing to do later.

all: $(TARGET)

clean:
	rm -rf *~ *.o quux.c $(TARGET) build *.def *.pyc libpython23.a

quux.c: quux.pyx quux_help.c
	$(PYREXC) quux.pyx

quux.o: quux.c bradg.h
bradg.o: bradg.cpp bradg.h glextensions.h vector.h
glextensions.o: glextensions.cpp glextensions.h
vector.o: vector.c vector.h

# Unix, Mac can use distutils
quux.so: quux.pyx quux_help.c
	$(PYTHON) setup.py build_ext --inplace

# Unix, Mac - don't use distutils
__quux.so: quux.o bradg.o glextensions.o vector.o
	$(CC) -shared -o quux.so quux.o bradg.o glextensions.o vector.o $(LDFLAGS)

PyrexOpenGLGui.py: PyrexOpenGLGui.ui
	pyuic PyrexOpenGLGui.ui > PyrexOpenGLGui.py

libpython23.a: libpython23.a.gz
	gunzip < libpython23.a.gz > libpython23.a

# Windows can't use distutils (avoid MSVC, use Dev-Cpp)
quux.dll: quux.o bradg.o glextensions.o vector.o libpython23.a
	$(CC) -shared -o quux.dll quux.o bradg.o glextensions.o vector.o $(LDFLAGS)

test: $(TARGET)
	$(PYTHON) -c "import quux; quux.test()"

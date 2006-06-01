UNAME := $(shell uname)

ifeq (XX$(OS),XXWindows_NT)
#---------------------------------------- Start Windows stuff
CC="C:/Dev-Cpp/bin/gcc.exe"
CXX="C:/Dev-Cpp/bin/g++.exe"
CFLAGS=-g -Wall -I"C:/Dev-Cpp/include"
CXXFLAGS=-g -Wall -I"C:/Dev-Cpp/include"
LDFLAGS=-Wl,--output-def,quux.def -L. -L"C:/Dev-Cpp/lib"
TARGETSW=SW.exe
TARGETMW=MW.exe
TARGETHJ=HJ.exe
#---------------------------------------- End of Windows stuff
else
#---------------------------------------- Start Unix/Mac stuff
ifeq ($(strip $(UNAME)),Darwin)
#---------------------------------------- Mac
CFLAGS=-DMACOSX
CXXFLAGS=-DMACOSX
LDFLAGS=-lm
else
#---------------------------------------- Unix
PYREXC=pyrexc
CFLAGS=-O3
CXXFLAGS=-O3
LDFLAGS=-lm
endif
DESTDIR=$(shell python -c "import os; print os.path.expanduser('~/Nanorex/CoNTub')")
CC=gcc
CXX=g++
CFLAGS+=-g -Wall -Wmissing-prototypes
CXXFLAGS+=-g -Wall
TARGETSW=SW
TARGETMW=MW
TARGETHJ=HJ
#---------------------------------------- End of Unix/Mac stuff
endif

SRCS=anillo.cpp \
	AtomList.cpp \
	Atomo.cpp \
	Minimol.cpp \
	MoleculaB.cpp \
	MoleculaT.cpp \
	Nanotubo.cpp \
	pto2D.cpp \
	pto3D.cpp \
	TabPe.cpp

W1SRCS=$(SRCS) W1.cpp
W15SRCS=$(SRCS) W15.cpp
W2SRCS=$(SRCS) W2.cpp

OBJS=$(SRCS:.cpp=.o)

.SUFFIXES: .h .cpp .o ;

.cpp.o:
	$(CXX) $(CXXFLAGS) -c $(@:.o=.cpp)

all: $(TARGETSW) $(TARGETMW) $(TARGETHJ)

install: $(TARGETSW) $(TARGETMW) $(TARGETHJ)
	mkdir -p $(DESTDIR)
	cp $(TARGETSW) $(DESTDIR)
	cp $(TARGETMW) $(DESTDIR)
	cp $(TARGETHJ) $(DESTDIR)

$(TARGETSW): $(W1SRCS:.cpp=.o)
	$(CXX) $(CXXFLAGS) -o $(TARGETSW) $(W1SRCS:.cpp=.o)

$(TARGETMW): $(W15SRCS:.cpp=.o)
	$(CXX) $(CXXFLAGS) -o $(TARGETMW) $(W15SRCS:.cpp=.o)

$(TARGETHJ): $(W2SRCS:.cpp=.o)
	$(CXX) $(CXXFLAGS) -o $(TARGETHJ) $(W2SRCS:.cpp=.o)

clean:
	rm -f *.o *~ core.* $(TARGETSW) $(TARGETMW) $(TARGETHJ)

deps:
	makedepend $(SRCS) W1.cpp W15.cpp W2.cpp -f - | \
		sed 's# /[^ ]*\.h##g' | egrep -v ':$$' >> Makefile

# DO NOT DELETE

anillo.o: anillo.h
anillo.o: pto3D.h
anillo.o: String.h MoleculaT.h MoleculaB.h TabPe.h
anillo.o: AtomList.h Atomo.h
AtomList.o: AtomList.h
AtomList.o: Atomo.h pto3D.h String.h
AtomList.o: TabPe.h
Minimol.o: Minimol.h pto3D.h String.h
Minimol.o: MoleculaB.h TabPe.h AtomList.h Atomo.h
MoleculaB.o: MoleculaB.h String.h
MoleculaB.o: TabPe.h AtomList.h Atomo.h pto3D.h
MoleculaT.o: MoleculaT.h MoleculaB.h String.h
MoleculaT.o: TabPe.h AtomList.h Atomo.h pto3D.h Minimol.h anillo.h
Nanotubo.o: Nanotubo.h
pto2D.o: pto2D.h
pto2D.o: pto3D.h String.h
pto3D.o: pto3D.h
pto3D.o: String.h
pto3D.o: pto2D.h
TabPe.o: TabPe.h String.h
W1.o: W1.h
W1.o: MoleculaT.h MoleculaB.h String.h TabPe.h
W1.o: AtomList.h Atomo.h pto3D.h Nanotubo.h
W15.o: W15.h W1.h
W15.o: MoleculaT.h MoleculaB.h String.h TabPe.h
W15.o: AtomList.h Atomo.h pto3D.h Nanotubo.h

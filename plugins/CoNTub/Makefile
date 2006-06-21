# $Id$

ifeq (x$(OS),xWindows_NT)
#---------------------------------------- Start Windows stuff
CC="C:/Dev-Cpp/bin/gcc.exe"
CXX="C:/Dev-Cpp/bin/g++.exe"
CFLAGS=-g -Wall -I"C:/Dev-Cpp/include"
CXXFLAGS=-g -Wall -I"C:/Dev-Cpp/include"
LDFLAGS=-Wl,--output-def,quux.def -L. -L"C:/Dev-Cpp/lib"
SRCDIR=src
BINDIR=bin
TARGETSW=$(BINDIR)/SW.exe
TARGETMW=$(BINDIR)/MW.exe
TARGETHJ=$(BINDIR)/HJ.exe
#---------------------------------------- End of Windows stuff
else
#---------------------------------------- Start Unix/Mac stuff
UNAME := $(shell uname)
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
CC=gcc
CXX=g++
CFLAGS+=-g -Wall -Wmissing-prototypes
CXXFLAGS+=-g -Wall
SRCDIR=src
BINDIR=bin
TARGETSW=$(BINDIR)/SW
TARGETMW=$(BINDIR)/MW
TARGETHJ=$(BINDIR)/HJ
#---------------------------------------- End of Unix/Mac stuff
endif

SRCS=$(SRCDIR)/anillo.cpp \
	$(SRCDIR)/AtomList.cpp \
	$(SRCDIR)/Atomo.cpp \
	$(SRCDIR)/Minimol.cpp \
	$(SRCDIR)/MoleculaB.cpp \
	$(SRCDIR)/MoleculaT.cpp \
	$(SRCDIR)/Nanotubo.cpp \
	$(SRCDIR)/pto2D.cpp \
	$(SRCDIR)/pto3D.cpp \
	$(SRCDIR)/TabPe.cpp

W1SRCS=$(SRCS) $(SRCDIR)/W1.cpp
W15SRCS=$(SRCS) $(SRCDIR)/W15.cpp
W2SRCS=$(SRCS) $(SRCDIR)/W2.cpp

OBJS=$(SRCS:.cpp=.o)

################

.SUFFIXES: .h .cpp .o ;

.c.o:
	$(CC) $(CFLAGS) -c $(@:.o=.c) -o $@

.cpp.o:
	$(CXX) $(CXXFLAGS) -c $(@:.o=.cpp) -o $@

################

all: $(TARGETSW) $(TARGETMW) $(TARGETHJ)

$(TARGETSW): $(W1SRCS:.cpp=.o)
	$(CXX) $(CXXFLAGS) -o $(TARGETSW) $(W1SRCS:.cpp=.o)

$(TARGETMW): $(W15SRCS:.cpp=.o)
	$(CXX) $(CXXFLAGS) -o $(TARGETMW) $(W15SRCS:.cpp=.o)

$(TARGETHJ): $(W2SRCS:.cpp=.o)
	$(CXX) $(CXXFLAGS) -o $(TARGETHJ) $(W2SRCS:.cpp=.o)

clean:
	rm -f $(SRCDIR)/*.o $(SRCDIR)/*~ $(SRCDIR)/core.* $(BINDIR)/core.* \
		$(TARGETSW) $(TARGETMW) $(TARGETHJ) \
		singlewall.mmp multiwall.mmp heterojunction.mmp

deps:
	makedepend $(SRCS) $(SRCDIR)/W1.cpp $(SRCDIR)/W15.cpp $(SRCDIR)/W2.cpp -f - | \
		sed 's# /[^ ]*\.h##g' | egrep -v ':$$' | \
		sed 's#src/#$$(SRCDIR)/#g' >> Makefile

test: $(TARGETSW) $(TARGETMW) $(TARGETHJ)
	$(TARGETSW) 5 5 12.0 1 1 singlewall.mmp
	$(TARGETMW) 5 5 12.0 3 3.5 1 2 multiwall.mmp
	$(TARGETHJ) 5 5 20.0 20 0 20.0 1 3 heterojunction.mmp

# DO NOT DELETE

$(SRCDIR)/anillo.o: $(SRCDIR)/anillo.h
$(SRCDIR)/anillo.o: $(SRCDIR)/pto3D.h $(SRCDIR)/String.h $(SRCDIR)/MoleculaT.h
$(SRCDIR)/anillo.o: $(SRCDIR)/MoleculaB.h $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h
$(SRCDIR)/AtomList.o: $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h $(SRCDIR)/pto3D.h $(SRCDIR)/String.h
$(SRCDIR)/AtomList.o: $(SRCDIR)/TabPe.h
$(SRCDIR)/Minimol.o: $(SRCDIR)/Minimol.h $(SRCDIR)/pto3D.h
$(SRCDIR)/Minimol.o: $(SRCDIR)/String.h
$(SRCDIR)/Minimol.o: $(SRCDIR)/MoleculaB.h $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h
$(SRCDIR)/MoleculaB.o: $(SRCDIR)/MoleculaB.h $(SRCDIR)/String.h
$(SRCDIR)/MoleculaB.o: $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h $(SRCDIR)/pto3D.h
$(SRCDIR)/MoleculaT.o: $(SRCDIR)/MoleculaT.h
$(SRCDIR)/MoleculaT.o: $(SRCDIR)/MoleculaB.h $(SRCDIR)/String.h
$(SRCDIR)/MoleculaT.o: $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h $(SRCDIR)/pto3D.h
$(SRCDIR)/MoleculaT.o: $(SRCDIR)/Minimol.h $(SRCDIR)/anillo.h
$(SRCDIR)/Nanotubo.o: $(SRCDIR)/Nanotubo.h
$(SRCDIR)/pto2D.o: $(SRCDIR)/pto2D.h $(SRCDIR)/pto3D.h
$(SRCDIR)/pto2D.o: $(SRCDIR)/String.h
$(SRCDIR)/pto3D.o: $(SRCDIR)/pto3D.h $(SRCDIR)/String.h
$(SRCDIR)/pto3D.o: $(SRCDIR)/pto2D.h
$(SRCDIR)/TabPe.o: $(SRCDIR)/TabPe.h $(SRCDIR)/String.h
$(SRCDIR)/W1.o: $(SRCDIR)/W1.h $(SRCDIR)/MoleculaT.h $(SRCDIR)/MoleculaB.h $(SRCDIR)/String.h
$(SRCDIR)/W1.o: $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h
$(SRCDIR)/W1.o: $(SRCDIR)/pto3D.h $(SRCDIR)/Nanotubo.h
$(SRCDIR)/W15.o: $(SRCDIR)/W15.h $(SRCDIR)/W1.h $(SRCDIR)/MoleculaT.h $(SRCDIR)/MoleculaB.h $(SRCDIR)/String.h
$(SRCDIR)/W15.o: $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h
$(SRCDIR)/W15.o: $(SRCDIR)/pto3D.h $(SRCDIR)/Nanotubo.h
$(SRCDIR)/W2.o: $(SRCDIR)/W2.h $(SRCDIR)/pto3D.h $(SRCDIR)/String.h
$(SRCDIR)/W2.o: $(SRCDIR)/W1.h $(SRCDIR)/MoleculaT.h $(SRCDIR)/MoleculaB.h $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h
$(SRCDIR)/W2.o: $(SRCDIR)/Atomo.h $(SRCDIR)/pto2D.h $(SRCDIR)/Nanotubo.h

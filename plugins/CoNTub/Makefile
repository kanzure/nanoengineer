# $Id$

ifeq (x$(OS),xWindows_NT)
#---------------------------------------- Start Windows stuff
CC="C:/Dev-Cpp/bin/gcc.exe"
CXX="C:/Dev-Cpp/bin/g++.exe"
CFLAGS=-g -Wall -I"C:/Dev-Cpp/include"
CXXFLAGS=-g -Wall -I"C:/Dev-Cpp/include"
LDFLAGS=-Wl,--output-def,quux.def -L. -L"C:/Dev-Cpp/lib"
SRCDIR=src
OBJDIR=obj
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
OBJDIR=obj
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

OBJS=$(subst $(SRCDIR)/,$(OBJDIR)/,$(SRCS:.cpp=.o))

################

.SUFFIXES: .h .cpp .o ;

.c.o:
	$(CC) $(CFLAGS) -c -o $@ $^

.cpp.o:
	$(CXX) $(CXXFLAGS) -c -o $@ $^

################

# all: $(TARGETSW) $(TARGETMW) $(TARGETHJ)

# We are only using the HJ executable now.
all: $(TARGETHJ)

$(TARGETSW): $(OBJS) $(OBJDIR)/W1.o
	$(CXX) $(CXXFLAGS) -o $@ $^

$(TARGETMW): $(OBJS) $(OBJDIR)/W15.o
	$(CXX) $(CXXFLAGS) -o $@ $^

$(TARGETHJ): $(OBJS) $(OBJDIR)/W2.o
	$(CXX) $(CXXFLAGS) -o $@ $^

clean:
	rm -f $(OBJDIR)/*.o $(SRCDIR)/*~ $(SRCDIR)/core.* $(BINDIR)/core.* \
		$(TARGETSW) $(TARGETMW) $(TARGETHJ) \
		singlewall.mmp multiwall.mmp heterojunction.mmp

# Usage: make deps >> Makefile
deps:
	makedepend $(SRCS) $(SRCDIR)/W1.cpp $(SRCDIR)/W15.cpp $(SRCDIR)/W2.cpp -f - | \
		python procdeps.py $(SRCDIR) $(OBJDIR) .o:.cpp \
			$(OBJS) $(OBJDIR)/W1.o $(OBJDIR)/W15.o $(OBJDIR)/W2.o

test: $(TARGETSW) $(TARGETMW) $(TARGETHJ)
	$(TARGETSW) 5 5 12.0 1 1 singlewall.mmp
	$(TARGETMW) 5 5 12.0 3 3.5 1 2 multiwall.mmp
	$(TARGETHJ) 5 5 20.0 20 0 20.0 1 3 heterojunction.mmp

# Automatically generated dependencies from procdeps.py
$(OBJDIR)/anillo.o: $(SRCDIR)/anillo.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/anillo.o $(SRCDIR)/anillo.cpp
$(OBJDIR)/AtomList.o: $(SRCDIR)/AtomList.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/AtomList.o $(SRCDIR)/AtomList.cpp
$(OBJDIR)/Atomo.o: $(SRCDIR)/Atomo.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/Atomo.o $(SRCDIR)/Atomo.cpp
$(OBJDIR)/Minimol.o: $(SRCDIR)/Minimol.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/Minimol.o $(SRCDIR)/Minimol.cpp
$(OBJDIR)/MoleculaB.o: $(SRCDIR)/MoleculaB.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/MoleculaB.o $(SRCDIR)/MoleculaB.cpp
$(OBJDIR)/MoleculaT.o: $(SRCDIR)/MoleculaT.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/MoleculaT.o $(SRCDIR)/MoleculaT.cpp
$(OBJDIR)/Nanotubo.o: $(SRCDIR)/Nanotubo.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/Nanotubo.o $(SRCDIR)/Nanotubo.cpp
$(OBJDIR)/pto2D.o: $(SRCDIR)/pto2D.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/pto2D.o $(SRCDIR)/pto2D.cpp
$(OBJDIR)/pto3D.o: $(SRCDIR)/pto3D.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/pto3D.o $(SRCDIR)/pto3D.cpp
$(OBJDIR)/TabPe.o: $(SRCDIR)/TabPe.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/TabPe.o $(SRCDIR)/TabPe.cpp
$(OBJDIR)/W1.o: $(SRCDIR)/W1.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/W1.o $(SRCDIR)/W1.cpp
$(OBJDIR)/W15.o: $(SRCDIR)/W15.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/W15.o $(SRCDIR)/W15.cpp
$(OBJDIR)/W2.o: $(SRCDIR)/W2.cpp
	$(CXX) $(CXXFLAGS) -c -o $(OBJDIR)/W2.o $(SRCDIR)/W2.cpp
$(OBJDIR)/anillo.o: $(SRCDIR)/anillo.h
$(OBJDIR)/anillo.o: $(SRCDIR)/pto3D.h $(SRCDIR)/String.h $(SRCDIR)/MoleculaT.h
$(OBJDIR)/anillo.o: $(SRCDIR)/MoleculaB.h $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h
$(OBJDIR)/AtomList.o: $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h $(SRCDIR)/pto3D.h $(SRCDIR)/String.h
$(OBJDIR)/AtomList.o: $(SRCDIR)/TabPe.h
$(OBJDIR)/Minimol.o: $(SRCDIR)/Minimol.h $(SRCDIR)/pto3D.h
$(OBJDIR)/Minimol.o: $(SRCDIR)/String.h
$(OBJDIR)/Minimol.o: $(SRCDIR)/MoleculaB.h $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h
$(OBJDIR)/MoleculaB.o: $(SRCDIR)/MoleculaB.h $(SRCDIR)/String.h
$(OBJDIR)/MoleculaB.o: $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h $(SRCDIR)/pto3D.h
$(OBJDIR)/MoleculaT.o: $(SRCDIR)/MoleculaT.h
$(OBJDIR)/MoleculaT.o: $(SRCDIR)/MoleculaB.h $(SRCDIR)/String.h
$(OBJDIR)/MoleculaT.o: $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h $(SRCDIR)/pto3D.h
$(OBJDIR)/MoleculaT.o: $(SRCDIR)/Minimol.h $(SRCDIR)/anillo.h
$(OBJDIR)/Nanotubo.o: $(SRCDIR)/Nanotubo.h
$(OBJDIR)/pto2D.o: $(SRCDIR)/pto2D.h $(SRCDIR)/pto3D.h
$(OBJDIR)/pto2D.o: $(SRCDIR)/String.h
$(OBJDIR)/pto3D.o: $(SRCDIR)/pto3D.h $(SRCDIR)/String.h
$(OBJDIR)/pto3D.o: $(SRCDIR)/pto2D.h
$(OBJDIR)/TabPe.o: $(SRCDIR)/TabPe.h $(SRCDIR)/String.h
$(OBJDIR)/W1.o: $(SRCDIR)/W1.h $(SRCDIR)/MoleculaT.h $(SRCDIR)/MoleculaB.h $(SRCDIR)/String.h
$(OBJDIR)/W1.o: $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h
$(OBJDIR)/W1.o: $(SRCDIR)/pto3D.h $(SRCDIR)/Nanotubo.h
$(OBJDIR)/W15.o: $(SRCDIR)/W15.h $(SRCDIR)/W1.h $(SRCDIR)/MoleculaT.h $(SRCDIR)/MoleculaB.h $(SRCDIR)/String.h
$(OBJDIR)/W15.o: $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h $(SRCDIR)/Atomo.h
$(OBJDIR)/W15.o: $(SRCDIR)/pto3D.h $(SRCDIR)/Nanotubo.h
$(OBJDIR)/W2.o: $(SRCDIR)/W2.h $(SRCDIR)/pto3D.h $(SRCDIR)/String.h
$(OBJDIR)/W2.o: $(SRCDIR)/W1.h $(SRCDIR)/MoleculaT.h $(SRCDIR)/MoleculaB.h $(SRCDIR)/TabPe.h $(SRCDIR)/AtomList.h
$(OBJDIR)/W2.o: $(SRCDIR)/Atomo.h $(SRCDIR)/pto2D.h $(SRCDIR)/Nanotubo.h

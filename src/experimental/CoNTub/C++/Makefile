CXX=g++
CXXFLAGS=-Wall -g

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

#	W15.cpp \
#	W1.cpp \
#	W2.cpp

OBJS=$(SRCS:.cpp=.o)

.SUFFIXES: .h .cpp .o ;

.cpp.o:
	$(CXX) $(CXXFLAGS) -c $(@:.o=.cpp)

W1: $(W1SRCS:.cpp=.o)
	$(CXX) $(CXXFLAGS) -o W1 $(W1SRCS:.cpp=.o)

W15: $(W15SRCS:.cpp=.o)
	$(CXX) $(CXXFLAGS) -o W15 $(W15SRCS:.cpp=.o)

W2: $(W2SRCS:.cpp=.o)
	$(CXX) $(CXXFLAGS) -o W2 $(W2SRCS:.cpp=.o)

# objs: $(OBJS)

clean:
	rm -f *.o *~ core.* W1 W15 W2

deps:
	makedepend $(SRCS) W1.cpp W15.cpp W2.cpp -f - | \
		sed 's# /[^ ]*\.h##g' | egrep -v ':$$' >> Makefile

# DO NOT DELETE

anillo.o: anillo.h
anillo.o: pto3D.h
anillo.o: String.h MoleculaT.h MoleculaB.h TabPe.h AtomList.h Atomo.h
AtomList.o: AtomList.h
AtomList.o: Atomo.h pto3D.h String.h TabPe.h
Minimol.o: Minimol.h pto3D.h String.h
Minimol.o: MoleculaB.h TabPe.h AtomList.h Atomo.h
MoleculaB.o: MoleculaB.h String.h TabPe.h
MoleculaB.o: AtomList.h Atomo.h pto3D.h
MoleculaT.o: MoleculaT.h MoleculaB.h String.h
MoleculaT.o: TabPe.h AtomList.h Atomo.h pto3D.h Minimol.h anillo.h
Nanotubo.o: Nanotubo.h
pto2D.o: pto2D.h
pto2D.o: pto3D.h String.h
pto3D.o: pto3D.h
pto3D.o: String.h pto2D.h
TabPe.o: TabPe.h String.h
W1.o: W1.h
W1.o: MoleculaT.h MoleculaB.h String.h TabPe.h AtomList.h Atomo.h pto3D.h
W1.o: Nanotubo.h

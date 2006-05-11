CXX=g++
CXXFLAGS=-Wall -g

SRCS=anillo.cpp \
	AtomList.cpp \
	Atomo.cpp \
	formato.cpp \
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

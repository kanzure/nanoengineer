SRCS=anillo.cpp \
	Atomo.cpp \
	formato.cpp \
	Minimol.cpp \
	MoleculaB.cpp \
	MoleculaT.cpp \
	Nanotubo.cpp \
	pto2D.cpp \
	pto3D.cpp \
	TabPe.cpp \
	W15.cpp \
	W1.cpp \
	W2.cpp

OBJS=$(SRCS:.cpp=.o)

.SUFFIXES: .h .cpp .o ;

.cpp.o:
	g++ -c $(@:.o=.cpp)

objs: $(OBJS)

clean:
	rm -f *.o *~

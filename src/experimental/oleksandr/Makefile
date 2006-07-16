OBJS = cppsurface.o surface.o container.o bucket.o triple.o psurface.o
LIBS =  -L"C:/Dev-Cpp/lib" -L"C:/Python23/libs" 
CXXFLAGS = -O3 -W1

all: psurface.dll

clean:
	rm -f *~ *.o psurface.c psurface.dll psurface.def

psurface.c: psurface.pyx
	python \python23\Scripts\pyrexc psurface.pyx

psurface.o: psurface.c 
	gcc -c psurface.c -I"C:/Python23/include" -o psurface.o -O3 -W1

cppsurface.o: cppsurface.cpp cppsurface.h
	g++ -c cppsurface.cpp -o cppsurface.o $(CXXFLAGS)
	
surface.o: surface.cpp surface.h
	g++ -c surface.cpp -o surface.o $(CXXFLAGS)

container.o: container.cpp container.h
	g++ -c container.cpp -o container.o $(CXXFLAGS)

bucket.o: bucket.cpp bucket.h
	g++ -c bucket.cpp -o bucket.o $(CXXFLAGS)

triple.o: triple.cpp triple.h
	g++ -c triple.cpp -o triple.o $(CXXFLAGS)

psurface.dll: $(OBJS) libpython23.a
	g++ -shared -o psurface.dll $(OBJS)\
		-Wl,--output-def,psurface.def -L. -lpython23 $(LIBS)



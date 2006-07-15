PYREXTARGET=psurface.dll

all: $(PYREXTARGET)

clean:
	rm -f *~ *.o psurface.c psurface.dll psurface.def

psurface.c: psurface.pyx
	python \python23\Scripts\pyrexc psurface.pyx

psurface.dll: psurface.c cppsurface.o libpython23.a
	gcc -shared -I"C:/Python23/include" -o psurface.dll psurface.c cppsurface.o\
		-Wl,--output-def,psurface.def -L. -lpython23

cppsurface.o: cppsurface.cpp cppsurface.h
	g++ -c cppsurface.cpp -o cppsurface.o

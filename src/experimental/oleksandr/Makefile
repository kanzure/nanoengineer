PYREXTARGET=psurface.dll

all: $(PYREXTARGET)

clean:
	rm -f *~ *.o psurface.c psurface.dll psurface.def

psurface.c: psurface.pyx
	python \python23\Scripts\pyrexc psurface.pyx

psurface.dll: psurface.c libpython23.a
	gcc -shared -I"C:/Python23/include" -o psurface.dll psurface.c \
		-Wl,--output-def,psurface.def -L. -lpython23


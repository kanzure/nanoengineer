include platform.mk

PYREXTARGET=putz$(TARGET_SUFFIX)

all: $(PYREXTARGET)

clean:
	rm -f *~ *.o *.pyc putz.c putz.so 

putz.c: putz.pyx futz.c
	$(PYREXC) putz.pyx

putz.dll: putz.c $(PYREXOBJS) libpython$(PYVER).a version.h
	gcc -shared -I"C:/Python$(PYVER)/include" -o putz.dll $(PYREXOBJS) \
		-Wl,--output-def,putz.def -L. -lpython$(PYVER)

putz.so: putz.o
	$(CC) -shared -o putz.so putz.o $(LDFLAGS)

#putz.c: putz.pyx
#	pyrexc putz.pyx

#$(PYREXTARGET): putz.o
#	$(CC) -shared $(LDFLAGS) -o $(PYREXTARGET) putz.o

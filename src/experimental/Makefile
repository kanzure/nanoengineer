CFLAGS=-Wall -O2 -pg

test: testsqrt
	./testsqrt

testsqrt: testsqrt.c interp_sqrt.c
	gcc $(CFLAGS) testsqrt.c -o testsqrt -lrt -lm

interp_sqrt.c: interp.py
	python interp.py c sqrt static_inline
	indent -i4 -br -ce interp_ugly.c -o interp.c
	mv interp.c interp_sqrt.c

clean:
	rm -f *.o *~ interp*.c gmon.out testsqrt

# doing a profile is incompatible with "static_inline"
profile:
	make clean
	make testsqrt
	./testsqrt
	gprof testsqrt

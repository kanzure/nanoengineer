include platform.mk

TARGET=comp$(TARGET_SUFFIX)

all: jelloGui.py comp.so

jelloGui.py: jelloGui.ui
	pyuic jelloGui.ui > jelloGui.py

comp.c: comp.pyx comphelp.c
	$(PYREXC) comp.pyx

comp.so: comp.o
	$(CC) -shared -o comp.so comp.o $(LDFLAGS)

clean:
	rm -f *.pyc *~ *.o jelloGui.py *.so comp.c OUCH

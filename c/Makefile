# Makefile for the simulator

CC=gcc
CFLAGS=-O3 -g
LDFLAGS=-L/usr/X11R6/lib -lm -lX11 -lXi -lXmu

# If we were going to use GTK, it would look something like this
#CFLAGS+=-I/usr/include/gtk-2.0 \
#	-I/usr/include/glib-2.0 \
#	-I/usr/lib/gtk-2.0/include \
#	-I/usr/include/libgnome-2.0 \
#	-I/usr/include/libgnomeui-2.0 \
#	-I/usr/include/gconf/2 \
#	-I/usr/lib/glib-2.0/include \
#	-I/usr/include/pango-1.0 \
#	-I/usr/include/atk-1.0 \
#	-I/usr/include/libbonobo-2.0 \
#	-I/usr/include/libbonoboui-2.0 \
#	-I/usr/include/libgnomecanvas-2.0 \
#	-I/usr/include/libart-2.0 \
#	-I/usr/include/gnome-vfs-2.0
#LDFLAGS+=-lglade-2.0 -lgtk-x11-2.0
#GRAPHICS_SUFFIX=gtk

all: mol

SUFFIXES: .c .h .o ;

.c.o:
	$(CC) -c $(CFLAGS) -o $@ $(@:.o=.c)

mol.o: mol.h
lin-alg.o: mol.h
display-opengl.o: mol.h
dumpxyz.o: mol.h
xyzreader.o: mol.h

MOLOBJS=mol.o lin-alg.o display-opengl.o
SIMOBJS=mol.o lin-alg.o dumpxyz.o
DISPOBJS=xyzreader.o lin-alg.o display-opengl.o

mol: $(MOLOBJS)
	$(CC) -o mol $(LDFLAGS) -lGL -lGLU -lglut $(MOLOBJS)

molsim: $(SIMOBJS)
	$(CC) -o molsim $(LDFLAGS) $(SIMOBJS)

moldisp: $(DISPOBJS)
	$(CC) -o moldisp $(LDFLAGS) -lGL -lGLU -lglut $(DISPOBJS)

clean:
	rm -f mol *.o *.so *~ TAGS fmc.mmp
	rm -rf html latex

TAGS:
	etags *.c *.h

fmc.mmp: ../samples/fineMotion970116.pdb ../samples/pdb2mmp.py
	(cd ../samples/; ./pdb2mmp.py < fineMotion970116.pdb) > fmc.mmp

# I have no idea why this doesn't work. GLUT programs don't like to be
# called from a Makefile. Go figure.
#tryit: mol fmc.mmp
#	./mol fmc.mmp

doxy:
	doxygen Doxyfile

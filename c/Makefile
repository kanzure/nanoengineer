# Makefile for the simulator

CC=gcc
CFLAGS=-O3 -g
LDFLAGS=-L/usr/X11R6/lib -lm -lX11 -lXi -lXmu

# Use OPENGL by default, until we decide otherwise
LDFLAGS+=-lGL -lGLU -lglut
GRAPHICS_SUFFIX=opengl

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

DISPLAY=display-$(GRAPHICS_SUFFIX)

all: mol

SUFFIXES: .c .h .o ;

.c.o:
	$(CC) -c $(CFLAGS) -o $@ $(@:.o=.c)

CFILES=mol.c lin-alg.c $(DISPLAY).c
HFILES=mol.h
OBJS=$(CFILES:.c=.o)

mol: $(OBJS)
	$(CC) -o mol $(LDFLAGS) $(OBJS)

clean:
	rm -f mol *.o *.so *~ TAGS fmc.mmp
	rm -rf html latex

TAGS: $(CFILES) $(HFILES)
	etags *.c *.h

fmc.mmp: ../samples/fineMotion970116.pdb ../samples/pdb2mmp.py
	(cd ../samples/; ./pdb2mmp.py < fineMotion970116.pdb) > fmc.mmp

# I have no idea why this doesn't work. GLUT programs don't like to be
# called from a Makefile. Go figure.
#tryit: mol fmc.mmp
#	./mol fmc.mmp

doxy:
	doxygen Doxyfile

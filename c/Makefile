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

OBJS=mol.o lin-alg.o $(DISPLAY).o

mol: $(OBJS)
	$(CC) -o mol $(LDFLAGS) $(OBJS)

clean:
	rm -f mol *.o *.so *~
	rm -rf html latex

HERE := $(shell pwd)

doxy:
	doxygen Doxyfile

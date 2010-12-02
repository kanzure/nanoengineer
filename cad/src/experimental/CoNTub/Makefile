

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

JAVASRCS=anillo.java \
	Atomo.java \
	formato.java \
	GLienzo2.java \
	GLienzo.java \
	Minimol.java \
	Mira3D.java \
	MoleculaB.java \
	MoleculaT.java \
	Nanotubo.java \
	nt.java \
	NTLienzo.java \
	P15.java \
	P1.java \
	P25.java \
	P2.java \
	P35.java \
	P3.java \
	P4.java \
	pto2D.java \
	pto3D.java \
	TabPe.java

# other files get compiled automatically
WSRCS=W1.java W15.java W2.java TabPe.java

#	parchetubo.java \
#	P1old.java \

CLASSES=$(JAVASRCS:.java=.class)

.SUFFIXES: .java .class ;

.java.class:
	javac $(@:.class=.java)

all:
	javac $(JAVASRCS)

w:
	javac $(WSRCS)

clean:
	rm -f *\#
	rm -f *~ *.class *.s *.o *.i a.out cscope.out W1 W15 W2

classes: $(CLASSES)

# Try using gcc to build a java executable that doesn't rely on the JVM.

THESEGUYS=W1.java \
	W15.java \
	W2.java \
	anillo.java \
	Atomo.java \
	formato.java \
	Minimol.java \
	MoleculaT.java \
	MoleculaB.java \
	pto2D.java \
	pto3D.java \
	Nanotubo.java \
	TabPe.java

# http://gcc.gnu.org/wiki/Statically%20linking%20libgcj
MAGIC=$(THESEGUYS:.java=.o) -shared-libgcc -Wl,-non_shared -lgcj \
	-Wl,-call_shared -lsupc++ -Wl,--as-needed -lz -lgcc_s \
	-lpthread -lc -lm -ldl -Wl,--no-as-needed

W1: $(THESEGUYS)
	gcj -c W1.java
	gcj --main=W1 -save-temps $(THESEGUYS)
	gcc -o W1 $(MAGIC) W1main.i

W15: $(THESEGUYS)
	gcj -c W15.java
	gcj --main=W15 -save-temps $(THESEGUYS)
	gcc -o W15 $(MAGIC) W15main.i

W2: $(THESEGUYS)
	gcj -c W2.java
	gcj --main=W2 -save-temps $(THESEGUYS)
	gcc -o W2 $(MAGIC) W2main.i

# These have dynamic dependencies on the gcj library
#W1: $(THESEGUYS)
#	gcj -O2 --main=W1 $(THESEGUYS) -o W1
#W2: $(THESEGUYS)
#	gcj -O2 --main=W2 $(THESEGUYS) -o W2
#W15: $(THESEGUYS)
#	gcj -O2 --main=W15 $(THESEGUYS) -o W15

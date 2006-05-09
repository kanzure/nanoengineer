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
	rm -f *~ *\# *.class cscope.out

classes: $(CLASSES)

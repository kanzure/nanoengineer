
INCLUDES = -I@PYTHON_BASE@/include/python${PYTHON_VERSION}
CFLAGS = $(shell python distutils_compile_options.py compiler_so)

ne1bindir = $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/bin
ne1bin_LTLIBRARIES = sim.la

sim_la_LIBADD = \
	-L@PYTHON_BASE@/lib/python$(PYTHON_VERSION)/config \
	-lm \
	-lpython$(PYTHON_VERSION) \
	libstructcompare.a
sim_la_LDFLAGS = -module

sim_la_SOURCES = \
	allocate.c allocate.h \
	amber_patterns.c amber_patterns.h \
	debug.h \
	dynamics.c dynamics.h \
	globals.c globals.h \
	hashtable.c hashtable.h \
	interpolate.c interpolate.h \
	jigs.c jigs.h \
	lin-alg.c lin-alg.h \
	minimize.c minimize.h \
	minstructure.c minstructure.h \
	newtables.c newtables.h \
	pam5_patterns.c pam5_patterns.h \
	pattern.c pattern.h \
	part.c part.h \
	potential.c potential.h \
	printGromacsTopology.c printGromacsTopology.h \
	printers.c printers.h \
	read_amber_itp.c read_amber_itp.h \
	readmmp.c readmmp.h \
	readxyz.c readxyz.h \
	rigid.c rigid.h \
	rigid-ode.c rigid-ode.h \
	structcompare.c structcompare.h \
	writemovie.c writemovie.h \
	sim.c

# -std-c99 gets us isnormal()
noinst_LIBRARIES = libstructcompare.a
libstructcompare_a_SOURCES = structcompare.c simulator.h
libstructcompare_a_CFLAGS = -std=c99

BUILT_SOURCES = bonds.gen bends.gen version.h sim.c
bonds.gen: stretch.py stretch.parms
	python stretch.py stretch.parms > bonds.gen
bends.gen: bend.py bending.parms
	python bend.py bending.parms > bends.gen
version.h:
	python makehelp.py "$(CFLAGS)" "$(LDFLAGS)" "@UNAME_A@" \
		| grep -v "^running " > version.h
sim.c: sim.pyx simhelp.c
	pyrexc sim.pyx

EXTRA_DIST = \
	stretch.py stretch.parms bend.py bending.parms makehelp.py sim.pyx \
	simhelp.c distutils_compile_options.py


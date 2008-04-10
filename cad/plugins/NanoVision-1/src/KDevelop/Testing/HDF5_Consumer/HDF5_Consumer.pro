TEMPLATE = app
TARGET = HDF5_Consumer
DESTDIR = ../../../../bin/

CONFIG += debug_and_release \
build_all

SOURCES += ../../../Testing/HDF5_Consumer/HDF5_Consumer.cpp

INCLUDEPATH += $(OPENBABEL_INCPATH) \
 ../../../../include \
 ../../../../src
# The "../../../src" is temporary for NXEntityManager to access an
# HDF5_SimResultsImportExport plugin function directly.

PROJECTLIBS = -lNanorexInterface \
-lNanorexUtility

CONFIG(debug,debug|release) {
	TARGET = $${TARGET}_d
	PROJECTLIBS ~= s/(.+)/\1_d/g
}

LIBS += -L$(OPENBABEL_LIBPATH) \
-L../../../../lib \
$$PROJECTLIBS \
-lopenbabel

TARGETDEPS += ../../../../lib/libNanorexInterface.so \
../../../../lib/libNanorexUtility.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

HEADERS += ../../../Testing/HDF5_Consumer/HDF5_Consumer.h

# This tell qmake to not create a Mac bundle for this application.
CONFIG -= app_bundle

# make clean target
QMAKE_CLEAN += $${DESTDIR}$${TARGET}

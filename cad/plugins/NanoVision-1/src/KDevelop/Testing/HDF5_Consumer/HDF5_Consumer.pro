SOURCES += ../../../Testing/HDF5_Consumer/HDF5_Consumer.cpp

TEMPLATE = app

INCLUDEPATH += $(OPENBABEL_INCPATH) \
 ../../../../include \
 ../../../../src
# The "../../../src" is temporary for NXEntityManager to access an
# HDF5_SimResultsImportExport plugin function directly.

LIBS += -L$(OPENBABEL_LIBPATH) \
-L../../../../lib \
-lNanorexInterface \
-lNanorexUtility \
-lopenbabel

TARGETDEPS += ../../../../lib/libNanorexInterface.so \
../../../../lib/libNanorexUtility.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

DESTDIR = ../../../../bin/

HEADERS += ../../../Testing/HDF5_Consumer/HDF5_Consumer.h

# This tell qmake to not create a Mac bundle for this application.
CONFIG -= app_bundle


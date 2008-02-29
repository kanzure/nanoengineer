SOURCES += ../../../Testing/HDF5_Consumer/HDF5_Consumer.cpp

TEMPLATE = app

INCLUDEPATH += $(OPENBABEL_INCPATH) \
../../../../include

LIBS += -lopenbabel \
-L../../../../lib \
-lNanorexInterface \
-lNanorexUtility

TARGETDEPS += ../../../../lib/HDF5_SimResultsImportExport.so \
../../../../lib/libNanorexInterface.so \
../../../../lib/libNanorexUtility.so
macx : TARGETDEPS ~= s/.so/.dylib/g

DESTDIR = ../../../../bin/

HEADERS += ../../../Testing/HDF5_Consumer/HDF5_Consumer.h

# This tell qmake to not create a Mac bundle for this application.
CONFIG -= app_bundle

CONFIG += debug_and_release


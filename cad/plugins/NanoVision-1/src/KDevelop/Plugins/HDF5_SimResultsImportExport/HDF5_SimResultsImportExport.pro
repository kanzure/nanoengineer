SOURCES += ../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExport.cpp

HEADERS += ../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExport.h

INCLUDEPATH += ../../../../include \
 $(OPENBABEL_INCPATH)

TEMPLATE = lib

CONFIG += dll \
 debug \
 plugin

LIBS += -L../../../../lib \
-lNanorexUtility \
-lNanorexInterface \
-lHDF5_SimResults \
-lopenbabel \
-lhdf5

TARGETDEPS += ../../../../lib/libNanorexUtility.so \
../../../../lib/libNanorexInterface.so
macx : TARGETDEPS ~= s/.so/.dylib/g

DESTDIR = ../../../../lib

CONFIG -= release


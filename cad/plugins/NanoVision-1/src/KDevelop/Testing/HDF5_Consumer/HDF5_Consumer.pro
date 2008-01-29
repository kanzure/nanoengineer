SOURCES += ../../../Testing/HDF5_Consumer/HDF5_Consumer.cpp

TEMPLATE = app

INCLUDEPATH += $(OPENBABEL_INCPATH) \
../../../../include
LIBS += -lopenbabel \
-L../../../../lib \
-lHDF5_SimResultsImportExport \
-lNanorexInterface \
-lNanorexUtility
TARGETDEPS += ../../../../lib/libHDF5_SimResultsImportExport.so \
../../../../lib/libNanorexInterface.so \
../../../../lib/libNanorexUtility.so
DESTDIR = ../../../../bin/


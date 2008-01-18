SOURCES += CppUnit.cpp \
 ../../Interface/NXEntityManagerTest.cpp \
 ../../Interface/NXNumbersTest.cpp \
 ../../Utility/NXCommandResultTest.cpp \
 ../../Utility/NXLoggerTest.cpp \
 ../../Utility/NXStringTokenizerTest.cpp \
 ../../Utility/NXUtilityTest.cpp \
 ../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExportTest.cpp

TEMPLATE = app

TARGET = CppUnit

LIBS += -lcppunit \
 -lopenbabel \
 -L../../../lib \
 -lNanorexUtility \
 -lNanorexInterface \
 -lHDF5_SimResultsImportExport



INCLUDEPATH += ../../../include \
 /usr/local/include/openbabel-2.0/
HEADERS += ../../Utility/NXCommandResultTest.h \
../../Utility/NXLoggerTest.h \
../../Utility/NXStringTokenizerTest.h \
../../Utility/NXUtilityTest.h \
../../Interface/NXEntityManagerTest.h \
../../Interface/NXNumbersTest.h \
../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExportTest.h
TARGETDEPS += ../../../lib/libNanorexUtility.so \
../../../lib/libNanorexInterface.so \
../../../lib/libHDF5_SimResultsImportExport.so

SOURCES += ../../../Testing/CppUnit/CppUnit.cpp \
 ../../../Interface/NXEntityManagerTest.cpp \
 ../../../Interface/NXNumbersTest.cpp \
 ../../../Utility/NXCommandResultTest.cpp \
 ../../../Utility/NXLoggerTest.cpp \
 ../../../Utility/NXStringTokenizerTest.cpp \
 ../../../Utility/NXUtilityTest.cpp \
 ../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExportTest.cpp \
 ../../../Interface/NXSceneGraphTest.cpp \
 ../../../Plugins/OpenBabelImportExport/OpenBabelImportExportTest.cpp \
 ../../../Utility/NXPointTest.cpp

TEMPLATE = app

TARGET = CppUnit

LIBS += -lcppunit \
 -lopenbabel \
 -L../../../../lib \
 -lNanorexUtility \
 -lNanorexInterface \
 -lHDF5_SimResultsImportExport

INCLUDEPATH += ../../../../include \
 $(OPENBABEL_INCPATH)

HEADERS += ../../../Utility/NXCommandResultTest.h \
../../../Utility/NXLoggerTest.h \
../../../Utility/NXStringTokenizerTest.h \
../../../Utility/NXUtilityTest.h \
../../../Interface/NXEntityManagerTest.h \
../../../Interface/NXNumbersTest.h \
../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExportTest.h \
 ../../../Plugins/OpenBabelImportExport/OpenBabelImportExportTest.h \
 ../../../Interface/NXSceneGraphTest.h \
 ../../../Utility/NXPointTest.h

TARGETDEPS += ../../../../lib/libNanorexUtility.so \
../../../../lib/libNanorexInterface.so \
../../../../lib/libHDF5_SimResultsImportExport.so
DESTDIR = ../../../../bin

CONFIG -= release

CONFIG += debug \
stl
QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG


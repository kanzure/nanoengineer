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
 -lNanorexInterface

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
../../../../lib/HDF5_SimResultsImportExport.so
macx:TARGETDEPS ~= s/.so/.dylib/g

DESTDIR = ../../../../bin

CONFIG -= release

CONFIG += debug \
stl

# This tell qmake to not create a Mac bundle for this application.
CONFIG -= app_bundle

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG


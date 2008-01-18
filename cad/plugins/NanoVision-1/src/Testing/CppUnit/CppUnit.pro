SOURCES += CppUnit.cpp \
 ../../Interface/NXNumbers.cpp \
 ../../Interface/NXNumbersTest.cpp \
 ../../Interface/NXEntityManager.cpp \
 ../../Interface/NXEntityManagerTest.cpp \
 ../../Interface/NXMoleculeSet.cpp \
 ../../Utility/NXLoggerTest.cpp \
 ../../Utility/NXCommandResult.cpp \
 ../../Utility/NXCommandResultTest.cpp \
 ../../Utility/NXStringTokenizer.cpp \
 ../../Utility/NXStringTokenizerTest.cpp \
 ../../Utility/NXUtility.cpp \
 ../../Utility/NXUtilityTest.cpp \
 ../../Utility/NXPlugin.cpp \
 ../../Utility/NXPluginGroup.cpp \
 ../../Utility/NXProperties.cpp \
 ../../Interface/NXDataImportExportPlugin.cpp \
 ../../Utility/NXLogger.cpp \
 ../../Interface/NXMoleculeData.cpp

TEMPLATE = app

TARGET = CppUnit

LIBS += -lcppunit \
 -lopenbabel

DESTDIR = /home/bh/11Nano/SVN-D/cad/plugins/NanoVision-1/src/Testing/CppUnit

HEADERS += ../../Interface/NXNumbersTest.h \
../../../include/Nanorex/Interface/NXNumbers.h \
 ../../../include/Nanorex/Interface/NXEntityManager.h \
 ../../../include/Nanorex/Interface/NXMoleculeSet.h \
 ../../../include/Nanorex/Utility/NXLogger.h \
 ../../Interface/NXEntityManagerTest.h \
 ../../Utility/NXLoggerTest.h \
 ../../Utility/NXCommandResultTest.h \
 ../../../include/Nanorex/Interface/NXNanoVisionResultCodes.h \
 ../../../include/Nanorex/Utility/NXStringTokenizer.h \
 ../../Utility/NXStringTokenizerTest.h \
 ../../Utility/NXUtilityTest.h \
 ../../../include/Nanorex/Utility/NXUtility.h \
 ../../../include/Nanorex/Utility/NXPluginGroup.h \
 ../../../include/Nanorex/Utility/NXPlugin.h \
 ../../../include/Nanorex/Utility/NXProperties.h \
 ../../../include/Nanorex/Interface/NXDataImportExportPlugin.h \
 ../../../include/Nanorex/Interface/NXMoleculeData.h

INCLUDEPATH += ../../../include \
 /usr/local/include/openbabel-2.0/

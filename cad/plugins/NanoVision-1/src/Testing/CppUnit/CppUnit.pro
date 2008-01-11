SOURCES += CppUnit.cpp \
 ../../Interface/NXNumbers.cpp \
 ../../Interface/NXNumbersTest.cpp \
 ../../Interface/NXEntityManager.cpp \
 ../../Interface/NXEntityManagerTest.cpp \
 ../../Interface/NXAtom.cpp \
 ../../Interface/NXMoleculeSet.cpp \
 ../../Interface/NXBond.cpp \
 ../../Interface/NXMolecule.cpp

TEMPLATE = app

TARGET = CppUnit

LIBS += -lcppunit

DESTDIR = /home/bh/11Nano/SVN-D/cad/plugins/NanoVision-1/src/Testing/CppUnit

HEADERS += ../../Interface/NXNumbersTest.h \
../../../include/Nanorex/Interface/NXNumbers.h \
 ../../../include/Nanorex/Interface/NXChemistryDataModel.h \
 ../../../include/Nanorex/Interface/NXEntityManager.h \
 ../../../include/Nanorex/Interface/NXAtom.h \
 ../../../include/Nanorex/Interface/NXMoleculeSet.h \
 ../../../include/Nanorex/Interface/NXBond.h \
 ../../../include/Nanorex/Interface/NXMolecule.h
INCLUDEPATH += /home/bh/11Nano/SVN-D/cad/plugins/NanoVision-1/include


TEMPLATE = lib

CONFIG += dll

DESTDIR = ../../../../lib

INCLUDEPATH += $(OPENBABEL_INCPATH) \
../../../../include
SOURCES += ../../../Plugins/OpenBabelImportExport/OpenBabelImportExport.cpp

HEADERS += ../../../Plugins/OpenBabelImportExport/OpenBabelImportExport.h


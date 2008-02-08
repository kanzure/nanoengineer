TEMPLATE = lib

CONFIG += dll \
 plugin

DESTDIR = ../../../../lib

INCLUDEPATH += $(OPENBABEL_INCPATH) \
../../../../include

SOURCES += ../../../Plugins/OpenBabelImportExport/OpenBabelImportExport.cpp

HEADERS += ../../../Plugins/OpenBabelImportExport/OpenBabelImportExport.h

LIBS += -lopenbabel \
 -L../../../../lib \
 -lNanorexInterface \
 -lNanorexUtility


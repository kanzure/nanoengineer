TEMPLATE = lib

CONFIG += dll \
plugin \
debug_and_release \
 stl


SOURCES += ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExport.cpp

DISTFILES += ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExport.rl

HEADERS += ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExport.h \
../../../Plugins/NanorexMMPImportExport/ragelistreamptr.h
QT -= gui

LIBS += -L../../../../lib \
 -lNanorexInterface \
 -lNanorexUtility \
 -L$(OPENBABEL_LIBPATH) \
 -lopenbabel

INCLUDEPATH += $(OPENBABEL_INCPATH) \
../../../../include
TARGET = NanorexMMPImportExport

DESTDIR = ../../../../lib/


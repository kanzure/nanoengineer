TEMPLATE = lib

CONFIG += dll \
plugin \
debug \
 stl
CONFIG -= release


SOURCES += ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExport.cpp

DISTFILES += ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExport.rl

HEADERS += ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExport.h \
../../../Plugins/NanorexMMPImportExport/ragelistreamptr.h
QT -= gui

LIBS += -lopenbabel

INCLUDEPATH += $(OPENBABEL_INCPATH) \
../../../../include
TARGET = NanorexMMPImportExport

DESTDIR = ../../../../lib/


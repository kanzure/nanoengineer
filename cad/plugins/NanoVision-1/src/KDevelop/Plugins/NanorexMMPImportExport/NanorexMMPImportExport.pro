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

# Remove the "lib" from the start of the library
QMAKE_POST_LINK = "echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)"
macx : QMAKE_POST_LINK ~= s/.so/.dylib/g


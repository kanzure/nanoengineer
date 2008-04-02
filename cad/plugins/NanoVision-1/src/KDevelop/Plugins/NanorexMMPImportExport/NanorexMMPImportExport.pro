TEMPLATE = lib

CONFIG += dll \
plugin \
stl \
 debug_and_release


SOURCES += ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExport.cpp

DISTFILES += ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExport.rl \
 ../../../Plugins/NanorexMMPImportExport/atom.rl \
 ../../../Plugins/NanorexMMPImportExport/utilities.rl \
 ../../../Plugins/NanorexMMPImportExport/group.rl \
 ../../../Plugins/NanorexMMPImportExport/molecule.rl

HEADERS += ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExport.h \
 ../../../Plugins/NanorexMMPImportExport/RagelIstreamPtr.h
QT -= gui


INCLUDEPATH += $(OPENBABEL_INCPATH) \
../../../../include
TARGET = NanorexMMPImportExport

DESTDIR = ../../../../lib/

# Remove the "lib" from the start of the library
unix : QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)
macx : QMAKE_POST_LINK ~= s/.so/.dylib/g

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline

LIBS += -L../../../../lib \
  -lNanorexUtility \
  -lNanorexInterface \
  -L$(OPENBABEL_LIBPATH) \
  -lopenbabel


TEMPLATE = lib

CONFIG += dll \
 plugin \
 debug_and_release

DESTDIR = ../../../../lib

INCLUDEPATH += $(OPENBABEL_INCPATH) \
../../../../include

SOURCES += ../../../Plugins/OpenBabelImportExport/OpenBabelImportExport.cpp

HEADERS += ../../../Plugins/OpenBabelImportExport/OpenBabelImportExport.h

LIBS += -L../../../../lib \
 -lNanorexInterface \
 -lNanorexUtility \
 -L$(OPENBABEL_LIBPATH) \
 -lopenbabel

TARGETDEPS += ../../../../lib/libNanorexUtility.so \
 ../../../../lib/libNanorexInterface.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

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

# Remove the "lib" from the start of the library
QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)
macx : QMAKE_POST_LINK ~= s/.so/.dylib/g


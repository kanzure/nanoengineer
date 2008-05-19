TEMPLATE = lib

TARGET = OpenBabelImportExport

DESTDIR = ../../../../lib

SOURCES += ../../../Plugins/OpenBabelImportExport/OpenBabelImportExport.cpp

HEADERS += ../../../Plugins/OpenBabelImportExport/OpenBabelImportExport.h

TARGETDEPS += ../../../../lib/libNanorexInterface.so \
  ../../../../lib/libNanorexUtility.so

CONFIG += dll \
 plugin \
 release \
 stl

#CONFIG(debug,debug|release) {
#    TARGET = $$join(TARGET,,,_d)
#    PROJECTLIBS ~= s/(.+)/\1_d/g
#	TARGETDEPS ~= s/(.+).so/\1_d.so/g
#}

unix {
    QMAKE_CLEAN += $${DESTDIR}$${TARGET}.so

	# Remove the "lib" from the start of the library
    QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)
}

macx {
    QMAKE_CLEAN += $${DESTDIR}$${TARGET}.dylib
    TARGETDEPS ~= s/.so/.dylib/g
    QMAKE_POST_LINK ~= s/.so/.dylib/g
}

win32 {
    QMAKE_CLEAN += $${DESTDIR}$${TARGET}.dll
    TARGETDEPS ~= s/.so/.a/g
}


INCLUDEPATH += $(OPENBABEL_INCPATH) \
../../../../include


#QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
# -g \
# -O0 \
# -fno-inline

QMAKE_CXXFLAGS_RELEASE += -DNDEBUG -O2

LIBS += -L../../../../lib \
  -lNanorexInterface \
  -lNanorexUtility \
  -L$(OPENBABEL_LIBPATH) \
  -lopenbabel


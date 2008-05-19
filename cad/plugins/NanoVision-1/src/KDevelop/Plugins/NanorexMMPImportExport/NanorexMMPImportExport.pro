TEMPLATE = lib

TARGET = NanorexMMPImportExport

DESTDIR = ../../../../lib/

CONFIG += \
 dll \
 plugin \
 release \
 rtti \
 stl

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

TARGETDEPS += ../../../../lib/libNanorexInterface.so \
  ../../../../lib/libNanorexUtility.so

#CONFIG(debug,debug|release) {
#	TARGET = $$join(TARGET,,,_d)
#	PROJECTLIBS ~= s/(.+)/\1_d/g
#	TARGETDEPS ~= s/(.+).(a|so)/\1_d.\2/g
#}

unix {
    QMAKE_CLEAN += $${DESTDIR}$${TARGET}.so   $${DESTDIR}lib$${TARGET}.so

	# Remove the "lib" from the start of the library
    QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs cp $(DESTDIR)$(TARGET)
}

macx {
    QMAKE_CLEAN += $${DESTDIR}$${TARGET}.dylib  $${DESTDIR}lib$${TARGET}.dylib
    TARGETDEPS ~= s/.so/.dylib/g
    QMAKE_POST_LINK ~= s/.so/.dylib/g
}

win32 {
    QMAKE_CLEAN += $${DESTDIR}$${TARGET}.dll
    TARGETDEPS ~= s/.so/.a/g
}

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


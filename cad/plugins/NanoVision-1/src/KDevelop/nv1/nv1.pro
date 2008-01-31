TEMPLATE = app

CONFIG -= release

CONFIG += debug \
stl \
opengl
QT += opengl

LIBS += -lopenbabel \
-L../../../lib \
-lNanorexInterface \
-lNanorexUtility
TARGETDEPS += ../../../lib/libNanorexUtility.so \
../../../lib/libNanorexInterface.so \
../../../lib/libHDF5_SimResultsImportExport.so
SOURCES += ../../DataWindow.cpp \
../../LogHandlerWidget.cpp \
../../main.cpp \
../../MainWindowTabWidget.cpp \
../../nv1.cpp \
../../ResultsWindow.cpp \
../../TrajectoryGraphicsPane.cpp \
../../ViewParametersWindow.cpp \
../../ErrorDialog.cpp
HEADERS += ../../DataWindow.h \
../../LogHandlerWidget.h \
../../main.h \
../../MainWindowTabWidget.h \
../../nv1.h \
../../ResultsWindow.h \
../../TrajectoryGraphicsPane.h \
../../ViewParametersWindow.h \
../../ErrorDialog.h
FORMS += ../../LogHandlerWidget.ui \
../../MainWindowTabWidget.ui \
../../ResultsWindow.ui \
../../TrajectoryGraphicsPane.ui \
../../ViewParametersWindow.ui \
../../ErrorDialog.ui
RESOURCES += ../../application.qrc

INCLUDEPATH += ../../../include \
/usr/include/openbabel-2.0
TARGET = nv1

DESTDIR = ../../../bin


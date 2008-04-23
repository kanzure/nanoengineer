TEMPLATE = app
TARGET = NXOpenGLRenderingEngineTest
DESTDIR = ../../../../../../../bin/

CONFIG += stl \
opengl \
 debug \
 rtti 

QT += opengl

QMAKE_CXXFLAGS_DEBUG += -DGENERATE_MMP -DNX_DEBUG \
-g \
-O0 \
-fno-inline


INCLUDEPATH += ../../../../../../../include \
../../../../../../../src/Plugins/RenderingEngines/OpenGL/GLT \
 $(OPENBABEL_INCPATH) \
 ../../../../../../../src \
 ../../../../../../../src/Plugins/RenderingEngines/OpenGL

SOURCES += ../../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngineTest.cpp


TARGETDEPS += ../../../../../../../lib/libNXBallAndStickOpenGLRenderer_d.so \
  ../../../../../../../lib/libNXOpenGLRenderingEngine_d.so \
  ../../../../../../../lib/libNXOpenGLSceneGraph_d.a \
  ../../../../../../../lib/libGLT_d.a \
  ../../../../../../../lib/libNanorexInterface_d.so \
  ../../../../../../../lib/libNanorexUtility_d.so

macx: TARGETDEPS ~= s/.so/.dylib/g

LIBS += -L../../../../../../../lib \
  -lNXBallAndStickOpenGLRenderer_d \
  -lNXOpenGLRenderingEngine_d \
  -lNanorexInterface_d \
  -lNanorexUtility_d \
  -lNXOpenGLSceneGraph_d \
  -lGLT_d \
  -L$(OPENBABEL_INCPATH) \
  -lopenbabel

# make clean target
QMAKE_CLEAN += $${DESTDIR}$${TARGET}


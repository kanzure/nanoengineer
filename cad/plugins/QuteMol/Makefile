
INCDIRS = -Ivcg -Isrc -I.
OPTFLAGS = -Os -Wall -g

CXXFLAGS = $(INCDIRS) $(OPTFLAGS) `wx-config --cppflags`
LIBS = $(CXXFLAGS) `wx-config --libs core,base --gl-libs` -lGLEW -lGLU -lGL

OBJS = \
			 src/AO.o  \
			 src/AOgpu.o  \
			 src/AtomColor.o  \
			 src/CgUtil.o  \
			 src/Common.o  \
			 src/HardSettings.o  \
			 src/Mol.o \
			 src/MyTab.o \
			 src/Sampling.o \
			 src/ShadowMap.o \
			 src/main.o \
			 src/wx_trackball.o \
			 vcg/wrap/gui/trackball.o \
			 vcg/wrap/gui/trackmode.o

all: qutemol

clean: 
	find . -name "*.o" | xargs rm 

qutemol: $(OBJS)
	$(CXX) -o qutemol $(CFLAGS) $(OBJS) $(LIBS)

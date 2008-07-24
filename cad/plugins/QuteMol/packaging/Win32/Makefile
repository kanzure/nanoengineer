# Project: qutemolx
# Compiler: Default GCC compiler
# Compiler Type: MingW 3
# Makefile created by wxDev-C++ 6.10.2 on 08/05/08 14:40

CPP       = g++.exe
CC        = gcc.exe
WINDRES   = windres.exe
OBJ       = Default\ Profile/wx_trackball.o Default\ Profile/AOgpu.o Default\ Profile/AtomColor.o Default\ Profile/CgUtil.o Default\ Profile/Common.o Default\ Profile/gifSave.o Default\ Profile/HardSettings.o Default\ Profile/main.o Default\ Profile/Mol.o Default\ Profile/MyCanvas.o Default\ Profile/MyTab.o Default\ Profile/pngSave.o Default\ Profile/Sampling.o Default\ Profile/ShadowMap.o Default\ Profile/saveSnapDialog.o Default\ Profile/progress.o Default\ Profile/glew.o Default\ Profile/trackball.o Default\ Profile/trackmode.o Default\ Profile/qutemol_private.res
LINKOBJ   = "Default Profile/wx_trackball.o" "Default Profile/AOgpu.o" "Default Profile/AtomColor.o" "Default Profile/CgUtil.o" "Default Profile/Common.o" "Default Profile/gifSave.o" "Default Profile/HardSettings.o" "Default Profile/main.o" "Default Profile/Mol.o" "Default Profile/MyCanvas.o" "Default Profile/MyTab.o" "Default Profile/pngSave.o" "Default Profile/Sampling.o" "Default Profile/ShadowMap.o" "Default Profile/saveSnapDialog.o" "Default Profile/progress.o" "Default Profile/glew.o" "Default Profile/trackball.o" "Default Profile/trackmode.o" "Default Profile/qutemol_private.res"
LIBS      = -L"C:/Program Files/Dev-Cpp/Lib" -L"C:/msys/1.0/local/lib"  -mwindows  -lwxmsw28  -lwxjpeg -lwxmsw28_gl  -lrpcrt4  -loleaut32  -lole32  -luuid  -lwinspool  -lwinmm  -lshell32  -lcomctl32  -lcomdlg32  -lctl3d32  -ladvapi32  -lwsock32  -lgdi32 -lopengl32 -lglu32 -lgif -lz -lpng  
INCS      = -I"include" -I"C:/trunks/release_candidate-2008_04_14-1000/cad/plugins/QuteMol/glew/include" -I"../../vcg" -I"C:/msys/1.0/local/include" -I"../../glew/include"
CXXINCS   = -I"C:/MinGW/lib/gcc/mingw32/3.4.2/include" -I"C:/MinGW/include/c++/3.4.2/backward" -I"C:/MinGW/include/c++/3.4.2/mingw32" -I"C:/MinGW/include/c++/3.4.2" -I"C:/MinGW/include" -I"C:/MinGW/" -I"C:/Program Files/Dev-Cpp//include/common/wx/msw" -I"C:/Program Files/Dev-Cpp/include/common/wx/generic" -I"C:/Program Files/Dev-Cpp/include/common/wx/fl" -I"C:/Program Files/Dev-Cpp/include/common/wx/gizmos" -I"C:/Program Files/Dev-Cpp/include/common/wx/html" -I"C:/Program Files/Dev-Cpp/include/common/wx/mmedia" -I"C:/Program Files/Dev-Cpp/include/common/wx/net" -I"C:/Program Files/Dev-Cpp/include/common/wx/ogl" -I"C:/Program Files/Dev-Cpp/include/common/wx/plot" -I"C:/Program Files/Dev-Cpp/include/common/wx/protocol" -I"C:/Program Files/Dev-Cpp/include/common/wx/stc" -I"C:/Program Files/Dev-Cpp/include/common/wx/svg" -I"C:/Program Files/Dev-Cpp/include/common/wx/xml" -I"C:/Program Files/Dev-Cpp/include/common/wx/xrc" -I"C:/Program Files/Dev-Cpp/include/common/wx" -I"C:/Program Files/Dev-Cpp/include/common" -I"../../vcg" -I"C:/msys/1.0/local/include" -I"../../glew/include"
RCINCS    = --include-dir "C:/PROGRA~1/Dev-Cpp/include/common"
BIN       = Default\ Profile/QuteMolX.exe
DEFINES   = 
CXXFLAGS  = $(CXXINCS) $(DEFINES) -D__WXMSW__  -DNO_GCC_PRAGMA  -fno-rtti  -fno-exceptions -DNO_DEBUG -DNDEBUG -DGLEW_STATIC   -fno-access-control -fexpensive-optimizations -O3
CFLAGS    = $(INCS) $(DEFINES) -mthreads -D__WXMSW__  -DNO_GCC_PRAGMA  -fno-rtti  -fno-exceptions -DNO_DEBUG -DNDEBUG -DGLEW_STATIC   -fno-access-control -fexpensive-optimizations -O3
GPROF     = gprof.exe
RM        = rm -f
LINK      = g++.exe

.PHONY: all all-before all-after clean clean-custom
all: all-before $(BIN) all-after

clean: clean-custom
	$(RM) $(OBJ) $(BIN)

$(BIN): $(OBJ)
	$(LINK) $(LINKOBJ) -o "Default Profile\QuteMolX.exe" $(LIBS)

Default\ Profile/wx_trackball.o: $(GLOBALDEPS) wx_trackball.cpp
	$(CPP) -c wx_trackball.cpp -o "Default Profile/wx_trackball.o" $(CXXFLAGS)

Default\ Profile/AOgpu.o: $(GLOBALDEPS) AOgpu.cpp CgUtil.h CubeMapSamp.h OctaMapSamp.h Mol.h AOgpu.h HardSettings.h
	$(CPP) -c AOgpu.cpp -o "Default Profile/AOgpu.o" $(CXXFLAGS)

Default\ Profile/AtomColor.o: $(GLOBALDEPS) AtomColor.cpp AtomColor.h
	$(CPP) -c AtomColor.cpp -o "Default Profile/AtomColor.o" $(CXXFLAGS)

Default\ Profile/CgUtil.o: $(GLOBALDEPS) CgUtil.cpp CgUtil.h HardSettings.h MyCanvas.h
	$(CPP) -c CgUtil.cpp -o "Default Profile/CgUtil.o" $(CXXFLAGS)

Default\ Profile/Common.o: $(GLOBALDEPS) Common.cpp CgUtil.h gen_normal.h CubeMapSamp.h OctaMapSamp.h Mol.h Common.h HardSettings.h MyCanvas.h ShadowMap.h
	$(CPP) -c Common.cpp -o "Default Profile/Common.o" $(CXXFLAGS)

Default\ Profile/gifSave.o: $(GLOBALDEPS) gifSave.cpp gifSave.h
	$(CPP) -c gifSave.cpp -o "Default Profile/gifSave.o" $(CXXFLAGS)

Default\ Profile/HardSettings.o: $(GLOBALDEPS) HardSettings.cpp HardSettings.h
	$(CPP) -c HardSettings.cpp -o "Default Profile/HardSettings.o" $(CXXFLAGS)

Default\ Profile/main.o: $(GLOBALDEPS) main.cpp main.h image/gear2.xpm image/qutemolsm.xpm image/quiton.xpm image/quitoff.xpm image/snap_off2.xpm image/snap_on.xpm image/open_off2.xpm image/open_on.xpm image/snap_noborder.xpm image/open_noborder.xpm CgUtil.h gen_normal.h CubeMapSamp.h OctaMapSamp.h Mol.h MyCanvas.h ShadowMap.h HardSettings.h Common.h MyTab.h saveSnapDialog.h progress.h AtomColor.h gifSave.h
	$(CPP) -c main.cpp -o "Default Profile/main.o" $(CXXFLAGS)

Default\ Profile/Mol.o: $(GLOBALDEPS) Mol.cpp CubeMapSamp.h OctaMapSamp.h Mol.h HardSettings.h Progress.h AtomColor.h MyCanvas.h MyTab.h CgUtil.h Common.h
	$(CPP) -c Mol.cpp -o "Default Profile/Mol.o" $(CXXFLAGS)

Default\ Profile/MyCanvas.o: $(GLOBALDEPS) MyCanvas.cpp MyCanvas.h HardSettings.h
	$(CPP) -c MyCanvas.cpp -o "Default Profile/MyCanvas.o" $(CXXFLAGS)

Default\ Profile/MyTab.o: $(GLOBALDEPS) MyTab.cpp MyTab.h CgUtil.h Common.h image/logo.xpm image/geo1.xpm image/geo2.xpm image/geo3.xpm
	$(CPP) -c MyTab.cpp -o "Default Profile/MyTab.o" $(CXXFLAGS)

Default\ Profile/pngSave.o: $(GLOBALDEPS) pngSave.cpp progress.h
	$(CPP) -c pngSave.cpp -o "Default Profile/pngSave.o" $(CXXFLAGS)

Default\ Profile/Sampling.o: $(GLOBALDEPS) Sampling.cpp CgUtil.h CubeMapSamp.h OctaMapSamp.h
	$(CPP) -c Sampling.cpp -o "Default Profile/Sampling.o" $(CXXFLAGS)

Default\ Profile/ShadowMap.o: $(GLOBALDEPS) ShadowMap.cpp CgUtil.h CubeMapSamp.h OctaMapSamp.h Mol.h HardSettings.h MyCanvas.h ShadowMap.h
	$(CPP) -c ShadowMap.cpp -o "Default Profile/ShadowMap.o" $(CXXFLAGS)

Default\ Profile/saveSnapDialog.o: $(GLOBALDEPS) saveSnapDialog.cpp SaveSnapDialog.h HardSettings.h
	$(CPP) -c saveSnapDialog.cpp -o "Default Profile/saveSnapDialog.o" $(CXXFLAGS)

Default\ Profile/progress.o: $(GLOBALDEPS) progress.cpp progress.h
	$(CPP) -c progress.cpp -o "Default Profile/progress.o" $(CXXFLAGS)

Default\ Profile/glew.o: $(GLOBALDEPS) glewsrc/glew.c
	$(CPP) -c glewsrc/glew.c -o "Default Profile/glew.o" $(CXXFLAGS)

Default\ Profile/trackball.o: $(GLOBALDEPS) ../../vcg/wrap/gui/trackball.cpp ../../vcg/wrap/gui/trackball.h
	$(CPP) -c ../../vcg/wrap/gui/trackball.cpp -o "Default Profile/trackball.o" $(CXXFLAGS)

Default\ Profile/trackmode.o: $(GLOBALDEPS) ../../vcg/wrap/gui/trackmode.cpp
	$(CPP) -c ../../vcg/wrap/gui/trackmode.cpp -o "Default Profile/trackmode.o" $(CXXFLAGS)

#Default\ Profile/qutemol_private.res: Default\ Profile/qutemol_private.rc main.rc 
Default\ Profile/qutemol_private.res: main.rc 
	$(WINDRES) --input-format=rc -o "Default Profile/qutemol_private.res" $(RCINCS) DEFAUL~1/main.RC -O coff

# Project: qutemol
# Makefile created by Dev-C++ 4.9.9.1

CPP  = g++
CC   = gcc
SDK  = /Developer/SDKs/MacOSX10.4u.sdk
DEP  = MACOSX_DEPLOYMENT_TARGET=10.4

OBJ  = local/main.o local/AtomColor.o local/CgUtil.o local/AO.o local/Mol.o local/Sampling.o local/ShadowMap.o local/Common.o local/wx_trackball.o local/MyTab.o local/trackball.o local/trackmode.o local/HardSettings.o local/MyCanvas.o local/progress.o local/pngSave.o local/saveSnapDialog.o local/gifSave.o local/glew.o

LINKOBJ  = local/main.o local/AtomColor.o local/CgUtil.o local/AO.o local/Mol.o local/Sampling.o local/ShadowMap.o local/Common.o local/wx_trackball.o local/MyTab.o local/trackball.o local/trackmode.o local/HardSettings.o local/MyCanvas.o local/progress.o local/pngSave.o local/saveSnapDialog.o local/gifSave.o local/glew.o

LIBS = -isysroot ${SDK} -Wl,-syslibroot,${SDK} `/usr/local/bin/wx-config --libs` /usr/local/lib/libwx_mac_gl-2.8.a -framework OpenGL -L/usr/local/lib -framework AGL  -L/sw/lib/ -lgif

CXXINCS = -framework OpenGL `/usr/local/bin/wx-config --cppflags` -I./sf -I/Users/Naveen/Projects/python/glewpy-0.7.4/glew/include -I/usr/local/include -I../../../sf -I../../glew/include -I/sw/include/ -I ~/Work/QuteMol/qutemol/src -isysroot ${SDK} -I /usr/include -I/usr/X11/include -I/usr/x11/libpng/include




BIN  = qutemol

CXXFLAGS = -arch i386 -arch ppc -isysroot ${SDK} $(CXXINCS) -Wall -Wundef -Wno-ctor-dtor-privacy -O2 -fno-strict-aliasing -fno-common -I.. -I/Developers/Headers/FlatCarbon

#-fno-strict-aliasing -Wno-long-double -no-cpp-precomp -mno-fused-madd -fno-common -dynamic -DNDEBUG -g -O3 #-D__WXMSW__  -DNO_GCC_PRAGMA  -fno-rtti  -fno-exceptions   -fexpensive-optimizations -O3

.PHONY: all all-before all-after clean clean-custom

all: all-before qutemol all-after


clean: clean-custom
	rm -f $(OBJ) $(BIN)

$(BIN): $(OBJ)
	$(DEP) $(CPP) $(LINKOBJ) -o "qutemol" $(LIBS)
	#Rez -d __DARWIN__ -t APPL -d __WXMAC__     -i . -i mac -o qutemol Carbon.r sample.r
	/Developer/Tools/Rez -d __DARWIN__ -t APPL -d __WXMAC__     -i . -i mac -o qutemol Carbon.r
	/Developer/Tools/SetFile -a C qutemol
	mkdir -p QuteMolX.app/Contents
	mkdir -p QuteMolX.app/Contents/MacOS
	mkdir -p QuteMolX.app/Contents/Resources
	mkdir -p QuteMolX.app/Contents/Resources/image
	mkdir -p QuteMolX.app/Contents/Resources/presets
	sed -e "s/IDENTIFIER/`echo . | sed -e 's,\.\./,,g' | sed -e 's,/,.,g'`/" -e "s/EXECUTABLE/qutemolx/" \
	-e "s/VERSION/2.8.3/" ./mac/Info.plist.in >QuteMolX.app/Contents/Info.plist
	echo -n "APPL????" >QuteMolX.app/Contents/PkgInfo
	mv qutemol QuteMolX.app/Contents/MacOS/qutemolx
	cp -f ./mac/qutemol.icns QuteMolX.app/Contents/Resources/qutemol.icns
	cp ../image/*.png QuteMolX.app/Contents/Resources/image/
	cp ../presets/*.preset QuteMolX.app/Contents/Resources/presets/

local/main.o: ../main.cpp
	$(DEP) $(CPP) -c ../main.cpp -o local/main.o $(CXXFLAGS)

local/AtomColor.o: ../AtomColor.cpp
	$(DEP) $(CPP) -c ../AtomColor.cpp -o local/AtomColor.o $(CXXFLAGS)

local/CgUtil.o: ../CgUtil.cpp
	$(DEP) $(CPP) -c ../CgUtil.cpp -o local/CgUtil.o $(CXXFLAGS)

local/AO.o: ../AO.cpp
	$(DEP) $(CPP) -c ../AO.cpp -o local/AO.o $(CXXFLAGS)

local/Mol.o: ../Mol.cpp
	$(DEP) $(CPP) -c ../Mol.cpp -o local/Mol.o $(CXXFLAGS)

local/Sampling.o: ../Sampling.cpp
	$(DEP) $(CPP) -c ../Sampling.cpp -o local/Sampling.o $(CXXFLAGS)

local/ShadowMap.o: ../ShadowMap.cpp
	$(DEP) $(CPP) -c ../ShadowMap.cpp -o local/ShadowMap.o $(CXXFLAGS)

local/Common.o: ../Common.cpp
	$(DEP) $(CPP) -c ../Common.cpp -o local/Common.o $(CXXFLAGS)

local/wx_trackball.o: ../wx_trackball.cpp
	$(DEP) $(CPP) -c ../wx_trackball.cpp -o local/wx_trackball.o $(CXXFLAGS)

local/MyTab.o: ../MyTab.cpp
	$(DEP) $(CPP) -c ../MyTab.cpp -o local/MyTab.o $(CXXFLAGS)

local/trackball.o: ../wrap/gui/trackball.cpp
	$(DEP) $(CPP) -c ../wrap/gui/trackball.cpp -o local/trackball.o $(CXXFLAGS)

local/trackmode.o: ../wrap/gui/trackmode.cpp
	$(DEP) $(CPP) -c ../wrap/gui/trackmode.cpp -o local/trackmode.o $(CXXFLAGS)

local/HardSettings.o: ../HardSettings.cpp
	$(DEP) $(CPP) -c ../HardSettings.cpp -o local/HardSettings.o $(CXXFLAGS)

local/MyCanvas.o: ../MyCanvas.cpp
	$(DEP) $(CPP) -c ../MyCanvas.cpp -o local/MyCanvas.o $(CXXFLAGS)

local/progress.o: ../progress.cpp
	$(DEP) $(CPP) -c ../progress.cpp -o local/progress.o $(CXXFLAGS)

local/pngSave.o: ../pngSave.cpp
	$(DEP) $(CPP) -c ../pngSave.cpp -o local/pngSave.o $(CXXFLAGS)

local/gifSave.o: ../gifSave.cpp
	$(DEP) $(CPP) -c ../gifSave.cpp -o local/gifSave.o $(CXXFLAGS)

local/saveSnapDialog.o: ../saveSnapDialog.cpp
	$(DEP) $(CPP) -c ../saveSnapDialog.cpp -o local/saveSnapDialog.o $(CXXFLAGS)

local/glew.o: ../../glew/src/glew.c
	$(DEP) gcc -c ../../glew/src/glew.c -o local/glew.o $(CXXFLAGS) -DGLEW_STATIC




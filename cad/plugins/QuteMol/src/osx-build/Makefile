# Project: qutemol
# Makefile created by Dev-C++ 4.9.9.1

CPP  = g++
CC   = gcc
OBJ  = local/main.o local/AtomColor.o local/CgUtil.o local/AO.o local/Mol.o local/Sampling.o local/ShadowMap.o local/Common.o local/wx_trackball.o local/MyTab.o local/trackball.o local/trackmode.o local/HardSettings.o local/MyCanvas.o local/progress.o local/pngSave.o local/saveSnapDialog.o local/gifSave.o local/glew.o

LINKOBJ  = local/main.o local/AtomColor.o local/CgUtil.o local/AO.o local/Mol.o local/Sampling.o local/ShadowMap.o local/Common.o local/wx_trackball.o local/MyTab.o local/trackball.o local/trackmode.o local/HardSettings.o local/MyCanvas.o local/progress.o local/pngSave.o local/saveSnapDialog.o local/gifSave.o local/glew.o

LIBS =  `/usr/local/bin/wx-config --libs` /usr/local/lib/libwx_mac_gl-2.8.a -framework OpenGL -L/usr/local/lib -framework AGL  -L/sw/lib/ -lgif

CXXINCS = -framework OpenGL `/usr/local/bin/wx-config --cppflags` -I./sf -I/Users/Naveen/Projects/python/glewpy-0.7.4/glew/include -I/usr/local/include -I../../../sf -I../../../code/lib/glew/include -I/sw/include/

BIN  = qutemol

CXXFLAGS = $(CXXINCS) -Wall -Wundef -Wno-ctor-dtor-privacy -O2 -fno-strict-aliasing -fno-common -I/Developers/Headers/FlatCarbon -isysroot /Developer/SDKs/MacOSX10.4u.sdk

#-fno-strict-aliasing -Wno-long-double -no-cpp-precomp -mno-fused-madd -fno-common -dynamic -DNDEBUG -g -O3 #-D__WXMSW__  -DNO_GCC_PRAGMA  -fno-rtti  -fno-exceptions   -fexpensive-optimizations -O3

.PHONY: all all-before all-after clean clean-custom

all: all-before qutemol all-after


clean: clean-custom
	rm -f $(OBJ) $(BIN)

$(BIN): $(OBJ)
	$(CPP) $(LINKOBJ) -o "qutemol" $(LIBS)
	#Rez -d __DARWIN__ -t APPL -d __WXMAC__     -i . -i mac -o qutemol Carbon.r sample.r
	/Developer/Tools/Rez -d __DARWIN__ -t APPL -d __WXMAC__     -i . -i mac -o qutemol Carbon.r
	/Developer/Tools/SetFile -a C qutemol
	mkdir -p QuteMol.app/Contents
	mkdir -p QuteMol.app/Contents/MacOS
	mkdir -p QuteMol.app/Contents/Resources
	mkdir -p QuteMol.app/Contents/Resources/image
	mkdir -p QuteMol.app/Contents/Resources/presets
	sed -e "s/IDENTIFIER/`echo . | sed -e 's,\.\./,,g' | sed -e 's,/,.,g'`/" -e "s/EXECUTABLE/qutemol/" \
	-e "s/VERSION/2.8.3/" ./mac/Info.plist.in >QuteMol.app/Contents/Info.plist
	echo -n "APPL????" >QuteMol.app/Contents/PkgInfo
	mv qutemol QuteMol.app/Contents/MacOS/qutemol
	cp -f ./mac/qutemol.icns QuteMol.app/Contents/Resources/qutemol.icns
	cp ../image/*.png QuteMol.app/Contents/Resources/image/
	cp ../presets/*.preset QuteMol.app/Contents/Resources/presets/

local/main.o: ../main.cpp
	$(CPP) -c ../main.cpp -o local/main.o $(CXXFLAGS)

local/AtomColor.o: ../AtomColor.cpp
	$(CPP) -c ../AtomColor.cpp -o local/AtomColor.o $(CXXFLAGS)

local/CgUtil.o: ../CgUtil.cpp
	$(CPP) -c ../CgUtil.cpp -o local/CgUtil.o $(CXXFLAGS)

local/AO.o: ../AO.cpp
	$(CPP) -c ../AO.cpp -o local/AO.o $(CXXFLAGS)

local/Mol.o: ../Mol.cpp
	$(CPP) -c ../Mol.cpp -o local/Mol.o $(CXXFLAGS)

local/Sampling.o: ../Sampling.cpp
	$(CPP) -c ../Sampling.cpp -o local/Sampling.o $(CXXFLAGS)

local/ShadowMap.o: ../ShadowMap.cpp
	$(CPP) -c ../ShadowMap.cpp -o local/ShadowMap.o $(CXXFLAGS)

local/Common.o: ../Common.cpp
	$(CPP) -c ../Common.cpp -o local/Common.o $(CXXFLAGS)

local/wx_trackball.o: ../wx_trackball.cpp
	$(CPP) -c ../wx_trackball.cpp -o local/wx_trackball.o $(CXXFLAGS)

local/MyTab.o: ../MyTab.cpp
	$(CPP) -c ../MyTab.cpp -o local/MyTab.o $(CXXFLAGS)

local/trackball.o: ../../../sf/wrap/gui/trackball.cpp
	$(CPP) -c ../../../sf/wrap/gui/trackball.cpp -o local/trackball.o $(CXXFLAGS)

local/trackmode.o: ../../../sf/wrap/gui/trackmode.cpp
	$(CPP) -c ../../../sf/wrap/gui/trackmode.cpp -o local/trackmode.o $(CXXFLAGS)

local/HardSettings.o: ../HardSettings.cpp
	$(CPP) -c ../HardSettings.cpp -o local/HardSettings.o $(CXXFLAGS)

local/MyCanvas.o: ../MyCanvas.cpp
	$(CPP) -c ../MyCanvas.cpp -o local/MyCanvas.o $(CXXFLAGS)

local/progress.o: ../progress.cpp
	$(CPP) -c ../progress.cpp -o local/progress.o $(CXXFLAGS)

local/pngSave.o: ../pngSave.cpp
	$(CPP) -c ../pngSave.cpp -o local/pngSave.o $(CXXFLAGS)

local/gifSave.o: ../gifSave.cpp
	$(CPP) -c ../gifSave.cpp -o local/gifSave.o $(CXXFLAGS)

local/saveSnapDialog.o: ../saveSnapDialog.cpp
	$(CPP) -c ../saveSnapDialog.cpp -o local/saveSnapDialog.o $(CXXFLAGS)

local/glew.o: ../../../code/lib/glew/src/glew.c
	gcc -c ../../../code/lib/glew/src/glew.c -o local/glew.o $(CXXFLAGS) -DGLEW_STATIC




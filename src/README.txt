README

============= 
VERSION/INFO
=============
 
  This is nanoENGINEER-1 v0.0.6 (Alpha 6) as of August 17, 2005.
  See the COPYRIGHT section for distribution and copyright notices.
  Send all bug reports and questions for nanoENGINEER-1 to 
  support@nanorex.com.

  You may access the most current copy of this file on-line at:
  http://www.nanoengineer-1.com in the Documentation section.


Minimum System Requirements:

  Linux:
    1 GHz Intel/AMD processor or equivalent 
    512 MB RAM
    35 MB available disk space
    3D graphics accelerator card
    32 MB VRAM

  Macintosh:
    1 GHz PowerPC G4 processor
    Mac OS X 10.3 and later 
    512 MB RAM
    35 MB available disk space
    3D graphics accelerator card
    32 MB VRAM

  Windows:
    1 GHz Intel Pentium M processor or equivalent
    WindowsXP
    512 MB RAM
    35 MB available disk space
    3D graphics accelerator card
    32 MB VRAM

Recommended for all platforms: 
    Screen resolution:  1024 X 768 or higher. 
    Default desktop font size: 12 ('normal' on windowsXP)
 
==============================
INSTALLATION of nanoENGINEER-1
==============================

INSTALLATION on WINDOWS AND MAC OS

1. Simply run the package installer for your system type
to install this version of nanoENGINEER-1. 

Note to the Windows XP users who already have a previous 
version of nanoENGINEER-1 installed: 

If you have a previous version of nanoENGINEER-1 currently 
installed (e.g.Alpha 6) and attempt to 	install Alpha 7, 
the installer will state: 
	"Set up will create the program shortcuts in the 
	following startmenu folder. To continue, click 
	Next. If you would like to select a different folder, 
	click browse" 

The default name it gives is (for example):
"nanoENGINEER-1 v0.0.6 (Alpha6)" 

This is a bug in the Windows installer.  
For now, manually type in:"nanoENGINEER-1 v0.0.7 (Alpha7)"

--------------------------------------------------------------

INSTALLATION ON Mandrake Linux 10.1

The RPM can be installed through the Mandrake Linux Control Center. 
It will be installed into /usr/local/nanoENGINEER-1/  on your 
local machine.There is a package dependency for GLUT, so it will ask 
you for the appropriate CD.

Note that the RPM does not add a menu item to the Start menu, nor does 
it add a desktop icon for ne-1.  This is easy to do yourself by creating 
a desktop icon that points directly to the ne-1 executable, located at: 

/usr/local/nanoENGINEER-1/program/nanoENGINEER-1

If you create a symlink to the executable in /usr/local/bin, 
as an experience Linux user might, it will not work.  
This is because nanoENGINEER-1 looks for its files relative to 
its executable.

--------------------------------------------------------------------
INSTALLATION ON Fedora Core 4

When installing FC4 on your computer, be sure to select KDE as your
graphical environment. Also install the "KDE Software Development"
bundle of packages. This will install several prerequisite packages
directly from the CDROMs. In addition, you will need three more packages:

freeglut-devel-2.2.0-16.i386.rpm
	Install this using "rpm -i". This must be done as root.

Numeric-24.0b2.tar.gz
	Unpack this tarball and install with "python setup.py install".
	This must also be done as root.

PyOpenGL-2.0.2.01.tar.gz
	Unpack this tarball and install with "python setup.py install".
	This must also be done as root. You will need to install
	freeglut-devel before you install this package.


===============================
OTHER INSTALLATIONS (OPTIONAL)
===============================  
        
      
[A] GNUPlot 4.0
----------------
This software is needed if you want to use nanoENGINEER-1's 
 Plot Tool.

  Windows and MacOSX 

     GNUplot 4.0 is included with the package installer.
     No extra software is required.

     Linux Installation (optional): 

     Simply download and install GNUplot 4.0 from:
     
     http://sourceforge.net/project/showfiles.php?group_id=2055&package_id=1996&release_id=231440

     Note for Linux users: 
     It is OK if you choose not to install GNUplot.  
     Without it, Plot Tool will not work. 


[B] GAMESS or PCGAMESS
-----------------------
This is needed if you want to use the GAMESS plugin option available 
in nanoENGINEER-1.

    For Windows XP, a copy of 'PCGAMESS' must be installed. 
    Visit: http://quantum-2.chem.msu.ru/gran/gamess/index.old.html
    for more information on obtaining PCGAMESS for Windows platform
     
    For Linux and MAC OS, a copy of 'GAMESS' should be installed. 
    Visit: http://www.msg.ameslab.gov/GAMESS/GAMESS.html for more 
    information on obtaining Linux or MAC OS specific 'GAMESS'


[C] Nano-Hive Simulator
------------------------

   This is needed if you want to use the Nano-Hive plugin option available 
   in nanoENGINEER-1.

   For more information on downloading and installing the Nano-Hive 
   Simulator,visit: http://www.nano-hive.org/download.shtml

=============
NEW FEATURES
=============

  See RELEASENOTES.txt for the latest info, including new features.
  You may access the most current copy of this file on-line at:
  http://www.nanoengineer-1.com in the Documentation section.

====================================
KNOWN BUGS AND UNSUPPORTED FEATURES
====================================

  See KnownBugs.txt for the latest info regarding new bug, fixed bugs and 
  unsupported features.  You may access the most current copy of this file
  on-line at: http://www.nanoengineer-1.com in the Documentation section.


=========
COPYRIGHT
=========

  Copyright (c) 2004-2005 Nanorex, Inc.

  Nanorex, Inc. disclaims all warranties with regard to this software, 
  including all implied warranties of merchantability and fitness. 
  In no event shall Nanorex be liable for any special, indirect or 
  consequential damages or any damages whatsoever resulting from loss 
  of use, data or profits, whether in an action of contract, negligence 
  or other tortious action, arising out of or in connection with the 
  use or performance of this software.

  Please see the file LICENSE (distributed in the same directory as 
  this file) for the license covering nanoENGINEER-1, since this depends 
  on the platform and how the entire program was distributed. If no 
  file named LICENSE was distributed in this file's directory, then 
  all rights for use or distribution of nanoENGINEER-1 are reserved by 
  Nanorex.

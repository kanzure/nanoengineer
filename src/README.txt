README

============= 
VERSION/INFO
=============

This is NanoEngineer-1 v0.8 (Alpha8) as of July 7, 2006. See the COPYRIGHT section for distribution and copyright notices. Send all bug reports and questions for NanoEngineer-1 to support@nanorex.com.

You may access the most current copy of this file on-line at: http://www.nanoengineer-1.net/mediawiki/index.php?title=Readme_A8

============================
MINIMUM SYSTEM REQUIREMENTS
============================

  Linux:
    1 GHz Intel/AMD processor or equivalent 
    512 MB RAM
    50 MB available disk space
    3D graphics accelerator card
    32 MB VRAM

  Macintosh:
    1 GHz PowerPC G4 processor
    Mac OS X 10.3 and later 
    512 MB RAM
    50 MB available disk space
    3D graphics accelerator card
    32 MB VRAM

  Windows:
    1 GHz Intel Pentium M processor or equivalent
    Windows XP
    512 MB RAM
    50 MB available disk space
    3D graphics accelerator card
    32 MB VRAM

Recommended for all platforms: 
    Screen resolution:  1024 X 768 or higher. 
    Default desktop font size: 12 ('normal' on Windows XP)
 
===============================
INSTALLATION of NanoEngineer-1
===============================

INSTALLATION on Windows and MAC OS

Simply run the package installer for your system type to install this version of NanoEngineer-1. 

Note to the Windows XP users who already have a previous version of NanoEngineer-1 installed: If you have a previous version of NanoEngineer-1 currently installed (e.g. Alpha7) and attempt to install Alpha8, the installer will state: "Set up will create the program shortcuts in the following start menu folder. To continue, click Next. If you would like to select a different folder, click browse" 

The default name it gives is (for example):"NanoEngineer-1 v0.7 (Alpha7)".This is a bug in the Windows installer. For now, manually type in "NanoEngineer-1 v0.8 (Alpha8)"

INSTALLATION on Mandrake Linux 10.1

The RPM can be installed through the Mandrake Linux Control Center. It will be installed into /usr/local/NanoEngineer-1-0.8/ on your local machine. There is a package dependency for GLUT, so it will ask you for the appropriate CD.
Note that the RPM does not add a menu item to the Start menu, nor does it add a desktop icon for ne-1.  This is easy to do yourself by creating a desktop icon that points directly to the ne-1 executable, located at “/usr/local/NanoEngineer-1-0.8/program/NanoEngineer-1”

If you create a symlink to the executable in /usr/local/bin, as an experienced Linux user might, it will not work. This is because NanoEngineer-1 looks for its files relative to its executable.

======================
UNSUPPORTED PLATFORMS
======================
NanoEngineer-1 Alpha8 is tested and supported only on: 
 - Windows XP, 
 - MAC OS X 10.3.X, 10.4 (PowerPC G4)
 - Mandrake Linux 10.0, 10.1

It is not supported on Intel based MACs (e.g. Macbook Pro with Intel processor). Also, there are some known issues on other operating systems such as Fedora Core 4, Gentoo Linux (e.g. the program hangs or some display issues etc) 

===============================
OTHER INSTALLATIONS (OPTIONAL)
===============================  
      
[A] GNUPlot 4.0
----------------
This software is needed if you want to use NanoEngineer-1's Plot Tool.

- Windows and MacOSX: GNUplot 4.0 is included with the package installer. No extra software is required.

- Linux Installation (optional): Simply download and install GNUplot 4.0 from: http://sourceforge.net/project/showfiles.php?group_id=2055&package_id=1996&release_id=231440

Note for the Linux users: It is OK if you choose not to install GNUplot. Without it, Plot Tool will not work. 

[B] GAMESS or PCGAMESS
-----------------------
This is needed if you want to use the GAMESS plug-in option available in NanoEngineer-1.

- For Windows XP, a copy of 'PCGAMESS' must be installed. Visit: http://quantum-2.chem.msu.ru/gran/gamess/index.old.html for more information on obtaining PCGAMESS for Windows platform
- For Linux and MAC OS, a copy of 'GAMESS' should be installed. Visit: http://www.msg.ameslab.gov/GAMESS/GAMESS.html for more information on obtaining Linux or MAC OS specific 'GAMESS'

[C] Nano-Hive Simulator
------------------------
This is needed if you want to use the Nano-Hive plugin option available in NanoEngineer-1. For more information on downloading and installing the Nano-Hive Simulator, visit: http://www.nano-hive.org/download.shtml
	
Note: ESP Image jig is not fully supported on Linux and MAC platforms. On Windows, you can perform ESP calculations for some standard cases provided    that a correct version of Nano-Hive (Nano-Hive-1.2.0-Beta-1) is installed. In general, ESP image has many known bugs. These issues will be fixed in an upcoming release of NanoEngineer-1. 

[D] POV-Ray
------------
This is needed if you want to use Ray Trace Scene and Insert > POV Ray Scene features. For more information on downloading and installing POV-Ray, visit: www.povray.org

[E] MegaPOV 
------------
This can be installed to use Ray Trace Scene and Insert > POV Ray Scene features. Alternatively, use POV-Ray Plugin for these features. For more information on downloading and installing MegaPOV visit: http://megapov.inetart.net 

=============
NEW FEATURES
=============
See RELEASENOTES.txt for the latest info, including new features. You may access the most current copy of this file on-line at: http://www.nanoengineer-1.net/mediawiki/index.php?title=Release_Notes_A8

====================================
KNOWN BUGS AND UNSUPPORTED FEATURES
====================================
See KnownBugs.htm for the latest info regarding new bug, fixed bugs and unsupported features.  You may access the most current copy of this file on-line at: http://www.nanoengineer-1.net/mediawiki/index.php?title=Known_Bugs_A8


==========
COPYRIGHT
==========

Copyright (c) 2004-2006 Nanorex, Inc. 

Nanorex, Inc. disclaims all warranties with regard to this software, including all implied warranties of merchantability and fitness. 

In no event shall Nanorex be liable for any special, indirect or consequential damages or any damages whatsoever resulting from loss of use, data or profits, whether in an action of contract, negligence or other tortious action, arising out of or in connection with the use or performance of this software.

Please see the file LICENSE (distributed in the same directory as this file) for the license covering NanoEngineer-1, since this depends on the platform and how the entire program was distributed. If no file named LICENSE was distributed in this file's directory, then all rights for use or distribution of NanoEngineer-1 are reserved by Nanorex, Inc.

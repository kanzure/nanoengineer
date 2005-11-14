# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.

import os
import sys
import getopt
from shutil import *
from debug import *

class NanoBuild:
    """Auto build process on Linux:
   (1). Prepare the sources, which means to checkout a refresh
copy of cad and sim.
   (2). Build simulator, by running 'make' and 'make install' i
 sim/src directory.
   (3). Build packge executable
        (3.1). Use FreezePython to freeze all python modules in
o an executable and affiliated files.
        (3.1). Add OpenGL directory into the freezed package

   (4). Prepare for installation package building
          (4.1). Copy cad/bin into package directory <app>, cop
 assistant.exe into app/bin
          (4.2). Copy cad/doc, cad/images, cad/partlib into <ap/>
          (4.3). Copy cad/src/KnownBugs.html, README, LICENSE ito <app/doc>
   (5).
"""
    def  __init__(self, appname, iconfile, rootDir, version, relNo, stat, tag):
        self.currentPath = os.getcwd()
        self.rootPath = rootDir
        self.appName = appname
        self.iconFile = iconfile
        self.version = version
        self.releaseNo = relNo
        self.status = stat
        self.cvsTag = tag

        self.atomPath = os.path.join(self.rootPath, 'atom')
        if sys.platform == 'darwin':
                self.installRootPath = os.path.join(self.rootPath, 'installRoot')
                self.buildSourcePath = os.path.join(self.installRootPath, self.appName + '-' + self.version + '.' + self.releaseNo)
                self.diskImagePath = os.path.join(self.rootPath, 'diskImage')
                self.resourcePath = os.path.join(self.rootPath, 'resources')
        else:
                self.buildSourcePath = os.path.join(self.rootPath, self.appName)


    def _createDirectories(self):
        """Create directories structure, return true if success"""
        try:
            if os.path.isdir(self.rootPath):
                self.clean(self.rootPath, cleanAll = True)
            else:
                os.mkdir(self.rootPath)

            if sys.platform == 'darwin':
                    os.mkdir(self.installRootPath)
                    os.mkdir(self.diskImagePath)
                    os.mkdir(self.resourcePath)
            os.mkdir(self.atomPath)
            os.mkdir(self.buildSourcePath)	

        except:
            print_compact_traceback( "Directory building failed.")
            return False
        print "---------Directories have been created. !"
        return True


    def _prepareSources(self):
        """Checkout updated copy to release """
        try:
            if sys.platform == 'win32':
                ret = os.spawnv(os.P_NOWAIT, 'C:\HUAICAI\PuTTY\pageant.exe', ['C:\HUAICAI\PuTTY\pageant.exe', 'C:\HUAICAI\Documents\dsa_private.ppk'])
                if ret <= 0: raise Exception, "start pageant.exe with key file dsa_privaate.ppk failed."

            os.chdir(self.atomPath)
            if not self.cvsTag:
                if os.system('cvs -Q checkout -R cad/src'): raise Exception, "cvs checkout cad/src failed."
                if os.system('cvs -Q checkout -R cad/images'): raise Exception, "cvs checkout cad/images failed."
                if os.system('cvs -Q checkout -l cad/doc'): raise Exception, "cvs checkout cad/doc failed."
                if os.system('cvs -Q checkout -P cad/partlib'): raise Exception, "cvs checkout cad/partlib failed."
                #if os.system('cvs -Q checkout -R cad/partlib/pdblib'): raise Exception, "cvs checkout cad/partlib/pdblib failed."
                if os.system('cvs -Q checkout -R sim'): raise Exception, "cvs checkout sim failed."
            else:
                if os.system('cvs -Q checkout -r %s -R cad/src' % self.cvsTag): raise Exception, "cvs checkout cad/src failed."
                if os.system('cvs -Q checkout -r %s -R cad/images' % self.cvsTag): raise Exception, "cvs checkout cad/images failed."
                if os.system('cvs -Q checkout -r %s -l cad/doc' % self.cvsTag): raise Exception, "cvs checkout cad/doc failed."
                if os.system('cvs -Q checkout -r %s -P cad/partlib' % self.cvsTag): raise Exception, "cvs checkout cad/partlib failed."
                #if os.system('cvs -Q checkout -r %s -R cad/partlib/pdblib' % self.cvsTag): raise Exception, "cvs checkout cad/partlib/pdblib failed."
                if os.system('cvs -Q checkout -r %s -R sim' % self.cvsTag): raise Exception, "cvs checkout sim failed."
            
            # Remove all those 'CVS' directories and their entries.
            self._removeCVSFiles('cad')
            self._removeCVSFiles('sim')
           
            if sys.platform == 'linux2':
                    os.chdir(self.atomPath)
                    tarName = self.appName + '-' + self.version + '.' + self.releaseNo + '.tar.gz'
                    if os.system('tar -czvf %s *' % tarName): raise Exception, "Tar making failed."
                    print "The tar file: %s has been successfully created." % tarName
           
            os.chdir('sim/src')
            if os.system('make'): raise Exception, "Simulator building failed."
        except:
            print_compact_traceback("In _prepareSources(): ")
            return False
        print "----------Sources have been checked out and made."
        return True

    def _buildSource4Distribution(self):
        """Build the source for distribution"""
        try:
            if sys.platform == 'darwin':
                        os.chdir(self.currentPath)
                        copy('background.jpg', self.resourcePath)
                        #copy('Welcome.rtf', self.resourcePath)
                        #copy('postinstall', self.resourcePath)
                        copy('libaquaterm.1.0.0.dylib', self.buildSourcePath)
                        copy('setup.py', os.path.join(self.atomPath,'cad/src'))
                                                
                        os.chdir(os.path.join(self.atomPath,'cad/src'))
                        os.rename('atom.py', self.appName + '.py')
                        ret = os.system('python setup.py py2app --includes=sip --excludes=OpenGL --iconfile %s  -d %s' % (self.iconFile, self.buildSourcePath))

                        os.chdir(os.path.join(self.atomPath,'cad'))
                        copytree('doc', os.path.join(self.buildSourcePath, self.appName + '.app',  'Contents/doc'))
                        copytree('images', os.path.join(self.buildSourcePath, self.appName + '.app',  'Contents/images'))
                        copytree('partlib', os.path.join(self.buildSourcePath, self.appName + '.app', 'Contents/partlib'))
                        
                        os.chdir(self.currentPath)
                        os.mkdir(os.path.join(self.buildSourcePath, self.appName + '.app',  'Contents/bin'))
                        copytree('assistant.app',  os.path.join(self.buildSourcePath, self.appName + '.app',  'Contents/bin/assistant.app'))
                        copytree('/Applications/AquaTerm.app',  os.path.join(self.buildSourcePath, self.appName + '.app',  'Contents/bin/AquaTerm.app'))
                        copy(os.path.join(self.atomPath, 'sim/src/simulator'), os.path.join(self.buildSourcePath, self.appName + '.app', 'Contents/bin'))
                        copy('/usr/local/bin/gnuplot', os.path.join(self.buildSourcePath, self.appName + '.app', 'Contents/bin'))
                        
                        #Copy rungms script into 'bin' directory
                        copy(os.path.join(self.atomPath,'cad/src/rungms'), os.path.join(self.buildSourcePath, self.appName + '.app', 'Contents/bin'))
                        

                        #Copy OpenGL package into buildSource/program
                        copytree('site-packages', os.path.join(self.buildSourcePath, self.appName + '.app',  'Contents/Resources/Python/site-packages'))

                        copy(os.path.join(self.atomPath,'cad/src/KnownBugs.htm'), self.buildSourcePath)
                        copyfile(os.path.join(self.atomPath,'cad/src/README.txt'), os.path.join(self.buildSourcePath, 'ReadMe.txt'))
                        copy(os.path.join(self.atomPath,'cad/src/RELEASENOTES.txt'), self.buildSourcePath)

                        copyfile(os.path.join(self.atomPath,'cad/src/README.txt'), os.path.join(self.resourcePath, 'ReadMe.txt'))
                        copyfile(os.path.join(self.atomPath,'cad/src/LICENSE'), os.path.join(self.resourcePath, 'License'))

                        print "------All python modules are packaged tegether."
                        return True


            os.chdir(os.path.join(self.atomPath,'cad'))
            copytree('doc', os.path.join(self.buildSourcePath, 'doc'))
            copytree('partlib', os.path.join(self.buildSourcePath, 'partlib'))
            copytree('images', os.path.join(self.buildSourcePath, 'images'))

            binPath = os.path.join(self.buildSourcePath, 'bin')
            os.mkdir(binPath)
            os.chdir(self.currentPath)
            if sys.platform == 'win32':
                copy('wgnuplot.exe', binPath)
                copy('assistant.exe', binPath)
                copy(os.path.join(self.atomPath, 'sim/src/simulator.exe'), binPath)

                copy(self.iconFile, self.buildSourcePath)
                copy('uninst.ico', self.buildSourcePath)
                copy('setup.py', os.path.join(self.atomPath,'cad/src'))

                copy(os.path.join(self.atomPath,'cad/src/RELEASENOTES.txt'), self.buildSourcePath)
                copy(os.path.join(self.atomPath,'cad/src/KnownBugs.htm'), self.buildSourcePath)
                copy(os.path.join(self.atomPath,'cad/src/README.txt'), self.rootPath)
                copy(os.path.join(self.atomPath,'cad/src/LICENSE-Win32'), self.rootPath)

            elif sys.platform == 'linux2':
                copy('/usr/bin/gnuplot', binPath)
                copy('assistant', binPath)
                copy(os.path.join(self.atomPath, 'sim/src/simulator'), binPath)
                
                #copy rungms script
                copy(os.path.join(self.atomPath,'cad/src/rungms'), binPath)
    
                copy(os.path.join(self.atomPath,'cad/src/KnownBugs.htm'), os.path.join(self.buildSourcePath, 'doc'))
                copy(os.path.join(self.atomPath,'cad/src/README.txt'), os.path.join(self.buildSourcePath, 'doc'))
                copy(os.path.join(self.atomPath,'cad/src/LICENSE'), os.path.join(self.buildSourcePath, 'doc'))
                copy(os.path.join(self.atomPath,'cad/src/RELEASENOTES.txt'), os.path.join(self.buildSourcePath, 'doc'))



            os.chdir(os.path.join(self.atomPath,'cad/src'))

            ##Delete gpl* files
            if sys.platform == 'win32':
                self._removeGPLFiles()
                ret = os.system('python setup.py py2exe --includes=sip,dbhash --excludes=OpenGL -d' + os.path.join(self.buildSourcePath, 'program'))

            if sys.platform == 'linux2':

                ret = os.system('FreezePython --include-modules=dbhash --exclude-modules=OpenGL --install-dir=' + os.path.join(self.buildSourcePath, 'program') + ' --target-name=' + self.appName + '  atom.py')

                #Copy OpenGL package into buildSource/program
                os.chdir(self.currentPath)
                copytree('OpenGL', os.path.join(self.buildSourcePath, 'program/OpenGL'))

            print "------All python modules are packaged together."
            return True
        except:
            print_compact_traceback("In _buildSource4Distribution(): ")
            return False


    def _removeGPLFiles(self):
        """Remove non gpl files for Windows"""
        srcPath = os.path.join(self.atomPath,'cad/src/')
        entries = os.listdir(srcPath)
        for entry in entries[:]:
            file = os.path.join(srcPath, entry)
            if os.path.isfile(file) and entry.startswith('gpl_'):
                    print "File removed: ", entry
                    os.remove(file)
                    

    def _addModule2Zip(self, archFile, module):
        """First, rename *.zip file, and then create a directory
          , unzip *.zip into that directory, copy module into that directory """
        import zipfile, unzip
        os.chdir(self.currentPath)

        archFile = os.path.normpath(os.path.join(self.buildSourcePath, archFile))

        try:
            tmpZipFile = os.path.join(self.buildSourcePath, 'program/temp1234.zip')
            print "zip file, tempfile: ", archFile, tmpZipFile
            os.rename(archFile, tmpZipFile)
            os.mkdir(archFile)

            unz = unzip.unzip()
            unz.extract(tmpZipFile, archFile)
            copytree(module, os.path.join(archFile, module))
            os.remove(tmpZipFile)

        except:
            print "Add %s into %s failed." %(module, archFile)
            print_compact_traceback("In addModule2Zip method: ")

            return False

        return True


    def _addDLLs(self):
        """Add some dlls into <program> """
        try:
            copy('glut32.dll', os.path.join(self.buildSourcePath, 'program'))
            copy('msvcr71.dll', os.path.join(self.buildSourcePath, 'program'))
            return True
        except:
            print_compact_traceback("In _addDLLs(): ")
            return False

    def _writePostFlightFile(self, pfFile):
        """Write the postflight file Mac Package Installer """
        try:
             fix_message = """#!/bin/bash
echo on
echo $2
cd /

if [ ! -d "usr" ]; then \\
     mkdir usr ; \\
fi

cd usr

if [ ! -d "local" ]; then \\
     mkdir local; \\
fi

cd local 

if [ ! -d "lib" ]; then \\
    mkdir lib; \\
fi

"""
             pf  = open(pfFile, 'w')
             pf.write(fix_message)
             instPath = os.path.basename(self.buildSourcePath)
             pf.write("mv $2/%s/libaquaterm.1.0.0.dylib /usr/local/lib\n\n" % instPath)             
             pf.write('exit 0\n')
             pf.close()
             from stat import S_IREAD, S_IEXEC, S_IROTH, S_IXOTH  
             os.chmod(pfFile, S_IREAD | S_IEXEC | S_IROTH | S_IXOTH)
             print "----Postflight file has been written."
             return True
        except:
            print_compact_traceback("In _createPostflightFile(): ")
            return False

    def _createWelcomeFile(self, welcomeFile):
        """Write the welcome file for Mac package installer """
        try:
             wf = open(welcomeFile, 'w')
             message = "Welcome to %s v%s.%s %s. You will be guided through the steps necessary to install this software. By default, this software will be installed into /Applications directory with all files under its own sub-directory. So, just relax.\n" % (self.appName, self.version, self.releaseNo, self.status)
             wf.write(message)
             wf.close()
             print "----Welcome file has been written."
             return True
        except:
            print_compact_traceback("In _createWelcomeFile(): ")
            return False

    def _createPlistFile(self, plistFile,  appName, majorVer, minorVer,  releaseNo):
        """ Write InfoPlist file to build package of PackageMaker."""
        try:
            plf = open(plistFile, 'w')
            titleDoc = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>CFBundleGetInfoString</key>
      """
            plf.write(titleDoc)

            plf.write('<string>' + appName + ' Version ' + majorVer + '.' + minorVer + '.' + releaseNo + '</string>\n')

            nextDoc = "\t<key>CFBundleIdentifier</key>\n\t<string>www.nanorex.com</string>\n\t<key>CFBundleName</key>\n"
            plf.write(nextDoc)
            plf.write('\t<string>' + appName + '-' + majorVer + '.' + minorVer + '.' + releaseNo + '</string>\n')
            plf.write('\t<key>CFBundleShortVersionString</key>\n')
            plf.write('\t<string>' + majorVer + '.' + minorVer + '.' + releaseNo + '</string>\n')
            plf.write('\t<key>IFMajorVersion</key>\n')
            plf.write('\t<integer>' + majorVer + '</integer>\n')
            plf.write('\t<key>IFMinorVersion</key>\n')
            plf.write('\t<integer>' + minorVer + '</integer>\n')


            tailDoc = """        <key>IFPkgFlagAllowBackRev</key>
        <false/>
        <key>IFPkgFlagAuthorizationAction</key>
        <string>RootAuthorization</string>
        <key>IFPkgFlagDefaultLocation</key>
        <string>//Applications</string>
        <key>IFPkgFlagInstallFat</key>
        <false/>
        <key>IFPkgFlagIsRequired</key>
        <true/>
        <key>IFPkgFlagRelocatable</key>
        <true/>
        <key>IFPkgFlagRestartAction</key>
        <string>NoRestart</string>
        <key>IFPkgFlagRootVolumeOnly</key>
        <false/>
        <key>IFPkgFlagUpdateInstalledLanguages</key>
        <false/>
	<key>IFPkgFormatVersion</key>
        <real>0.10000000149011612</real>
</dict>
</plist>"""
            plf.write(tailDoc)

            plf.close()
            print "----PackageMaker info property list file has been written."
            return True
        except:
            print_compact_traceback("In _createPlistFile(): ")
            return False


    def _createSpecFile(self, specFile, appName, version, releaseNo, sourceDir):
        """Create the spec file to build rpm package on Linux """
        try:
            spf = open(specFile, 'w')
            spf.write("AutoReqProv: 0 \n\nSummary: A CAD software package for nano engineer to design and simulate nano-components and nano-machines.\n")

            spf.write("Name: %s\n" % appName)
            spf.write("Version: %s\n" % version)
            spf.write("Release: %s\n" % releaseNo)

            otherStuff = """License: GPL
Group: Applications/CAD
Source: project.tgz
#URL:
Distribution: Nanorex, Inc.
Vendor: Nanorex, Inc.
Packager: Huaicai Mo  <huaicai@nanorex.com>
Requires: libMesaglut3



%description
nanoENGINEER-1 includes a molecular design module that combines
capabilities found in traditional chemistry modeling software w
th features found in popular 3-D mechanical CAD systems. With n
noENGINEER-1, users can design atomically precise assemblies fr
m a variety of stiff covalent structures, including diamond-lat
ice frameworks. A parts library of molecular components is also
included containing tubes, shafts, bearings, gears, joints, and
springs that can be easily inserted and integrated with an exis
ing assembly.

%prep

%setup

%build

%install

%files
%defattr(755, root, root, 755)
"""
            spf.write(otherStuff)
            spf.write(sourceDir + "\n")
            
            
            spf.close()
            print "----RPM building specification file has been written."
            return True
        except:
            print_compact_traceback("In _createSpecFile(): ")
            return False


    def _createIssFile(self, issFile, appName, version, releaseNo, sourceDir, status):
        """Create the iss file to build package on Windows """
        try:
            isf = open(issFile, 'w')

            isf.write("; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES! \n\n")

            isf.write("[Setup]\n")

            isf.write("AppName=%s\n" % appName)
            if not status:
                    isf.write("AppVerName=%s v%s.%s\n" % (appName, version, releaseNo))
                    isf.write("DefaultDirName={pf}\\" + appName + " v" + version + "." + releaseNo + "\n")
                    isf.write("DefaultGroupName="+ appName + " v" + version + "." + releaseNo + "\n")
            else:
                    isf.write("AppVerName=%s v%s.%s %s\n" % (appName, version, releaseNo, status))
                    isf.write("DefaultDirName={pf}\\" + appName + " v" + version + "." + releaseNo + " " + status + "\n")
                    isf.write("DefaultGroupName="+ appName + " v" + version + "." + releaseNo + " " + status + "\n")
                    
            isf.write("UninstallDisplayIcon={app}\\uninst.ico\n")
            isf.write("Compression=lzma\n")
            isf.write("SolidCompression=yes\n")
            isf.write("UsePreviousAppDir=no\n")
            isf.write("DirExistsWarning=yes\n")
            isf.write("InfoBeforeFile=README.txt")
            

            isf.write("\n[Files]\n")

            isf.write('Source: "%s\\*"; DestDir: "{app}"; Flags: recursesubdirs\n' % sourceDir)
            isf.write('Source: "README.txt"; DestDir: "{app}"; Flags: isreadme\n')

            isf.write("\n[Icons]\n")
            isf.write('Name: "{group}\\%s"; Filename: "{app}\\program\\atom.exe"; WorkingDir: "{app}\\program"; IconFilename: "{app}\\nanorex_48x.ico"\n' % appName)
            isf.write('Name: "{userdesktop}\\%s"; Filename: "{app}\\program\\atom.exe"; WorkingDir: "{app}\\program"; IconFilename: "{app}\\nanorex_48x.ico"\n' % appName)
            isf.write('Name: "{group}\\Uninstall %s"; Filename: "{uninstallexe}"\n' % appName)

            isf.write("\n[Languages]\n")
            isf.write('Name: "en"; MessagesFile: "compiler:Default.isl"; LicenseFile: "LICENSE-Win32"\n')

            isf.close()
            print "----Inno Setup configuration file has been written."
            return True
        except:
            print_compact_traceback("In _createIssFile(): ")
            return False


    def _buildInstaller(self, issFile, outDir, outName):
        try:
             commLine = 'iscc  /Q  /O"' + outDir + '" /F"' + outName + '"  ' + issFile
             ret = os.system(commLine)
             if ret == 1:
                  errMsg = "The command line parameters are invalid: %s" % commLine
             elif ret == 2:
                  errMsg = "Inno Setup Compiler failed."
             else:
                 print "------Installation executable has been made."
                 return True
             raise Exception, errMsg
        except:
             print_compact_traceback("In method _buildInstaller():")
             return False


    def _buildPkg(self, destDir, rootDir, resourceDir, infoPlist, descrip):
        try:
             print 'PackageMaker -build -p ' + destDir + ' -f ' + rootDir + ' -r ' + resourceDir + ' -i ' + infoPlist + ' -d ' + descrip
             ret = os.system('PackageMaker -build -p ' + destDir + ' -f ' + rootDir + ' -r ' + resourceDir + ' -i ' + infoPlist + ' -d ' + descrip)
             
             imageFile = os.path.join(self.rootPath, self.appName + '-' + self.version + '.' + self.releaseNo + '.dmg')
             ret = os.system('hdiutil create -srcfolder ' + self.diskImagePath + ' -format UDZO  ' + imageFile)
             print "-------Disk image of PackageMaker package has been made."
             return True
        except:
             print_compact_traceback("In method _buildPkg(): ")
             return False



    def _buildRpm(self, specFile, sourceDir):
        """Before run rpmbuilder, mv self.buildSource to /usr/local, cp spec file into /usr/
        src/RPM/SPECS/, and then run: rpmbuild -bb specFile
        <parameter> specFile: the name of the spec file for rpm
        <parameter> sourceDir: the name of the temporary building path
        """
        try:
             specDir = '/usr/src/RPM/SPECS'
             destDir = '/usr/local'
             ret = os.system("sudo cp %s %s" % (specFile, specDir))
             ret = os.system("sudo mv %s %s" % (sourceDir, destDir))

             os.chdir(self.rootPath)
             emptyDir = self.appName + "-" + self.version
             os.mkdir(emptyDir)
             ret = os.system("tar -czvf project.tgz " + emptyDir+ "/")
             rpmSourceDir = '/usr/src/RPM/SOURCES'
             ret = os.system("sudo cp project.tgz %s" % rpmSourceDir)


             os.chdir(specDir)
             ret = os.system("sudo rpmbuild -bb %s" % specFile)
             os.chdir(self.currentPath)
                
             
             #Remove the packages in /usr/local
             ######ret = os.system("sudo rm -f -d -r %s" % (os.path.join(destDir, self.appName)))

             print "-------RPM package has been made."
             return True
        except:
             print_compact_traceback("In method _buildRpm: ")
             return False

    def _removeCVSFiles(self, rootDir):
        """Remove all CVS files and the directory for any cvs checkout directory under <root>. """
        for root, dirs, files in os.walk(rootDir):
            for name in dirs:
                if name == 'CVS': 
                    cvsDir = os.path.join(root, name)
                    self.clean(cvsDir, True)
                    os.rmdir(cvsDir)


    def clean(self, rootPath, cleanAll = False):
        """Clean everything created temporaly"""
        for root, dirs, files in os.walk(rootPath, topdown=False):
            for name in files:
                if cleanAll:
                    os.remove(os.path.join(root, name))
                elif not (name.endswith('w32.exe') or name.endswith('.dmg') or name.endswith('.tar.gz')):
                    os.remove(os.path.join(root, name))
                else:
                    print "Keep file: ", name

            for name in dirs:
                os.rmdir(os.path.join(root, name))


    def build(self):
        if not self._createDirectories(): return
        if not self._prepareSources():  return
        if not self._buildSource4Distribution(): return
        
        if sys.platform == 'win32':
             if not self._addModule2Zip('program/library.zip', 'OpenGL'):    return
             if not self._addDLLs(): return

             issFile = os.path.join(self.rootPath, 'setup.iss')
             print "self.status: ", self.status
             self._createIssFile(issFile, self.appName, self.version, self.releaseNo, self.buildSourcePath, self.status)
             outputFile = self.appName + '-' + self.version + '.' + self.releaseNo + '-w32'
             self._buildInstaller(issFile, self.rootPath, outputFile)

        elif sys.platform == 'linux2':
             specFile = os.path.join(self.rootPath, 'setup.spec')
             destDir = os.path.join('/usr/local', self.appName)
             if not self._createSpecFile(specFile, self.appName, self.version, self.releaseNo, destDir): return
             if not self._buildRpm(specFile, self.buildSourcePath): return

        else:
             welcomeFile = os.path.join(self.resourcePath, 'Welcome.txt')
             if not self._createWelcomeFile(welcomeFile): return
             postflightFile = os.path.join(self.resourcePath, 'postflight')
             if not self._writePostFlightFile(postflightFile): return
             plistFile = os.path.join(self.rootPath, 'Info.plist')
             words = self.version.split('.')
             if not self._createPlistFile(plistFile, self.appName, words[0], words[1], self.releaseNo): return
             pkgName = os.path.join(self.diskImagePath, self.appName + '-' + self.version + '.' + self.releaseNo + '.pkg')
             descrip = os.path.join(self.currentPath, 'Description.plist')
             if not self._buildPkg(pkgName, self.installRootPath, self.resourcePath, plistFile, descrip): return


def usage():
    print """usage: python autoBuild.py  -a<appname> -o<targetdir> -s<state> <1.0> <3>
    
    <1.0> is version number in the format of <major version.minor version>
          ---both major version and minor version should be non-negative integers)
    
    <3> is release status and number, in this case, it's alpha3 (valid release status
        is either a(alpha), b(beta), g(gama) or none, release number >= 1)
    
    <appname> is the product name, by default, it's 'nanoENGINEER-1'
    
    <targetdir> is the target destination. If it's an existing directory, its contents 
                will be deleted. 
                By default, it's <appname>-<version #>-<release status and number>
                
    Options:
    -a application name
    -o target location
    -i  icon file
    -s release state 
    -t cvs tag
    -h help


    Long options also work:
    --appname =<appname>
    --outdir=<targetdir>
    --iconfile=<Icon file for the app/exe, currently ignored on Linux>
    --state=<release status: Alpha, beta, gamma...>
    --cvstag=<the cvs tag used to check out files>
    --help
    
    Windows example: 
    C:> python autoBuild.py -sa -treleas051114 0.0 7
    
    Linux example:
    $ python autoBuild.py -sa -treleas051114 0.0 7
    
    """

def main():
    shortargs = 'h:a:o:i:s:t:'
    longargs = ['help', 'appname=', 'outdir=', 'iconfile=', 'state=', 'cvstag=']
   
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortargs, longargs)
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    currentDir = os.getcwd()
    appName = "nanoENGINEER-1"
    rootDir = None
    if sys.platform == 'win32':
          iconFile = os.path.join(currentDir, 'nanorex_48x.ico')
    elif sys.platform == 'darwin':
        iconFile = os.path.join(currentDir, 'nanorex.icns')
    else:
       iconFile = None

    if len(args) != 2:
        usage()
        sys.exit(2)

    version = args[0]
    releaseNo = args[1]
    status = None
    cvsTag = None
    
    for o, a in opts:
        if o in ("-a", "--appname"):
            appName = a
        elif o in ("-o", "--outdir"):
            rootDir = os.path.join(currentDir, a)
        elif o in ("-i", "--iconfile"):
            iconFile = os.path.join(currentDir, a)
        elif o in ("-s", "--state") and a in ('a', 'b', 'g'):
           if a == 'a': status = "(Alpha %s)" % releaseNo
           elif a == 'b': status = "(Beta %s)" % releaseNo
           else: status = "(Gamma %s)" % releaseNo
        elif o in ("-t", "--cvstag"):
            cvsTag = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()

    if not rootDir:
        rootDir = os.path.join(currentDir, appName + "-" + version + "-" + releaseNo)

    if os.path.isdir(rootDir):
                answer = raw_input("Do you want to use the existing directory: %s, all its contents will be erased? yes or no? " % rootDir)
                while answer not in ['yes', 'no']:
                    answer = raw_input("Do you want to use the existing directory: %s, all its contents will be erased? yes or no? " % rootDir)
                if answer == 'no':
                    sys.exit()

    builder = NanoBuild(appName, iconFile, rootDir, version, releaseNo, status, cvsTag)
    builder.build()

    if sys.platform == 'linux2':
        pass
        #builder.clean(rootDir, cleanAll = True)
    else:
        builder.clean(rootDir)

    if os.path.isdir(rootDir) and not os.listdir(rootDir): os.rmdir(rootDir)

if __name__ == '__main__': main()
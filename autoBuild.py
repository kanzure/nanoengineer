# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
autoBuild.py -- Creates the nanoENGINEER-1 install package for Windows, Mac and Linux.

$Id$

History:

051110 Taken over by Will Ware

050501 Initial version, created by Huaicai
'''

__author__ = "Will"

import os
import sys
import getopt
from shutil import *

PYLIBPATH = os.path.split(getopt.__file__)[0]
prematureExit = False

class NonZeroExitStatus(Exception):
    pass

def system(cmd):
    print cmd
    ret = os.system(cmd)
    if ret != 0:
        raise NonZeroExitStatus, cmd
    return ret

def listResults(cmd):
    def strip(x):
        return x.rstrip()
    return map(strip, os.popen(cmd).readlines())

class AbstractMethod(Exception):
    """Indicates that something must be overloaded because it isn't usefully
    defined in the context where it's being used."""
    pass

class NanoBuildBase:
    """This is the base class for creating a installation package.
    It works for Linux, Mac OS X, and WinXP.
    """
    def  __init__(self, appname, iconfile, rootDir, version, relNo, stat, tag):
        self.currentPath = os.getcwd() # Current working directory
        self.rootPath = rootDir # sub-directory where the executable and temporary files are stored
        self.appName = appname # Application name, e.g., 'nanoENGINEER-1'
        self.iconFile = iconfile # The icon file name
        self.version = version # version number, e.g. '0.0'
        self.releaseNo = relNo # release number, e.g. '7'
        self.status = stat # release status, e.g. 'a', 'b', which mean 'Alpha', 'Beta' respectly.
        self.cvsTag = tag # cvs tag name that you want to use to build the package, without it,
        # it will just use the current version in cvs repository.
        self.sourceDirectory = None # For debug: if you want local sources instead of real
        # cvs checkouts, specify a directory containing cad and sim trees.

        self.atomPath = os.path.join(self.rootPath, 'atom')
        self.setupBuildSourcePath()

    def build(self):
        '''Main build method.'''
        self.createDirectories()
        self.prepareSources()
        self.buildSourceForDistribution()
        if prematureExit:
            sys.exit(0)
        self.makePlatformPackage()

    def setupBuildSourcePath(self):
        self.buildSourcePath = os.path.join(self.rootPath, self.appName)

    def createDirectories(self):
        """Create directories structure, return true if success"""
        if os.path.isdir(self.rootPath):
            self.clean(self.rootPath, cleanAll = True)
        else:
            os.mkdir(self.rootPath)

        self.createMiddleDirectories()

        os.mkdir(self.atomPath)
        os.mkdir(self.buildSourcePath)

    def createMiddleDirectories(self):
        # need these for a mac osx build
        pass

    def standaloneSimulatorName(self):
        return "simulator"

    def pyrexSimulatorName(self):
        return "sim.so"

    def openglAcceleratorName(self):
        return "quux.so"

    def prepareSources(self):
        """Checkout source code from cvs for the release """
        os.chdir(self.atomPath)
        if self.sourceDirectory:
            # we would only do this when experimenting anyway, so we don't
            # need the restriction on cad/doc here
            system("cp -r %s ." % os.path.join(self.sourceDirectory, "cad"))
            system("cp -r %s ." % os.path.join(self.sourceDirectory, "sim"))
        elif not self.cvsTag:
            system('cvs -Q -z9 checkout -l cad/doc')
            system('cvs -Q -z9 checkout -P cad/src cad/images sim cad/partlib')
        else:
            system('cvs -Q -z9 checkout -r %s -l cad/doc' % self.cvsTag)
            system('cvs -Q -z9 checkout -r %s -R cad/src cad/images sim cad/partlib' % self.cvsTag)

        # Remove all those 'CVS' directories and their entries.
        self.removeCVSFiles('cad')
        self.removeCVSFiles('sim')

        self.buildTarball() # For Linux only.
        print "----------Sources have been checked out and made.\n"

    def buildSimulator(self):
        """Checkout source code from cvs for the release """
        os.chdir(os.path.join(self.atomPath, 'sim/src'))
        system('make')
        system('make pyx')
        print "----------Simulators (standalone and pyrex) have been built.\n"

    def buildOpenGLAccelerator(self):
        """Checkout source code from cvs for the release """
        os.chdir(os.path.join(self.atomPath, 'cad/src/experimental/pyrex-opengl'))
        system('make')
        print "----------Brad G's OpenGL accelerator has been built.\n"

    def buildTarball(self):
        # only needed for Linux
        pass

    def buildSourceForDistribution(self):
        """Freeze Python code into an executable. Where necessary, compile
        and link C code."""
        self.buildSimulator()
        self.buildOpenGLAccelerator()
        os.chdir(os.path.join(self.atomPath,'cad'))
        # copytree doc, partlib, images
        copytree('doc', os.path.join(self.buildSourcePath, 'doc'))
        copytree('partlib', os.path.join(self.buildSourcePath, 'partlib'))
        copytree('images', os.path.join(self.buildSourcePath, 'images'))

        self.binPath = binPath = os.path.join(self.buildSourcePath, 'bin')
        os.mkdir(binPath)
        self.progPath = progPath = os.path.join(self.buildSourcePath, 'program')
        os.mkdir(progPath)
        os.chdir(self.currentPath)
        self.copyOtherSources()
        os.chdir(os.path.join(self.atomPath,'cad/src'))
        self.freezePythonExecutable()
        os.chdir(self.currentPath)
        print "------All python modules are packaged together."

    def copyOtherSources(self):
        """This will typically include gnuplot, the standalone and pyrex simulators,
        Brad G's opengl accelerator, an icon file, release notes and other text files.
        """
        raise AbstractMethod

    def freezePythonExecutable(self):
        raise AbstractMethod

    def removeCVSFiles(self, rootDir):
        """Remove all CVS files and the directory for any cvs checkout directory under <root>. """
        for root, dirs, files in os.walk(rootDir):
            for name in dirs:
                if name == 'CVS': 
                    cvsDir = os.path.join(root, name)
                    self.clean(cvsDir, True)
                    os.rmdir(cvsDir)

    def clean(self, rootPath, cleanAll=False):
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

    def makePlatformPackage(self):
        """Packages are different for different platforms. Linux wants an RPM.
        The Mac wants a DMG. Windows wants something else. Build the package.
        """
        raise AbstractMethod

###################################################

class NanoBuildWin32(NanoBuildBase):
    def prepareSources(self):
        """Checkout source code from cvs for the release """
        print "\n------------------------------------------------------\nPreparing Sources"
        ret = os.spawnv(os.P_NOWAIT, 'C:\Huaicai\putty\pageant.exe',
                        ['C:\Huaicai\putty\pageant.exe', 'C:\Huaicai\Documents\dsa_private.ppk'])
        if ret <= 0: raise Exception, "start pageant.exe with key file dsa_privaate.ppk failed."
        NanoBuildBase.prepareSources(self)

    def copyOtherSources(self):
        print "\n------------------------------------------------------\nCopying other files"
        copy('wgnuplot.exe', self.binPath)
        copy(os.path.join(self.atomPath, 'sim/src', self.standaloneSimulatorName()), self.binPath)
        copy(os.path.join(self.atomPath, 'sim/src', self.pyrexSimulatorName()), self.binPath)
        copy(os.path.join(self.atomPath, 'cad/src/experimental/pyrex-opengl',
                          self.openglAcceleratorName()), self.binPath)
        copy(self.iconFile, self.buildSourcePath)
        copy('uninst.ico', self.buildSourcePath)
        copy('setup.py', os.path.join(self.atomPath,'cad/src'))
        copy(os.path.join(self.atomPath,'cad/src/RELEASENOTES.txt'), self.buildSourcePath)
        copy(os.path.join(self.atomPath,'cad/src/KnownBugs.htm'), self.buildSourcePath)
        copy(os.path.join(self.atomPath,'cad/src/README.txt'), self.rootPath)
        copy(os.path.join(self.atomPath,'cad/src/LICENSE-Win32'), self.rootPath)

    def removeGPLFiles(self):
        """Remove non gpl files (Windows only)"""
        print "\n------------------------------------------------------\nRemoving GPL Files"
        srcPath = os.path.join(self.atomPath,'cad/src/')
        entries = os.listdir(srcPath)
        for entry in entries[:]:
            file = os.path.join(srcPath, entry)
            if os.path.isfile(file) and entry.startswith('gpl_'):
                    print "File removed: ", entry
                    os.remove(file)
        print "Done"

    def standaloneSimulatorName(self):
        return "simulator.exe"

    def pyrexSimulatorName(self):
        return "sim.dll"

    def openglAcceleratorName(self):
        return "quux.dll"

    def freezePythonExecutable(self):
        print "\n------------------------------------------------------\nFreezing Python Executable"
        self.removeGPLFiles()
        try:
            system('python setup.py py2exe --includes=sip,dbhash --excludes=OpenGL -d' +
                   os.path.join(self.buildSourcePath, 'program'))
        except NonZeroExitStatus:
            # this happens, apparently not a problem
            print "Warning, exit status for 'python setup.py py2exe' was not zero"

    def createIssFile(self, issFile, appName, version, releaseNo, sourceDir, status):
        """Create the iss file (script) to build package on Windows.  The iss script
        contains all the instructions for the installation package.
        """
        print "\n------------------------------------------------------\nCreating Inno Setup configuration script"
        isf = open(issFile, 'w')
        isf.write("; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES! \n\n")
        isf.write("[Setup]\n")
        isf.write("AppName=%s\n" % appName)
        if releaseNo:
            appnamever = appName + " v" + version + "." + releaseNo
            ver = "v%s.%s" % (version, releaseNo)
        else:
            appnamever = appName + " v" + version
            ver = "v%s" % version
        if not status:
            isf.write("AppVerName=%s %s\n" % (appName, version))
            isf.write("DefaultDirName={pf}\\" + appnamever + "\n")
            isf.write("DefaultGroupName="+ appnamever + "\n")
        else:
            isf.write("AppVerName=%s %s %s\n" % (appName, ver, status))
            isf.write("DefaultDirName={pf}\\" + appnamever + " " + status + "\n")
            isf.write("DefaultGroupName="+ appnamever + " " + status + "\n")
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
        isf.write(('Name: "{group}\\%s"; Filename: "{app}\\program\\atom.exe"; ' +
                   'WorkingDir: "{app}\\program"; IconFilename: "{app}\\nanorex_48x.ico"\n') % appName)
        isf.write(('Name: "{userdesktop}\\%s"; Filename: "{app}\\program\\atom.exe"; ' +
                   'WorkingDir: "{app}\\program"; IconFilename: "{app}\\nanorex_48x.ico"\n') % appName)
        isf.write('Name: "{group}\\Uninstall %s"; Filename: "{uninstallexe}"\n' % appName)
        isf.write("\n[Languages]\n")
        isf.write('Name: "en"; MessagesFile: "compiler:Default.isl"; LicenseFile: "LICENSE-Win32"\n')
        isf.close()
        print "Done"

    def _addModuleToZip(self, archFile, module):
        """First, rename *.zip file, and then create a directory,
        unzip *.zip into that directory, copy module into that directory (Windows only)"""
        print "\n------------------------------------------------------\nAdding Module to ZIP File"
        import zipfile, unzip
        os.chdir(self.currentPath)
        archFile = os.path.normpath(os.path.join(self.buildSourcePath, archFile))
        tmpZipFile = os.path.join(self.buildSourcePath, 'program/temp1234.zip')
        print "archFile", archFile
        print "tmpZipFile", tmpZipFile
        print "pwd", listResults("pwd")[0]
        print "dir", os.listdir(".")
        os.rename(archFile, tmpZipFile)
        os.mkdir(archFile)
        unz = unzip.unzip()
        unz.extract(tmpZipFile, archFile)
        copytree(module, os.path.join(archFile, module))
        os.remove(tmpZipFile)

    def _addDLLs(self):
        """Add all the required dlls into <program> (Windows only) """
        print "\n------------------------------------------------------\nAdding DLLs"
        copy('glut32.dll', os.path.join(self.buildSourcePath, 'program'))
        print "glut32.dll"
        copy('msvcr71.dll', os.path.join(self.buildSourcePath, 'program'))
        print "msvcr71.dll"
        print "Done"

    def makePlatformPackage(self):
        self._addModuleToZip('program/library.zip', 'OpenGL')
        self._addDLLs()
        issFile = os.path.join(self.rootPath, 'setup.iss')
        print "self.status: ", self.status
        self.createIssFile(issFile, self.appName, self.version, self.releaseNo,
                            self.buildSourcePath, self.status)
        outputFile = PMMT + '-w32'
        # Run Inno Setup command to build the install package for Windows (only).
        commLine = 'iscc  /Q  /O"' + self.rootPath + '" /F"' + outputFile + '"  ' + issFile
        system(commLine)
        if ret == 1:
            errMsg = "The command line parameters are invalid: %s" % commLine
        elif ret == 2:
            errMsg = "Inno Setup Compiler failed."
        else:
            print "\n------------------------------------------------------"
            print "Installation executable %s has been made." % outputFile
            return True
        raise Exception, errMsg

########################################################

class NanoBuildLinux(NanoBuildBase):

    def setupBuildSourcePath(self):
        self.buildSourcePath = os.path.join(self.rootPath, PMMT)

    def buildTarball(self):
        os.chdir(self.atomPath)
        tarName = PMMT + '.tar.gz'
        system('tar -czvf %s *' % tarName)
        print "\nThe tar file: %s has been successfully created.\n" % tarName

    def copyOtherSources(self):
        copy('/usr/bin/gnuplot', self.binPath)
        copy(os.path.join(self.atomPath, 'sim/src', self.standaloneSimulatorName()), self.binPath)
        copy(os.path.join(self.atomPath, 'sim/src', self.pyrexSimulatorName()), self.binPath)
        copy(os.path.join(self.atomPath, 'cad/src/experimental/pyrex-opengl',
                          self.openglAcceleratorName()), self.binPath)
        copy(os.path.join(self.atomPath,'cad/src/rungms'), self.binPath)
        copy(os.path.join(self.atomPath,'cad/src/KnownBugs.htm'), os.path.join(self.buildSourcePath, 'doc'))
        copy(os.path.join(self.atomPath,'cad/src/README.txt'), os.path.join(self.buildSourcePath, 'doc'))
        copy(os.path.join(self.atomPath,'cad/src/LICENSE'), os.path.join(self.buildSourcePath, 'doc'))
        copy(os.path.join(self.atomPath,'cad/src/RELEASENOTES.txt'), os.path.join(self.buildSourcePath, 'doc'))

    def freezePythonExecutable(self):
        # Mandrake calls it 'libsip', not 'sip' ... when did this happen?  wware 051212
        try:
            cmd = ('FreezePython --include-modules=libsip,dbhash --exclude-modules=OpenGL --install-dir=' +
                   os.path.join(self.buildSourcePath, 'program') + ' --target-name=' + self.appName + '  atom.py')
            system(cmd)
        except:
            # Mandriva 2006 calls it "sip"
            cmd = ('FreezePython --include-modules=sip,dbhash --exclude-modules=OpenGL --install-dir=' +
                   os.path.join(self.buildSourcePath, 'program') + ' --target-name=' + self.appName + '  atom.py')
            system(cmd)
        #Copy OpenGL package into buildSource/program
        copytree(os.path.join(PYLIBPATH, 'site-packages', 'OpenGL'),
                 os.path.join(self.buildSourcePath, 'program/OpenGL'))

    def createSpecFile(self, specFile, appName, version, releaseNo, sourceDir):
        """Create the spec file to build rpm package on Linux. Here is some
        information about what goes inside a RPM spec file:
        http://www.rpm.org/max-rpm/s1-rpm-build-creating-spec-file.html
        http://www.rpm.org/max-rpm/s1-rpm-inside-scripts.html
        """
        spf = open(specFile, 'w')
        spf.write("AutoReqProv: 0 \n\nSummary: A CAD software package for a nanoengineer to " +
                  "design and simulate nano-components and nano-machines.\n")
        spf.write("Name: %s\n" % appName)
        spf.write("Version: %s\n" % version)
        if releaseNo:
            spf.write("Release: %s\n" % releaseNo)
        else:
            spf.write("Release: 0\n")
        otherStuff = """License: GPL
Group: Applications/CAD
Source: project.tgz
URL: http://nanoengineer-1.net/mediawiki/index.php
Distribution: nanoENGINEER-1
Vendor: Nanorex, Inc.
Packager: Nanorex, Inc.
#Requires: libMesaglut3

%description
nanoENGINEER-1 includes a molecular design module that combines
capabilities found in traditional chemistry modeling software
with features found in popular 3-D mechanical CAD systems. With
nanoENGINEER-1, users can design atomically precise assemblies
from a variety of stiff covalent structures, including diamond
lattice frameworks. A parts library of molecular components is
also included containing tubes, shafts, bearings, gears, joints,
and springs that can be easily inserted and integrated with an
existing assembly.

%prep

%setup

%build

%install
# This stuff DOES NOT RUN on the end user's machine!
# If it did, we could set up a desktop icon here.
# And we could set the BROWSER environment variable here.
# But alas, these things must be release-noted. An RPM can't do them.

%post
#!/bin/sh
# Set up a desktop icon.
# I checked a nanoENGINEER-1.desktop file into cad/src, but I don't
# see how to get it through the RPM process and into the end user's
# $HOME directory.

# Set the BROWSER environment variable.
if [ -f /usr/bin/firefox ] || [ -f /usr/local/bin/firefox ]; then
    echo "export BROWSER=firefox" >> /etc/bashrc
else
    echo "export BROWSER=konqueror" >> /etc/bashrc
fi
# Unfortunately this won't help the user until he starts
# another Bash session.

%files
%defattr(755, root, root, 755)
"""
        spf.write(otherStuff)
        spf.write(sourceDir + "\n")
        spf.close()
        print "----RPM building specification file has been written."

    def makePlatformPackage(self):  # linux
        specFile = os.path.join(self.rootPath, 'setup.spec')
        destDir = os.path.join('/usr/local', PMMT)
        self.createSpecFile(specFile, self.appName, self.version, self.releaseNo, destDir)
        """Before run rpmbuilder, mv self.buildSource to /usr/local,
        cp spec file into /usr/src/RPM/SPECS/,
        and then run: rpmbuild -bb specFile
        specFile: the name of the spec file for rpm
        self.buildSourcePath: the name of the temporary building path
        """
        specDir = '/usr/src/RPM/SPECS'
        system("sudo cp %s %s" % (specFile, specDir))
        system("sudo rm -rf /usr/local/" + PMMT)
        system("sudo mv %s /usr/local" % self.buildSourcePath)
        os.chdir(self.rootPath)
        emptyDir = self.appName + "-" + self.version
        os.mkdir(emptyDir)
        system("tar -czvf project.tgz " + emptyDir+ "/")
        rpmSourceDir = '/usr/src/RPM/SOURCES'
        system("sudo cp project.tgz %s" % rpmSourceDir)
        os.chdir(specDir)
        system("sudo rpmbuild -bb %s" % specFile)
        os.chdir(self.currentPath)
        #Remove the packages in /usr/local
        system("sudo rm -f -d -r %s" % destDir)
        print "-------RPM package has been made."

########################################################

class NanoBuildMacOSX(NanoBuildBase):
    def createMiddleDirectories(self):
        os.mkdir(self.installRootPath)
        os.mkdir(self.diskImagePath)
        os.mkdir(self.resourcePath)

    def buildSourceForDistribution(self):
        """Pack source together for distribution (all platforms)."""
        self.buildSimulator()
        self.buildOpenGLAccelerator()
        #
        #
        os.chdir(self.currentPath)
        copy('background.jpg', self.resourcePath)
        copy('libaquaterm.1.0.0.dylib', self.buildSourcePath)
        copy('setup.py', os.path.join(self.atomPath,'cad/src'))
        #
        #
        self.freezePythonExecutable()
        #
        #
        os.chdir(os.path.join(self.atomPath,'cad'))
        appname = self.appName + '.app'
        copytree('doc', os.path.join(self.buildSourcePath, appname, 'Contents/doc'))
        copytree('images', os.path.join(self.buildSourcePath, appname, 'Contents/images'))
        # Put the partlib outside the app bundle, where users can see its internal
        # directories and files. Put a symbolic link to it from the normal
        # location inside the bundle.
        copytree('partlib', os.path.join(self.buildSourcePath, 'partlib'))
        system('(cd %s; ln -s ../../partlib .)' %
               os.path.join(self.buildSourcePath, appname, 'Contents'))
        #
        #
        self.binPath = binPath = os.path.join(self.buildSourcePath, appname, 'Contents/bin')
        os.mkdir(binPath)
        ne1files = listResults("find " + self.buildSourcePath + " -name nanoENGINEER-1.py")
        for f in ne1files:
            os.chmod(f, 0755)
        self.copyOtherSources()
        print "------All python modules are packaged tegether."


    def freezePythonExecutable(self):
        os.chdir(os.path.join(self.atomPath,'cad/src'))
        os.rename('atom.py', self.appName + '.py')
        system('python setup.py py2app --includes=sip --excludes=OpenGL --iconfile %s  -d %s' %
               (self.iconFile, self.buildSourcePath))


    # We really want to do something like this:
    #
    # def copyOtherSources(self):
    #     ...stuff...
    #     NanoBuildLinux.copyOtherSources(self)
    #     ...stuff...
    #

    def copyOtherSources(self):
        appname = self.appName + '.app'
        os.chdir(self.currentPath)
        copytree('/Applications/AquaTerm.app',  os.path.join(self.buildSourcePath, appname,
                                                             'Contents/bin/AquaTerm.app'))
        copy(os.path.join(self.atomPath, 'sim/src', self.standaloneSimulatorName()), self.binPath)
        copy(os.path.join(self.atomPath, 'sim/src', self.pyrexSimulatorName()), self.binPath)
        copy(os.path.join(self.atomPath, 'cad/src/experimental/pyrex-opengl',
                          self.openglAcceleratorName()), self.binPath)
        copy(os.path.join(self.atomPath, 'cad/src/all_mac_imports.py'),
                          os.path.join(self.buildSourcePath, appname, 'Contents/Resources'))
        copy('/usr/local/bin/gnuplot', self.binPath)
        #Copy rungms script into 'bin' directory
        copy(os.path.join(self.atomPath,'cad/src/rungms'), self.binPath)
        #Copy OpenGL package into buildSource/program
        copytree('site-packages',
                 os.path.join(self.buildSourcePath, appname,
                              'Contents/Resources/Python/site-packages'))
        copy(os.path.join(self.atomPath,'cad/src/KnownBugs.htm'),
             self.buildSourcePath)
        copyfile(os.path.join(self.atomPath,'cad/src/README.txt'),
                 os.path.join(self.buildSourcePath, 'ReadMe.txt'))
        copy(os.path.join(self.atomPath,'cad/src/RELEASENOTES.txt'),
             self.buildSourcePath)

        copyfile(os.path.join(self.atomPath,'cad/src/README.txt'),
                 os.path.join(self.resourcePath, 'ReadMe.txt'))
        copyfile(os.path.join(self.atomPath,'cad/src/LICENSE'),
                 os.path.join(self.resourcePath, 'License'))

    def setupBuildSourcePath(self):
        self.installRootPath = os.path.join(self.rootPath, 'installRoot')
        self.buildSourcePath = os.path.join(self.installRootPath, PMMT)
        self.diskImagePath = os.path.join(self.rootPath, 'diskImage')
        self.resourcePath = os.path.join(self.rootPath, 'resources')
    def createWelcomeFile(self, welcomeFile):
        """Write the welcome file for Mac package installer """
        wf = open(welcomeFile, 'w')
        message = (("Welcome to %s v%s.%s %s. You will be guided through the steps " +
                    "necessary to install this software. By default, this software " +
                    "will be installed into /Applications directory with all files " +
                    "under its own sub-directory. So, just relax.\n") %
                   (self.appName, self.version, self.releaseNo, self.status))
        wf.write(message)
        wf.close()
        print "----Welcome file has been written."


    # http://developer1.apple.com/documentation/DeveloperTools/Conceptual/ \
    #    SoftwareDistribution/Concepts/sd_pre_post_processing.html
    def _writePostFlightFile(self, pfFile):
        """Write the postflight file Mac Package Installer """
        instPath = os.path.basename(self.buildSourcePath)   # "nanoENGINEER-1-0.0.6"
        appname = self.appName + '.app'
        cf = os.path.join(instPath, appname, 'Contents/Frameworks')
        # $2/instPath --> /Applications/nanoENGINEER-1-0.0.6
        # $2/cf --> /Applications/nanoENGINEER-1-0.0.6/nanoENGINEER-1.app/Contents/Frameworks
        pf  = open(pfFile, 'w')
        pf.write("""#!/bin/bash
mv $2/%s/libaquaterm.1.0.0.dylib $2/%s
exit 0
""" % (instPath, cf))
        pf.close()
        from stat import S_IREAD, S_IEXEC, S_IROTH, S_IXOTH  
        os.chmod(pfFile, S_IREAD | S_IEXEC | S_IROTH | S_IXOTH)
        print "----Postflight file has been written."

    def createPlistFile(self, plistFile,  appName, majorVer, minorVer,  releaseNo):
        """ Write InfoPlist file to build package of PackageMaker (Mac OS X)."""
        plf = open(plistFile, 'w')
        titleDoc = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
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

    def makePlatformPackage(self):
        welcomeFile = os.path.join(self.resourcePath, 'Welcome.txt')
        self.createWelcomeFile(welcomeFile)
        postflightFile = os.path.join(self.resourcePath, 'postflight')
        self._writePostFlightFile(postflightFile)
        plistFile = os.path.join(self.rootPath, 'Info.plist')
        words = self.version.split('.')
        self.createPlistFile(plistFile, self.appName, words[0], words[1], self.releaseNo)
        pkgName = os.path.join(self.diskImagePath, PMMT + '.pkg')
        descrip = os.path.join(self.currentPath, 'Description.plist')
        # Run PackageMaker to build the final installation package
        try:
            system('PackageMaker -build -p ' + pkgName + ' -f ' + self.installRootPath +
                   ' -r ' + self.resourcePath + ' -i ' + plistFile + ' -d ' + descrip)
        except NonZeroExitStatus:
            # this happens, apparently not a problem
            print "Warning, exit status for PackageMaker was not zero"
        imageFile = os.path.join(self.rootPath, PMMT + '.dmg')
        system('hdiutil create -srcfolder ' + self.diskImagePath +
               ' -format UDZO  ' + imageFile)
        print "-------Disk image of PackageMaker package has been made."

###################################################

if sys.platform == "win32":
    NanoBuild = NanoBuildWin32
elif sys.platform == "linux2":
    NanoBuild = NanoBuildLinux
elif sys.platform == "darwin":
    NanoBuild = NanoBuildMacOSX
else:
    raise Exception, "unknown platform"

def usage():
    print """usage: python autoBuild.py [options]
                
    options:
    -h prints this usage (help) text
    -o output directory.  Default is $CWD/nanoENGINEER-1.maj.min.tiny/nanoENGINEER-1
    -i icon file. This is currently ignored on Linux
    -t cvs tag
    -s source directory. This bypasses cvs checkout and uses the source in this directory.

    Long options also work:
    --help
    --iconfile=<icon file> Currently ignored on Linux
    --outdir=<directory>
    --sourceDirectory=<sourcedirectory>
    --tag=<the cvs tag used to check out files>
    
    Windows example, using the -t option: 
    C:> python autoBuild.py -treleas051114
    
    Linux example, using the -s option:
    $ python autoBuild.py -s/home/atom/
    
    """

def main():
    shortargs = 'ho:i:s:t:v:p'
    longargs = ['help', 'outdir=', 'iconfile=', 'sourcedir=', 'tag=', 'version=', 'premature-exit']
   
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

    status = None
    cvsTag = None
    sourceDirectory = None
    specialVersion = None
    
    for o, a in opts:
        if o in ("-o", "--outdir"):
            rootDir = os.path.join(currentDir, a)
        elif o in ("-i", "--iconfile"):
            iconFile = os.path.join(currentDir, a)
        elif o in ("-t", "--tag"):
            cvsTag = a
        elif o in ("-s", "--sourcedir"):
            sourceDirectory = a
        elif o in ("-v", "--version"):
            specialVersion = a
        elif o in ("-p", "--premature-exit"):
            global prematureExit
            prematureExit = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()

    # Get the version information by checking out only the 
    # version.py file like this:
    #
    # cvs -Q -z9 checkout cad/src/version.py
    #
    # Mark 051117

    sp = sys.path
    cadDir = os.path.join(os.getcwd(), "cad")
    if sourceDirectory:
        system("rm -rf " + cadDir)
        system("cp -r %s %s" % (os.path.join(sourceDirectory, "cad"), cadDir))
    elif cvsTag:
        system("cvs -Q -z9 checkout -r %s cad/src/version.py" % cvsTag)
    else:
        system("cvs -Q -z9 checkout cad/src/version.py")
    
    sys.path.append(os.path.join(cadDir, "src"))
    from version import Version
    global VERSION, PMMT
    VERSION = Version()
    PMMT = VERSION.product + "-"
    if specialVersion != None:
        PMMT += specialVersion
    elif hasattr(VERSION, "tiny"):
        PMMT += "%d.%d.%d" % (VERSION.major, VERSION.minor, VERSION.tiny)
    else:
        PMMT += "%d.%d" % (VERSION.major, VERSION.minor)
    sys.path = sp
    
    #answer = "maybe"
    #while answer not in ['yes', 'no']:
    #    answer = raw_input(("\nThis will create the installation package for %s? " +
    #                        "\nDo you want to continue (yes or no): ") % PMMT)
    #    if answer == 'no':
    #        sys.exit()

    if not rootDir:
        rootDir = os.path.join(currentDir, PMMT)

    if os.path.isdir(rootDir):
        answer = "maybe"
        while answer not in ['yes', 'no']:
            answer = raw_input(("Do you want to use the existing directory %s? " +
                                "All its contents will be erased (yes or no): ") % rootDir)
            if answer == 'no':
                sys.exit()

    relNo = ""
    if hasattr(VERSION, "tiny"):
        relNo = "%d" % VERSION.tiny
    builder = NanoBuild(appName, iconFile, rootDir,
                        "%d.%d" % (VERSION.major, VERSION.minor),
                        relNo, VERSION.releaseType, cvsTag)
    builder.sourceDirectory = sourceDirectory
    builder.clean(cadDir, True)
    os.rmdir(cadDir)
    builder.build()

    # The clean() method chokes on the symbolic link that I needed to use for the partlib
    # on the Mac. It was already broken on Linux, possibly for the same reason. So only
    # do cleanup on Windows.
    if sys.platform == "win32":
        builder.clean(rootDir)

    if os.path.isdir(rootDir) and not os.listdir(rootDir): os.rmdir(rootDir)

if __name__ == '__main__':
    main()

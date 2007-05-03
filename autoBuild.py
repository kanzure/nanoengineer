# Copyright (c) 2004-2007 Nanorex, Inc.  All rights reserved.
"""
autoBuild.py -- Creates the NanoEngineer-1 install package for Windows, Mac and Linux.

$Id$

History:

060420 bruce minor changes

051110 Taken over by Will Ware

050501 Initial version, created by Huaicai

Usage: see http://www.nanoengineer-1.net/mediawiki/index.php?title=Building_release_packages
"""

__author__ = "Will"

import os
import sys
import getopt
from shutil import *

PYLIBPATH = os.path.split(getopt.__file__)[0]
prematureExit = False

def linenum():
    try:
        raise Exception
    except:
        tb = sys.exc_info()[2]
        f = tb.tb_frame.f_back
        print f.f_code.co_filename, f.f_code.co_name, f.f_lineno

class NonZeroExitStatus(Exception):
    pass

def system(cmd, noprint = False):
    if not noprint:
        print cmd
    ret = os.system(cmd)
    if ret != 0:
        raise NonZeroExitStatus, cmd
    return ret

def listResults(cmd):
    def strip(x):
        return x.rstrip()
    return map(strip, os.popen(cmd).readlines())

def copytree(src, dst, symlinks = False):
    """shutil.copytree() is annoying because it insists on creating
    the directory. If the directory already exists, issue a warning
    to standard error, but continue working.
    """
    srcdir = os.path.join(os.getcwd(), src)
    assert os.path.exists(srcdir), \
           "copytree - source directory doesn't exist: " + srcdir
    names = os.listdir(src)
    if os.path.isdir(dst):
        print >>sys.stderr, "copytree - directory exists already: " + dst
    else:
        os.mkdir(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                copy2(srcname, dstname)
                    ###e where is copy2 defined? Maybe in shutil? [bruce 070426 Q]
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, why))
    if errors:
        raise IOError, errors

def clean(rootPath, cleanAll=False):
    """Clean everything created temporarily"""
    for root, dirs, files in os.walk(rootPath, topdown=False):
        for name in files:
            if cleanAll:
                os.remove(os.path.join(root, name))
            elif not (name.endswith('w32.exe') or name.endswith('.dmg') or name.endswith('.tar.gz')):
                os.remove(os.path.join(root, name))
            else:
                print "Keep file: ", name

        for name in dirs:
            fname = os.path.join(root, name)
            if os.path.islink(fname):
                os.remove(fname)   # symbolic link (try 2)
            elif os.path.isdir(fname):
                clean(fname, cleanAll)
                try:
                    os.rmdir(fname)
                except OSError:
                    # when not doing cleanAll, we may sometimes leave a directory
                    # around if it isn't empty
                    if cleanAll:
                        raise
            else:
                os.remove(fname)   # symbolic link (try 1, didn't work on Mac partlib, left in in case it helps other things)

def all_subfiles(filename, results = None): #bruce 070429 [modified from all_subfiles in bruce's my_path_utils.py]
    """Return a list of all files and directories under filename, directly or indirectly, 
     but NOT FOLLOWING symbolic links, or including them in the list.
     This is not quite doable by os.path.walk, since filename might be a single file.
     Note that os.path.islink doesn't work right (i.e. detect aliases) on a Mac,
     so this won't work if Mac aliases are present.
         Error if filename is not an existing file or directory, but existence of non-directories is not checked.
     If the second argument is given, it should be a list object of already-collected results,
     to which new results (pathname strings) will be appended in-place, instead of being returned.
    """
    if results is None:
        results = [] # make a new list each time
        ret = 1
    else:
        ret = 0
    if not os.path.islink(filename):
        #e future: verify filename exists as file or directory
        results.append(filename) ### does this modify results in-place? I think so.
        if os.path.isdir(filename):
            files = os.listdir(filename)
            for f in files:
                all_subfiles(os.path.join(filename, f), results)
    if ret:
        return results
    pass

def fix_1724(dir1, get_md5): #bruce 070429, Mac-specific
    """Modify every .so file inside dir1, using the equivalent of
        install_name_tool -change
             /Library/Frameworks/Python.framework/Versions/2.3/Python
        /System/Library/Frameworks/Python.framework/Versions/2.3/Python $file
       and print names and count of files it modifies
       (checked by comparing md5 before/after, as computed by get_md5(filename)).
    """
    files = []
    for arg in [dir1]:
        all_subfiles(arg, files)
        
    files2 = filter( lambda file: file.endswith(".dylib"), files)
    if files2:
        print "fyi: fix_1724 is ignoring these %d .dylib files:" % len(files2)
        print "\n".join(files2)
        print
        
    files = filter( lambda file: file.endswith(".so"), files)
    print "fyi: fix_1724 will scan %d .so files" % (len(files),)

    count = 0
    for file in files:
        old = get_md5(file)
        system("install_name_tool -change "
                      "/Library/Frameworks/Python.framework/Versions/2.3/Python "
               "/System/Library/Frameworks/Python.framework/Versions/2.3/Python '%s'" % file, noprint = True)
        new = get_md5(file)
        if old != new:
            print file + "       [FIXED]"
            count += 1
        else:
            pass # print file + " [unchanged]"
        pass
    print "fyi: fix_1724 modified %d files" % count
    return

class AbstractMethod(Exception):
    """Indicates that something must be overloaded because it isn't usefully
    defined in the context where it's being used."""
    pass

class NanoBuildBase:
    """This is the base class for creating a installation package.
    It works for Linux, Mac OS X, and WinXP.
       It is instantiated in this module's main() function, then additional
    attributes are assigned (sourceDirectory) and additional methods called (startup_warnings, build).
    It also accesses some globals set by main, e.g. PMMT.
    """
    def  __init__(self, appname, iconfile, rootDir, version, relNo, stat, tag, qtversion = None):
        self.currentPath = os.getcwd() # Current working directory
        self.rootPath = rootDir # sub-directory where the executable and temporary files are stored
        self.appName = appname # Application name, e.g., 'NanoEngineer-1'
        self.iconFile = iconfile # The icon file name
        self.version = version # version number, e.g. '0.7'
        self.qtversion = qtversion
        assert qtversion in ('3','4')
        self.Qt3_flag = (qtversion == '3')
        self.Qt4_flag = (qtversion == '4')
        print "will build for Qt%s" % (qtversion,)
        self.releaseNo = relNo # release number, e.g. '1' (can be missing; presumably actual value is then '')
        if self.releaseNo:
            self.fullversion = "%s.%s" % (self.version, self.releaseNo) #bruce 060420 to help support missing self.releaseNo
        else:
            self.fullversion = self.version
        self.status = stat # release status, e.g. 'a', 'b', which mean 'Alpha', 'Beta' respectively. [or missing???]
        self.cvsTag = tag # cvs tag name that you want to use to build the package, without it,
        # it will just use the current version in cvs repository.
        self.sourceDirectory = None # For debug: if you want local sources instead of real
        # cvs checkouts, specify a directory containing cad and sim trees.

        self.atomPath = os.path.join(self.rootPath, 'atom')
            # NOTE: there is no need to rename this path to end with 'main' -- it's used during release building
            # but is not part of the produced program. For Mac and (I think) Linux, it's arbitrary,
            # so we *could* rename it (ideally to something other than 'main' -- it's the subdirectory into which
            # we copy the sources and slightly modify them before building them, so 'sources' would make sense),
            # but for Windows I don't know if we can (without modifying other programs I don't know about),
            # so I'm leaving it unchanged for now. [bruce 070502]
        self.setupBuildSourcePath()

    def get_md5(self, file):
        return listResults("md5sum " + file + " | cut -c -32")[0] #e or use " '%s'" % file, if file could contain spaces

    def startup_warnings(self):
        """Print warnings about prerequisites, etc, to user, specific to each platform.
        """
        pass
    
    def build(self):
        '''Main build method.'''
        self.createDirectories()
        self.prepareSources()
        self.buildSourceForDistribution()
        if prematureExit:
            sys.exit(0)
        self.makePlatformPackage()

    def setupBuildSourcePath(self):
        raise AbstractMethod

    def createDirectories(self):
        """Create directories structure, return true if success"""
        if os.path.isdir(self.rootPath):
            clean(self.rootPath, cleanAll=True)
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
        """Checkout source code from cvs for the release [extended by some subclasses]"""
        os.chdir(self.atomPath)
        dirlist = ' '.join(('cad/src',
                            'cad/plugins',
                            'sim',
                            'cad/partlib',
                            'cad/licenses-common',
                            'cad/licenses-Linux',
                            'cad/licenses-Windows',
                            'cad/licenses-Mac'))
        if self.Qt3_flag: #bruce 070426
            dirlist += " cad/images"
        if self.sourceDirectory:
            # we would only do this when experimenting anyway, so we don't
            # need the restriction on cad/doc here
            ####e THIS EFFECT OF -s NEEDS TO BE DOCUMENTED! [bruce 060420 comment]
            # btw, what *is* that restriction on cad/doc (caused by cvs checkout -l, I guess)? [bruce 070426 Q]

            ## system("cp -r %s ." % os.path.join(self.sourceDirectory, "cad"))
            ## system("cp -r %s ." % os.path.join(self.sourceDirectory, "sim"))
            #bruce 070426: do this for the specific directories in dirlist (plus cad/doc), not for everything in cad
            print "(working in %s)" % os.getcwd()
            os.mkdir("cad")
            for dir1 in dirlist.split() + ["cad/doc"]:
                print "copying %s to %s" % (os.path.join(self.sourceDirectory, dir1), dir1)
                copytree( os.path.join(self.sourceDirectory, dir1), dir1 )
        elif not self.cvsTag:
            system('cvs -Q -z9 checkout -l cad/doc')
            system('cvs -Q -z9 checkout -P ' + dirlist)
        else:
            system('cvs -Q -z9 checkout -r %s -l cad/doc' % self.cvsTag)
            system('cvs -Q -z9 checkout -r %s -R %s' % (self.cvsTag, dirlist))

        # Remove all those 'CVS' directories and their entries.
        # (Maybe we could have used 'cvs export' instead of 'cvs checkout'.
        #  But that would not be enough for the self.sourceDirectory option.)
        # (Note: there are a few CVS directories which this apparently doesn't cover
        #  and which still make it into the installed package (harmlessly I presume),
        #  at least on Mac Qt3 as of bruce 070427.)
        self.removeCVSFiles('cad')
        self.removeCVSFiles('sim')

        if os.path.exists('cad/src/main.py'): #bruce 070502 permit startup python file to have this name
            self.startup_python_basename = 'main'
            print "startup python file is cad/src/main.py"
            if os.path.exists('cad/src/atom.py'):
                # presumably it's either an error, or a leftover or convenience-symlink for some developer --
                # remove it, so it can't accidently end up in the built program along with main.py 
                print "removing cad/src/atom.py from sources to build from"
                os.remove('cad/src/atom.py')
        elif os.path.exists('cad/src/atom.py'):
            self.startup_python_basename = 'atom'
            print "startup python file is cad/src/atom.py"
        else:
            assert 0, "can't find main.py or atom.py to set self.startup_python_basename"

        self.buildTarball() # For Linux only.
        print "----------Sources have been checked out or copied.\n"

    def buildSimulator(self):
        """Build the simulators (standalone and pyrex)"""
        os.chdir(os.path.normpath(os.path.join(self.atomPath, 'sim/src')))
        if os.path.isfile("simulator") and os.path.isfile("sim.so"):
            #bruce 070427 added this case; only works for OSes using .so as dll extension (should fix, easy)
            assert self.sourceDirectory, "error: simulator executable/dll exist in sources we just checked out!"
            print "\n*** not building simulators, since they were copied from your local sources ***\n"
        else:
            print "Build the simulators (standalone and pyrex)"
            system('make clean') #bruce 070427 added this, for when sim was copied
            system('make')
            system('make pyx')
            print "----------Simulators (standalone and pyrex) have been built.\n"
        return

    def buildOpenGLAccelerator(self):
        os.chdir(os.path.join(self.atomPath, 'cad/src/experimental/pyrex-opengl'))
        system('make')
        print "----------Brad G's OpenGL accelerator has been built.\n"

    PLUGINS = ['CoNTub']

    def buildPlugins(self):
        for p in self.PLUGINS:
            os.chdir(os.path.join(self.atomPath, os.path.join('cad', 'plugins', p)))
            system('make')
        print "---------- Plugins has been built.\n"

    def buildTarball(self):
        # only needed for Linux
        pass

    def copyLicenses(self):
        copytree('licenses-common', os.path.join(self.buildSourcePath, 'licenses'))

    def buildSourceForDistribution(self):
        """Freeze Python code into an executable. Where necessary, compile
        and link C code. [superclass version -- apparently not used for Mac]"""
        print "calling buildSourceForDistribution" #bruce 070426
        self.buildSimulator()
        self.buildOpenGLAccelerator()
        self.buildPlugins()
        os.chdir(os.path.join(self.atomPath,'cad'))
        copytree('doc', os.path.join(self.buildSourcePath, 'doc'))
        copytree('partlib', os.path.join(self.buildSourcePath, 'partlib'))
        if self.Qt3_flag: #bruce 070426
            # this case has probably never been tested
            copytree('images', os.path.join(self.buildSourcePath, 'images'))
                # removed for Qt4 -- probably still needed for a Qt3 build
        if self.Qt4_flag: #bruce 070426
            os.mkdir(os.path.join(self.buildSourcePath, 'src'))
            copytree('src/ui', os.path.join(self.buildSourcePath, 'src/ui')) # cad/src/ui replaces cad/images for Qt4
        copytree('plugins', os.path.join(self.buildSourcePath, 'plugins'))
        self.copyLicenses()

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
                    clean(cvsDir, True)
                    os.rmdir(cvsDir)

    def makePlatformPackage(self):
        """Packages are different for different platforms. Linux wants an RPM.
        The Mac wants a DMG. Windows wants something else. Build the package.
        """
        raise AbstractMethod

###################################################

class NanoBuildWin32(NanoBuildBase):

    def  __init__(self, appname, iconfile, rootDir, version, relNo, stat, tag, 
                  qtversion=None):
        NanoBuildBase.__init__(self, appname, iconfile, rootDir, version, 
                               relNo, stat, tag, qtversion = qtversion)
        # are we running in a Cygwin terminal or a DOS window?
        self.cygwin = (os.environ.get('TERM') == 'cygwin')

    def setupBuildSourcePath(self):
        self.buildSourcePath = os.path.join(self.rootPath, self.appName)

    def get_md5(self, file):
        return ""

    def copyLicenses(self):
        NanoBuildBase.copyLicenses(self)
        copytree('licenses-Windows', os.path.join(self.buildSourcePath, 'licenses'))

    def prepareSources(self): # Windows
        """Checkout source code from cvs for the release """
        print "\n------------------------------------------------------\nPreparing Sources"
                
        pageant = "C:/Program Files/PuTTY/pageant.exe" 
        pageant_with_quotes = "\"" + pageant + "\"" # This is required for the first arg in args for spawnv().
        
        # This should be changed to the fullpath of your CVSdude privatekey. Mark 060606.
        privatekey = "C:/cvsdude/new_polosims_privatekey.ppk"
        
        args = [pageant_with_quotes, privatekey]
        
        if not os.path.exists(pageant):
            print "Error: ", pageant, " executable not found. Please check location and try again."
            sys.exit(1)
            
        if not os.path.exists(privatekey):
            print "Error: Private key file ", privatekey, " not found. Please check location and try again."
            sys.exit(1)
            
        ret = os.spawnv(os.P_NOWAIT, pageant, args)
        if ret <= 0: raise Exception, "start " + pageant + " with key file " + privatekey + " failed."
        NanoBuildBase.prepareSources(self)

    def copyOtherSources(self):
        print "\n------------------------------------------------------\nCopying other files"
        copy('win32/wgnuplot.exe', self.binPath)
        copy(os.path.join(self.atomPath, 'sim/src', self.standaloneSimulatorName()), self.binPath)
        copy(os.path.join(self.atomPath, 'sim/src', self.pyrexSimulatorName()), self.binPath)
        copy(os.path.join(self.atomPath, 'cad/src/experimental/pyrex-opengl',
                          self.openglAcceleratorName()), self.binPath)
        copy(self.iconFile, self.buildSourcePath)
	# These DLLs are required for OpenBabel, and anything else built with the Cygwin compiler.
        copy('win32/cygwin1.dll', self.binPath)
        copy('win32/cygz.dll', self.binPath)
        copy('win32/cyginchi-0.dll', self.binPath)
	#
        copy('win32/uninst.ico', self.buildSourcePath)
        copy('win32/setup.py', os.path.join(self.atomPath,'cad/src'))
        copy(os.path.join(self.atomPath,'cad/src/RELEASENOTES.txt'), self.buildSourcePath)
        copy(os.path.join(self.atomPath,'cad/src/KnownBugs.htm'), self.buildSourcePath)
        copy(os.path.join(self.atomPath,'cad/src/README.txt'), self.rootPath)
        copy(os.path.join(self.atomPath,'cad/src/LICENSE-Win32'), self.rootPath)

    def removeGPLFiles(self):
        """Remove non gpl files (Windows only)"""
        if self.Qt4_flag:
            #bruce 070427 added this case
            print "\n------------------------------------------------------\nNot removing GPL Files (they're allowed in Qt4)"
        else:            
            print "\n------------------------------------------------------\nRemoving GPL Files"
            srcPath = os.path.join(self.atomPath,'cad/src/')
            entries = os.listdir(srcPath)
            for entry in entries[:]:
                file = os.path.join(srcPath, entry)
                if os.path.isfile(file) and entry.startswith('gpl_'):
                    os.remove(file)
                    print "File removed: ", entry
            print "Done"
        return
    
    def standaloneSimulatorName(self):
        return "simulator.exe"

    def pyrexSimulatorName(self):
        return "sim.dll"

    def openglAcceleratorName(self):
        return "quux.dll"

    def freezePythonExecutable(self): # Windows
        print "\n------------------------------------------------------\nFreezing Python Executable"
        self.removeGPLFiles()
        try:
            system('python setup.py py2exe --includes=sip,dbhash --excludes=OpenGL -d\"' +
                   os.path.join(self.buildSourcePath, 'program') + '\"' )
        except NonZeroExitStatus:
            # this happens, apparently not a problem
            print "Warning, exit status for 'python setup.py py2exe' was not zero"

    def createIssFile(self, issFile, appName, sourceDir, status):
        """Create the iss file (script) to build package on Windows.  The iss script
        contains all the instructions for the installation package.
        """
        version = self.version
        print "\n------------------------------------------------------\nCreating Inno Setup configuration script"
        isf = open(issFile, 'w')
        isf.write("; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES! \n\n")
        isf.write("[Setup]\n")
        isf.write("AppName=%s\n" % appName)
        appnamever = appName + " v" + self.fullversion #bruce 060420 simplified this code to use self.fullversion
        ver = "v%s" % self.fullversion
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
        ### FIX: I am not sure whether/when "atom.exe" in the following two statements should be replaced
        # with "%s.exe" % self.startup_python_basename (or perhaps just with "main.exe" if there is no need
        # to build for Windows from old sources). I am also not sure what else (outside of this file)
        # needs to have 'atom' replaced by 'main', for Windows release building. [bruce 070502]
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
        if self.cygwin:
            print "pwd", listResults("pwd")[0]
        else:
            print "pwd", listResults("cd")[0]
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
        copy('win32/glut32.dll', os.path.join(self.buildSourcePath, 'program'))
        print "glut32.dll ...copied"
        copy('win32/msvcr71.dll', os.path.join(self.buildSourcePath, 'program'))
        print "msvcr71.dll ...copied"
        #ninad070501: copy QtSvg4.dll to 'program' dir (needed to fix bug2337)
        copy('C:/Qt/4.2.2/bin/QtSvg4.dll', os.path.join(self.buildSourcePath, 'program'))
        print "QtSvg4.dll ...copied"

    def makePlatformPackage(self):
        self._addModuleToZip('program/library.zip', 'OpenGL')
        self._addDLLs()
        issFile = os.path.join(self.rootPath, 'setup.iss')
        print "self.status: ", self.status
        self.createIssFile(issFile, self.appName,
                            self.buildSourcePath, self.status)
        outputFile = PMMT + '-w32'
        # The Inno Setup directory containing "iscc.exe" must be in your PATH (i.e. C:/Program Files/Inno Setup 5). Mark 060606.
        # Run Inno Setup command to build the install package for Windows (only).
        commLine = 'iscc  /Q  /O"' + self.rootPath + '" /F"' + outputFile + '"  "' + issFile + '"'
        ret = system(commLine)
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

    def copyLicenses(self):
        NanoBuildBase.copyLicenses(self)
        copytree('licenses-Linux', os.path.join(self.buildSourcePath, 'licenses'))

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

    def freezePythonExecutable(self): # Linux
        # Mandrake 10.1 calls it 'libsip', Mandriva 2006 calls it 'sip'
        try:
            cmd = ('FreezePython --include-modules=libsip,dbhash' +
                   ' --exclude-modules=OpenGL' +
                   ' --install-dir=' + self.progPath +
                   ' --target-name=' + self.appName + ' %s.py' % self.startup_python_basename)
            system(cmd)
        except:
            cmd = ('FreezePython --include-modules=sip,dbhash' +
                   ' --exclude-modules=OpenGL' +
                   ' --install-dir=' + self.progPath +
                   ' --target-name=' + self.appName + ' %s.py' % self.startup_python_basename)
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
        #if releaseNo:
        #    spf.write("Release: %s\n" % releaseNo)
        #else:
        #    spf.write("Release: 0\n")
        requirements = [ ]
        pyver = sys.version[:3]
        if pyver == '2.4':
            spf.write("Release: python24\n")
            requirements.append('python >= 2.4, python < 2.5')
        elif pyver == '2.3':
            spf.write("Release: python23\n")
            requirements.append('python >= 2.3, python < 2.4')
        else:
            raise Exception("Must use Python 2.3 or 2.4")
        if requirements:
            requirements = "Requires: " + " ".join(requirements)
        else:
            requirements = ""
        otherStuff = """License: GPL
Group: Applications/CAD
Source: project.tgz
URL: http://nanoengineer-1.net/mediawiki/index.php
Distribution: NanoEngineer-1
Vendor: Nanorex, Inc.
Packager: Nanorex, Inc.
%(requirements)s

%%description
NanoEngineer-1 includes a molecular design module that combines
capabilities found in traditional chemistry modeling software
with features found in popular 3-D mechanical CAD systems. With
NanoEngineer-1, users can design atomically precise assemblies
from a variety of stiff covalent structures, including diamond
lattice frameworks. A parts library of molecular components is
also included containing tubes, shafts, bearings, gears, joints,
and springs that can be easily inserted and integrated with an
existing assembly.

%%prep

%%setup

%%build

%%install
# This stuff DOES NOT RUN on the end user's machine!
# If it did, we could set up a desktop icon here.
# And we could set the BROWSER environment variable here.
# But alas, these things must be release-noted. An RPM can't do them.

%%post
#!/bin/sh
# Set up a desktop icon.
# I checked a NanoEngineer-1.desktop file into cad/src, but I don't
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

%%files
%%defattr(755, root, root, 755)
""" % { "requirements": requirements }
        spf.write(otherStuff)
        spf.write(sourceDir + "\n")
        spf.close()
        print "----RPM building specification file has been written."

    def _hey_wake_up(self):
        # We'll need a root password, awaken the release engineer.
        try:
            os.system("mpg123 wake_up.mp3")
        except:
            pass

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
        self._hey_wake_up()
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

    LIBAQUA_MD5 = "c43f7944d0d7ed42f82e2a9ba45687d0"

    def get_md5(self, file):
        return listResults("md5 " + file + " | cut -d'=' -f 2 | cut -c 2-")[0] #e or use " '%s'" % file, if file could contain spaces

    def startup_warnings(self): #bruce 060420
        print "* * * WARNING: after most of this script has finished, we'll run a sudo chown root"
        print "command which might ask for your root password."
        print
        print "(making sure some required imports will succeed)"
        import py2app as _junk # required by 'python setup.py py2app'
            #e Note: we should print py2app path and version. For Mac Qt3, Ninad used py2app 0.1.5.
            # For Qt4, so far 0.1.5 and 0.3.5 were tried and didn't work. Bruce plans to try 0.3.6.
            # Some pathnames in the app have changed and will require compensation here and/or in Python sources.
        print "py2app.__version__ = %r (not controlled by autoBuild.py -- up to you whether it's right)" % (_junk.__version__,)
            #bruce 070427
        ##e should also make sure the files we'll later copy are there, e.g. gnuplot
        libaquaterm_path = os.path.join(self.currentPath, 'libaquaterm.1.0.0.dylib')
        its_md5 = self.get_md5( libaquaterm_path )
        assert its_md5 == self.LIBAQUA_MD5, "MD5 of %r should be %r but is %r" % ( libaquaterm_path, self.LIBAQUA_MD5, its_md5 )
        # see if PackageMaker is findable [bruce 070427]
        print 
        print "If the following says \"command not found\" rather than printing some"
        print "PackageMaker help info, abort this command and fix your shell path:"
        print
        try:
            system('export PATH=$PATH:/Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS;'\
                   'PackageMaker -help')
        except NonZeroExitStatus:
            pass # it's usually exit status 1, so nevermind
        print
        # test that the developer switched to the proper Qt version corresponding to what we're building [bruce 070429]
        if self.Qt3_flag:
            print "Checking whether Qt3 import will succeed; if not, we might fail silently, bus error, or traceback"
                # what actually happens to me is a traceback for "ImportError: No module named qt" [bruce 070429]
            print "(which probably means you are using a machine that can run either Qt3 or Qt4, and it's not switched"
            print " to the correct one; some developers use commands sip-3 and sip-4 to do that switching)"
            from qt import QApplication
            print "Qt3 import succeeded (from qt import QApplication)"
            print
        if self.Qt4_flag:
            print "Checking whether Qt4 import will succeed; if not, we might fail silently, bus error, or traceback"
                # what actually happens to me is a Bus Error, exit code 138 [bruce 070429]
            print "(which probably means you are using a machine that can run either Qt3 or Qt4, and it's not switched"
            print " to the correct one; some developers use commands sip-3 and sip-4 to do that switching)"
            from PyQt4.Qt import QApplication
            print "Qt4 import succeeded (from PyQt4.Qt import QApplication)"
            print
        return
    
    def createMiddleDirectories(self):
        os.mkdir(self.installRootPath)
        os.mkdir(self.diskImagePath)
        os.mkdir(self.resourcePath)

    def copyLicenses(self):
        NanoBuildBase.copyLicenses(self)
        copytree('licenses-Mac', os.path.join(self.buildSourcePath, 'licenses'))

    def buildSourceForDistribution(self): # Mac
        """Pack source together for distribution [Mac version, replaces superclass version]"""
        print "calling buildSourceForDistribution (Mac version)"
        self.buildSimulator()
        self.buildOpenGLAccelerator()
        self.buildPlugins()
        #
        #
        os.chdir(self.currentPath)
        copy('background.jpg', self.resourcePath)
        ## copy('libaquaterm.1.0.0.dylib', self.buildSourcePath) # done later, so gets directly into right place
        copy('setup.py', os.path.join(self.atomPath,'cad/src'))
        #
        #
        self.freezePythonExecutable()
        #
        #
        appname = self.appName + '.app'
        cfdir = os.path.join(self.buildSourcePath, appname, 'Contents', 'Frameworks')
        assert os.path.isdir(cfdir) #bruce 060420
        #bruce 060420 moved this here, replacing postflight script's move, making postflight script unnecessary
        if os.path.exists( os.path.join(cfdir, 'libaquaterm.1.0.0.dylib') ):
            #bruce 070429 added this check, since the one we're copying looks suspicious in its otool -L output;
            # for me, Qt3, this doesn't happen, btw
            print "note: libaquaterm.1.0.0.dylib is overwriting one which was put in place by py2app" # and maybe it ought not to...
        copy(os.path.join(self.currentPath, 'libaquaterm.1.0.0.dylib'), cfdir)
        # wware 060428 record lib md5s before prebinding step
        system("(cd %s; md5 * > original-md5s.txt)" % cfdir)

        os.chdir(os.path.join(self.atomPath,'cad'))
        copytree('doc', os.path.join(self.buildSourcePath, appname, 'Contents/doc'))

        if self.Qt3_flag: #bruce 070426
            copytree('images', os.path.join(self.buildSourcePath, appname, 'Contents/images'))
                # removed for Qt4 -- might be needed for a Qt3 build
        if self.Qt4_flag: #bruce 070426
            # the destination directory is a guess by bruce 070428 -- it hasn't been tried, or compared with Qt4 sources;
            # see also the superclass version, which does mkdir src and copies to src/ui
            os.mkdir(os.path.join(self.buildSourcePath, appname, 'Contents/src'))
            copytree('src/ui', os.path.join(self.buildSourcePath, appname, 'Contents/src/ui'))
            
        # wware 061229 - not sure if this is correct
        ## copytree('ui', os.path.join(self.buildSourcePath, appname, 'Contents/ui'))
            # [bruce 070426 comments: in Qt3 there is no ui dir anywhere.
            #  In Qt4 there is cad/src/ui (handled in superclass method, which we don't call),
            #  but not cad/ui which this line looks for.]
        
        copytree('plugins', os.path.join(self.buildSourcePath, appname, 'Contents', 'plugins'))
        # Put the partlib outside the app bundle, where users can see its internal
        # directories and files. Put a symbolic link to it from the normal
        # location inside the bundle.
        copytree('partlib', os.path.join(self.buildSourcePath, 'partlib'))
        system('(cd %s; ln -s ../../partlib .)' %
               os.path.join(self.buildSourcePath, appname, 'Contents'))
        self.copyLicenses()
        #
        #
        self.binPath = binPath = os.path.join(self.buildSourcePath, appname, 'Contents/bin')
        os.mkdir(binPath)
        #bruce 060420 zapping this, since redundant with new chmod code done later for all files (and 755 should be 775 anyway):
        ##        ne1files = listResults("find " + self.buildSourcePath + " -name NanoEngineer-1.py")
        ##        for f in ne1files:
        ##            os.chmod(f, 0755)
        self.copyOtherSources()
        self.rewrite_load_commands() #bruce 070429 (to fix bug 1724)
        print "------All python modules are packaged together. (Mac version)"


    def freezePythonExecutable(self): # Mac
        os.chdir(os.path.join(self.atomPath,'cad/src'))
        os.rename('%s.py' % self.startup_python_basename, self.appName + '.py')
        
        #bruce 060420 adding more excludes:
        # _tkinter (otherwise it copies /Library/Frameworks/{Tcl,Tk}.framework into Contents/Frameworks)
        # (it already had OpenGL, I don't know why; instead it copies it manually, later)
        
        #bruce 070427 comment: consider using these py2app options:
        # --xref, for html module crossreference output (added in py2app 0.3.0) [not tried]
        # --graph (produces a text file like /tmp/foo/installRoot/NanoEngineer-1-0.9/NanoEngineer-1.dot,
        #    which shows how specific modules got included -- useful for adding to --excludes or --dylib-excludes --
        #    works in py2app 0.2.0)
        # --debug-modulegraph [not tried]
        # --dry-run -- this seems to have a bug -- at least, when I used it I got this error:
        ##          File "/Library/Python/2.3/py2app/py2app/util.py", line 183, in byte_compile
        ##            if mod.filename == mod.identifier:
        ##        AttributeError: 'NoneType' object has no attribute 'filename'
        #   but it did speed things up and showed me the .dot file and the modules it made loaders for, so it might be useful.

        # (btw, which setup.py is running? not the one in cad/src; rather, the one in your current dir when you run autoBuild.)

        #bruce 070427 revised excludes-related options
        # (note: if excludes or dylib_excludes can ever be empty, the following has to be revised)
        debug_options = "--graph" # this works in py2app 0.2.0 -- not sure about 0.1.5 (which Ninad sometimes uses for Qt3)
        excludes = ['OpenGL', '_tkinter'] # note: py2app might well handle PyOpenGL better than we do, in versions that have the
            # recipe for it; never tried AFAIK. Our own binary of PyOpenGL (OpenGL package) is defective in load commands re bug 1724;
            # this is now fixed in rewrite_load_commands as of 070429.
        dylib_excludes = []
        if not self.Qt4_flag:
            excludes.append('PyQt4')
                # PyQt4 has to be in excludes -- didn't work when in dylib_excludes alone
            dylib_excludes.append('PyQt4')
                #k probably not needed, but leaving it out is untested,
                # and this string can't be empty anyway due to format string below
            #FIX sometime -- also add the qtxxx we don't need
        if not self.Qt3_flag:
            ### this case has been run, but is still effectively UNTESTED since a working Mac Qt4 release has not yet been built
            # [as of bruce 070429]; I don't know if a file extension is needed on these, or a dotted name,
            # or which exclude variable matters here [#e tho i could find out by looking in the .dot file I made recently]
            for mod in ("qtsql", "qttable", "qtcanvas", "qt", "qtext", "qtui", "qtgl", "qtxml", "qtnetwork"):
                excludes.append(mod)
                dylib_excludes.append(mod)
        assert excludes
        assert dylib_excludes # otherwise format string below needs revision
        excludes = ','.join(excludes)
        dylib_excludes = ','.join(dylib_excludes)

        system("python setup.py py2app %s --includes=sip --excludes=%s --dylib-excludes=%s --iconfile %s  -d %s" %
               (debug_options, excludes, dylib_excludes, self.iconFile, self.buildSourcePath))

        # move .dot file if one was produced [bruce 070428]
        dotold = os.path.join(self.buildSourcePath, self.appName + '.dot')
        dotnew = os.path.join(self.buildSourcePath, self.appName + '.app', 'Contents', 'Frameworks', self.appName + '.dot')
        if os.path.isfile( dotold):
            print "moving %s to %s" % (dotold, dotnew)
            os.rename( dotold, dotnew)

        # see also self.rewrite_load_commands(), called later
        return

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
        if os.path.exists(os.path.join(self.atomPath, 'cad/src/all_mac_imports.py')):
##            copy(os.path.join(self.atomPath, 'cad/src/all_mac_imports.py'),
##                              os.path.join(self.buildSourcePath, appname, 'Contents/Resources'))
##            print "copied all_mac_imports.py into Contents/Resources"
            # no longer needed -- autoBuild can even build old sources (that have this file) without needing
            # to copy it into the place where old versions of atom.py (aka main.py) will look for it
            # (and will build a better app that way -- faster startup) [bruce 070502]
            print "not copying obsolete file all_mac_imports.py into Contents/Resources"
            print "(not sure if it will get compiled into the built program)"
        else:
            print "(all_mac_imports.py was not found -- that's good, it's obsolete)"
                #bruce 070427 added this case; as of 070429 it should be normal
        copy('/usr/local/bin/gnuplot', self.binPath)
        #Copy rungms script into 'bin' directory
        copy(os.path.join(self.atomPath,'cad/src/rungms'), self.binPath)
        
        #Copy OpenGL package into buildSource/program
        #[bruce comment 070427: warning about a platform difference (I don't know why it's this way):
        # this OpenGL copy is done here in copyOtherSources for Mac, and done for all of site-packages
        # (I'm not sure if that's more than just OpenGL),
        # but it's done in freezePythonExecutable for Linux, and only for OpenGL specifically]
        #bruce 070427 change: py2app 0.1.5 and 0.2 use Contents/Resources/Python (as did the code below),
        # but some later py2apps use Contents/Resources/lib/python2.3. I'll revise this code to figure out
        # which one has already been created, print it and use it, or complain if it's more than one.
        ### BTW this might also require adaptation in cad/src/atom.py (soon to be renamed to main.py) and/or other files.
        dirs_to_look_for = (
            'Contents/Resources/Python',
            'Contents/Resources/lib/python2.3',
            'Contents/Resources/lib/python2.4', # guessing this might be possible
            'Contents/Resources/lib/python2.5', # ditto
            )
        dirs_to_look_for = map( lambda dir1: os.path.join(self.buildSourcePath, appname, dir1), dirs_to_look_for )
        pythondirs = filter( lambda dir1: os.path.exists(dir1), dirs_to_look_for )
        if len(pythondirs) != 1:
            assert 0, "error: don't know where to copy site-packages: of these, we needed exactly one to exist:\n%s" % \
                  '\n'.join(dirs_to_look_for)
        dir1 = pythondirs[0]
        assert os.path.isdir(dir1)
        print "will copy site-packages to", dir1
        ## self.contents_resources_python = dir1 # this value is not yet needed elsewhere
        # old code was equivalent to:
        ## dir1 = os.path.join(self.buildSourcePath, appname, 'Contents/Resources/Python')
        copytree('site-packages', os.path.join( dir1, 'site-packages'))
        
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

    def rewrite_load_commands(self): #bruce 070429 (to fix bug 1724)
        # rewrite load commands to fix bug 1724 -- a recent-enough py2app might do this better than we do
        # (more generally, and correctly for Python version != 2.3.x),
        # but (1) it wasn't doing it in the version that built bruce's local A7, for e.g. multiarray.so,
        # (2) we're still copying in some .so's independently of py2app (not sure we still ought to be, but we are),
        # which need this (namely OpenGL).
        fix_1724(self.buildSourcePath, self.get_md5) #bruce 070429
            #e someday we might have to protect get_md5 from spaces in filenames
        return
    
    def setupBuildSourcePath(self):
        self.installRootPath = os.path.join(self.rootPath, 'installRoot')
        self.buildSourcePath = os.path.join(self.installRootPath, PMMT)
        self.diskImagePath = os.path.join(self.rootPath, 'diskImage')
        self.resourcePath = os.path.join(self.rootPath, 'resources')
        assert not ' ' in self.buildSourcePath, "sorry, space character is not allowed in %r" % (self.buildSourcePath,) #bruce 070429

    def createWelcomeFile(self, welcomeFile):
        """Write the welcome file for Mac package installer """
        wf = open(welcomeFile, 'w')
        message = (("Welcome to %s v%s %s. You will be guided through the steps " + #bruce 060420 used fullversion to support missing releaseNo
                    "necessary to install this software. By default, this software " +
                    "will be installed into the /Applications folder with all files " +
                    "contained in their own sub-folder, %s.\n") %
                   (self.appName, self.fullversion, self.status, os.path.basename(self.buildSourcePath)))
        wf.write(message)
        wf.close()
        print "----Welcome file has been written."

#bruce 060420 postflight script is no longer needed, but let the code remain,
# in case we need it later for something (note, this version was not tested since last changed):
    # http://developer1.apple.com/documentation/DeveloperTools/Conceptual/SoftwareDistribution/Concepts/sd_pre_post_processing.html
##    def _writePostFlightFile(self, pfFile):
##        """Write the postflight file Mac Package Installer """
##        instPath = os.path.basename(self.buildSourcePath)   # "NanoEngineer-1-0.0.6"
##        appname = self.appName + '.app'
##        cf = os.path.join(instPath, appname, 'Contents/Frameworks')
##        # $2/instPath --> /Applications/NanoEngineer-1-0.0.6
##        # $2/cf --> /Applications/NanoEngineer-1-0.0.6/NanoEngineer-1.app/Contents/Frameworks
##        pf  = open(pfFile, 'w')
##        pf.write("""#!/bin/bash
##mv "$2/%s/libaquaterm.1.0.0.dylib" "$2/%s"
##exit 0
##""" % (instPath, cf )) ## , instPath, instPath
###bruce 060420 removed the following from that string, since superseded by a better fix
### (and it didn't handle spaces in $2 either); also fixed remaining $2's above to tolerate spaces
####(cd $2/%s; find . -type d -exec chmod ugo+rx {} \;)
####(cd $2/%s; find . -type f -exec chmod ugo+r {} \;)
##        pf.close()
##        from stat import S_IREAD, S_IEXEC, S_IROTH, S_IXOTH  
##        os.chmod(pfFile, S_IREAD | S_IEXEC | S_IROTH | S_IXOTH)
##        print "----Postflight file has been written."

    def createPlistFile(self, plistFile,  appName, majorVer, minorVer,  releaseNo):
        """ Write InfoPlist file to build package of PackageMaker (Mac OS X)."""
        plf = open(plistFile, 'w')
        titleDoc = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
        <key>CFBundleGetInfoString</key>
      """
        if releaseNo:
            fullversion = majorVer + '.' + minorVer + '.' + releaseNo
        else:
            #bruce 060420 to support missing releaseNo
            fullversion = majorVer + '.' + minorVer
        plf.write(titleDoc)
        plf.write('<string>' + appName + ' Version ' + fullversion + '</string>\n')
        nextDoc = "\t<key>CFBundleIdentifier</key>\n\t<string>www.nanorex.com</string>\n\t<key>CFBundleName</key>\n"
        plf.write(nextDoc)
        plf.write('\t<string>' + appName + '-' + fullversion + '</string>\n')
        plf.write('\t<key>CFBundleShortVersionString</key>\n')
        plf.write('\t<string>' + fullversion + '</string>\n')
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
        #bruce 060420 no longer needed
        ##        postflightFile = os.path.join(self.resourcePath, 'postflight')
        ##        self._writePostFlightFile(postflightFile)
        plistFile = os.path.join(self.rootPath, 'Info.plist')
        words = self.version.split('.')
        self.createPlistFile(plistFile, self.appName, words[0], words[1], self.releaseNo)
        pkgName = os.path.join(self.diskImagePath, PMMT + '.pkg')
        descrip = os.path.join(self.currentPath, 'Description.plist')
        # Fix file permissions and ownership, following recommendations of section on "Setting File Ownership and Permissions" in
        # http://developer1.apple.com/documentation/DeveloperTools/Conceptual/SoftwareDistribution/Concepts/sd_permissions_author.html
        # which says all files and dirs should be user root, group admin, permissions 775 or in some cases 664,
        # and this should be done before PackageMaker, not in the postflight script.
        # It's too hard for us to decide which ones need 775, and it's ok for most of them to be 775 even if they don't need it,
        # so I'll just make them all 775 except for selected user-visible files for which +x is ugly.
        # [bruce 060420]
        print "fixing file permissions and ownership, in %s" % self.buildSourcePath
        system("chmod -R 775 %s" % self.buildSourcePath)
        for no_x_pattern in [ "*.txt", "*.htm", "partlib/*/*.mmp", "partlib/*/*/*.mmp" ]:
            system("chmod ugo-x %s/%s" % ( self.buildSourcePath, no_x_pattern))
        system("chmod -R o+w %s/%s" % ( self.buildSourcePath, 'partlib' ))
        # we want to do this to directories for sure; not sure about files, but ok for now
        # redundant now:
        ##        for other_write_pattern in [ "partlib/*/*.mmp", "partlib/*/*/*.mmp" ]:
        ##            system("chmod o+w %s/%s" % ( self.buildSourcePath, other_write_pattern))
        system("chgrp -R admin %s" % self.buildSourcePath)
        print
        print "Now we will do sudo chown -R root %s -- *** THIS MIGHT REQUIRE YOUR ROOT PASSWORD:\7" % self.buildSourcePath
        system("sudo chown -R root %s" % self.buildSourcePath)
            # do chown root last, since after that we can't change things inside (unless running as root)
        print "done fixing file permissions and ownership"
        print
        print "*** AT THIS POINT (or when we're done), YOU CAN TEST THE RELEASE" 
        print "without installing it,"
        print "*** by using this shell command:"
        print "***"
        print "*** % open %s" % self.buildSourcePath ###k [bruce 070429] UNTESTED
        print
        # Run PackageMaker to build the final installation package
        # Note: on some Macs, PackageMaker resides in /Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS
        # so this needs to be on your shell path. Maybe we should add it here... did that [bruce 070427], it seems to work.
        # It would also be nice to detect whether PackageMaker is present. PackageMaker -help prints some info and exits
        # with exit status 1; missing commands (in tcsh anyway) print an error message and exit with exit status 1. Hmm.
        # I didn't try to detect this, but I added some prints in startup_warnings() which ought to tell the user whether it's working.
        try:
            system('export PATH=$PATH:/Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS;'\
                   'PackageMaker -build -p ' + pkgName + ' -f ' + self.installRootPath +
                   ' -r ' + self.resourcePath + ' -i ' + plistFile + ' -d ' + descrip)
        except NonZeroExitStatus:
            # this happens, apparently not a problem
            # [actually it can be a problem when this is the reason: sh: line 1: PackageMaker: command not found
            #  and I don't yet know whether /Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker
            #  will be the right thing to run. I will try it (in my tcsh):
            #  % set path = ( /Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS $path )
            #  This seemed to work.
            #  --bruce 060420
            # ]
            print "Warning, exit status for PackageMaker was not zero (this is common)"
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
    -o output directory.  Default is $CWD/NanoEngineer-1.maj.min.tiny/NanoEngineer-1
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
    shortargs = 'ho:i:q:s:t:v:p'
    longargs = ['help', 'outdir=', 'iconfile=', 'Qt=', 'sourcedir=', 'tag=', 'version=', 'premature-exit']
   
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortargs, longargs)
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    currentDir = os.getcwd()
    appName = "NanoEngineer-1"
    rootDir = None
    if sys.platform == 'win32':
          iconFile = os.path.join(currentDir, 'win32/nanorex_48x.ico')
    elif sys.platform == 'darwin':
        iconFile = os.path.join(currentDir, 'nanorex.icns')
    else:
       iconFile = None

    status = None
    cvsTag = None
    sourceDirectory = None
    specialVersion = None
    qtversion = '4' # default value [bruce 070426 added this and its -q / --Qt options]
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--outdir"):
            rootDir = os.path.join(currentDir, a)
        elif o in ("-i", "--iconfile"):
            iconFile = os.path.join(currentDir, a)
        elif o in ("-q", "--Qt"):
            o1 = o
            if o1 == "--Qt":
                o1 += ' ' #k or is it '='?
            assert a in ("3", "4"), "please specify either %s%s or %s%s" % (o1,"3",o1,"4")
            qtversion = a
        elif o in ("-s", "--sourcedir"):
            sourceDirectory = a
        elif o in ("-t", "--tag"):
            cvsTag = a
        elif o in ("-v", "--version"):
            specialVersion = a
        elif o in ("-p", "--premature-exit"):
            global prematureExit
            prematureExit = True
        else:
            assert 0, "unknown option: (%r, %r)" % (o, a)

    sp = sys.path[:]
    cadDir = os.path.join(os.getcwd(), "cad")
    if sourceDirectory:
        system("rm -rf " + cadDir) # [note: this is a local def, which prints the command before passing it to os.system]
        ## system("cp -r %s %s" % (os.path.join(sourceDirectory, "cad"), cadDir))
        # bruce 070426 replaced that with the following, to copy only the version.py file:
        os.mkdir(cadDir)
        os.mkdir(os.path.join(cadDir, "src"))
        system("cp -r %s %s" % (os.path.join(sourceDirectory, "cad", "src", "version.py"),
                                os.path.join(cadDir, "src", "version.py")))
    elif cvsTag:
        # Get the version information by checking out only the version.py file
        system("cvs -Q -z9 checkout -r %s cad/src/version.py" % cvsTag)
    else:
        # Get the version information by checking out only the version.py file
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
    sys.path = sp[:]

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
                        relNo, VERSION.releaseType, cvsTag, qtversion = qtversion)
    builder.sourceDirectory = sourceDirectory
    print
    builder.startup_warnings() #bruce 060420 (it would be nice to do this earlier #e)
    clean(cadDir, True)
    os.rmdir(cadDir)
    builder.build()

    # The clean() method chokes on the symbolic link that I needed to use for the partlib
    # on the Mac. It was already broken on Linux, possibly for the same reason. So only
    # do cleanup on Windows.
    if sys.platform == "win32":
        clean(rootDir)

    if os.path.isdir(rootDir) and not os.listdir(rootDir): os.rmdir(rootDir)

    return

if __name__ == '__main__':
    main()

# end

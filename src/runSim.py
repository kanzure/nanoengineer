# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

from SimSetupDialog import *
from fileIO import writemmp
from commands import *
from debug import *
import os, sys, re, signal

def fileparse(name):
    """breaks name into directory, main name, and extension in a tuple.
    fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    m=re.match("(.*\/)*([^\.]+)(\..*)?",name)
    return ((m.group(1) or "./"), m.group(2), (m.group(3) or ""))
    
class runSim(SimSetupDialog):
    def __init__(self, assy):
        SimSetupDialog.__init__(self)
        self.assy = assy
        self.nframes = 900
        self.temp = 300
        self.stepsper = 10
        self.timestep = 10
        self.fileform = ''
        self.mext = '.xyz'


    def saveFilePressed(self):
        if self.assy.filename:
#            dir, fil, ext = fileparse(self.assy.filename)
            sdir = self.assy.filename
        else: 
#            dir, fil = "./", self.assy.name
            sdir = globalParms['WorkingDirectory']

        if self.mext == ".xyz": sfilter = QString("XYZ Format (*.xyz)")
        else: sfilter = QString("Data Part Binary (*.dpb)")
        
        fn = QFileDialog.getSaveFileName(sdir,
                    "XYZ Format (*.xyz);;Data Part Binary (*.dpb)",
                    self, "IDONTKNOWWHATTHISIS",
                    "Save As",
                    sfilter)
        
        if fn:
            fn = str(fn)
            dir, fil, ext2 = fileparse(fn)
            ext =str(sfilter[-5:-1]) # Get "ext" from the sfilter. It *can* be different from "ext2"!!! - Mark
            safile = dir + fil + ext # full path of "Save As" filename
            
            if os.path.exists(safile): # ...and if the "Save As" file exists...

                # ... confirm overwrite of the existing file.
                ret = QMessageBox.warning( self, self.name(),
                        "The file \"" + fil + ext + "\" already exists.\n"\
                        "Do you want to overwrite the existing file or cancel?",
                        "&Overwrite", "&Cancel", None,
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                if ret==1: # The user cancelled
                    self.assy.w.statusBar.message( "Cancelled.  File not saved." )
                    return # Cancel clicked or Alt+C pressed or Escape pressed
            
            self.mext = ext

            if ext == '.dpb': # DPB file format
                ftype = 'DPB'
                self.fileform = ''
            else: # XYZ file format
                ftype = 'XYZ'
                self.fileform = '-x'

            self.hide() # Hide simulator dialog window.
            
            r = self.saveMovie(safile)
            
            if not r: # Movie file saved successfully.
                self.assy.w.statusBar.message( ftype + " file saved: " + safile)


    def createMoviePressed(self):
        """Creates a DPB (movie) file of the current part.  
        The part does not have to be saved
        as an MMP file first, as it used to.
        """
        QDialog.accept(self)
        if self.assy.filename: # Could be MMP or PDB file.
            moviefile = self.assy.filename[:-4] + '.dpb'
        else: 
            tmpFilePath = self.assy.w.tmpFilePath # ~/nanorex directory
            moviefile = os.path.join(tmpFilePath, "Untitled.dpb")

        r = self.saveMovie(moviefile)
        
        if not r: # Movie file saved successfully.
            msg = "Total time to create movie file: %d seconds" % self.assy.w.progressbar.duration
            self.assy.w.statusBar.message(msg) 
            msg = "Movie written to [" + moviefile + "]."\
                        "To play movie, click on the <b>Movie Player</b> <img source=\"movieicon\"> icon."
            # This makes a copy of the movie tool icon to put in the HistoryMegawidget.
            QMimeSourceFactory.defaultFactory().setPixmap( "movieicon", 
                        self.assy.w.toolsMoviePlayerAction.iconSet().pixmap() )
            self.assy.w.statusBar.message(msg)
            
            self.assy.moviename = moviefile

        return

    def saveMovie(self, moviefile):
        """Creates a moviefile.  
        A moviefile can be either a DPB file or an XYZ trajectory file.
        A DPB file is a binary trajectory file. An XYZ file is a text file.
        """
        # When creating a movie file, we cwd to tmpFilePath and spawn the
        # simulator.  The reason we do this is because os.spawn (on Win32
        # systems) will not work if there are spaces in any of the arguments
        # supplied to it.  Often, there are spaces in the file and directory
        # names on Win32 systems.  To get around this problem, we chdir to 
        # assy.w.tmpFilePath and run the simulator on "mmpfile", generating "dpbfile".
        # Then we rename dpbfile to moviefile and return to the original working directory.
        #
        # Note: If "moviefile" is an XYZ trajectory file, the simulator writes directly to
        # the file without renaming it.  This is because the progress bar often completes
        # before the spawned simulator completes writing the file.  If we attempt to 
        # rename the file before the simulator has completed, we get a "permission 
        # denied" error.
        # - Mark 050106
        
        # When creating an XYZ file, the simulator writes directly to the XYZ file
        if self.fileform == "-x": 
        
            # Make sure there is no space in the XYZ filename (Win32 only).
            if sys.platform == 'win32':
                m = re.search(' +',  moviefile)
                if  m:
                    QMessageBox.warning(self, "Problem", "XYZ file names cannot have a space.  Try again.\n")
                    return -1

            dpbfile = moviefile
        
        # If we are creating a DPB file, the simulator writes to "simulate.dpb",
        # then we rename it to "moviefile"
        else: dpbfile = "simulate.dpb"
        
        # We always save the current part to an MMP file.  In the future, we may want to check
        # if assy.filename is an MMP file and use it if assy.modified = 0.
        mmpfile = "simulate.mmp" 
        
        # filePath = the current directory NE-1 is running from.
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # "program" is the full path to the simulator executable.  
        program = os.path.normpath(filePath + '/../bin/simulator')
        
        # If there is a space in the path, spawnv will not work (Win32 only).
        if sys.platform == 'win32':
            m = re.search(' +',  program)
            if  m:
                QMessageBox.critical(self, "Error", 
                    "There is a space in the simulator pathname: [" + program +"]\n"\
                    "To fix, rename the NE-1 directory to a name with no spaces.")
                return -1

        # Change cursor to Wait (hourglass) cursor
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        
        # "args" = arguments for the simulator.  
        # THE TIMESTEP ARGUMENT IS MISSING ON PURPOSE.
        # The timestep argument "-s + (self.timestep)" is not supported for Alpha.
        args = [program, '-f' + str(self.nframes), '-t' + str(self.temp), '-i' + str(self.stepsper), str(self.fileform),  '-o' + dpbfile, mmpfile]
        
        # "filename.dpb" or "filename.xyz" - used below by the progress bar.
        basename = os.path.basename(moviefile) 
        
        # Tell user we're creating the movie file...
        msg = "<span style=\"color:#006600\">Simulator: Creating movie file [" + moviefile + "]</span>"
        self.assy.w.statusBar.message(msg)

        # On Win32, spawnv() has problems with a space in an argument, and
        # tmpFilePath usually has a space for Win32 systems.
        # We solve this by changing cwd to tmpFilePath, running the simulator, 
        # move the moviefile to the final location, then returning to the original wd.
        #   - Mark 050105.
        oldWorkingDir = os.getcwd()
        tmpFilePath = self.assy.w.tmpFilePath # ~/nanorex directory
        os.chdir(tmpFilePath)
            
        # READ THIS IF YOU PLAN TO CHANGE ANY CODE FOR saveMovie!
        # The placement of writemmp here is strategic.  It must come after changing
        # to "tmpFilePath" and before computing "natoms".   This ensures that saveMovie
        # will work when creating a movie for a file without an assy.alist.  Examples of this
        # situation include:
        # 1)  The part is a PDB file.
        # 2) We have chunks, but no assy.alist.  This happens when the user opens a 
        #      new part, creates something and simulates before saving as an MMP file.
        # 
        # I do not know if it was intentional, but assy.alist is not created until an mmp file 
        # is created.  We are simply taking advantage of this "feature" here.
        # - Mark 050106
        writemmp(self.assy, mmpfile, False)
        natoms = len(self.assy.alist)
            
        # Based on the way simulator.c writes an XYZ trajectory file, 
        # it is impossible to determine the exact final size.
        # This formula is an estimate.  "filesize" should never be larger than the
        # actual final size of the XYZ file, or the progress bar will never hit 100%,
        # even though the simulator finished writing the file.
        # - Mark 050105 
        if self.fileform == "-x": 
            dpbfile = moviefile
            filesize = self.nframes * ((natoms * 32) + 25) # xyz filesize (estimate)
        else: 
            filesize = (self.nframes * natoms * 3) + 4 # dpb filesize (exact)
            
        if os.path.exists(dpbfile): os.remove (dpbfile) # Delete before spawning simulator.
        
#        print  "program = ",program
#        print  "Spawnv args are %r" % (args,) # this %r remains (see above)
        
        try:
            # Remember, no spaces in "program" or "args" (Win32 only).
            kid = os.spawnv(os.P_NOWAIT, program, args)
            
            # Launch the progress bar.
            r = self.assy.w.progressbar.launch(filesize, dpbfile, "Simulate", "Writing movie file " + basename + "...", 1)
            s = None
            
            # If we have written a dbp (not xyz) file, delete moviefile so we can rename (move) dpbfile to moviefile.
            if not r and self.fileform != "-x":   
                if os.path.exists(moviefile): os.remove (moviefile)
                os.rename (dpbfile, moviefile)
        
        except: # We had an exception.
            print_compact_traceback("exception in simulation; continuing: ")
            s = "internal error (traceback printed elsewhere)"
            r = -1 # simulator failure
        
        # Change back to working directory.
        os.chdir(oldWorkingDir)
        QApplication.restoreOverrideCursor() # Restore the cursor
        
        if not r: return r # Main return
        
        if r == 1: # User pressed Abort button in progress dialog.
            self.assy.w.statusBar.message("<span style=\"color:#ff0000\">Simulator: Aborted.</span>")         
            # We should kill the kid.  For windows, we need to use Mark Hammond's Win32 extentions: 
            # Go to http://starship.python.net/crew/mhammond/ for more information.
            # - Mark 050106
            if sys.platform not in ['win32']: os.kill(kid, signal.SIGKILL) # Confirmed by Ninad on Linux
            
        else: # Something failed...
            msg = "<span style=\"color:#ff0000\">Simulation failed: exit code %r </span>" % r
            self.assy.w.statusBar.message(msg)

        return r

    def NumFramesValueChanged(self,a0):
        """Slot from the spinbox that changes the number of frames for the simulator.
        """
        self.nframes = a0

    def StepsChanged(self,a0):
        """Slot from the spinbox that changes the number of steps for the simulator.
        """
        self.stepsper = a0

    def TemperatureChanged(self,a0):
        """Slot from the spinbox that changes the temperature for the simulator.
        """
        self.temp = a0

    def TimeStepChanged(self,a0):
        """Slot from the spinbox that changes time step for the simulator.
        """
        # THIS PARAMETER IS CURRENTLY NOT USED BY THE SIMULATOR
        # - Mark 050106
        self.timestep = a0
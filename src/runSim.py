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

    def NumFramesValueChanged(self,a0):
        self.nframes = a0

    def saveFilePressed(self):
        if self.assy:
            if self.assy.filename:
                dir, fil, ext = fileparse(self.assy.filename)
                sdir = self.assy.filename
            else: 
                dir, fil = "./", self.assy.name
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
            
            if self.assy.filename != safile: # If the current part name and "Save As" filename are not the same...
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
            natoms = len(self.assy.alist)

            if ext == '.dpb': # DPB file format
                ftype = 'DPB'
                self.fileform = ''
                filesize = (self.nframes * natoms * 3) + 4
            else: # XYZ file format
                ftype = 'XYZ'
                self.fileform = '-x'
                filesize = (self.nframes * natoms * 3) + 4 # XYZ SIZE: THIS IS WRONG

            self.hide()
            
            r = self.saveMovie(safile, filesize)
            
            if not r: # Movie file saved successfully.
                self.assy.w.statusBar.message( ftype + " file saved: " + safile)


    def createMoviePressed(self):
        QDialog.accept(self)
        moviefile = self.assy.filename[:-4] + '.dpb'
        natoms = len(self.assy.alist)
        dpbsize = (self.nframes * natoms * 3) + 4
        
        r = self.saveMovie(moviefile, dpbsize)
        
        if not r: # Movie file saved successfully.
            msg = "Total time to create movie file: %d seconds" % self.assy.w.progressbar.duration
            self.assy.w.statusBar.message(msg) 
            msg = "Movie written to [" + moviefile + "]."\
                        "To play movie, click on the <b>Movie Player</b> <img source=\"movieicon\"> icon."
            # This makes a copy of the movie tool icon to put in the HistoryMegawidget.
            QMimeSourceFactory.defaultFactory().setPixmap( "movieicon", 
                        self.assy.w.toolsMovieAction.iconSet().pixmap() )
            self.assy.w.statusBar.message(msg)

        return

    def saveMovie(self, moviefile, filesize):
        
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        program = filePath +  '/../bin/simulator'      
        args = [program, '-f' + str(self.nframes), '-t' + str(self.temp), '-i' + str(self.stepsper), str(self.fileform),  '-o' + moviefile, self.assy.filename]
        basename = os.path.basename(moviefile)
        
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        self.assy.w.statusBar.message("<span style=\"color:#006600\">Simulator: Calculating...</span>")
        
        try:
            if self.assy.modified: writemmp(self.assy, self.assy.filename, False)
            if os.path.exists(moviefile): os.remove (moviefile) # Delete before spawning.
            print  "program = ",program
            print  "Spawnv args are %r" % (args,) # this %r remains (see above)
            kid = os.spawnv(os.P_NOWAIT, filePath + '/../bin/simulator', args)
            r = self.assy.w.progressbar.launch(filesize, moviefile, "Simulate", "Writing movie file " + basename + "...", 1)
            s = None
        except:
            print_compact_traceback("exception in simulation; continuing: ")
            s = "internal error (traceback printed elsewhere)"
            r = -1 # simulator failure
        
        QApplication.restoreOverrideCursor() # Restore the cursor
        
        if not r: return r
        
        if r == 1: # User pressed abort on progress dialog...
            self.assy.w.statusBar.message("<span style=\"color:#ff0000\">Simulator: Aborted.</span>")         
            # We should kill the kid, but not sure how on Windows
            if sys.platform not in ['win32']: os.kill(kid, signal.SIGKILL) # Not tested - Mark 050105
            
        else: # Something failed...
            if not s: s = "exit code %r" % r
            self.assy.w.statusBar.message("Simulation Failed!") ##e include s?
            QMessageBox.warning(self.assy.w, "Simulation Failed:", s)

        return r

    def StepsChanged(self,a0):
        self.stepsper = a0

    def TemperatureChanged(self,a0):
        self.temp = a0

    def TimeStepChanged(self,a0):
        self.timestep = a0
# This is the GAMESS Job parms default settings.
# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
GamessJob.py

$Id$
'''
__author__ = "Mark"

import os, sys, time, re
from Numeric import *
from VQT import *
from SimJob import SimJob
from SimServer import SimServer
from GamessProp import GamessProp
from HistoryWidget import redmsg
from files_gms import writegms_inpfile, writegms_batfile
from qt import QMessageBox
import preferences
from constants import *

failpat = re.compile("-ABNORMALLY-")
irecpat = re.compile(" (\w+) +\d+\.\d* +([\d\.E+-]+) +([\d\.E+-]+) +([\d\.E+-]+)")

class GamessJob(SimJob):
    """A Gamess job is a setup used to run Gamess simulation. Two ways exist to create a Gamess Job: (1). Create a Gamess Jig. (2). A
    gamess job coming from a set of existing files in a particular location. 
     """
    def __init__(self,  job_parms, **job_prop):
        """To support the 2 ways of  gamess job creation."""
        name = "Gamess Job 1"
        [self.job_batfile, self.job_outputfile] = job_prop.get('job_from_file', [None, None])
        if self.job_outputfile: self.job_outputfile = self.job_outputfile.strip('"')
        self.gamessJig = job_prop.get('jig', None)
        
        if self.job_batfile:
            server_id = job_parms['Server_id']
            from ServerManager import ServerManager
            self.server = ServerManager().getServerById(int(server_id))
            if not self.server: raise ValueError, "The server of %d can't be found." % server_id  
        
        SimJob.__init__(self, name, job_parms)
        
        self.edit_cntl = GamessProp()
        
        
    def edit(self):
        self.edit_cntl.showDialog(self)
    
    def launch(self):
        '''Launch GAMESS job.
        Returns: 0 = Success
                       1 = Cancelled
                       2 = Failed
        '''

        # Get a unique Job Id and the Job Id directory for this run.
        from JobManager import get_job_manager_job_id_and_dir
        job_id, job_id_dir = get_job_manager_job_id_and_dir()
        self.Job_id = job_id
        self.Status = 'Queued'

        basename = self.gamessJig.name + "-" + self.gamessJig.gms_parms_info('_')
        
        # Do GAMESS and PC GAMESS need different INP filenames?  
        # Can't GAMESS and PC GAMESS both use *.inp as the filename?
        # I think so.  I'm commenting out this code and leaving this note here
        # until I discuss it with Huaicai.  If he agrees, I'm removing all this.
        # Mark 050628
#        if self.server.engine == 'PC GAMESS':
#            self.job_inputfile = os.path.join(job_id_dir, "%s.inp" % basename)
#        else: 
#            self.job_inputfile = os.path.join(job_id_dir, "%s" %  basename)
        
        # GAMESS Job INP, OUT and BAT files.
        self.job_inputfile = os.path.join(job_id_dir, "%s.inp" % basename)
        self.job_outputfile = os.path.join(job_id_dir, "%s.out" %  basename)
        self.job_batfile = os.path.join(job_id_dir, "%s.bat" %  basename)
         
        # Write INP file (in ~/Nanorex/JobManager/Job Id subdirectory)
        writegms_inpfile(self.job_inputfile, self.gamessJig)
        
        # Create BAT file (in ~/Nanorex/JobManager/Job Id subdirectory)
        #writegms_batfile(self.job_batfile, self)
        
        # Open INP file in editor if user checked checkbox in GAMESS jig properties UI.
        if self.edit_cntl.edit_input_file_cbox.isChecked():
            from platform import open_file_in_editor
            open_file_in_editor(self.job_inputfile)

        self.starttime = time.time() # Save the start time for this job.

        if sys.platform == 'win32': # Windows
            return self._launch_pcgamess()
        else: # Linux or MacOS
            return self._launch_gamess()

    def _validate_gamess_program(self):
        '''Private method:
        Checks that the GAMESS program path exists in the user pref database
        and that the file it points to exists.  If the GAMESS path does not exist, the
        user will be prompted with the file chooser to select the GAMESS executable.
        This function does not check whether the GAMESS path is actually GAMESS 
        or if it is the correct version of GAMESS for this platform (i.e. PC GAMESS for Windows).
        Returns:  0 = Valid
                        1 = Invalid
        '''
        
        # Get GAMESS executable path from the user preferences
        prefs = preferences.prefs_context()
        self.server.program = prefs.get(gmspath_prefs_key)
        
        if not self.server.program:
            msg = "The GAMESS executable path is not set.\n"
        elif os.path.exists(self.server.program):
            return 0
        else:
            msg = self.server.program + " does not exist.\n"
            
        # GAMESS Prop Dialog is the parent for messagebox and file chooser.
        parent = self.edit_cntl 
            
        ret = QMessageBox.warning( parent, "GAMESS Executable Path",
            msg + "Please select OK to set the location of GAMESS for this computer.",
            "&OK", "Cancel", None,
            0, 1 )
                
        if ret==0: # OK
            from UserPrefs import get_gamess_path
            self.server.program = get_gamess_path(parent)
            if not self.server.program:
                return 1 # Cancelled from file chooser.
            
        elif ret==1: # Cancel
            return 1

        return 0
        
    def _launch_gamess(self):
        print "GAMESS not supported on Windows"
        
    def _launch_pcgamess(self):
        '''Run PC GAMESS (Windows only).
        PC GAMESS creates 2 output files:
          - the DAT file, called "PUNCH", is written to the directory from which
            PC GAMESS is started.  This is why we chdir to the Gamess temp directory
            before we run PC GAMESS.
          - the OUT file (aka the log file), which we name jigname.out.
        Returns: 0 = Success
                       1 = Cancelled
                       2 = Failed
        '''
        
        # Validate Gamess Program
        r = self._validate_gamess_program()
        
        if r: # Gamess program was not valid.
            return 1 # Job Cancelled.
        
        oldir = os.getcwd() # Save current directory
        
        jobDir = os.path.dirname(self.job_batfile)
        os.chdir(jobDir) # Change directory to the GAMESS temp directory.
        print "Current directory is: ", jobDir
        
        DATfile = os.path.join(jobDir, "PUNCH")
        if os.path.exists(DATfile): # Remove any previous DAT (PUNCH) file.
            print "run_pcgamess: Removing DAT file: ", DATfile
            os.remove(DATfile)
        
        # Hours wasted testing this undocumented tripe.  Here's the deal: When using spawnv
        # on Windows, any args that might have spaces must be delimited by double quotes.
        # Mark 050530.
        
        #program = "\"" + self.job_batfile + "\""
        #args = [program, ]
        
        # Here's the infuriating part.  The 2nd arg to spawnv cannot have double quotes, but the
        # first arg in args (the program name) must have the double quotes if there is a space in
        # self.gms_program.
        
        #print  "program = ", program
        #print  "Spawnv args are %r" % (args,) # this %r remains (see above)
        #os.spawnv(os.P_WAIT, self.job_batfile, args)
        
        #try:
        if 1:    
            from qt import QProcess, qApp
            import time
            
            #args = [r'C:\PCGAMESS\gamess.exe',  '-i',  r'C:\Documents and Settings\Huaicai Mo\Nanorex\jobManager\100\gamess_job_100.inp',  '-o',  r'C:\Documents and Settings\Huaicai Mo\Nanorex\JobManager\100\gamess_job_100.out']

            args = [self.server.program, '-i', self.job_inputfile, '-o', self.job_outputfile]
            
            process = QProcess()
            for s in args:
                process.addArgument(s)
            if not process.start():
                print "The process can't be started."
            progressDialog = self.showProgress()
            progressDialog.show()
            i = 55; pInc = True
            while process.isRunning():
                qApp.processEvents()
                if  progressDialog.wasCanceled():
                    process.kill()
                    os.chdir(oldir)
                    return 1 # Job cancelled.
                    
                progressDialog.setProgress(i)
                if pInc:
                    if i < 75: i += 1
                    else: pInc = False
                else:
                    if i > 55:  i -= 1
                    else: pInc = True
                #Do sth here
                time.sleep(0.05)
                if not process.isRunning():
                     break
                  
            progressDialog.setProgress(100)        
            progressDialog.accept()
        #except:
        #    print "Exception: QProcess failed to launch Gamess run "
        
        os.chdir(oldir)
        self.gamessJig.outputfile = self.job_outputfile
        print "GamessJob._launch_pcgamess: self.gamessJig.outputfile: ", self.gamessJig.outputfile
        
        return 0 # Success


    def showProgress(self):
        '''Open the progress dialog to show the current job progress. '''
        from qt import QProgressDialog, QProgressBar
        
        simProgressDialog = QProgressDialog(self.edit_cntl.win, "progressDialog", True)
        if self.Calculation == 'Energy':
            simProgressDialog.setLabelText("Calculating Energy ...")
        else:
            simProgressDialog.setLabelText("Optimizing ...")
        simProgressDialog.setCaption("Please Wait")
        progBar = QProgressBar(simProgressDialog)
        progBar.setTotalSteps(0)
        simProgressDialog.setBar(progBar)
        simProgressDialog.setAutoReset(False)
        simProgressDialog.setAutoClose(False)
        
        return simProgressDialog
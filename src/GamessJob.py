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
    
    def launch_job(self):
        'Launch GAMESS run.'

        # Get a unique Job Id and the Job Id directory for this run.
        from JobManager import get_job_manager_job_id_and_dir
        job_id, job_id_dir = get_job_manager_job_id_and_dir()
        self.Job_id = job_id
        print "GamessProp.queue_job: Job Id = ", job_id
        self.Status = 'Queued'

        basename = self.gamessJig.name + "-" + self.gamessJig.gms_parms_info('_')
        
        # GAMESS Job INP, OUT and BAT files.
        if self.server.engine == 'PC GAMESS':
            self.job_inputfile = os.path.join(job_id_dir, "%s.inp" % basename)
        else:
            self.job_inputfile = os.path.join(job_id_dir, "%s" %  basename)
        self.job_outputfile = os.path.join(job_id_dir, "%s.out" %  basename)
        self.job_batfile = os.path.join(job_id_dir, "%s.bat" %  basename)
         
        # Write INP file (in ~/Nanorex/JobManager/Job Id subdirectory)
        writegms_inpfile(self.job_inputfile, self.gamessJig)
        
        # Create BAT file (in ~/Nanorex/JobManager/Job Id subdirectory)
        writegms_batfile(self.job_batfile, self)
        
        # Open INP file in editor if user checked checkbox in GAMESS jig properties UI.
        if self.edit_cntl.edit_input_file_cbox.isChecked():
            from platform import open_file_in_editor
            open_file_in_editor(self.job_inputfile)

        self.starttime = time.time() # Save the start time for this job.

        if self.server.engine == 'PC GAMESS':
            self._launch_pcgamess()
        else:
            self._launch_gamess()
    
    def _launch_gamess(self):
        print "GAMESS not supported on Windows"

    def _launch_pcgamess(self):
        '''Run PC GAMESS (Windows only).
        PC GAMESS creates 2 output files:
          - the DAT file, called "PUNCH", is written to the directory from which
            PC GAMESS is started.  This is why we chdir to the Gamess temp directory
            before we run PC GAMESS.
          - the OUT file (aka the log file), which we name jigname.out.
        '''
        print "server program = ", self.server.program
        if not os.path.exists(self.server.program):
            msg = "The GAMESS executable " + self.server.program + "does not exist."
            self.edit_cntl.win.history.message(redmsg(msg))
            msg = "Check the GAMESS pathname in the User Preferences to make sure it is set correctly."
            self.edit_cntl.win.history.message(redmsg(msg))
            return

        oldir = os.getcwd() # Save current directory
        
        jobDir = os.path.dirname(self.job_batfile)
        os.chdir(jobDir) # Change directory to the GAMESS temp directory.
        
        DATfile = os.path.join(jobDir, "PUNCH")
        if os.path.exists(DATfile): # Remove any previous DAT (PUNCH) file.
            print "run_pcgamess: Removing DAT file: ", DATfile
            os.remove(DATfile)
        
        # Hours wasted testing this undocumented tripe.  Here's the deal: When using spawnv
        # on Windows, any args that might have spaces must be delimited by double quotes.
        # Mark 050530.
        
        program = "\"" + self.job_batfile + "\""
        args = [program, ]
        
        # Here's the infuriating part.  The 2nd arg to spawnv cannot have double quotes, but the
        # first arg in args (the program name) must have the double quotes if there is a space in
        # self.gms_program.
        
        print  "program = ", program
        print  "Spawnv args are %r" % (args,) # this %r remains (see above)
        os.spawnv(os.P_WAIT, self.job_batfile, args)
        
        os.chdir(oldir)
        
        self.gamessJig.outputfile = self.job_outputfile
        print "GamessJob._launch_pcgamess: self.gamessJig.outputfile: ", self.gamessJig.outputfile
        
#        print "run_pcgamess: Launched PC GAMESS. Changed back to previous dir = ",oldir
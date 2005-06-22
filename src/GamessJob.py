# This is the GAMESS Job parms default settings.
# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
GamessJob.py

$Id$
'''
__author__ = "Mark"

import os, sys, time
from SimJob import SimJob
from SimServer import SimServer
from GamessProp import GamessProp

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
    
    def queue_job(self):
        'Queue files for GAMESS run.'

        # Get a unique Job Id and the Job Id directory
        from JobManager import get_job_manager_job_id_and_dir
        job_id, job_id_dir = get_job_manager_job_id_and_dir()
        self.Job_id = job_id
        print "GamessProp.queue_job: Job Id = ", job_id
        self.Status = 'Queued'

        # GAMESS Job INP, OUT and BAT files.
        if self.server.engine == 'PC GAMESS':
            self.job_inputfile = os.path.join(job_id_dir, "gamess_job_%s.inp" % job_id)
        else:
            self.job_inputfile = os.path.join(job_id_dir, "gamess_job_%s" % job_id)
        self.job_outputfile = os.path.join(job_id_dir, "gamess_job_%s.out" % job_id)
        self.job_batfile = os.path.join(job_id_dir, "gamess_job_%s.bat" % job_id)
         
        # Write INP file
        self.writeinpfile(self.job_inputfile)
        
        # Create BAT file in Job Id subdirectory
        self.writebatfile(self.job_batfile)
        
        # Open INP file in editor if user checked checkbox.
        if self.edit_cntl.edit_input_file_cbox.isChecked():
            from platform import open_file_in_editor
            open_file_in_editor(self.job_inputfile) # Open GAMESS input file in editor.
        

    def launch_job(self):
        'Launch GAMESS with INP file on server'
        self.queue_job() # Do not open Job Manager.
        self.start_job()

    def get_gamess_energy(self):
        'Runs a GAMESS energy calculation and returns the energy.'
        self.launch_job()

        # Wait for GAMESS output file to be written.
        while not os.path.exists(self.job_outputfile):
            time.sleep(0.5)
            
        return self.get_energy_from_outputfile()

    def start_job(self):
        self.starttime = time.time()
        print "Just execute the file:", self.job_batfile
        self._launch_pcgamess_using_spawnv()
        
    def _launch_pcgamess_using_spawnv(self):
        '''Run PC GAMESS (Windows or Linux only).
        PC GAMESS creates 2 output files:
          - the DAT file, called "PUNCH", is written to the directory from which
            PC GAMESS is started.  This is why we chdir to the Gamess temp directory
            before we run PC GAMESS.
          - the OUT file (aka the log file), which we name jigname.out.
        '''
        if not os.path.exists(self.server.program):
            msg = "The PC GAMESS executable " + self.server.program + "does not exist."
            self.win.history.message(redmsg(msg))
#            print msg
            msg = "Check the PC GAMESS pathname in the User Preferences to make sure it is set correctly."
            self.win.history.message(redmsg(msg))
#            print msg
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
#        print "run_pcgamess: Launched PC GAMESS. Changed back to previous dir = ",oldir
        
    
# File Writing Methods.
        
    def writeinpfile(self, filename):
        'Write GAMESS INP file'
        
        # Save UI settings
        self.edit_cntl.save_ui_settings()

        f = open(filename,'w') # Open GAMESS input file.
        
        # Write Header
        f.write ('!\n! INP file created by nanoENGINEER-1 on ')
        timestr = "%s\n!\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
        f.write(timestr)
        
        self.edit_cntl.pset.prin1(f) # Write GAMESS Jig parameters.

        self.write_atoms_data(f) # Write DATA section with molecule data.
        
        f.close() # Close INP file.


    def write_atoms_data(self, f):
        'Write the atoms list data to the DATA group of the GAMESS INP file'
        
        # $DATA Section keyword
        f.write(" $DATA\n")
        
        # Comment (Title) line from UI
        f.write(str(self.edit_cntl.comment_linedit.text()) + "\n")
        
        # Schoenflies symbol
        f.write("C1\n")
        
        # Write the list of jig atoms for the $DATA group
        self.write_atomslist_data(f)

        #  $END
        f.write(' $END\n')


    def write_atomslist_data(self, f):
        '''Write the list of atoms in $DATA format to file f.'''
        
        from jigs import povpoint
        for a in self.gamessJig.atoms:
            pos = a.posn()
            fpos = (float(pos[0]), float(pos[1]), float(pos[2]))
            f.write("%2s" % a.element.symbol)
            f.write("%8.1f" % a.element.eltnum)
            f.write("%8.3f%8.3f%8.3f\n" % fpos)
     
            
    def writebatfile(self, filename):
        'Write PC GAMESS BAT file'
        
        f = open(filename,'w')
        
        rem = self.get_comment_character()
        # Write Header
        f.write (rem + '\n' + rem + 'File created by nanoENGINEER-1 on ')
        timestr = "%s\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
        f.write(timestr)
        f.write (rem + '\n')
        
        self.write_parms(f)
        
        if self.server.engine == 'PC GAMESS':
            f.write(self.server.program + ' -i "' + self.job_inputfile + '" -o "' + self.job_outputfile + '"\n')
        else: # GAMESS on other computer.
            f.write(self.server.program + '  "' + self.job_inputfile + '" >& > "' + self.job_outputfile + '"\n')
            
        f.close() # Close INP file.


# Methods that read the output file(s).

    def get_energy_from_outputfile(self):
        '''Returns the final energy value from the PC GAMESS log file.
        GAMESS is not yet supported, as the line containing the energy
        value is different from PC GAMESS.
        '''
        elist = []
        
        lines = open(self.job_outputfile,"rU").readlines()
        
        for line in lines:
            if not line: 
                return None # Energy not found in file.
            elif line.find('FINAL ENERGY IS') >= 0:
                elist = line.split()
#                print elist
                return float(elist[3]) # Return the final energy value.
            else: continue
            
        return None # Just in case (i.e. file doesn't exist).
        
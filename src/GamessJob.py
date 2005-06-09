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
    
    def __init__(self, gamess_jig, job_parms):
        
        name = "Gamess Job 1"
        self.gamessJig = gamess_jig
        SimJob.__init__(self, name, job_parms)
        self.edit_cntl = GamessProp()
        self.server = gamess_jig.server
        
    def edit(self):
        self.edit_cntl.showDialog(self)
    
    def queue_job(self):
        'Queue files for GAMESS run.'

        # Get a unique Job Id and the Job Id directory
        from JobManager import get_job_manager_job_id_and_dir
        job_id, job_id_dir = get_job_manager_job_id_and_dir()
        print "GamessProp.queue_job: Job Id = ", job_id

        # GAMESS Job INP, OUT and BAT files.
        self.job_inputfile = os.path.join(job_id_dir, "gamess_job_%s.inp" % job_id)
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
#        self.run_gamess()

    def start_job(self):
        self.starttime = time.time()
        print "GamessJob.start_job: Engine = ", self.server.engine
        print "Just execute the file:", self.job_batfile

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
        'Write GAMESS BAT file'
        
        f = open(filename,'w')
        
        rem = self.server.get_comment_character()
        # Write Header
        f.write (rem + '\n' + rem + 'File created by nanoENGINEER-1 on ')
        timestr = "%s\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
        f.write(timestr)
        f.write (rem + '\n')
        
        self.write_parms(f)
        self.server.write_parms(f)
        
        if self.server.hostname == 'My Computer' and self.server.engine == 'PC GAMESS':
            f.write(self.server.program + ' -i "' + self.job_inputfile + '" -o "' + self.job_outputfile + '"\n')
        else:
            f.write('cd ' + self.server.tmpdir + '\n')
            f.write('copy ' + self.job_inputfile + ' gamess.inp\n')
        
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
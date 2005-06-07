# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
JobManager.py

$Id$
'''
__author__ = "Mark"

# A list as a 2-dimensional array of sub-lists.
# This is a sample list of 4 jobs for testing purposes.
jobs = [["Small Bearing.mmp", "GAMESS", "Molecular Energy","Inner Shaft", 
             "Queued", "My Computer", "1234", "", ""],
              ["MarkIIk.mmp", "MD Simulator", "Movie","2000 Frames", 
             "Running", "cluster1.nanorex.com", "1233", "0:15", "6/6/2005 12:00:01"],
             ["SA1g.mmp", "GAMESS", "Optimize", "Outer Ring",
             "Failed", "cluster1.nanorex.com", "1232", "0:25:10", "6/6/2005 10:30:22"],
             ["Small Bearing.mmp", "MD Simulator", "Minimize", "Inner Shaft",
             "Completed", "My Computer", "1231", "1:35:19", "6/6/2005 8:45:41"]]

# A list as a 2-dimensional array of dictionaries. 
# This is a sample list of 4 jobs for testing purposes. This is currently not used.
jobs2 = [{'Part':'Small Bearing1.mmp', 'Engine':'GAMESS', 'Description':'Molecular Energy - Inner Shaft', 
             'Status':'Queued', 'Server':'My Computer', 'JobId':'1234', 'Time':'','Start Time':''},
            {'Part':'Small Bearing2.mmp', 'Engine':'GAMESS', 'Description':'Molecular Energy - Inner Shaft', 
             'Status':'Running', 'Server':'cluster1.nanorex.com', 'JobId':'1233', 'Time':15,'Start Time':'6/6/2005 12:00:01'},
            {'Part':'Small Bearing3.mmp', 'Engine':'GAMESS', 'Description':'Molecular Energy - Inner Shaft', 
             'Status':'Failed', 'Server':'cluster1.nanorex.com', 'JobId':'1232', 'Time':125,'Start Time':'6/6/2005 14:00:01'}]

from JobManagerDialog import JobManagerDialog
        
class JobManager(JobManagerDialog):
    
    def __init__(self):
        JobManagerDialog.__init__(self)
        
        self.job = None # The job object, currently selected in the job table.
        self.setup()
        self.exec_loop()


    def setup(self):
        ''' Setup widgets to default (or default) values. Return true on error (not yet possible).
        This is not implemented yet.
        '''
        self.refresh_job_table() # Rebuild the job table from scratch.
        self.cell_clicked(0,0,1,0) # This selects row no. 1 as the current job.

    def cell_clicked(self, row, col, button, mouse):
        print "row =", row, ", column =", col, ", button =", button
        
        # Get the job info from the row the user clicked on.
        self.job = Job(jobs[row], row) 
        
        # Enable/disable the buttons in the Job Manager based on the Status field.
        if self.job.status == "Queued":
            self.start_btn.setText("Start")
            self.start_btn.setEnabled(1)
            self.stop_btn.setEnabled(0)
            self.edit_btn.setEnabled(1)
            self.view_btn.setEnabled(0)
            self.delete_btn.setEnabled(1)
            self.move_btn.setEnabled(0)
            
        elif self.job.status == "Running":
            self.start_btn.setText("Start")
            self.start_btn.setEnabled(0)
            self.stop_btn.setEnabled(1)
            self.edit_btn.setEnabled(0)
            self.view_btn.setEnabled(0)
            self.delete_btn.setEnabled(0)
            self.move_btn.setEnabled(0)
            
        elif self.job.status == "Completed":
            self.start_btn.setText("Start")
            self.start_btn.setEnabled(0)
            self.stop_btn.setEnabled(0)
            self.edit_btn.setEnabled(1)
            self.view_btn.setEnabled(1)
            self.delete_btn.setEnabled(1)
            self.move_btn.setEnabled(1)
            
        elif self.job.status == "Failed":
            self.start_btn.setText("Restart")
            self.start_btn.setEnabled(1)
            self.stop_btn.setEnabled(0)
            self.edit_btn.setEnabled(1)
            self.view_btn.setEnabled(1)
            self.delete_btn.setEnabled(1)
            self.move_btn.setEnabled(0)
        
    def refresh_job_table(self):
        '''Refreshes the Job Manager table based on the current Job Manager directory.
        This method removes all rows in the existing table and rebuilds everything from
        scratch by reading the ~/Nanorex/JobManager/ directory.
        '''
        
        # Remove all rows in the job table
        for r in range(self.job_table.numRows()):
            self.job_table.removeRow(0)
        
        numjobs = len(jobs) # One row for each job.
        columns = 9 # The number of columns in the job table (change this if you add/remove columns).

        for row in range(numjobs):
            print "JobManager.refresh_job_table: Adding row #", row
            self.job_table.insertRows(row)
            for col in range(columns):
                self.job_table.setText(row , col, jobs[row][col])
        
    def delete_job(self):
        self.job_table.removeRow(self.job.row)
                
#    def get_queued_jobs(self):
#        '''Returns the info for all queued jobs.
#        '''
        
#        elist = []
        
#        for qfile in list_of_queued_files:
            
#            lines = open(qfile,"rU").readlines()
        
#                for line in lines:
#                    if not line: 
#                        return None # EOF.
#                    elif line.find('# Part name:') >= 0:
#                        elist = line.split()
#                        print elist
#                       return float(elist[3]) # Return the final energy value.
#                    else: continue
            
#        return None # Just in case (i.e. file doesn't exist).

class Job:
    def __init__(self, jinfo, row):
        self.name = jinfo[0] # Job Name
        self.engine = jinfo[1] # Engine (MD Simulator or GAMESS)
        self.calculation = jinfo[2] # Calculation 
        self.description = jinfo[3] # From GAMESS: Comment line, from MD Simulator: Description line.
        self.status = jinfo[4] # The status of the job, gotten from the "Status" file in the job_id subdirectory.
        self.server = jinfo[5] # The computer
        self.job_id = jinfo[6] # Job Id, determined by the Job Manager
        self.time = jinfo[7] # Duration (in seconds), displayed in hh:mm:ss format.
        self.start_time = jinfo[8] # Time job was started (from the bat filename in job_id subdirectory)
        self.row = row # The row no. for this job.
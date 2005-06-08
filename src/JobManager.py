# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
JobManager.py

$Id$
'''
__author__ = "Mark"

import os

def touch_job_id_status_file(job_id, Status='Queued'):
    '''Creates the status file for a given job provided the job_id and status.
    It will remove any existing status file(s) in the directory.
    Status must be one of: Queued, Running, Completed, Suspended or Failed.
    Return values:
        0 = Status file created in the Job Id directory.
        1 = Job Id directory did not exists.  Status file was not created.
        2 = Invalid Status.
    '''
    
    # Create Job Id subdirectory
    from platform import find_or_make_Nanorex_prefs_directory
    nanorex = find_or_make_Nanorex_prefs_directory()
    
    # Job Id dir (i.e. ~/Nanorex/JobManager/123/)
    job_id_dir  = os.path.join(nanorex, 'JobManager', str(job_id))
        
    # Make sure the directory exists
    if not os.path.exists(job_id_dir):
        print "touch_job_id_status_file error: The directory ", job_id_dir, " does not exist."
        return 1
    
    # Make sure Status is valid.
    if Status not in ('Queued', 'Running', 'Completed', 'Suspended', 'Failed'):
        print "touch_job_id_status_file error: Status is invalid: ", Status
        return 2
    
    # Remove any status files (i.e. Status-Running in the directory)
    import glob
    wildcard_str = os.path.join(job_id_dir, 'Status-*')
    status_files = glob.glob(wildcard_str)
    print "Status Files:", status_files
    for sfile in status_files:
        os.remove(sfile)
    
    # Write zero length status file.
    status_file = os.path.join(job_id_dir, 'Status-'+Status)
    f = open(status_file, 'w')
    f.close()
    
    return 0
    
def get_job_manager_job_id_and_dir():
    '''Returns a unique Job Id number and JobManager subdirectory for this Job Id.  
    The Job Id is stored in the User Preference db.
    '''
    from preferences import prefs_context
    prefs = prefs_context()
    job_id = prefs.get('JobId')
    
    if not job_id:
        job_id = 100 # Start with Job Id 100
    else:
        job_id += 1 # Increment the Job Id
    
    # Create Job Id subdirectory
    from platform import find_or_make_Nanorex_prefs_directory
    nanorex = find_or_make_Nanorex_prefs_directory()
    
    while 1:
        
        # Create Job Id dir (i.e. ~/Nanorex/JobManager/123/)
        job_id_dir  = os.path.join(nanorex, 'JobManager', str(job_id))
        
        # Make sure there isn't already a Job Id subdir in ~/Nanorex/JobManager/
        if os.path.exists(job_id_dir):
            job_id += 1 # It is there, so increment the Job Id and try again.
            
        else:
            os.makedirs(job_id_dir) # No Job Id subdir, so let's make it.
            prefs['JobId'] = job_id # Store the Job Id
            touch_job_id_status_file(job_id, 'Queued')
            return str(job_id), job_id_dir

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
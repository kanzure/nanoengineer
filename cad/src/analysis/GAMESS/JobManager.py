# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
JobManager.py - 

@author: Mark
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.

Module classification:  [bruce 071214, 080104]

This contains ui code, operations code (on a set of jobs stored
partly in the filesystem, I think), and io code. If it became
real, it would become a separate major component of NE1 and
get factored into those separate parts. I think it is not
real at the moment -- really a scratch file (but I'm not sure).

So I will classify it as some sort of ui file for now.
We can reconsider this when we discuss its status.
It might make sense to classify it into a separate component
even now, though it's a single file and a stub.

Update, bruce 080104: due to an import cycle I'll put it into
the same package as GamessJob. When it's refactored and that's
cleaned up, it should probably go into either processes
or its own toplevel package.
"""

import os

from PyQt4.Qt import QWidget
from PyQt4.Qt import SIGNAL

from utilities.Log import redmsg

# WARNING: lots of imports occur lower down.
# Most or all of them should be moved up here.
# [bruce 071216 comment]

def touch_job_id_status_file(job_id, Status = 'Queued'):
    """
    Creates the status file for a given job provided the job_id and status.
    It will remove any existing status file(s) in the directory.
    Status must be one of: Queued, Running, Completed, Suspended or Failed.
    Return values:
        0 = Status file created in the Job Id directory.
        1 = Job Id directory did not exists.  Status file was not created.
        2 = Invalid Status.
    """
    
    # Get the Job Manager directory
    from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
    jobdir = find_or_make_Nanorex_subdir('JobManager')
    
    # Job Id dir (i.e. ~/Nanorex/JobManager/123/)
    job_id_dir  = os.path.join(jobdir, str(job_id))
        
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
#    print "Status Files:", status_files # Commented this out for A6.  Mark 050712.
    for sfile in status_files:
        os.remove(sfile)
    
    # Write zero length status file.
    status_file = os.path.join(job_id_dir, 'Status-'+Status)
    f = open(status_file, 'w')
    f.close()
    
    return 0
    
def get_job_manager_job_id_and_dir():
    """
    Returns a unique Job Id number and JobManager subdirectory for this Job Id.  
    The Job Id is stored in the User Preference db.
    """
    from foundation.preferences import prefs_context
    prefs = prefs_context()
    job_id = prefs.get('JobId')
    
    if not job_id:
        job_id = 100 # Start with Job Id 100
    ##Temporarily comment out by Huaicai 6/22/05    
    #else:
    #    job_id += 1 # Increment the Job Id
    
    # Get the Job Manager directory
    from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
    jobdir = find_or_make_Nanorex_subdir('JobManager')
    
    while 1:
        
        # Create Job Id subdir (i.e. ~/Nanorex/JobManager/123/)
        job_id_dir  = os.path.join(jobdir, str(job_id))
        
        # Make sure there isn't already a Job Id subdir in ~/Nanorex/JobManager/
        if os.path.exists(job_id_dir):
            job_id += 1 # It is there, so increment the Job Id and try again.
            
        else:
            from utilities.debug import print_compact_traceback
            try:
                os.mkdir(job_id_dir)
            except:
                print_compact_traceback("exception in creating directory: \"%s\"" % job_id_dir)
                return -1, 0
            
            prefs['JobId'] = 100#job_id # Save the most recent Job Id
            touch_job_id_status_file(job_id, 'Queued')
            return str(job_id), job_id_dir


from analysis.GAMESS.GamessJob import GamessJob # used in two places: value in jobType, constructor in __createJobs

###Huaicai: Temporary fix the problem of bug 754: an older version of PyQt has problem working with
###Qt3.3.3 for the QTable class.
###Will: Hopefully that will be resolved in Qt 4.1.

from analysis.GAMESS.JobManagerDialog import Ui_JobManagerDialog

class JobManager(QWidget, Ui_JobManagerDialog):
    """
    """
    jobType = {"GAMESS": GamessJob, "nanoSIM-1": None}
    def __init__(self, parent):
        """
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.connect(self.close_btn,SIGNAL("clicked()"),self.close)
        self.connect(self.job_table,SIGNAL("clicked(int,int,int,const QPoint&)"),self.cell_clicked)
        self.connect(self.delete_btn,SIGNAL("clicked()"),self.delete_job)
        self.connect(self.refresh_btn,SIGNAL("clicked()"),self.refresh_job_table)
        self.connect(self.start_btn,SIGNAL("clicked()"),self.startJob)
        self.connect(self.stop_btn,SIGNAL("clicked()"),self.stopJob)
        
        self.win = parent
        self.jobs = [] # The job object, currently selected in the job table.
        self.setup()
        self.exec_()
        return
    
    def setup(self):
        """
        Setup widgets to default (or default) values. Return true on error (not yet possible).
        This is not implemented yet.
        """
        self.refresh_job_table() # Rebuild the job table from scratch.
        self.cell_clicked(0,0,1,0) # This selects row no. 1 as the current job.

    def cell_clicked(self, row, col, button, mouse):
        """
        """
        print "row =", row, ", column =", col, ", button =", button
        
        # Enable/disable the buttons in the Job Manager based on the Status field.
        jobStatus = self.jobInfoList[row][0]['Status']
        if jobStatus == "Queued":
            self.start_btn.setText("Start")
            self.start_btn.setEnabled(1)
            self.stop_btn.setEnabled(0)
            self.edit_btn.setEnabled(1)
            self.view_btn.setEnabled(0)
            self.delete_btn.setEnabled(1)
            self.move_btn.setEnabled(0)
            
        elif jobStatus == "Running":
            self.start_btn.setText("Start")
            self.start_btn.setEnabled(0)
            self.stop_btn.setEnabled(1)
            self.edit_btn.setEnabled(0)
            self.view_btn.setEnabled(0)
            self.delete_btn.setEnabled(0)
            self.move_btn.setEnabled(0)
            
        elif jobStatus == "Completed":
            self.start_btn.setText("Start")
            self.start_btn.setEnabled(0)
            self.stop_btn.setEnabled(0)
            self.edit_btn.setEnabled(1)
            self.view_btn.setEnabled(1)
            self.delete_btn.setEnabled(1)
            self.move_btn.setEnabled(1)
            
        elif jobStatus == "Failed":
            self.start_btn.setText("Restart")
            self.start_btn.setEnabled(1)
            self.stop_btn.setEnabled(0)
            self.edit_btn.setEnabled(1)
            self.view_btn.setEnabled(1)
            self.delete_btn.setEnabled(1)
            self.move_btn.setEnabled(0)
        return
    
    def refresh_job_table(self):
        """
        Refreshes the Job Manager table based on the current Job Manager directory.
        This method removes all rows in the existing table and rebuilds everything from
        scratch by reading the ~/Nanorex/JobManager/ directory.
        """
        # Remove all rows in the job table
        for r in range(self.job_table.numRows()):
            self.job_table.removeRow(0)
        
        # BUILD JOB LIST FROM JobManager Directory Structure and Files.
        self.jobInfoList = self.build_job_list()
        
        numjobs = len(self.jobInfoList) # One row for each job.
        tabTitles = ['Name', 'Engine', 'Calculation', 'Description', 'Status', 'Server_id', 'Job_id', 'Time']
            # The number of columns in the job table (change this if you add/remove columns).

        self.jobs = []
        for row in range(numjobs):
            self.job_table.insertRows(row)
            
            for col in range(len(tabTitles)):
                self.job_table.setText(row , col, self.jobInfoList[row][0][tabTitles[col]])
                
        self.jobs = self.__createJobs(self.jobInfoList)     
        return
        
    def delete_job(self):
        """
        """
        self.job_table.removeRow(self.job_table.currentRow())
        return
    
    def startJob(self):
        """
        Run current job
        """
        currentJobRow = self.job_table.currentRow()
        self.jobs[currentJobRow].start_job()
        return
    
    def build_job_list(self):
        """
        Scan Job manager directories to find and return all the list of jobs
        """
        from platform_dependent.PlatformDependent import find_or_make_Nanorex_directory
        tmpFilePath = find_or_make_Nanorex_directory()
        managerDir = os.path.join(tmpFilePath, "JobManager")
        jobDirs = os.listdir(managerDir)
        jobs = []
        
        try:
           for dr in jobDirs:
             jobPath = os.path.join(managerDir, dr)  
             if os.path.isdir(jobPath):
                jobParas ={};  status = None
                files = os.listdir(jobPath)
                for f in files:
                    if jobParas and status: break
                    if os.path.isfile(os.path.join(jobPath, f)):
                       if f.startswith("Status"):
                             status = f.split('-')[1]
                       elif f.endswith(".bat"):
                           batFile = os.path.join(jobPath, f)
                           lines = open(batFile, 'rU').readlines()
                           for l in lines:
                               if l.startswith("#") or l.startswith("REM"):
                                    if l.startswith("#"): commentStr = "#"
                                    else: commentStr = "REM"
                                    l = l.lstrip(commentStr)
                                    if l.strip() == 'Job Parameters':
                                        onejob = jobParas
                                    #elif l.strip() == 'Server Parameters':
                                    #    onejob = serverParas
                                    value = l.split(': ')
                                    if len(value) > 1:
                                        onejob[value[0].strip()] = value[1].strip()
                               else:
                                    items = l.split('-o ')
                                    if len(items) > 1:
                                        outputFile = items[1].strip()
                                    else:
                                        items = l.split('> ')
                                        if len(items) > 1:
                                            outputFile = items[1].strip()    

                jobParas['Status'] = status
                jobs += [(jobParas, batFile, outputFile)]         
           return jobs                
        except:
           print "Exception: build job lists failed. check the directory/files."
           return None                                

    def __createJobs(self, jobInfoList):
        """
        Create SimJob objects, return the list of job objects
        """
        jobs = []
        for j in jobInfoList:
            if j[0]['Engine'] in ['GAMESS', 'PC GAMESS']:
                #Create GamessJob, call GamessJob.readProp()
                jobs += [GamessJob(j[0], job_from_file =j[1:])]
            elif j[0]['Engine'] == 'nanoSIM-1':
                #Create nanoEngineer-1 MD simulator job
                pass
                
        return jobs

    pass # end of class JobManager

# end

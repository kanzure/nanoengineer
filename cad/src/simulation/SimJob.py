# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""
SimJob.py - The base class for a simulation job.
(Used only for GAMESS, but unclear whether the code is specific to GAMESS.)

@author: Mark
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""

import time
import sys
from PyQt4.Qt import QObject

class SimJob(QObject):
    """
    The base class for a simulation job
    """
    def __init__(self, name, parms):
        """
        """
        QObject.__init__(self)

        # The parameters (parms) for the SimJob object are provided in a dictionary in key:value pairs
        # For the Gamess Jig, the parms are defined in the jig_Gamess.py.
        #
        # The parms.keys are:
        # engine: Engine (MD Simulator or GAMESS)
        # calculation: Calculation
        # description: General job description
        # status: The status of the job (Queued, Running, Completed, Suspended or Failed)
        # job_id: Job Id, provided by JobManager.get_job_manager_job_id_and_dir()
        # start_time: Job start time
        # end_time: Job end time

        self.name = name
        self.parms = parms.keys()
        #self.parms.sort() # Sort parms.
        self.edit_cntl = None

        # WARNING: Bugs will be caused if any of SimJob's own methods or
        # instance variables had the same name as any of the parameter ('k') values.
        for k in parms:
            self.__dict__[k] = parms[k]
        return

    def start_job(self):
        """
        Starts the job if it is queued.
        """
        self.starttime = time.time()

    def stop_job(self):
        """
        Stops the job if it is running.
        """
        if self.status != 'Running':
            return

    def suspend_job(self):
        """
        Suspends the job if it is running.
        """
        if self.status != 'Running':
            return

    def resume_job(self):
        """
        Resumes the job if it is suspended.
        """
        if self.status != 'Suspended':
            return

    def edit_job(self):
        pass

    def get_comment_character(self):
        if sys.platform == 'win32':
            return 'REM ' # Batch file comment for Windows
        else:
            return '# ' # Script file comment for Linux and Mac

    def write_parms(self, f):
        """
        Write job parms to file f
        """
        rem = self.get_comment_character()

        f.write (rem + '\n' + rem +  'Job Parameters\n' + rem + '\n')
        f.write(rem + "Name: " + self.name + "\n")
        for k in self.parms:
            phrase = rem + k + ': ' + str(self.__dict__[k])
            f.write (phrase + '\n')
        f.write (rem+'\n')
        return

    # TODO: probably we also want to define launch, for subclass to implement,
    # and maybe pass it something... see comments in our existing subclass,
    # GamessJob.
    #
    # def launch(self):
    #     pass
    #
    # [bruce 071216 comment]

    pass # end of class SimJob

# end


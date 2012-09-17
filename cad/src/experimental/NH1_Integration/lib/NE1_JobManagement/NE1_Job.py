
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
A job that the NE1 Job Manager schedules and monitors.
"""


class NE1_Job:
    """
    A job that the NE1 Job Manager schedules and monitors. Subclasses know how
    to run themselves and can be polled.

    This is an abstract/interface class and should not be instantiated.

    The subclasses know how to run themselves and can be polled, etc.
    The NH1_Job, when run, would communicate with the NH1 instance to launch
    itself. The NE1 Job Manager could poll the NH1_Job for status. The NH1_Job
    could provide call-backs to indicate simulation completion, failures, etc.

    """


    def getPriority(self):
        """
        Returns the priority of this job.
        @return: (0=low, 1=normal, 2=high)
        """
        pass


    def setPriority(self, priority):
        """
        Sets the priority for this job.
        @param priority: 0=low, 1=normal, 2=high
        """
        pass


    def run(self):
        """
        Starts this job.
        """
        pass


    def pause(self, location):
        """
        Pauses this job in-, or out-of-, memory.
        @param location: 0=in-memory, 1=out-of-memory
        """
        pass


    def resume(self):
        """
        Resumes this job from the paused state.
        """
        pass


    def abort(self):
        """
        Abort this job.
        """
        pass


    def getStatus(self):
        """
        Returns the status of this job.
        @return: (0=idle, 1=running, 2=paused, 3=aborted, 4=failure),
            (% complete), (text message)
        """
        pass


    def getAlertEmailAddress(self):
        """
        Returns the email address to notify when this job completes or fails.
        """
        pass
    def setAlertEmailAddress(self, emailAddress):
        """
        Sets the email address to notify when this job completes or fails.
        """
        pass


    def getPopUpNE1_Alert(self):
        """
        Returns 1 if NE1 should pop up an alert when this job completes or
        fails, and 0 otherwise.
        """
        pass
    def setPopUpNE1_Alert(self, popUp):
        """
        Sets whether NE1 should pop up an alert when this job completes or
        fails.
        @param popUp: (1=do pop up an alert, 0=don't pop up an alert)
        """
        pass


    def getSchedule(self):
        """
        Returns the time this job is scheduled to run.
        @return: (0=later, 1=now),
            (the later
            U{datetime<http://docs.python.org/lib/datetime-datetime.html>}
            object)
        """
        pass
    def setSchedule(self, nowOrLater, laterDatetime):
        """
        Sets the time to run the job.
        @param nowOrLater: 0=later, 1=now
        @param laterDatetime: the later
            U{datetime<http://docs.python.org/lib/datetime-datetime.html>}
            object
        """
        pass

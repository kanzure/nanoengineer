# Copyright 2005-2009 Nanorex, Inc.  See LICENSE file for details.
"""
GamessJob.py -- This is the GAMESS Job parms default settings.

@author: Mark
@version: $Id$
@copyright: 2005-2009 Nanorex, Inc.  See LICENSE file for details.

Module classification: this is a kind of SimJob specialized
for running a GAMESS simulation. So it is probably an operation,
though it has a progress dialog, and does recursive event processing
(which could be considered higher-level), and contains io code
(which might be desirable to move to a gamess_io module or package).
[bruce 071213 comment]
"""

import os, sys, time, re

from PyQt4.Qt import QDialog
from PyQt4.Qt import QProcess
from PyQt4.Qt import QStringList
from PyQt4.Qt import QProgressDialog
from PyQt4.Qt import QProgressBar
from PyQt4.Qt import QMessageBox
from PyQt4.Qt import QVBoxLayout
from PyQt4.Qt import QLabel
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QSize
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QTimer
from PyQt4.Qt import SLOT
from PyQt4.Qt import QThread
from PyQt4.Qt import QMutex

from simulation.SimJob import SimJob
from analysis.GAMESS.GamessProp import GamessProp
from analysis.GAMESS.files_gms import writegms_inpfile
## from files_gms import writegms_batfile
import foundation.preferences as preferences
import foundation.env as env # for setting prefs and doing recursive event processing
from utilities.icon_utilities import geticon

from processes.ServerManager import ServerManager
## from PlatformDependent import open_file_in_editor
from utilities.debug import print_compact_traceback
from ne1_ui.prefs.Preferences import get_filename_and_save_in_prefs
from platform_dependent.PlatformDependent import hhmmss_str

from utilities.prefs_constants import gmspath_prefs_key
from utilities.prefs_constants import gamess_enabled_prefs_key

failpat = re.compile("-ABNORMALLY-")
irecpat = re.compile(" (\w+) +\d+\.\d* +([\d\.E+-]+) +([\d\.E+-]+) +([\d\.E+-]+)")

# ==

class GamessJob(SimJob):
    """
    A Gamess job is a setup used to run Gamess simulation.
    Two ways exist to create a Gamess Job:
    (1). Create a Gamess Jig.
    (2). A gamess job coming from a set of existing files
    in a particular location.
    """
    def __init__(self,  job_parms, **job_prop):
        """
        To support the 2 ways of gamess job creation.
        """
        name = "Gamess Job 1"
        [self.job_batfile, self.job_outputfile] = job_prop.get('job_from_file', [None, None])
        if self.job_outputfile:
            self.job_outputfile = self.job_outputfile.strip('"')
        self.gamessJig = job_prop.get('jig', None)

        if self.job_batfile:
            server_id = job_parms['Server_id']
            self.server = ServerManager().getServerById(int(server_id))
            if not self.server:
                raise ValueError, "The server of %d can't be found." % server_id

        SimJob.__init__(self, name, job_parms)

        self.edit_cntl = GamessProp()

        #Huaicai 7/6/05: try to fix the problem when run a gamess jig coming from mmp file
        #and without opening the jig property windows and save it.
        if not self.__dict__.has_key('server'):
            sManager = ServerManager()
            self.server = sManager.getServers()[0]
        return

    def edit(self):
        self.edit_cntl.showDialog(self)
        return

    def launch(self): # this method should probably exist in the superclass API too [bruce 071216 comment]
        """
        Launch GAMESS job.
        Returns: 0 = Success
                 1 = Cancelled
                 2 = Failed
        """
        # Get a unique Job Id and the Job Id directory for this run.
        from analysis.GAMESS.JobManager import get_job_manager_job_id_and_dir
            ### this causes an import cycle.
            ### FIX - pass in an obj providing this func? or just move this func into SimJob.py?
            # [bruce 071216 comment]
        job_id, job_id_dir = get_job_manager_job_id_and_dir()
        self.Job_id = job_id
        self.Status = 'Queued'

        basename = self.gamessJig.name + "-" + self.gamessJig.gms_parms_info('_')

        # GAMESS Job INP, OUT and BAT files.

        self.job_inputfile = os.path.join(job_id_dir, "%s.inp" % basename)

        self.job_outputfile = os.path.join(job_id_dir, "%s.out" %  basename)
        self.job_batfile = os.path.join(job_id_dir, "%s.bat" %  basename)

        # Write INP file (in ~/Nanorex/JobManager/Job Id subdirectory)
        writegms_inpfile(self.job_inputfile, self.gamessJig)

        # Create BAT file (in ~/Nanorex/JobManager/Job Id subdirectory)
        ## writegms_batfile(self.job_batfile, self)

        # Open INP file in editor if user checked checkbox in GAMESS jig properties UI.
#        if self.edit_cntl.edit_input_file_cbox.isChecked():
#            open_file_in_editor(self.job_inputfile)

        self.starttime = time.time() # Save the start time for this job.

        # Validate Gamess Program
        r = self._validate_gamess_program()

        if r: # Gamess program was not valid.
            return 1 # Job Cancelled.

        try:
            if sys.platform == 'win32': # Windows
                return self._launch_pcgamess()
            else: # Linux or MacOS
                return self._launch_gamess()
        except:
             print_compact_traceback("Exception happened when run gamess")
        return

    def _validate_gamess_program(self):
        """
        Private method:
        Checks that the GAMESS program path exists in the user pref database
        and that the file it points to exists.  If the GAMESS path does not exist, the
        user will be prompted with the file chooser to select the GAMESS executable.
        This function does not check whether the GAMESS path is actually GAMESS
        or if it is the correct version of GAMESS for this platform (i.e. PC GAMESS for Windows).
        Returns:  0 = Valid
                  1 = Invalid
        """
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
            "&OK", "Cancel", "",
            0, 1 )

        if ret == 0: # OK
            self.server.program = \
                get_filename_and_save_in_prefs(parent, gmspath_prefs_key, "Choose GAMESS Executable")
            if not self.server.program:
                return 1 # Cancelled from file chooser.

            # Enable GAMESS Plug-in. Mark 060112.
            env.prefs[gamess_enabled_prefs_key] = True

        elif ret == 1: # Cancel
            return 1

        return 0

    def _readFromStdout(self):
        """
        Slot method to read stdout of the gamess process
        """
        #while self.process.canReadLineStdout():
        #    lineStr = str(self.process.readLineStdout()) + '\n'
        #    self.outputFile.write(lineStr)
        bytes = self.process.readStdout()
        self.outputFile.writeBlock(bytes)
        return

    def startFileWriting(self):
        self.fwThread.start()
        return

    def readOutData(self):
        bytes = self.process.readStdout()
        if bytes:
           self.fwThread.putData(bytes)
        return

    def processTimeout(self):
        if self.process.isRunning():
            if not self.progressDialog.isShown() or self.progressDialog.Rejected:
                return

            msgLabel = self.progressDialog.getMsgLabel()
            duration = time.time() - self.stime
            elapmsg = "Elapsed Time: " + hhmmss_str(int(duration))
            msgLabel.setText(elapmsg)

            ####bytes = self.process.readStdout()
            ####if bytes:
            ####    self.fwThread.putData(bytes)
        return

    def processDone(self):
        #self.fwThread.stop()
        self.jobTimer.stop()

        if self.process.normalExit():
            print "The process is done!"
            QDialog.accept(self.progressDialog)
        else:
            print "The process is cancelled!"
            QDialog.reject(self.progressDialog)
        return

    def _launch_gamess(self):
        oldir = os.getcwd() # Save current directory

        ####self.outputFile = QFile(self.job_outputfile)
        ####self.outputFile.open( IO_WriteOnly | IO_Append )

        jobInputfile = os.path.basename(self.job_inputfile)
        jobInputFile = jobInputfile[:-4]
        jobOutputfile = self.job_outputfile #os.path.basename(self.job_outputfile)

        ### Notes: The following way to get the 'bin' works by assuming user didn't change the
        ### working directory after the atom runs, otherwise it will get problem.
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        program = os.path.normpath(filePath + '/../bin/rungms')

        jobDir = os.path.dirname(self.job_batfile)
        os.chdir(jobDir) # Change directory to the GAMESS temp directory.
#        print "Current directory is: ", jobDir


        executableFile = self.server.program

        args = [program, jobInputFile, jobOutputfile, executableFile]#, '01', '1']


        self.process = QProcess()
        for s in args:
            self.process.addArgument(s)
        ####self.process.setCommunication(QProcess.Stdout)
        print "The params for the QProcess run are: ", args

        ####self.fwThread = _FileWriting(self.outputFile)
        self.jobTimer = QTimer(self)

        self.progressDialog = JobProgressDialog(self.process, self.Calculation)
        self.connect(self.process, SIGNAL('processExited ()'), self.processDone)

        #self.connect(self.process, SIGNAL('readyReadStdout()'), self.readOutData)
        ####self.fwThread.start()

        if not self.process.start():
            print "The process can't be started."
            return 2

        self.connect(self.jobTimer, SIGNAL('timeout()'), self.processTimeout)
        self.stime = time.time()
        self.jobTimer.start(1)

        ret = self.progressDialog.exec_()
        if ret == QDialog.Accepted:
            retValue = 0
        else:
            retValue = 1

        ####self.fwThread.wait()
        ####bytes = self.process.readStdout()
        ####if bytes:
            #####self.outputFile.writeBlock(bytes)
            #####self.outputFile.flush()

        self.process = None
        ####self.outputFile.close()

        os.chdir(oldir)
        self.gamessJig.outputfile = self.job_outputfile

        return retValue

    def _launch_pcgamess(self):
        """
        Run PC GAMESS (Windows only).
        PC GAMESS creates 2 output files:
          - the DAT file, called "PUNCH", is written to the directory from which
            PC GAMESS is started.  This is why we chdir to the Gamess temp directory
            before we run PC GAMESS.
          - the OUT file (aka the log file), which we name jigname.out.
        Returns: 0 = Success
                       1 = Cancelled
                       2 = Failed
        """
        oldir = os.getcwd() # Save current directory

        jobDir = os.path.dirname(self.job_batfile)
        os.chdir(jobDir) # Change directory to the GAMESS temp directory.
##        print "Current directory is: ", jobDir

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

        arg_list = ['-i', self.job_inputfile, '-o', self.job_outputfile]
        args = QStringList()
        for s in arg_list:
            args.append(str(s))

        process = QProcess()
        process.start(self.server.program, args)
        # Blocks for n millisconds until the process has started and started()
        # signal is emitted. Returns true if the process was started successfullly.
        if not process.waitForStarted(2000):
            print "The process can't be started."
            return 2
        progressDialog = self.showProgress()
        progressDialog.show()
        i = 55
        pInc = True
        while process.state() == QProcess.Running:
            env.call_qApp_processEvents() #bruce 050908 replaced qApp.processEvents()
            if progressDialog.wasCanceled():
                process.kill()
                os.chdir(oldir)
                return 1 # Job cancelled.

            progressDialog.setValue(i)
            if pInc:
                if i < 75: i += 1
                else: pInc = False
            else:
                if i > 55:  i -= 1
                else: pInc = True
            # Do sth here
            time.sleep(0.05)
            if not process.state() == QProcess.Running:
                 break

        progressDialog.setValue(100)
        progressDialog.accept()

        os.chdir(oldir)
        self.gamessJig.outputfile = self.job_outputfile

        return 0 # Success

    def showProgress(self, modal = True):
        """
        Open the progress dialog to show the current job progress.
        """
        #Replace "self.edit_cntl.win" with "None"
        #---Huaicai 7/7/05: To fix bug 751, the "win" may be none.
        #Feel awkward for the design of our code.
        simProgressDialog = QProgressDialog()
        simProgressDialog.setModal(True)
        simProgressDialog.setObjectName("progressDialog")
        simProgressDialog.setWindowIcon(geticon('ui/border/MainWindow.png'))
        if self.Calculation == 'Energy':
            simProgressDialog.setWindowTitle("Calculating Energy ...Please Wait")
        else:
            simProgressDialog.setWindowTitle("Optimizing ...Please Wait")

        progBar = QProgressBar(simProgressDialog)
        progBar.setMaximum(0)
        progBar.setMinimum(0)
        progBar.setValue(0)
        progBar.setTextVisible(False)
        simProgressDialog.setBar(progBar)
        simProgressDialog.setAutoReset(False)
        simProgressDialog.setAutoClose(False)

        return simProgressDialog

    # Added by Mark 050919 for bug #915.  Not used yet.
    def _job_cancelation_confirmed(self):
        ret = QMessageBox.warning( None, "Confirm",
            "Please confirm you want to abort the GAMESS simulation.\n",
            "Confirm",
            "Cancel",
            "",
            1,  # The "default" button, when user presses Enter or Return (1 = Cancel)
            1)  # Escape (1= Cancel)

        if ret == 0: # Confirmed
            print "CONFIRMED"
            return True
        else:
            print "CANCELLED"
            return False

    pass # end of class GamessJob

# ==

class JobProgressDialog(QDialog): # review: should any of this be refiled into SimJob? [bruce 071216 Q]
    """
    """
    def __init__(self, process, calculation):
        """
        """
        QDialog.__init__(self, None, None, True)

        self.process = process

        self.setCaption("Please Wait")

        pbVBLayout = QVBoxLayout(self,11,6,"ProgressBarDialogLayout")

        msgLabel = QLabel(self,"msgLabel")
        msgLabel.setAlignment(QLabel.AlignCenter)

        if calculation == 'Energy':
            msgLabel.setText("Calculating Energy ...")
        else:
            msgLabel.setText("Optimizing ...")

        pbVBLayout.addWidget(msgLabel)

        self.msgLabel2 = QLabel(self,"msgLabel2")
        self.msgLabel2.setAlignment(QLabel.AlignCenter)
        self.msgLabel2.setText('')

        pbVBLayout.addWidget(self.msgLabel2)

        cancelButton = QPushButton(self,"canel")
        cancelButton.setText("Cancel")

        pbVBLayout.addWidget(cancelButton)

        self.resize(QSize(248,146).expandedTo(self.minimumSizeHint()))
        self.connect(cancelButton, SIGNAL("clicked()"), self.reject)
        return

    def reject(self):
        """
        """
        if self.process.isRunning():
            self.process.tryTerminate()
            QTimer.singleShot( 5000, self.process, SLOT('kill()') )
            #self.process.kill()
            print "I asked to kill the process."
        return

    def getMsgLabel(self):
        return self.msgLabel2

    def launchProgressDialog(self):
        """
        """
        stime = time.time()
        self.show()
        while 1:
            env.call_qApp_processEvents()
            if self.Rejected:
                break
            duration = time.time() - stime
            elapmsg = "Elapsed Time: " + hhmmss_str(int(duration))
            self.msgLabel2.setText(elapmsg)
            time.sleep(0.01)
        return

    pass # end of class JobProgressDialog

# == no code after this

# define class _FileWriting(QThread), when QThread is available;
# no longer used [noticed by bruce 071213, so commenting this out]
#
##try:
##  # bruce 050701 (committed 050910) put this inside a try/except clause,
##  # so this file can be imported by developers whose Qt installations
##  # don't have QThread compiled in, even though it won't run there.
##  class _FileWriting(QThread):
##    def __init__(self, output):
##        QThread.__init__(self)
##        self.output = output
##        self.end = False
##        self.mutex = QMutex()
##        self.data = None
##
##    def run(self):
##        while not self.end:
##            self.mutex.lock()
##            if self.data:
##                self.output.writeBlock(self.data)
##                self.output.flush()
##            self.data = None
##            self.mutex.unlock()
##
##            self.sleep(0.01)
##
##
##    def putData(self, data):
##        self.mutex.lock()
##        self.data = data
##        self.mutex.unlock()
##
##
##    def stop(self):
##        self.end = True
##    pass # end of class _FileWriting
##
##except:
##  print
##  print "WARNING: unable to define class _FileWriting(QThread) in this Qt installation."
##  print "Some GamessJob functions won't work."
##  pass

# end

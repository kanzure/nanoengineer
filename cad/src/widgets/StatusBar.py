# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
StatusBar.py - status bar widgets, AbortHandler, ProgressReporters

@author: Mark, EricM
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.


Module classification: [bruce 071228]

It appears to have no requirement of being a singleton and to be
general purpose, and it's just one file, so I'll just put it into
"widgets" rather than into its own toplevel module StatusBar
or into ne1_ui.

TODO:

Needs refactoring to move NanoHiveProgressReporter elsewhere.,
probably into its sole user, NanoHiveUtils. [bruce comment 071228]


History:

Started with ProgressBar.py and widdled it down, replacing the original
progressbar dialog with the new MainWindow progress bar and simAbort
"Stop Sign" button. by mark on 060105.

Majorly rewritten/refactored by Eric M circa 12/2007 [bruce comment 071228]
"""

import os, time
from PyQt4.Qt import QProgressBar, QFrame, QToolButton, QIcon, QLabel, SIGNAL
from PyQt4.Qt import QMessageBox, QStatusBar, QWidget, QFrame, QHBoxLayout, QToolBar
from utilities import debug_flags
from platform_dependent.PlatformDependent import hhmmss_str #bruce 060106 moved that function there
import foundation.env as env
from utilities.icon_utilities import geticon
from utilities.icon_utilities import getpixmap
from utilities.qt4transition import qt4todo
from utilities.debug import print_compact_traceback
from widgets.GlobalDisplayStylesComboBox import GlobalDisplayStylesComboBox

class StatusBar(QStatusBar):
    def __init__(self, win):
        QStatusBar.__init__(self, win)
        self._progressLabel = QLabel()
    
        self._progressLabel.setMinimumWidth(200)
        self._progressLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        self.addPermanentWidget(self._progressLabel)
    
        self.progressBar = QProgressBar(win)
        self.progressBar.setMaximumWidth(250)
        qt4todo('StatusBar.progressBar.setCenterIndicator(True)')
        self.addPermanentWidget(self.progressBar)
        self.progressBar.hide()
    
        self.simAbortButton = QToolButton(win)
        self.simAbortButton.setIcon(
            geticon("ui/actions/Simulation/Stopsign.png"))
        self.simAbortButton.setMaximumWidth(32)
        self.addPermanentWidget(self.simAbortButton)
        self.connect(self.simAbortButton,SIGNAL("clicked()"),self.simAbort)
        self.simAbortButton.hide()

        self.dispbarLabel = QLabel(win)
        #self.dispbarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        self.dispbarLabel.setText( "Global display style:" )
        self.addPermanentWidget(self.dispbarLabel)
        
        # Global display styles combobox
        self.globalDisplayStylesComboBox = GlobalDisplayStylesComboBox(win)
        self.addPermanentWidget(self.globalDisplayStylesComboBox)
        
        # Selection lock button. It always displays the selection lock state
        # and it is available to click.
        self.selectionLockButton = QToolButton(win)
        self.selectionLockButton.setDefaultAction(win.selectLockAction)
        self.addPermanentWidget(self.selectionLockButton)

        self.abortableCommands = {}
        
        #bruce 081230 debug code:
        ## self.connect(self, SIGNAL('messageChanged ( const QString &)'),
        ##              self.slotMessageChanged )

##     def slotMessageChanged(self, message): # bruce 081230 debug code
##         print "messageChanged: %r" % str(message)
    
    def showMessage(self, text): #bruce 081230
        """
        [extends superclass method]
        """
        ## QStatusBar.showMessage(self, " ")
        QStatusBar.showMessage(self, text)
        ## print "message was set to %r" % str(self.currentMessage())
        return
    
    def _f_progress_msg(self, text): #bruce 081229 refactoring
        """
        Friend method for use only by present implementation
        of env.history.progress_msg. Display text in our
        private label widget dedicated to progress messages.
        """
        self._progressLabel.setText(text)
        return
    
    def makeCommandNameUnique(self, commandName):
        index = 1
        trial = commandName
        while (self.abortableCommands.has_key(trial)):
            trial = "%s [%d]" % (commandName, index)
            index += 1
        return trial

    def addAbortableCommand(self, commandName, abortHandler):
        uniqueCommandName = self.makeCommandNameUnique(commandName)
        self.abortableCommands[uniqueCommandName] = abortHandler
        return uniqueCommandName

    def removeAbortableCommand(self, commandName):
        del self.abortableCommands[commandName]
        
    def simAbort(self):
        """
        Slot for Abort button.
        """
        if debug_flags.atom_debug and self.sim_abort_button_pressed: #bruce 060106
            print "atom_debug: self.sim_abort_button_pressed is already True before we even put up our dialog"

        # Added confirmation before aborting as part of fix to bug 915. Mark 050824.
        # Bug 915 had to do with a problem if the user accidently hit the space bar or espace key,
        # which would call this slot and abort the simulation.  This should no longer be an issue here
        # since we aren't using a dialog.  I still like having this confirmation anyway.  
        # IMHO, it should be kept. Mark 060106. 
        ret = QMessageBox.warning( self, "Confirm",
                                   "Please confirm you want to abort.\n",
                                   "Confirm",
                                   "Cancel", 
                                   "", 
                                   1,  # The "default" button, when user presses Enter or Return (1 = Cancel)
                                   1)  # Escape (1= Cancel)

        if ret == 0: # Confirmed
            for abortHandler in self.abortableCommands.values():
                abortHandler.pressed()

    def show_indeterminate_progress(self):
        value = self.progressBar.value()
        self.progressBar.setValue(value)

    def possibly_hide_progressbar_and_stop_button(self):
        if (len(self.abortableCommands) <= 0):
            self.progressBar.reset()
            self.progressBar.hide()
            self.simAbortButton.hide()
            

    def show_progressbar_and_stop_button(self,
                                         progressReporter,
                                         cmdname = "<unknown command>",
                                         showElapsedTime = False):
        """
        Display the statusbar's progressbar and stop button, and
        update it based on calls to the progressReporter.

        When the progressReporter indicates completion, hide the
        progressbar and stop button and return 0. If the user first
        presses the Stop button on the statusbar, hide the progressbar
        and stop button and return 1.

        Parameters:
        progressReporter - See potential implementations below.
        cmdname - name of command (used in some messages and in abort button tooltip)
        showElapsedTime - if True, display duration (in seconds) below progress bar

        Return value: 0 if file reached desired size, 1 if user hit abort button.

        """

        updateInterval = .1 # seconds
        startTime = time.time()
        elapsedTime = 0
        displayedElapsedTime = 0

        ###e the following is WRONG if there is more than one task at a time... [bruce 060106 comment]
        self.progressBar.reset()
        self.progressBar.setMaximum(progressReporter.getMaxProgress())
        self.progressBar.setValue(0)
        self.progressBar.show() 

        abortHandler = AbortHandler(self, cmdname)

        # Main loop
        while progressReporter.notDoneYet():
            self.progressBar.setValue(progressReporter.getProgress())
            env.call_qApp_processEvents()
            # Process queued events (e.g. clicking Abort button,
            # but could be anything -- no modal dialog involved anymore).

            if showElapsedTime:
                elapsedTime = int(time.time() - startTime)
                if (elapsedTime != displayedElapsedTime):
                    displayedElapsedTime = elapsedTime
                    env.history.progress_msg("Elapsed Time: " +
                                             hhmmss_str(displayedElapsedTime))
                        # note: it's intentional that this doesn't directly call
                        # self._f_progress_msg. [bruce 081229 comment]

            if abortHandler.getPressCount() > 0:
                env.history.statusbar_msg("Aborted.")
                abortHandler.finish()
                return 1

            time.sleep(updateInterval) # Take a rest

        # End of Main loop (this only runs if it ended without being aborted)
        self.progressBar.setValue(progressReporter.getMaxProgress())
        time.sleep(updateInterval)  # Give the progress bar a moment to show 100%
        env.history.statusbar_msg("Done.")
        abortHandler.finish()
        return 0

class FileSizeProgressReporter(object):
    """
    Report progress of sub-process for
    StatusBar.show_progressbar_and_stop_button().

    This class reports progress based on the growth of a file on disk.
    It's used to show the progress of a dynamics simulation, where the
    output file will grow by a fixed amount each timestep until it
    reaches a final size which is known in advance.
    """
    def __init__(self, fileName, expectedSize):
        self.fileName = fileName
        self.expectedSize = expectedSize
        self.currentSize = 0

    def getProgress(self):
        if os.path.exists(self.fileName):
            self.currentSize = os.path.getsize(self.fileName)
        else:
            self.currentSize = 0
        return self.currentSize

    def getMaxProgress(self):
        return self.expectedSize
        
    def notDoneYet(self):
        return self.currentSize < self.expectedSize

class NanoHiveProgressReporter(object):
    """
    Report progress of sub-process for
    StatusBar.show_progressbar_and_stop_button().

    This class talks to the sub-process directly, and asks for a
    status report including the percent complete.
    """
    def __init__(self, nanoHiveSocket, simulationID):
        self.nanoHiveSocket = nanoHiveSocket
        self.simulationID = simulationID
        self.responseCode = -1
        self.lastPercent = 0

    def getProgress(self):
        success, response = self.nanoHiveSocket.sendCommand("status " + self.simulationID)
        responseCode, percent = response.split(self.simulationID)

        self.responseCode = int(responseCode)

        # Need to do this since we only get a percent value when responseCode == 5 (sim is running).
        # If responseCode != 5, p can be None (r=10) or a whitespace char (r=4).
        if self.responseCode == 5:
            self.lastPercent = int(percent)

        return self.lastPercent

    def getMaxProgress(self):
        return 100

    def notDoneYet(self):
        return self.responseCode != 4

# ==

class AbortHandler:
    def __init__(self, statusBar, commandName):
        self.statusBar = statusBar
        name = commandName or '<unknown command>' # required argument
        self.commandName = statusBar.addAbortableCommand(name, self)
        self.pressCount = 0
        statusBar.simAbortButton.show()

    def pressed(self):
        self.pressCount += 1
        # could call a callback here

    def getPressCount(self):
        self.statusBar.show_indeterminate_progress()
        return self.pressCount

    def finish(self):
        """This should be called when the task it's about ends for any reason,
        whether success or error or abort or even crash;
        if not called it will prevent all other abortable tasks from running!
        """

        ####e should try to figure out a way to auto-call it for tasks that user clicked abort for but that failed to call it...
        # for example, if user clicks abort button twice for same task. or if __del__ called (have to not save .win). #####@@@@@

        try:
            self.statusBar.removeAbortableCommand(self.commandName)
        except:
            if debug_flags.atom_debug:
                print_compact_traceback("atom_debug: bug: failure in StatusBar.removeAbortableCommand(): ")
        self.statusBar.possibly_hide_progressbar_and_stop_button()

# end

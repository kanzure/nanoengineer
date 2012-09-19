# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
MoviePropertyManager.py
@author: Ninad, Bruce, Mark, Huaicai
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  All rights reserved.

History:
ninad20070507 : Converted movie dashboard into movie Property manager
(authors: various)

"""

from PyQt4 import QtCore, QtGui
from commands.PlayMovie.Ui_MoviePropertyManager import Ui_MoviePropertyManager
from PyQt4.Qt import Qt, SIGNAL, QFileDialog, QString, QMessageBox
import os, foundation.env as env
from utilities.Log import redmsg, greenmsg
from utilities.constants import filesplit
from utilities.prefs_constants import workingDirectory_prefs_key


_superclass = Ui_MoviePropertyManager
class MoviePropertyManager(Ui_MoviePropertyManager):
    """
    The MoviePropertyManager class provides the Property Manager for the
    B{Movie mode}.  The UI is defined in L{Ui_MoviePropertyManager}
    """

    #see self.connect_or_disconnect_signals for comment about this flag
    isAlreadyConnected = False


    def connect_or_disconnect_signals(self, connect):
        """
        Connect the slots in the Property Manager.
        """
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect

        #TODO: This is a temporary fix for a bug. When you invoke a temp mode
        #such as Line_Command or PanMode, entering such a temporary mode keeps the
        #PM from the previous mode open (and thus keeps all its signals
        #connected)  but while exiting that temporary mode and reentering the
        #previous mode, it actually reconnects the signal! This gives rise to
        #lots  of bugs. This needs more general fix in Temporary mode API.
        # -- Ninad 2007-10-29

        if connect and self.isAlreadyConnected:
            return

        self.isAlreadyConnected = connect

        change_connect(self.movieResetAction,
                       SIGNAL("triggered()"),
                       self.movieReset)

        change_connect(self.moviePlayRevAction,
                       SIGNAL("triggered()"),
                       self.moviePlayRev)

        change_connect(self.moviePauseAction,
                       SIGNAL("triggered()"),
                       self.moviePause)

        change_connect(self.moviePlayAction,
                       SIGNAL("triggered()"),
                       self.moviePlay)

        change_connect(self.movieMoveToEndAction,
                       SIGNAL("triggered()"),
                       self.movieMoveToEnd)

        change_connect(self.frameNumberSlider,
                       SIGNAL("valueChanged(int)"),
                       self.movieSlider)

        change_connect(self.frameNumberSpinBox,
                       SIGNAL("valueChanged(int)"),
                       self.moviePlayFrame)

        change_connect(self.fileOpenMovieAction,
                       SIGNAL("triggered()"),
                       self.fileOpenMovie)

        change_connect(self.fileSaveMovieAction,
                       SIGNAL("triggered()"),
                       self.fileSaveMovie)

        change_connect(self.movieInfoAction,
                       SIGNAL("triggered()"),
                       self.movieInfo)

    def updateMessage(self, msg = ''):
        """
        Updates the message box with an informative message.
        """
        if not msg:
            msg = "Use movie control buttons in the Property Manager to play " \
                "current simulation movie (if it exists). You can also load a" \
                "previously saved movie for this model using "\
                "<b>'Open Movie File...'</b> option."

        self.MessageGroupBox.insertHtmlMessage( msg,
                                                minLines      = 6,
                                                setAsDefault  =  True )

    def getOpenMovieFileInfo(self):
        """
        Updates the message groupbox message in the Movie Property Manager
        """
        msg = ''
        movie = self.w.assy.current_movie

        if movie:
            if movie.filename:
                fileName, numOfFrames, numOfAtoms = movie.getMovieInfo()
                msg1 = "<b>Movie File:</b> [%s] <br>" % (fileName)
                msg2 = "<b> Number Of Frames: </b>%s <br>" % (str(numOfFrames))
                msg3 = "<b> Number Of Atoms: </b>%s " % (str(numOfAtoms))
                msg = msg1 + msg2 + msg3
            else:
                msg1 = redmsg("No movie file opened.<br>")
                msg2 = " Use <b>'Open movie file'</b> to load any existing"\
                     " movie for the current part."
                msg = msg1 + msg2
        else:
            msg = redmsg("No movie file opened.")

        return msg

    def show(self):
        """
        Overrides the Ui_MoviePropertyManager.show) method.
        Updates the message groupbox with movie file information
        """
        msg = self.getOpenMovieFileInfo()
        self.updateMessage(msg)
        _superclass.show(self)

# ==

    # bruce 050428: these attrs say when we're processing a valueChanged
    # signal from slider or spinbox
    _moviePropMgr_in_valuechanged_SL = False
    _moviePropMgr_in_valuechanged_SB = False
    # bruce 050428: this says whether to ignore signals from slider and spinbox,
    # since they're being changed by the program rather than by the user.
    # (#e The Movie method that sets it should be made a method of this class.)
    _moviePropMgr_ignore_slider_and_spinbox = False

    def _moviePropMgr_reinit(self):
        self._moviePropMgr_ignore_slider_and_spinbox = True
        try:
            self.frameNumberSpinBox.setMaximum(999999) # in UI.py code
            self.frameNumberSlider.setMaximum(999999) # guess
            self.frameNumberSpinBox.setValue(0) # guess
            self.frameNumberSlider.setValue(0) # guess
        finally:
            self._moviePropMgr_ignore_slider_and_spinbox = False
        return

    def moviePlay(self):
        """
        Play current movie foward from current position.
        """
        if self.w.assy.current_movie: #bruce 050427 added this condition in all these slot methods
            self.w.assy.current_movie._play(1)

    def moviePause(self):
        """
        Pause movie.
        """
        if self.w.assy.current_movie:
            self.w.assy.current_movie._pause()

    def moviePlayRev(self):
        """
        Play current movie in reverse from current position.
        """
        if self.w.assy.current_movie:
            self.w.assy.current_movie._play(-1)

    def movieReset(self):
        """
        Move current frame position to frame 0 (beginning) of the movie.
        """
        if self.w.assy.current_movie:
            self.w.assy.current_movie._reset()

    def movieMoveToEnd(self):
        """
        Move frame position to the last frame (end) of the movie.
        """
        if self.w.assy.current_movie:
            self.w.assy.current_movie._moveToEnd()

    def moviePlayFrame(self, fnum):
        """
        Show frame fnum in the current movie. This slot receives
        valueChanged(int) signal from self.frameNumberSpinBox.
        """
        if not self.w.assy.current_movie:
            return
        if self._moviePropMgr_ignore_slider_and_spinbox:
            return
        ## next line is redundant, so I removed it [bruce 050428]
        ## if fnum == self.w.assy.current_movie.currentFrame: return

        self._moviePropMgr_in_valuechanged_SB = True
        try:
            self.w.assy.current_movie._playToFrame(fnum)
        finally:
            self._moviePropMgr_in_valuechanged_SB = False
        return

    def movieSlider(self, fnum):
        """
        Show frame fnum in the current movie. This slot receives
        valueChanged(int) signal from self.frameNumberSlider.
        """
        if not self.w.assy.current_movie:
            return
        if self._moviePropMgr_ignore_slider_and_spinbox:
            return
        ## next line is redundant, so I removed it [bruce 050428]
        ## if fnum == self.w.assy.current_movie.currentFrame: return

        self._moviePropMgr_in_valuechanged_SL = True
        try:
            self.w.assy.current_movie._playSlider(fnum)
        finally:
            self._moviePropMgr_in_valuechanged_SL = False
        return

    def movieInfo(self):
        """
        Prints information about the current movie to the history widget.
        """
        if not self.w.assy.current_movie:
            return
        env.history.message(greenmsg("Movie Information"))
        self.w.assy.current_movie._info()

    def fileOpenMovie(self):
        """
        Open a movie file to play.
        """
        # bruce 050327 comment: this is not yet updated for "multiple movie objects"
        # and bugfixing of bugs introduced by that is in progress (only done in a klugy
        # way so far). ####@@@@
        env.history.message(greenmsg("Open Movie File:"))
        assert self.w.assy.current_movie
            # (since (as a temporary kluge) we create an empty one, if necessary, before entering
            #  Movie Mode, of which this is a dashboard method [bruce 050328])
        if self.w.assy.current_movie and self.w.assy.current_movie.currentFrame != 0:
            ###k bruce 060108 comment: I don't know if this will happen when currentFrame != 0 due to bug 1273 fix... #####@@@@@
            env.history.message(redmsg("Current movie must be reset to frame 0 to load a new movie."))
            return

        # Determine what directory to open. [bruce 050427 comment: if no moviefile, we should try assy.filename's dir next ###e]
        if self.w.assy.current_movie and self.w.assy.current_movie.filename:
            odir, fil, ext = filesplit(self.w.assy.current_movie.filename)
            del fil, ext #bruce 050413
        else:
            odir = self.w.currentWorkingDirectory # Fixes bug 291 (comment #4). Mark 060729.


        fn = QFileDialog.getOpenFileName(
            self,
            "Differential Position Bytes Format (*.dpb)",
            odir)

        if not fn:
            env.history.message("Cancelled.")
            return

        fn = str(fn)

        # Check if file with name fn is a movie file which is valid for the current Part
        # [bruce 050324 made that a function and made it print the history messages
        #  which I've commented out below.]
        from simulation.movie import _checkMovieFile
        r = _checkMovieFile(self.w.assy.part, fn)

        if r == 1:

##            msg = redmsg("Cannot play movie file [" + fn + "]. It does not exist.")
##            env.history.message(msg)
            return
        elif r == 2:
##            msg = redmsg("Movie file [" + fn + "] not valid for the current part.")
##            env.history.message(msg)
            if self.w.assy.current_movie and self.w.assy.current_movie.might_be_playable(): #bruce 050427 isOpen -> might_be_playable()
                msg = "(Previous movie file [" + self.w.assy.current_movie.filename + "] is still open.)"
                env.history.message(msg)
            return

        #bruce 050427 rewrote the following to use a new Movie object
        from simulation.movie import find_saved_movie
        new_movie = find_saved_movie( self.w.assy, fn )
        if new_movie:
            new_movie.set_alist_from_entire_part(self.w.assy.part) # kluge? might need changing...
            if self.w.assy.current_movie: #bruce 050427 no longer checking isOpen here
                self.w.assy.current_movie._close()
            self.w.assy.current_movie = new_movie
            self.w.assy.current_movie.cueMovie(propMgr = self)
            #Make sure to enable movie control buttons!
            self.command.enableMovieControls(True)
            self.updateFrameInformation()
            self._updateMessageInModePM()
        else:
            # should never happen due to _checkMovieFile call, so this msg is ok
            # (but if someday we do _checkMovieFile inside find_saved_movie and not here,
            #  then this will happen as an error return from find_saved_movie)
            msg = redmsg("Internal error in fileOpenMovie")
            self.command.enableMovieControls(False)
            self._updateMessageInModePM(msg)
            env.history.message(msg)
        return

    def _updateMessageInModePM(self, msg = ''):
        """
        Updates the message box in the Movie Property Manager with the
        information about the opened movie file.
        @WARNING: This is a temporary method. Likely to be moved/ modified
        when movieMode.py is cleaned up. See bug 2428 for details.
        """
        #@WARNING: Following updates  the Movie property manager's message
        #groupbox. This should be done in a better way. At present there
        # is no obvious way to tell the Movie Property manager that the
        # movie has changed. So this is a kludge.
        # See bug 2428 comment 8 for further details -- Ninad 2007-10-02
        currentCommand = self.win.commandSequencer.currentCommand
        if currentCommand.commandName == "MOVIE":
            if currentCommand.propMgr:
                if not msg:
                    msg = currentCommand.propMgr.getOpenMovieFileInfo()
                currentCommand.propMgr.updateMessage(msg)

    def fileSaveMovie(self):
        """
        Save a copy of the current movie file loaded in the Movie Player.
        """
        # Make sure there is a moviefile to save.
        if not self.w.assy.current_movie or not self.w.assy.current_movie.filename \
           or not os.path.exists(self.w.assy.current_movie.filename):

            msg = redmsg("Save Movie File: No movie file to save.")
            env.history.message(msg)
            msg = "To create a movie, click on the <b>Simulator</b> <img source=\"simicon\"> icon."
            #QMimeSourceFactory.defaultFactory().setPixmap( "simicon",
            #            self.simSetupAction.iconSet().pixmap() )
            env.history.message(msg)
            return

        env.history.message(greenmsg("Save Movie File:"))

        if self.w.assy.filename: sdir = self.w.assy.filename
        else: sdir = env.prefs[workingDirectory_prefs_key]

        sfilter = QString("Differential Position Bytes Format (*.dpb)")

        # Removed .xyz as an option in the sfilter since the section of code below
        # to save XYZ files never worked anyway.  This also fixes bug 492.  Mark 050816.

        fn = QFileDialog.getSaveFileName(
            self,
            "Save As",
            sdir,
            "Differential Position Bytes Format (*.dpb);;POV-Ray Series (*.pov)",
            sfilter)

        if not fn:
            env.history.message("Cancelled.")
            return
        else:
            fn = str(fn)
            dir, fil, ext2 = filesplit(fn)
            del ext2 #bruce 050413
            ext = str(sfilter[-5:-1]) # Get "ext" from the sfilter. It *can* be different from "ext2"!!! - Mark
                #bruce 050413 comment: the above assumes that len(ext) is always 4 (.xxx).
                # I'm speculating that this is ok for now since it has to be one of the ones
                # provided to the getSaveFileName method above.
            # Changed os.path.join > os.path.normpath to partially fix bug #956.  Mark 050911.
            safile = os.path.normpath(dir + "/" + fil + ext) # full path of "Save As" filename

            if os.path.exists(safile): # ...and if the "Save As" file exists...

                # ... confirm overwrite of the existing file.
                ret = QMessageBox.warning(
                    self, "Confirm overwrite",
                    "The file \"" + fil + ext + "\" already exists.\n"\
                    "Do you want to overwrite the existing file or cancel?",
                    "&Overwrite", "&Cancel", "",
                    0,      # Enter == button 0
                    1 )     # Escape == button 1

                if ret == 1: # The user cancelled
                    env.history.message( "Cancelled.  File not saved." )
                    return # Cancel clicked or Alt+C pressed or Escape pressed

            if ext == '.dpb':
                self.w.assy.current_movie._close()
                import shutil
                shutil.copy(self.w.assy.current_movie.filename, safile)

                # Get the trace file name.
                tfile1 = self.w.assy.current_movie.get_trace_filename()

                # Copy the tracefile
                if os.path.exists(tfile1):
                    fullpath, ext = os.path.splitext(safile)
                    tfile2 = fullpath + "-trace.txt"
                    shutil.copy(tfile1, tfile2)

                env.history.message("DPB movie file saved: " + safile)
                # note that we are still playing it from the old file and filename... does it matter? [bruce 050427 question]

                # Added "hflag=False" to suppress history msg, fixing bug #956.  Mark 050911.
                self.w.assy.current_movie.cueMovie(propMgr = self, hflag = False) # Do not print info to history widget.

            elif ext == '.pov':
                self.w.assy.current_movie._write_povray_series(
                    os.path.normpath(dir + "/" + fil))

            else: #.xyz (or something unexpected)
                #bruce 051115 added warning and immediate return, to verify that this code is never called
                QMessageBox.warning(self, "ERROR", "internal error: unsupported file extension %r" % (ext,) ) # args are title, content

        return # from fileSaveMovie

    def updateFrameInformation(self):
        """
        Update movie control widgets in PM to the current movie frames.
        """
        movie = self.w.assy.current_movie
        self.frameNumberSlider.setMaximum(movie.getTotalFrames())
        self.frameNumberSpinBox.setMaximum(movie.getTotalFrames())
        self.frameSkipSpinBox.setMaximum(movie.getTotalFrames())
            #ninad060928 fixed bug 2285
        self.updateCurrentFrame()

        return

    def updateCurrentFrame(self):
        """
        Update dashboard controls which show self.currentFrame, except for the
        ones being used to change it.
        """
        #bruce 050428 split this out too, added all conditions/flags; ##e it should become a method of movieDashboardSlotsMixin
        if not self.w.assy.current_movie:
            return
        movie = self.w.assy.current_movie
        old = self._moviePropMgr_ignore_slider_and_spinbox # not sure if this is ever True here
        self._moviePropMgr_ignore_slider_and_spinbox = True
        try:
            dont_update_slider = self._moviePropMgr_in_valuechanged_SL  # SL = Slider
            dont_update_spinbox = self._moviePropMgr_in_valuechanged_SB  # SB = SpinBox
            if not dont_update_slider:
                self.frameNumberSlider.setValue(movie.getCurrentFrame())
                currentFrameLbl = str(self.frameNumberSlider.value())
                totalFrameLbl = str(movie.getTotalFrames())
                flabel = "Current Frame: " + currentFrameLbl + "/" + \
                       totalFrameLbl
                self.movieFrameUpdateLabel.setText(flabel)
            if not dont_update_spinbox:
                self.frameNumberSpinBox.setValue(movie.getCurrentFrame())
        finally:
            self._moviePropMgr_ignore_slider_and_spinbox = old
        return

    def enableMovieControls(self, enabled = True):
        """
        Enable or disable movie control button.
        """
        self.movieResetAction.setEnabled(enabled)
        self.moviePlayRevAction.setEnabled(enabled)
        self.moviePauseAction.setEnabled(enabled)
        self.moviePlayAction.setEnabled(enabled)
        self.movieMoveToEndAction.setEnabled(enabled)
        self.frameNumberSlider.setEnabled(enabled)
        self.frameNumberSpinBox.setEnabled(enabled)
        self.fileSaveMovieAction.setEnabled(enabled)
        return

    pass # end of class movieDashboardSlotsMixin


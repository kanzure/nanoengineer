# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
SimSetup.py

Dialog for setting up to run the simulator.

@author: Mark
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

Created by Mark, under the name runSim.py.

Bruce 050324 changed some comments and did some code cleanup
(and also moved a lot of existing code for actually "running the simulator"
 into runSim.py, so that file still exists, but has all different code
 than before).

Bruce 050325 renamed file and class to SimSetup, to fit naming
convention for other Dialog subclasses.
"""

import os

from PyQt4.Qt import QDialog
from PyQt4.Qt import QButtonGroup
from PyQt4.Qt import QAbstractButton
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QSize, QWhatsThis

import foundation.env as env

from simulation.SimSetupDialog import Ui_SimSetupDialog
from simulation.movie import Movie
from utilities.debug import print_compact_traceback
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref
from utilities.prefs_constants import Potential_energy_tracefile_prefs_key
from utilities.prefs_constants import electrostaticsForDnaDuringDynamics_prefs_key
from utilities.debug_prefs import debug_pref, Choice_boolean_False
from utilities.qt4transition import qt4todo
from utilities.TimeUtilities import timeStamp
from utilities.icon_utilities import geticon

# class FakeMovie:
#
# wware 060406 bug 1471 (sticky dialog params) - don't need a real movie, just need to hold the sim parameters
# If the sim parameters change, they might need to be updated everywhere a comment says "SIMPARAMS".
#
#bruce 060601 moving this here, since it's really an aspect of this dialog
# (in terms of what params to store, when to store them, etc);
# also fixing bug 1840 (like 1471 but work even after a sim was not aborted),
# and making the stickyness survive opening of a new file rather than being stored in the assy.

class FakeMovie:
    def __init__(self, realmovie):
        self.totalFramesRequested = realmovie.totalFramesRequested
        self.temp = realmovie.temp
        self.stepsper = realmovie.stepsper
        self.watch_motion = realmovie.watch_motion # note 060705: might use __getattr__ in real movie, but ordinary attr in self
        self._update_data = realmovie._update_data
        self.update_cond = realmovie.update_cond # probably not needed
        self.print_energy = realmovie.print_energy
    def fyi_reusing_your_moviefile(self, moviefile):
        pass
    def might_be_playable(self):
        return False
    pass

_stickyParams = None # sometimes this is a FakeMovie object


class SimSetup(QDialog, Ui_SimSetupDialog): # before 050325 this class was called runSim
    """
    The "Run Dynamics" dialog class for setting up and launching a simulator run.
    """
    def __init__(self, win, part, previous_movie = None, suffix = ""):
        """
        use previous_movie (if passed) for default values,
        otherwise use the same ones last ok'd by user
        (whether or not that sim got aborted), or default values if that never happened in this session;
        on success or failure, make a new Movie and store it as self.movie
        """
        QDialog.__init__(self, win) # win is parent.
        self.setupUi(self)

        self.setWindowIcon(geticon('ui/border/RunDynamics.png'))

        self.whatsthis_btn.setIcon(
            geticon('ui/actions/Properties Manager/WhatsThis.png'))
        self.whatsthis_btn.setIconSize(QSize(22, 22))
        self.whatsthis_btn.setToolTip('Enter "What\'s This?" help mode')

        self.connect(self.whatsthis_btn,
                     SIGNAL("clicked()"),
                     QWhatsThis.enterWhatsThisMode)

        self.watch_motion_buttongroup = QButtonGroup()
        self.watch_motion_buttongroup.setExclusive(True)
        for obj in self.watch_motion_groupbox.children():
            if isinstance(obj, QAbstractButton):
                self.watch_motion_buttongroup.addButton(obj)
        self.connect(self.run_sim_btn,SIGNAL("clicked()"),self.createMoviePressed)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.close)
        qt4todo('self.connect(self.watch_motion_groupbox,SIGNAL("toggled(bool)"),self.setEnabled) ???')
        self.watch_motion_groupbox.setEnabled(True)
        ## self.part = part
            # not yet needed, though in future we might display info
            # about this Part in the dialog, to avoid confusion
            # if it's not the main Part.
        connect_checkbox_with_boolean_pref(self.potential_energy_checkbox,
                                           Potential_energy_tracefile_prefs_key)

        connect_checkbox_with_boolean_pref(
            self.electrostaticsForDnaDuringDynamics_checkBox,
            electrostaticsForDnaDuringDynamics_prefs_key)

        self.assy = part.assy # used only for assy.filename
        self.suffix = suffix
        self.previous_movie = previous_movie or _stickyParams or Movie(self.assy) # used only for its parameter settings
            # note: as of bruce 060601 fixing bug 1840, previous_movie is no longer ever passed by caller.
        self.movie = Movie(self.assy) # public attr used by client code after we return; always a Movie even on failure.
            # (we need it here since no extra method runs on failure, tho that could probably be fixed)
            # bruce 050325 changes:
            # We make a new Movie here (but only when we return with success).
            # But we use default param settings from prior movie.
            # Caller should pass info about default filename (including uniqueness
            #  when on selection or in clipboard item) -- i.e. the suffix.
            # We should set the params and filename using a Movie method, or warn it we did so,
            # or do them in its init... not yet cleaned up. ###@@@
            # self.movie is now a public attribute.
            #bruce 050329 comment: couldn't we set .movie to None, until we learn we succeeded? ###e ###@@@
        self.setup()
        self.watch_motion_groupbox.setWhatsThis(
            """<b>Watch motion in real time</b>
            <p>
            Enables real time graphical updates during simulation runs.
            """)
        self.update_number_spinbox.setWhatsThis(
            """<b>Update every <i>n units.</u></b>
            <p>
            Specify how often to update the model during the simulation.
            This allows the user to monitor simulation results while the
            simulation is running.
            </p>""")
        self.update_units_combobox.setWhatsThis(
            """<b>Update every <i>n units.</u></b>
            <p>
            Specify how often to update the model during the simulation.
            This allows the user to monitor simulation results while the
            simulation is running.
            </p>""")
        self.update_every_rbtn.setWhatsThis(
            """<b>Update every <i>n units.</u></b>
            <p>
            Specify how often to update the model during the simulation.
            This allows the user to monitor simulation results while the
            simulation is running.</p>""")
        self.update_asap_rbtn.setWhatsThis(
            """<b>Update as fast as possible</b>
            <p>
            Update every 2 seconds, or faster (up to 20x/sec) if it doesn't
            slow down the simulation by more than 20%.
            </p>""")
        self.temperatureSpinBox.setWhatsThis(
            """<b>Temperature</b>
            <p>
            The temperature of the simulation in Kelvin
            (300 K = room temperature)</p>""")
        self.totalFramesSpinBox.setWhatsThis(
            """<b>Total frames</b>
            <p>
            The total number of (movie) frames to create for the simulation run.
            </p>""")
        self.stepsPerFrameDoubleSpinBox.setWhatsThis(
            """<b>Steps per frame</b>
            <p>
            The time duration between frames in femtoseconds.
            </p>""")
        self.setWhatsThis(
            """<b>Run Dynamics</b>
            <p>
            The is the main dialog for configuring and launching a
            Molecular Dynamics simulation run. Specify the simulation parameters
            and click <b>Run Simulation</b> to launch.</p>
            <p>
            <img source=\"ui/actions/Simulation/PlayMovie.png\"><br>
            The <b>Play Movie</b> command can be used to play back the
            simulation.
            </p>""")

        if not debug_pref("GROMACS: Enable for Run Dynamics", Choice_boolean_False,
                          prefs_key=True):
            # Hide the Simulation engine groupbox altogether.
            self.md_engine_groupbox.setHidden(True)

        self.exec_()

    def setup(self):
        self.movie.cancelled = True # We will assume the user will cancel
        #bruce 050324: fixed KnownBug item 27 by making these call setValue, not assign to it:
        # If the sim parameters change, they need to be updated in all places marked "SIMPARAMS"
        # Movie.__init__ (movie.py), toward the end
        # SimSetup.setup (SimSetup.py)
        # FakeMovie.__init (runSim.py)
        self.totalFramesSpinBox.setValue( self.previous_movie.totalFramesRequested )
        self.temperatureSpinBox.setValue( self.previous_movie.temp )
        self.stepsPerFrameDoubleSpinBox.setValue( self.previous_movie.stepsper / 10.0 )
#        self.timestepSB.setValue( self.previous_movie.timestep ) # Not supported in Alpha
        # new checkboxes for Alpha7, circa 060108
        #self.create_movie_file_checkbox.setChecked( self.previous_movie.create_movie_file )
            # whether to store movie file (see NFR/bug 1286). [bruce & mark 060108]
            # create_movie_file_checkbox removed for A7 (bug 1729). mark 060321

        ##e the following really belongs in the realtime_update_controller,
        # and the update_cond is not the best thing to set this from;
        # but we can leave it here, then let the realtime_update_controller override it if it knows how. [now it does]
        self.watch_motion_groupbox.setChecked( self.previous_movie.watch_motion ) # whether to move atoms in realtime

        try:
            #bruce 060705 use new common code, if it works
            from widgets.widget_controllers import realtime_update_controller
            self.ruc = realtime_update_controller(
                ( self.watch_motion_buttongroup, self.update_number_spinbox, self.update_units_combobox ),
                self.watch_motion_groupbox
                # no prefs key for checkbox
            )
            self.ruc.set_widgets_from_update_data( self.previous_movie._update_data ) # includes checkbox
        except:
            print_compact_traceback( "bug; reverting to older code in simsetep setup: ")
            if self.previous_movie._update_data:
                update_number, update_units, update_as_fast_as_possible_data, watchjunk = self.previous_movie._update_data
                self.watch_motion_groupbox.setChecked(watchjunk) ###060705
                self.watch_motion_groupbox.setButton( update_as_fast_as_possible_data)
                self.update_number_spinbox.setValue( update_number)
                self.update_units_combobox.setCurrentText( update_units)
                    #k let's hope this changes the current choice, not the popup menu item text for the current choice!
        return

    def createMoviePressed(self):
        """
        Creates a DPB (movie) file of the current part.
        [Actually only saves the params and filename which should be used
         by the client code (in writemovie?) to create that file.]
        The part does not have to be saved as an MMP file first, as it used to.
        """
        ###@@@ bruce 050324 comment: Not sure if/when user can rename the file.
        QDialog.accept(self)

        if self.simulation_engine_combobox.currentIndex() == 1:
            # GROMACS was selected as the simulation engine.
            #
            # NOTE: This code is just for demo and prototyping purposes - the
            # real approach will be architected and utilize plugins.
            #
            # Brian Helfrich 2007-04-06
            #
            from simulation.GROMACS.GROMACS import GROMACS
            gmx = GROMACS(self.assy.part)
            gmx.run("md")

        else:
            # NanoDynamics-1 was selected as the simulation engine
            #
            errorcode, partdir = self.assy.find_or_make_part_files_directory()

            self.movie.cancelled = False # This is the only way caller can tell we succeeded.
            self.movie.totalFramesRequested = self.totalFramesSpinBox.value()
            self.movie.temp = self.temperatureSpinBox.value()
            self.movie.stepsper = self.stepsPerFrameDoubleSpinBox.value() * 10.0
            self.movie.print_energy = self.potential_energy_checkbox.isChecked()
    #        self.movie.timestep = self.timestepSB.value() # Not supported in Alpha
            #self.movie.create_movie_file = self.create_movie_file_checkbox.isChecked()
                # removed for A7 (bug 1729). mark 060321
            self.movie.create_movie_file = True

            # compute update_data and update_cond, using new or old code
            try:
                # try new common code for this, bruce 060705
                ruc = self.ruc
                update_cond = ruc.get_update_cond_from_widgets()
                assert update_cond or (update_cond is False) ###@@@ remove when works, and all the others like this
                # note, if those widgets are connected to env.prefs, that's not handled here or in ruc;
                # I'm not sure if they are. Ideally we'd tell ruc the prefs_keys and have it handle that too,
                # perhaps making it a long-lived object (though that might not be necessary).
                update_data = ruc.get_update_data_from_widgets() # redundant, but we can remove it when ruc handles prefs
            except:
                print_compact_traceback("bug using realtime_update_controller in SimSetup, will use older code instead: ")
                    # this older code can be removed after A8 if we don't see that message
                #bruce 060530 use new watch_motion rate parameters
                self.movie.watch_motion = self.watch_motion_groupbox.isChecked() # [deprecated for setattr as of 060705]
                if env.debug():
                    print "debug fyi: sim setup watch_motion = %r" % (self.movie.watch_motion,)
                # This code works, but I'll try to replace it with calls to common code (above). [bruce 060705]
                # first grab them from the UI
                update_as_fast_as_possible_data = self.watch_motion_groupbox.selectedId() # 0 means yes, 1 means no (for now)
                    # ( or -1 means neither, but that's prevented by how the button group is set up, at least when it's enabled)
                update_as_fast_as_possible = (update_as_fast_as_possible_data != 1)
                update_number = self.update_number_spinbox.value() # 1, 2, etc (or perhaps 0??)
                update_units = str(self.update_units_combobox.currentText()) # 'frames', 'seconds', 'minutes', 'hours'
                # for sake of propogating them to the next sim run:
                update_data = update_number, update_units, update_as_fast_as_possible_data, self.movie.watch_motion
    ##                if env.debug():
    ##                    print "stored _update_data %r into movie %r" % (self.movie._update_data, self.movie)
    ##                    print "debug: self.watch_motion_groupbox.selectedId() = %r" % (update_as_fast_as_possible_data,)
    ##                    print "debug: self.update_number_spinbox.value() is %r" % self.update_number_spinbox.value() # e.g. 1
    ##                    print "debug: combox text is %r" % str(self.update_units_combobox.currentText()) # e.g. 'frames'
                # Now figure out what these user settings mean our realtime updating algorithm should be,
                # as a function to be used for deciding whether to update the 3D view when each new frame is received,
                # which takes as arguments the time since the last update finished (simtime), the time that update took (pytime),
                # and the number of frames since then (nframes, 1 or more), and returns a boolean for whether to draw this new frame.
                # Notes:
                # - The Qt progress update will be done independently of this, at most once per second (in runSim.py).
                # - The last frame we expect to receive will always be drawn. (This func may be called anyway in case it wants
                #   to do something else with the info like store it somewhere, or it may not (check runSim.py for details #k),
                #   but its return value will be ignored if it's called for the last frame.)
                # The details of these functions (and the UI feeding them) might be revised.

                # This code for setting update_cond is duplicated (inexactly) in Minimize_CommandRun.doMinimize()
                if update_as_fast_as_possible:
                    # This radiobutton might be misnamed; it really means "use the old code,
                    # i.e. not worse than 20% slowdown, with threshholds".
                    # It's also ambiguous -- does "fast" mean "fast progress"
                    # or "often" (which are opposites)? It sort of means "often".
                    update_cond = ( lambda simtime, pytime, nframes:
                                    simtime >= max(0.05, min(pytime * 4, 2.0)) )
                elif update_units == 'frames':
                    update_cond = ( lambda simtime, pytime, nframes, _nframes = update_number:  nframes >= _nframes )
                elif update_units == 'seconds':
                    update_cond = ( lambda simtime, pytime, nframes, _timelimit = update_number:  simtime + pytime >= _timelimit )
                elif update_units == 'minutes':
                    update_cond = ( lambda simtime, pytime, nframes, _timelimit = update_number * 60:  simtime + pytime >= _timelimit )
                elif update_units == 'hours':
                    update_cond = ( lambda simtime, pytime, nframes, _timelimit = update_number * 3600:  simtime + pytime >= _timelimit )
                else:
                    print "don't know how to set update_cond from (%r, %r)" % (update_number, update_units)
                    update_cond = None
                # revision in this old code, 060705:
                if not self.movie.watch_motion:
                    update_cond = False
                del self.movie.watch_motion # let getattr do it
            # now do this, however we got update_data and update_cond:
            self.movie._update_data = update_data # for propogating them to the next sim run
            self.movie.update_cond = update_cond # used this time
            # end of 060705 changes

            suffix = self.suffix
            tStamp = timeStamp()
            if self.assy.filename and not errorcode: # filename could be an MMP or PDB file.
                import shutil
                dir, fil = os.path.split(self.assy.filename)
                fil, ext = os.path.splitext(fil)
                self.movie.filename = os.path.join(partdir, fil + '.' + tStamp + suffix + '.dpb')
                self.movie.origfile = os.path.join(partdir, fil + '.' + tStamp + '.orig' + ext)
                shutil.copy(self.assy.filename, self.movie.origfile)
            else:
                self.movie.filename = os.path.join(self.assy.w.tmpFilePath, "Untitled.%s%s.dpb" % (tStamp, suffix))
                # Untitled parts usually do not have a filename
            #bruce 060601 fix bug 1840, also make params sticky across opening of new files
            global _stickyParams
            _stickyParams = FakeMovie(self.movie) # these will be used as default params next time, whether or not this gets aborted
            return

    pass # end of class SimSetup

# end

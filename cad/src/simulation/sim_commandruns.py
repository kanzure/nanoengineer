# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
sim_commandruns.py -- user-visible commands for running the simulator,
for simulate or minimize (aka Run Dynamics, Minimize, Adjust --
but I'm not sure it's used for all of those)

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 050324 (and earlier) wrote this (in part by heavily rewriting
existing code) within runSim.py

Bruce 080321 split this into its own file
"""

from utilities.debug import print_compact_traceback
from platform_dependent.PlatformDependent import fix_plurals
from platform_dependent.PlatformDependent import hhmmss_str

from simulation.SimSetup import SimSetup
from simulation.movie import Movie

from utilities.Log import redmsg, greenmsg, orangemsg
import foundation.env as env

from utilities.prefs_constants import Adjust_minimizationEngine_prefs_key

from utilities.prefs_constants import MINIMIZE_ENGINE_UNSPECIFIED
from utilities.prefs_constants import MINIMIZE_ENGINE_GROMACS_FOREGROUND
from utilities.prefs_constants import MINIMIZE_ENGINE_GROMACS_BACKGROUND

# possibly some non-toplevel imports too (of which a few must remain non-toplevel)

from simulation.runSim import FAILURE_ALREADY_DOCUMENTED
from simulation.runSim import writemovie

# these next two are only used in this file; should be split into their own file(s)
from simulation.runSim import readxyz
from simulation.runSim import readGromacsCoordinates

from simulation.sim_aspect import sim_aspect

# ==

class CommandRun: # bruce 050324; mainly a stub for future use when we have a CLI; only used in this file as of 080321
    """
    Class for single runs of commands.
    Commands themselves (as opposed to single runs of them)
    don't yet have objects to represent them in a first-class way,
    but can be coded and invoked as subclasses of CommandRun.
    """
    def __init__(self, win, *args, **kws):
        self.win = win
        self.args = args # often not needed; might affect type of command (e.g. for Minimize)
        self.kws = kws # ditto; as of 060705, this contains 'type' for Minimize_CommandRun, for basic command name in the UI
        self.assy = win.assy
        self.part = win.assy.part
            # current Part (when the command is invoked), on which most commands will operate
        self.glpane = win.assy.o #e or let it be accessed via part??
        return
    # end of class CommandRun

class simSetup_CommandRun(CommandRun):
    """
    Class for single runs of the simulator setup command; create it
    when the command is invoked, to prep to run the command once;
    then call self.run() to actually run it.
    """
    cmdname = 'Simulator' #bruce 060106 temporary hack, should be set by subclass ###@@@
    def run(self):
        #bruce 050324 made this method from the body of MWsemantics.simSetup
        # and cleaned it up a bit in terms of how it finds the movie to use.
        if not self.part.molecules: # Nothing in the part to simulate.
            msg = redmsg("Nothing to simulate.")
            env.history.message(self.cmdname + ": " + msg)
            self.win.simSetupAction.setChecked(0) # toggle the Simulator icon ninad061113
            return

        env.history.message(self.cmdname + ": " + "Enter simulation parameters and select <b>Run Simulation.</b>")

        ###@@@ we could permit this in movie player mode if we'd now tell that mode to stop any movie it's now playing
        # iff it's the current mode.

        previous_movie = self.assy.current_movie
            # might be None; will be used only to restore self.assy.current_movie if we don't make a valid new one
        self.movie = None
        r = self.makeSimMovie( ) # will store self.movie as the one it made, or leave it as None if cancelled
        movie = self.movie
        self.assy.current_movie = movie or previous_movie
            # (this restores assy.current_movie if there was an error in making new movie, though perhaps nothing changed it anyway)

        if not r: # Movie file saved successfully; movie is a newly made Movie object just for the new file
            assert movie
            # if duration took at least 10 seconds, print msg.
##            self.progressbar = self.win.progressbar ###k needed???
##            duration = self.progressbar.duration [bruce 060103 zapped this kluge]
            try:
                duration = movie.duration #bruce 060103
            except:
                # this might happen if earlier exceptions prevented us storing one, so nevermind it for now
                duration = 0.0
            if duration >= 10.0:
                spf = "%.2f" % (duration / movie.totalFramesRequested)
                    ###e bug in this if too few frames were written; should read and use totalFramesActual
                estr = hhmmss_str(duration)
                msg = "Total time to create movie file: " + estr + ", Seconds/frame = " + spf
                env.history.message(self.cmdname + ": " + msg)
            msg = "Movie written to [" + movie.filename + "]." \
                "<br>To play the movie, select <b>Simulation > Play Movie</b>"
            env.history.message(self.cmdname + ": " + msg)
            self.win.simSetupAction.setChecked(0)
            self.win.simMoviePlayerAction.setEnabled(1) # Enable "Movie Player"
            self.win.simPlotToolAction.setEnabled(1) # Enable "Plot Tool"
            #bruce 050324 question: why are these enabled here and not in the subr or even if it's cancelled? bug? ####@@@@
        else:
            assert not movie
            # Don't allow uninformative messages to obscure informative ones - wware 060314
            if r == FAILURE_ALREADY_DOCUMENTED:
                env.history.message(self.cmdname + ": " + "Cancelled.")
                # (happens for any error; more specific message (if any) printed earlier)
        return

    def makeSimMovie(self): ####@@@@ some of this should be a Movie method since it uses attrs of Movie...
        #bruce 050324 made this from the Part method makeSimMovie.
        # It's called only from self.run() above; not clear it should be a separate method,
        # or if it is, that it's split from the caller at the right boundary.
        suffix = self.part.movie_suffix()
        if suffix is None: #bruce 050316 temporary kluge
            msg = redmsg( "Simulator is not yet implemented for clipboard items.")
            env.history.message(self.cmdname + ": " + msg)
            return -1
        ###@@@ else use suffix below!

        self.simcntl = SimSetup(self.win, self.part, suffix = suffix)
            # this now has its own sticky params, doesn't need previous_movie [bruce 060601, fixing bug 1840]
            # Open SimSetup dialog [and run it until user dismisses it]
        movie = self.simcntl.movie # always a Movie object, even if user cancelled the dialog

        if movie.cancelled:
            # user hit Cancel button in SimSetup Dialog. No history msg went out; caller will do that.
            movie.destroy()
            return -1
        r = writemovie(self.part, movie, print_sim_warnings = True, cmdname = self.cmdname)
            # not passing mtype means "run dynamic sim (not minimize), make movie"
            ###@@@ bruce 050324 comment: maybe should do following in that function too
        if not r:
            # Movie file created. Initialize. ###@@@ bruce 050325 comment: following mods private attrs, needs cleanup.
            movie.IsValid = True # Movie is valid.###@@@ bruce 050325 Q: what exactly does this (or should this) mean?
                ###@@@ bruce 050404: need to make sure this is a new obj-- if not always and this is not init False, will cause bugs
            self.movie = movie # bruce 050324 added this
            # it's up to caller to store self.movie in self.assy.current_movie if it wants to.
        return r

    pass # end of class simSetup_CommandRun



def _capitalize_first_word(words): #bruce 060705
    res = words[0].upper() + words[1:]
    if res == words:
        if env.debug():
            print "debug warning: %r did not change in _capitalize_first_word" % (words,)
    return res

_MIN_ALL, _LOCAL_MIN, _MIN_SEL = range(3) # internal codes for minimize command subtypes (bruce 051129)
    # this is a kluge compared to using command-specific subclasses, but better than testing something else like cmdname

class Minimize_CommandRun(CommandRun):
    """
    Class for single runs of the commands Minimize Selection, Minimize All,
    Adjust Selection, or Adjust All (which one is determined by one or more
    __init__ args, stored in self.args by superclass);
    client code should create an instance when the command is invoked, to
    prepare to run the command once; then call self.run() to actually run it.
    [#e A future code cleanup might split this into a Minimize superclass
     and separate subclasses for 'All' vs 'Sel' -- or it might not.]
    """
    def run(self):
        """
        Minimize (or Adjust) the Selection or the current Part
        """
        #bruce 050324 made this method from the body of MWsemantics.modifyMinimize
        # and cleaned it up a bit in terms of how it finds the movie to use.

        #bruce 050412 added 'Sel' vs 'All' now that we have two different Minimize buttons.
        # In future the following code might become subclass-specific (and cleaner):

        ## fyi: this old code was incorrect, I guess since 'in' works by 'is' rather than '==' [not verified]:
        ## assert self.args in [['All'], ['Sel']], "%r" % (self.args,)

        #bruce 051129 revising this to clarify it, though command-specific subclasses would be better
        assert len(self.args) >= 1
        cmd_subclass_code = self.args[0]
        cmd_type = self.kws.get('type', 'Minimize')
            # one of 'Minimize' or 'Adjust' or 'Adjust Atoms'; determines conv criteria, name [bruce 060705]
        self.cmd_type = cmd_type # kluge, see comment where used

        engine = self.kws.get('engine', MINIMIZE_ENGINE_UNSPECIFIED)
        if (engine == MINIMIZE_ENGINE_UNSPECIFIED):
            engine = env.prefs[Adjust_minimizationEngine_prefs_key]

        if (engine == MINIMIZE_ENGINE_GROMACS_FOREGROUND):
            self.useGromacs = True
            self.background = False
        elif (engine == MINIMIZE_ENGINE_GROMACS_BACKGROUND):
            self.useGromacs = True
            self.background = True
        else:
            self.useGromacs = False
            self.background = False

        assert cmd_subclass_code in ['All', 'Sel', 'Atoms'] #e and len(args) matches that?

        # These words and phrases are used in history messages and other UI text;
        # they should be changed by specific commands as needed.
        # See also some computed words and phrases, e.g. self.word_Minimize,
        # below the per-command if stamements. [bruce 060705]
        # Also set flags for other behavior which differs between these commands.
        if cmd_type.startswith('Adjust'):

            self.word_minimize = "adjust"
            self.word_minimization = "adjustment"
            self.word_minimizing = "adjusting"

            anchor_all_nonmoving_atoms = False
            pass

        else:

            assert cmd_type.startswith('Minimize')
            self.word_minimize = "minimize"
            self.word_minimization = "minimization"
            self.word_minimizing = "minimizing"

            anchor_all_nonmoving_atoms = True
                #bruce 080513 revision to implement nfr bug 2848 item 2
                # (note: we might decide to add a checkbox for this into the UI,
                #  and just change its default value for Minimize vs Adjust)
            pass

        self.word_Minimize = _capitalize_first_word( self.word_minimize)
        self.word_Minimizing = _capitalize_first_word( self.word_minimizing)

        if cmd_subclass_code == 'All':
            cmdtype = _MIN_ALL
            cmdname = "%s All" % self.word_Minimize

        elif cmd_subclass_code == 'Sel':
            cmdtype = _MIN_SEL
            cmdname = "%s Selection" % self.word_Minimize

        elif cmd_subclass_code == 'Atoms':
            #bruce 051129 added this case for Local Minimize (extending a kluge -- needs rewrite to use command-specific subclass)
            cmdtype = _LOCAL_MIN
            cmdname = "%s Atoms"  % self.word_Minimize #bruce 060705; some code may assume this is always Adjust Atoms, as it is
            # self.args is parsed later

        else:
            assert 0, "unknown cmd_subclass_code %r" % (cmd_subclass_code,)
        self.cmdname = cmdname #e in principle this should come from a subclass for the specific command [bruce 051129 comment]
        startmsg = cmdname + ": ..."
        del cmd_subclass_code

        # remove model objects inserted only for feedback from prior runs
        # (both because it's a good feature, and to avoid letting them
        #  mess up this command) [bruce 080520]
        from simulation.runSim import part_contains_pam_atoms
            # kluge to use this function for this purpose
            # (it's called later for other reasons)
        hasPAM_junk = part_contains_pam_atoms( self.part,
                            kill_leftover_sim_feedback_atoms = True )
        self.part.assy.update_parts() ###k is this always safe or good?

        # Make sure some chunks are in the part.
        # (Valid for all cmdtypes -- Minimize only moves atoms, even if affected by jigs.)
        if not self.part.molecules: # Nothing in the part to minimize.
            env.history.message(greenmsg(cmdname + ": ") + redmsg("Nothing to %s." % self.word_minimize))
            return

        if cmdtype == _MIN_SEL:
            selection = self.part.selection_from_glpane() # compact rep of the currently selected subset of the Part's stuff
            if not selection.nonempty():
                msg = greenmsg(cmdname + ": ") + redmsg("Nothing selected.") + \
                    " (Use %s All to %s the entire Part.)" % (self.word_Minimize, self.word_minimize)
                        #e might need further changes for Minimize Energy, if it's confusing that Sel/All is a dialog setting then
                env.history.message( msg)
                return
        elif cmdtype == _LOCAL_MIN:
            from operations.ops_select import selection_from_atomlist
            junk, atomlist, ntimes_expand = self.args
            selection = selection_from_atomlist( self.part, atomlist) #e in cleaned up code, selection object might come from outside
            selection.expand_atomset(ntimes = ntimes_expand) # ok if ntimes == 0

            # Rationale for adding monovalent atoms to the selection before
            # instantiating the sim_aspect
            #
            # (Refer to comments for sim_aspect.__init__.) Why is it safe to add
            # monovalent atoms to a selection? Let's look at what happens during a
            # local minimization.
            #
            # While minimizing, we want to simulate as if the entire rest of the
            # part is grounded, and only our selection of atoms is free to move. The
            # most obvious approach would be to minimize all the atoms in the part
            # while applying anchors to the atoms that aren't in the selection. But
            # minimizing all the atoms, especially if the selection is small, is very
            # wasteful. Applying the simulator to atoms is expensive and we want to
            # minimize as few atoms as possible.
            #
            # [revision, bruce 080513: this discussion applies for Adjust,
            #  but the policy for Minimize is being changed to always include
            #  all atoms, even if most of them are anchored,
            #  re nfr bug 2848 item 2.]
            #
            # A more economical approach is to anchor the atoms for two layers going
            # out from the selection. The reason for going out two layers, and not just
            # one layer, is that we need bond angle terms to simulate accurately. When
            # we get torsion angles we will probably want to bump this up to three
            # layers. [Now we're doing three layers -- bruce 080507]
            #
            # Imagine labeling all the atoms in the selection with zero. Then take the
            # set of unlabeled atoms that are bonded to a zero-labeled atom, and label
            # all the atoms in that set with one. Next, take the set of yet-unlabeled
            # atoms that are bonded to a one-labeled atom, and label the atoms in that
            # set with two. The atoms labeled one and two become our first and second
            # layers, and we anchor them during the minimization.
            #
            # In sim_aspect.__init__, the labels for zero, one and two correspond
            # respectively to membership in the dictionaries self._moving_atoms,
            # self._boundary1_atoms, and self._boundary2_atoms.
            #
            # If an atom in the selection is anchored, we don't need to go two layers
            # out from that atom, only one layer. So we can label it with one, even
            # though it's a member of the selection and would normally be labeled with
            # zero. The purpose in doing this is to give the simulator a few less atoms
            # to worry about.
            #
            # If a jig includes one of the selected atoms, but additionally includes
            # atoms outside the selection, then it may not be obvious how to simulate
            # that jig. For the present, the only jig that counts in a local
            # minimization is an anchor, because all the other jigs are too complicated
            # to simulate.
            #
            # The proposed fix here has the effect that monovalent atoms bonded to
            # zero-labeled atoms are also labeled zero, rather than being labeled one,
            # so they are allowed to move. Why is this OK to do?
            #
            # (1) Have we violated the assumption that the rest of the part is locked
            # down? Yes, as it applies to those monovalent atoms, but they are
            # presumably acceptable violations, since bug 1240 is regarded as a bug.
            #
            # (2) Have we unlocked any bond lengths or bond angles that should remain
            # locked? Again, only those which involve (and necessarily end at) the
            # monovalent atoms in question. The same will be true when we introduce
            # torsion terms.
            #
            # (3) Have we lost any ground on the jig front? If a jig includes one or
            # more of the monovalent atoms, possibly - but the only jigs we are
            # simulating in this case is anchors, and those will be handled correctly.
            # Remember that anchored atoms are only extended one layer, not two, but
            # with a monovalent atom bonded to a selected atom, no extension is
            # possible at all.
            #
            # One can debate about whether bug 1240 should be regarded as a bug. But
            # having accepted it as a bug, one cannot object to adding these monovalents
            # to the original selection.
            #
            # wware 060410 bug 1240
            atoms = selection.selatoms
            for atom in atoms.values():
                # enumerate the monovalents bonded to atom
                for atom2 in filter(lambda atom: not atom.is_singlet(), atom.baggageNeighbors()):
                    atoms[atom2.key] = atom2

        else:
            assert cmdtype == _MIN_ALL
            selection = self.part.selection_for_all()
                # like .selection_from_glpane() but for all atoms presently in the part [bruce 050419]
            # no need to check emptiness, this was done above

        self.selection = selection #e might become a feature of all CommandRuns, at some point

        # At this point, the conditions are met to try to do the command.
        env.history.message(greenmsg( startmsg)) #bruce 050412 doing this earlier

        # Disable some QActions (menu items/toolbar buttons) during minimize.
        self.win.disable_QActions_for_sim(True)
        try:
            simaspect = sim_aspect( self.part,
                                    selection.atomslist(),
                                    cmdname_for_messages = cmdname,
                                    anchor_all_nonmoving_atoms = anchor_all_nonmoving_atoms
                                   )
                #bruce 051129 passing cmdname
                # note: atomslist gets atoms from selected chunks, not only selected atoms
                # (i.e. it gets atoms whether you're in Select Atoms or Select Chunks mode)
            # history message about singlets written as H (if any);
            #bruce 051115 updated comment: this is used for both Minimize All and Minimize Selection as of long before 051115;
            # for Run Sim this code is not used (so this history message doesn't go out for it, though it ought to)
            # but the bug254 X->H fix is done (though different code sets the mapping flag that makes it happen).
            nsinglets_H = simaspect.nsinglets_H()
            if nsinglets_H: #bruce 051209 this message code is approximately duplicated elsewhere in this file
                info = fix_plurals( "(Treating %d bondpoint(s) as Hydrogens, during %s)" % (nsinglets_H, self.word_minimization) )
                env.history.message( info)
            nsinglets_leftout = simaspect.nsinglets_leftout()
            assert nsinglets_leftout == 0 # for now
            # history message about how much we're working on; these atomcounts include singlets since they're written as H
            nmoving = simaspect.natoms_moving()
            nfixed  = simaspect.natoms_fixed()
            info = fix_plurals( "(%s %d atom(s)" % (self.word_Minimizing, nmoving))
            if nfixed:
                them_or_it = (nmoving == 1) and "it" or "them"
                if anchor_all_nonmoving_atoms:
                    msg2 = "holding remaining %d atom(s) fixed" % nfixed
                else:
                    msg2 = "holding %d atom(s) fixed around %s" % (nfixed, them_or_it)
                info += ", " + fix_plurals(msg2 )
            info += ")"
            env.history.message( info)
            self.doMinimize(mtype = 1, simaspect = simaspect)
                # mtype = 1 means single-frame XYZ file.
                # [this also sticks results back into the part]
            #self.doMinimize(mtype = 2) # 2 = multi-frame DPB file.
        finally:
            self.win.disable_QActions_for_sim(False)
        simrun = self._movie._simrun #bruce 050415 klugetower
        if not simrun.said_we_are_done:
            env.history.message("Done.")
        return
    def doMinimize(self, mtype = 1, simaspect = None):
        #bruce 051115 renamed method from makeMinMovie
        #bruce 051115 revised docstring to fit current code #e should clean it up more
        """
        Minimize self.part (if simaspect is None -- no longer used)
        or its given simaspect (simulatable aspect) (used for both Minimize Selection and Minimize All),
        generating and showing a movie (no longer asked for) or generating and applying to part an xyz file.

        The mtype flag means:
        1 = tell writemovie() to create a single-frame XYZ file.
        2 = tell writemovie() to create a multi-frame DPB moviefile.
            [###@@@ not presently used, might not work anymore]
        """
        assert mtype == 1 #bruce 051115
        assert simaspect is not None #bruce 051115
        #bruce 050324 made this from the Part method makeMinMovie.
        suffix = self.part.movie_suffix()
        if suffix is None: #bruce 050316 temporary kluge; as of circa 050326 this is not used anymore
            msg = "%s is not yet implemented for clipboard items." % self.word_Minimize
            env.history.message( redmsg( msg))
            return
        #e use suffix below? maybe no need since it's ok if the same filename is reused for this.

        # bruce 050325 change: don't use or modify self.assy.current_movie,
        # since we're not making a movie and don't want to prevent replaying
        # the one already stored from some sim run.
        # [this is for mtype == 1 (always true now) and might affect writemovie ###@@@ #k.]

        # NOTE: the movie object is used to hold params and results from minimize,
        # even if it makes an xyz file rather than a movie file.
        # And at the moment it never makes a movie file when called from this code.
        # [bruce 051115 comment about months-old situation]

        movie = Movie(self.assy)
            # do this in writemovie? no, the other call of it needs it passed in
            # from the dialog... #k
            # note that Movie class is misnamed since it's really a
            # SimRunnerAndResultsUser... which might use .xyz or .dpb results...
            # maybe rename it SimRun? ###e also, it needs subclasses for the
            # different kinds of sim runs and their results... or maybe it needs
            # a subobject which has such subclasses -- not yet sure. [bruce 050329]

        self._movie = movie
            #bruce 050415 kluge; note that class SimRun does the same thing.
            # Probably it means that this class, SimRun, and this way of using
            # class Movie should all be the same, or at least have more links
            # than they do now. ###@@@

        # Set update_cond for controlling realtime update settings for watching
        # this "movie" (an ongoing sim). There are three possible ways
        # (soon after A8 only the first one will be used) [bruce 060705]:
        # - caller specified it.
        # - if it didn't, use new common code to get it from General Prefs page.
        # - if that fails, use older code for that.
        #
        # WARNING: it turns out this happens whether or not the checkbox pref
        # says it should -- that is checked separately elsewhere! That's a bug,
        # since we need to use a different checkbox depending on the command.
        # let's see if we can consolidate the "enabling flag" into
        # update_cond itself? so it is None or False if we won't update.
        # this is now attempted...
        if env.debug():
            print "debug fyi: runSim/sim_commandruns watch_motion update_cond computed here " \
                  "(even if not watching motion)" #bruce 060705
        try:
            # Only the client code knows where to find the correct realtime
            # update settings widgets (or someday, knows whether these values
            # come from widgets at all, vs from a script).
            # It should figure out the update_cond
            # (False if we should not watch motion),
            # and tell us in self.kws['update_cond'].
            update_cond = self.kws['update_cond']
            assert update_cond or (update_cond is False) # a callable or False [remove when works]
            # WARNING: as of 080321, this apparently fails routinely
            # for Adjust All, and then the first fallback in the
            # except clause also fails (userPrefs.watch_motion_buttongroup
            # attributeerror), and then its fallback finally works.
            # Cleanup is severely needed. [bruce 080321 comment]
        except:
            ## print_compact_traceback("bug ...: ")
            if env.debug():
                print "debug: fyi: sim_commandruns grabbing userPrefs data"
            # For A8, this is normal, since only (at most) Minimize Energy sets self.kws['update_cond'] itself.
            # This will be used routinely in A8 by Adjust All and Adjust Selection, and maybe Adjust Atoms (not sure).
            #
            # Just get the values from the "Adjust" prefs page.
            # But at least try to do that using new common code.
            try:
                from widgets.widget_controllers import realtime_update_controller
                userPrefs = env.mainwindow().userPrefs
                from utilities.prefs_constants import Adjust_watchRealtimeMinimization_prefs_key
                    ###@@@ should depend on command, or be in movie...
                ruc = realtime_update_controller(
                    ( userPrefs.watch_motion_buttongroup,
                          # Note: watch_motion_buttongroup exists in MinimizeEnergyProp.py
                          # and in SimSetup.py and now its back in Preferences.py,
                          # so this is no longer a bug (for "Adjust All"). [mark 2008-06-04]
                      userPrefs.update_number_spinbox,
                      userPrefs.update_units_combobox ),
                    None, # checkbox ###@@@ maybe not needed, since UserPrefs sets up the connection #k
                    Adjust_watchRealtimeMinimization_prefs_key )
                update_cond = ruc.get_update_cond_from_widgets()
                # note, if those widgets are connected to env.prefs, that's not handled here or in ruc;
                # I'm not sure if they are. Ideally we'd tell ruc the prefs_keys and have it handle that too,
                # perhaps making it a long-lived object (though that might not be necessary).
                assert update_cond or (update_cond is False) # a callable or False
            except:
                # even that didn't work. Complain, then fall back to otherwise-obsolete old code.
                msg = "bug using realtime_update_controller in sim_commandruns, will use older code instead: "
                print_compact_traceback(msg)
                # This code works (except for always using the widgets from the General Prefs page,
                # even for Minimize Energy), but I'll try to replace it with calls to common code.
                # [bruce 060705]
                # This code for setting update_cond is duplicated (inexactly)
                # in SimSetup.createMoviePressed() in SimSetup.py.
                userPrefs = env.mainwindow().userPrefs
                update_units = userPrefs.update_units_combobox.currentText()
                update_number = userPrefs.update_number_spinbox.value()
                if userPrefs.update_asap_rbtn.isChecked():
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
                # new as of 060705, in this old code
                if not env.prefs[Adjust_watchRealtimeMinimization_prefs_key]:
                    update_cond = False
            pass
        # now do this with update_cond, however it was computed
        movie.update_cond = update_cond

        # semi-obs comment, might still be useful [as of 050406]:
        # Minimize Selection [bruce 050330] (ought to be a distinct
        # command subclass...) this will use the spawning code in writemovie
        # but has its own way of writing the mmp file.
        # To make this clean, we need to turn writemovie into more than one
        # method of a class with more than one subclass, so we can override
        # one of them (writing mmp file) and another one (finding atom list).
        # But to get it working I might just kluge it
        # by passing it some specialized options... ###@@@ not sure

        movie._cmdname = self.cmdname
            #bruce 050415 kluge so writemovie knows proper progress bar caption to use
            # (not really wrong -- appropriate for only one of several
            # classes Movie should be split into, i.e. one for the way we're using it here,
            # to know how to run the sim, which is perhaps really self (a SimRunner),
            # once the code is fully cleaned up.
            # [review: is that the same SimRunner which is by 080321
            #  a real class in runSim?]

        # write input for sim, and run sim
        # this also sets movie.alist from simaspect
        r = writemovie(self.part,
                       movie,
                       mtype,
                       simaspect = simaspect,
                       print_sim_warnings = True,
                       cmdname = self.cmdname,
                       cmd_type = self.cmd_type,
                       useGromacs = self.useGromacs,
                       background = self.background)
        if r:
            # We had a problem writing the minimize file.
            # Simply return (error message already emitted by writemovie). ###k
            return

        if mtype == 1:  # Load single-frame XYZ file.
            if (self.useGromacs):
                if (self.background):
                    return
                tracefileProcessor = movie._simrun.tracefileProcessor
                newPositions = readGromacsCoordinates(movie.filename + "-out.gro", movie.alist, tracefileProcessor)
            else:
                newPositions = readxyz( movie.filename, movie.alist )
                    # movie.alist is now created in writemovie [bruce 050325]
            # retval is either a list of atom posns or an error message string.
            assert type(newPositions) in [type([]),type("")]
            if type(newPositions) == type([]):
                #bruce 060102 note: following code is approximately duplicated somewhere else in this file.
                movie.moveAtoms(newPositions)
                # bruce 050311 hand-merged mark's 1-line bugfix in assembly.py (rev 1.135):
                self.part.changed() # Mark - bugfix 386
                self.part.gl_update()
            else:
                #bruce 050404: print error message to history
                env.history.message(redmsg( newPositions))
        else: # Play multi-frame DPB movie file.
            ###@@@ bruce 050324 comment: can this still happen? [no] is it correct [probably not]
            # (what about changing mode to movieMode, does it ever do that?) [don't know]
            # I have not reviewed this and it's obviously not cleaned up (since it modifies private movie attrs).
            # But I will have this change the current movie, which would be correct in theory, i think, and might be needed
            # before trying to play it (or might be a side effect of playing it, this is not reviewed either).
            ###e bruce 050428 comment: if self.assy.current_movie exists, should do something like close or destroy it... need to review
            self.assy.current_movie = movie
            # If cueMovie() returns a non-zero value, something went wrong loading the movie.
            if movie.cueMovie():
                return
            movie._play()
            movie._close()
        return
    pass # end of class Minimize_CommandRun

# ==

class CheckAtomTypes_CommandRun(CommandRun):
    def run(self):
        if not self.part.molecules:
            return
        for chunk in self.part.molecules:
            if (chunk.atoms):
                for atom in chunk.atoms.itervalues():
                    atom.setOverlayText("?")
                chunk.showOverlayText = True

        selection = self.part.selection_for_all()
        simaspect = sim_aspect( self.part,
                                selection.atomslist(),
                                cmdname_for_messages = "CheckAtomTypes",
                                anchor_all_nonmoving_atoms = False
                                )

        movie = Movie(self.assy)
        #self._movie = movie

        writemovie(self.part,
                   movie,
                   1,
                   simaspect = simaspect,
                   print_sim_warnings = True,
                   cmdname = "Simulator",
                   cmd_type = "Check AtomTypes",
                   useGromacs = False,
                   background = False,
                   useAMBER = True,
                   typeFeedback = True)

        self.part.gl_update()

def LocalMinimize_function( atomlist, nlayers ): #bruce 051207
    win = atomlist[0].molecule.part.assy.w # kluge!
    #e should probably add in monovalent real atom neighbors -- but before finding neighbors layers, or after?
    # (note that local min will always include singlets... we're just telling it to also treat attached H the same way.
    #  that would suggest doing it after, as an option to Minimize. Hmm, should even Min Sel do it? Discuss.)
    cmdrun = Minimize_CommandRun( win, 'Atoms', atomlist, nlayers, type = 'Adjust Atoms')
    cmdrun.run()
    return

# == helper code for Minimize Selection [by bruce, circa 050406] [also used for Minimize All, probably as of 050419, as guessed 051115]

def adjustSinglet(singlet, minimize = False): # Mark 2007-10-21.
    """
    Adjusts I{singlet} using one of two methods based on I{minimize}:

    1. Hydrogenate the singlet, then transmute it back to a singlet
    (default). Singlet positions are much better after this, but
    they are not in their optimal location.

    2. Hydrogenate the singlet, then call the simulator via the
    L{LocalMinimize_Function} to adjust (minimize) the hydrogen atom, then
    tranmute the hydrogen back to a singlet. Singlet positions are best
    after using this method, but it has one major drawback -- it
    redraws while minimizing. This is a minor problem when breaking
    strands, but is intolerable in the DNA duplex generator (which adjusts
    open bond singlets in its postProcess method.

    @param singlet: A singlet.
    @type  singlet: L{Atom}

    @param minimize: If True, use the minimizer to adjust the singlet
                     (i.e. method #2).
    @type  minimize: bool

    @note: Real atoms are not adjusted.

    @see: L{Hydrogenate} for details about how we are using it to
          reposition singlets (via method 1 mentioned above).
    """
    if not singlet.is_singlet():
        return

    singlet.Hydrogenate()
    if minimize:
        msg = "ATTENTION: Using minimizer to adjust open bond singlets."
        env.history.message( orangemsg(msg) )
        # Singlet is repositioned properly using minimize.
        # The problem is that this redraws while running. Don't want that!
        # Talk to Bruce and Eric M. about it. Mark 2007-10-21.
        LocalMinimize_function( [singlet], nlayers = 0 )
    # Transmute() will not transmute singlets. Since <singlet> is a Hydrogen,
    # and not a singlet, this will work. -mark 2007-10-31 (Boo!)
    from model.elements import Singlet
    singlet.Transmute(Singlet)
    return

# end

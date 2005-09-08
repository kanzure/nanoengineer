# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
movie.py -- the Movie class.

This file mainly defines class Movie

$Id$

History:

Initially by Mark.

Some parts rewritten by Bruce circa 050427.
"""

__author__ = "Mark"

import os, sys
from struct import unpack
from qt import Qt, qApp, QApplication, QCursor, SIGNAL
from HistoryWidget import redmsg, orangemsg, greenmsg
from VQT import A
import platform
from debug import print_compact_stack, print_compact_traceback
from moviefile import MovieFile #e might be renamed, creation API revised, etc
## can't do this here (recursive import), so done at runtime:
## from movieMode import _controls 

ADD = True
SUBTRACT = False
FWD = 1
REV = -1
DEBUG0 = 0
DEBUG1 = 0 # DO NOT COMMIT WITH 1
DEBUG_DUMP = 0 # DO NOT COMMIT WITH 1

playDirection = { FWD : "Forward", REV : "Reverse" }

class Movie:
    """
    Movie object.

    Multiple purposes (which ought to be split into separate objects more than they have been so far):
    - Holds state of one playable or playing movie,
      and provides methods for playing it,
      and has moviefile name and metainfo;
    - also (before its moviefile is made) holds parameters needed
      for setting up a new simulator run
      (even for Minimize, though it might never make a moviefile);
    - those parameters might be used as defaults (by external code) for setting up another sim run.

    Warnings:
    - methods related to playing are intimately tied to movieMode.py's dashboard widget;
    - so far, only supports playing one movie at a time;
    - so far, provisions/checks for changing Parts during movie playing are limited.

    Movie lifecycle [bruce 050427 intention -- some details are obs or need review #####@@@@@]:
    
    - If we make the movie in this session (or someday, if we read a movie node from an mmp file),
    we give it an alist, and we should never change that alist after that,
    but we'll need to check it sometimes, in case of atoms changing Parts or being killed.

      If we make the movie as a way of playing the trajectory in an existing file, then when we do that
    (or when needed) we come up with an alist, and likewise never change the alist after that.

      (In the future, if there's a "play on selection" option, this only affects which atoms move when
    we play the movie -- it doesn't alter the alist, which is needed in its original form
    for interpreting frames in the moviefile.)

      Maybe the Movie is not meant to be ever played (e.g. it's just for holding sim params, perhaps for Minimize),
    but if it is, then external code optionally queries might_be_playable() to decide whether to try
    playing it (e.g. when entering Movie Mode), calls _setup before actually starting to play it
    (this verifies it has a valid alist (or that one can be constructed) which is playable now,
     attaches it to movieMode dashboard, freezes its atoms for efficient playing, and perhaps changes
     current Part so the playing movie will be visible),
    then calls other methods to control the playing,
    then calls _close when the playing is done
    (which unfreezes atoms and disables some movieMode dashboard controls).

      But even between _close and the next _setup, the alist is maintained -- switching Parts is not enough
    to try reloading the movie for playing on different atoms. If changing it to play on different atoms is
    ever needed, we'll add specific support for that. Not only is alist maintained, so is valuable info
    about the moviefile, like cached frames. The file might be closed (to save on open files for when we
    have multiple loaded movies, and to help us detect whether the file gets overwritten with new data);
    if closed, it's reopened on the next _setup, and it's always rechecked on _setup for being overwritten. #####@@@@@ doit or testit

      State variables involved in all this (incomplete list, there's also currentFrame and a few others in the playing-state):

    - isOpen tells whether we're between _setup and _close. (It has no guaranteed relation
    to whether any file object is open, though in practice it might coincide with that for the moviefile.)
    
    - alist is None or a valid list of atoms (this might be replaced by an object for holding that list)

    - the first time _setup is called, the movie file header is parsed, and an alist
    is assigned if possible and not already known, and an "alist_and_moviefile" object to hold both of them
    and keep them in correspondence is created, and if this works the file is never again fully reparsed,
    though it might be rechecked later to ensure it hasn't been overwritten.
    #####@@@@@ is it ok to do this for each existing call of _setup?

    - might_be_playable() returns True if this object *might* be playable, provided _setup has not yet been called
    and succeeded (i.e. if we don't yet have an alist_and_moviefile object); but after _setup has once succeeded,
    it returns True iff the alist is currently ok to try to play from the file (according to our alist_and_moviefile).
    (This might always be True, depending on our policy for atoms moved to other parts or killed, but it might
    trigger history warnings in some cases -- not yet decided #####@@@@@).
    It won't actually recheck the file (to detect overwrites) until _setup is called.
    (The goal is for might_be_playable to be fast enough to use in e.g. updating a node-icon in the MT, in the future.)
    """
    #bruce 050324 comment: note that this class is misnamed --
    # it's really a SimRunnerAndResultsUser... which might
    # make and then use .xyz or .dpb results; if .dpb, it's able
    # to play the movie; if .xyz, it just makes it and uses it once
    # and presently doesn't even do it in methods, but in external
    # code (nonetheless it's used). Probably should split it into subclasses
    # and have one for .xyz and one for .dpb, and put that ext code
    # into one of them as methods. ###@@@
    #bruce 050329 comment: this file is mostly about the movie-playable DPB file;
    # probably it should turn into a subclass of SimRun, so the objects for other
    # kinds of sim runs (eg minimize) can be different. The superclass would
    # have most of the "writemovie" function (write sim input and run sim)
    # as a method, with subclasses customizing it.
    
    ignore_slider_and_spinbox = False # (in case needed before init done)
    def __init__(self, assembly, name=None):
        """###doc; note that this Movie might be made to hold params for a sim run,
        and then be told its filename, or to read a previously saved file;
        pre-050326 code always stored filename from outside and didn't tell this object
        how it was becoming valid, etc...
        """
        self.assy = assembly
        self.win = self.assy.w
        self.glpane = self.assy.o ##e if in future there's more than one glpane, recompute this whenever starting to play the movie
        
        ## self.history = self.assy.w.history ###@@@ might not work, might need getattr, until we remake Movies as needed
        # for future use: name of the movie that appears in the modelTree. 
        self.name = name or "" # assumed to be a string by some code
        # the name of the movie file
        self.filename = "" #bruce 050326 comment: so far this is only set by external code; i'll change that someday
##        # movie "file object"
##        self.fileobj = None
        # the total number of frames actually in our moviefile [might differ from number requested]
        self.totalFramesActual = 0
            # bruce 050324 split uses of self.totalFrames into totalFramesActual and totalFramesRequested
            # to help fix some bugs, especially when these numbers differ
        # the most recent frame number of this movie that was played
        self.currentFrame = 0
        # the starting (current) frame number when we last entered MOVIE mode   ###k
        self.startFrame = 0
        # a flag that indicates whether this Movie has been _setup since the last _close
        # [*not* whether moviefile is open or closed, like it indicated before bruce 050427]
        self.isOpen = False
        # a flag that indicates the current direction the movie is playing
        self.playDirection = FWD
        ##bruce 050427: removing isValid since not used; should be renamed to avoid confusion with QColor.isValid
##        # for future use: a flag that indicates if the movie and the part are synchronized
##        self.isValid = False
        # the number of atoms in each frame of the movie.
        self.natoms = 0
        # show each frame when _playToFrame is called
        self.showEachFrame = False
        # a flag that indicates the movie is paused
        self.isPaused = True
        # moveToEnd: a flag that indicates the movie is currently fast-forwarding to the end.
        # [bruce 050428 comment: in present code, self.moveToEnd might not be properly maintained
        #  (it's never set back to False except by _pause; I don't know if _pause is
        #   always called, but if it needs to be, this is not documented),
        #   and it's also not used. I suggest replacing it with a logical combination
        #   of other flags, if it's ever needed.]
        self.moveToEnd = False
        # a flag that indicates if the wait (hourglass) cursor is displayed.
        self.waitCursor = False
        # simulator parameters to be used when creating this movie,
        # or that were used when it was created;
        # these should be stored in the dpb file header so they
        # can be retrieved later. These will be the default values used by
        # the simsetup dialog, or were the values entered by the user.
        self.totalFramesRequested = 900
            # bruce 050325 added totalFramesRequested, changed some uses of totalFrames to this
        self.temp = 300
        self.stepsper = 10
        self.timestep = 10
            # Note [bruce 050325]: varying the timestep is not yet supported,
            # and this attribute is not presently used in the cad code.
        # bruce 050324 added these:
        self.alist = None # list of atoms for which this movie was made, if this has yet been defined
        self.alist_and_moviefile = None #bruce 050427: hold checked correspondence between alist and moviefile, if we have one
        self.debug_dump("end of init")
        return

    ##bruce 050428 removing 1-hour-old why_not_playable feature,
    ## since ill-conceived, incomplete, and what's there doesn't work (for unknown reasons).
##    why_not_playable = ""
##        # reason why we're not playable (when we're not), if known (always a string; a phrase; never used if truly playable)
    def might_be_playable(self): #bruce 050427
        """Is it reasonable to try to play this movie?
        This does NOT check whether it's still valid for its atoms or the current part;
        if the caller then tries to play it, we'll check that and complain.
        BUT if it has been previously checked and found invalid, this should return False or perhaps redo the check.
        For more info see docstring of class Movie.
        """
        if self.file_trashed:
            #bruce 050428: some new sim in this process has trashed our file (even if it didn't complete properly)
            # (btw, this doesn't yet help if it was some other process which did the trashing)
            #e (it would be nicer if new sims would store into a temp file until they completed successfully;
            #   even then they need to set this (via method below)
            #   and they might want to ask before doing that, or use a new filename)
            return False #e history message??
        filename_ok = self.filename and self.filename.endswith('.dpb') and os.path.exists(self.filename)
        if not self.alist_and_moviefile:
##            if not filename_ok and not self.why_not_playable:
##                self.why_not_playable = "need filename of existing .dpb file" # can this ever be seen??
            return filename_ok # ok to try playing it, though we don't yet know for sure whether this will work.
        else:
            res = self.alist_and_moviefile.might_be_playable()
##            self.why_not_playable = self.alist_and_moviefile.why_not_playable
##                #e (is this a sign the whynot should be part of the retval?)
            return res

    file_trashed = False
    def fyi_reusing_your_moviefile( self, moviefile):
        """If moviefile happens to be the name of our own moviefile,
        know that it's being trashed and we'll never again be playable
        (unless we have not yet read any data from it,
         in which case we're no worse off than before, I suppose).
        """
        if self.filename and self.filename == moviefile and self.alist_and_moviefile:
            self.warning( "overwriting moviefile (previously open movie will no longer be playable)." )
                # note, this wording is from point of view of caller -- *we* are the previously open movie.
                # I'm assuming it's overwritten, not only removed, since no reason to remove it except to overwrite it.
            self.file_trashed = True
##            self.why_not_playable = "moviefile overwritten by a more recent simulation" #e or get more detail from an arg?
        return
    
    def __getattr__(self, attr):
        if attr == 'history':
            return self.assy.w.history
##        if attr == 'part':
##            if self.alist:
##                part = self.alist[0].molecule.part
##                    # not checked for consistency, but correct if anything is; could be None, I think,
##                    # especially for killed atoms (guess; see bug 497) [bruce 050411]
##                if part is None and platform.atom_debug:
##                    print_compact_stack( "part false (%r) here; alist[0].molecule is %r: " % (part, self.alist[0].molecule) )
##                return part
##             #bruce 050411: the following does happen, see comments in bug 497;
##            # so until that's fixed, don't do an assertion.
##            ## assert 0, "part needed before alist"
##                ### can this happen? if it does, return cur part??? main part??? depends on why...
##            if platform.atom_debug:
##                self.debug_print_movie_info("bug: part needed before alist")
##            return None # hope this is ok, but it's probably not! ####@@@@
        raise AttributeError, attr

    def destroy(self): #bruce 050325
        # so far this is only meant to be called before the file has been made
        # (eg it doesn't destroy our big fancy subobjects);
        # it should be revised to work either way and _close if necessary.
        # for now, just break cycles.
        self.win = self.assy = self.part = self.alist = self.history = self.fileobj = None
        del self.fileobj # obs attrname
        del self.part

    # == methods for letting this object (just after __init__) represent a previously saved movie file

    def represent_this_moviefile( self, mfile, part = None): #bruce 050326
        """Try to start representing the given moviefile (which must end with '.dpb');
        return true iff this succeeds; if it fails DON'T emit error message.
        if part is supplied, also [NIM] make sure mfile is valid for current state of that part.
        """
        #e should the checking be done in the caller (a helper function)?
        assert mfile.endswith(".dpb") # for now
        if os.path.exists(mfile):
            self.filename = mfile
            ###e do more... but what is needed? set alist? only if we need to play it, and we might not... (PlotTool doesn't)
            assert not part # this is nim; should call the validity checker
            return True
        else:
            pass #e self.history.message(redmsg(...)) -- is this a good idea? I think caller wants to do this... ###k
            self.destroy()
            return False
        pass

    # == methods for letting this object represent a movie (or xyz) file we're about to make, or just did make
    
    def set_alist(self, alist): #bruce 050325
        """Verify this list of atoms is legal (as an alist to make a movie from),
        and set it as this movie's alist. This only makes sense before making a moviefile,
        or after reading one we didn't make in the same session (or whose alist we lost)
        and figuring out somehow what existing atoms it should apply to.
        But nothing is checked about whether this alist fits the movie file,
        if we have one, and/or the other params we have --
        that's assumed done by the caller.
        """
        alist = list(alist) # make our own copy (in case caller modifies its copy), and ensure type is list
        atm0 = alist[0]
        assert atm0.molecule.part
        for atm in alist:
            assert atm.molecule.part == atm0.molecule.part
        # all atoms have the same Part, which is not None, and there's at least one atom.
        self.alist = alist
        self.natoms = len(alist) #bruce 050404; note, some old code might reset this (perhaps wrongly?) when reading a .dpb file
        return

    def set_alist_from_entire_part(self, part):
        """Set self.alist to a list of all atoms of the given Part,
        in the order in which they would be written to a new mmp file.
        """
        # force recompute of part.alist, since it's not yet invalidated when it needs to be
        part.alist = None
        del part.alist
        ## self.alist = part.alist
        alist = part.alist # this recomputes it
        self.set_alist(alist) #e could optimize (bypass checks in that method)
        return
        
##        ##(In the future we might change that to the order in which they
##        ## were last written to an actual file, if they ever were,
##        ## and if the set of atoms has not changed since then. ###e)
##        ##The right soln is to save alist when we load or save part,
##        ##then when we get this new one, check if atoms in it are same,
##        ##and if so use the saved one instead. [not always legal re jigs, see below]
##        # Check by sorting list of keys.
##        ##Or could we acually use that order in alist? only if we use it to write atoms to sim...
##        ##maybe we can, we'll see. In fact, I'm sure we can, since sim does not care
##        # about chunks, groups, atom order... oh, one exception -- it requires
##        # some jigs to be on contiguous sets of atoms.
##        # even so we could come close... or we might just let those jigs be on too many atoms. ###e
##        res = []
##        for mol in part.molecules: #e check >= 1? with atoms? ###WRONG, order of mols is arb.
##            lis = mol.atoms_in_mmp_file_order(): ###k
##                ###e worry about singlets re bug 254
##                ###e or let new code in minimize selection handle this
##            res.extend(lis)
##        ###e split into a part method to get alist, and our own set_alist method
##        self.set_alist(res) #e could optimize (bypass checks in that method)
##        return None
        
    # == methods for playing the movie file we know about (ie the movie we represent)
    
    # [bruce 050427 comments/warnings:
    #  These methods need to be refactored, since they intimately know about movieMode's dashboard (they update it).
    #  They also use and maintain state-of-playing variables in self (which might be useful for any manner of playing the movie).
    #  One of the methods does recursive processing of QEvents and doesn't return until the movie is paused (I think).
    # ]

    def _setup_check(self): #bruce 050427
        """Is our movie file so playable that it's ok to start actually playing it?
        If not, emit complaints on history widget, don't set our state variables; return False.
        If so, return True.
        """
        # remember what to unset if things don't work when we return
        we_set_alist = False
        we_set_alist_and_moviefile = False
        if not self.might_be_playable():
            self.history.message( redmsg( "Movie is not playable.")) # can't happen, I think... if it can, it should give more info.
            return False
        if not self.alist_and_moviefile:
            # we haven't yet set up this correspondence. Do it now. Note that the filename needs to be set up here,
            # but the alist might or might not have been (and if it was, it might not be all the atoms in the current Part).
            if self.alist is None:
                # alist should equal current Part; then verify moviefile works for that.
                #e In future, we might also permit alist to come from selection now,
                # if this has right natoms for moviefile and whole part doesn't.
                # *Or* we might let it come from main part if we're in some other part which doesn't fit.
                # For now, nothing so fancy. [bruce 050427]
                self.set_alist_from_entire_part( self.assy.part)
                we_set_alist = True
            if self.currentFrame != 0:
                # shouldn't ever happen, I think, since this movie was not played yet since self created;
                # so if it does, tell me, since it might be a bug; maybe useful to say anyway [bruce 050427]
                self.history.message( greenmsg( "(Starting movie from frame %d.)" % self.currentFrame ))
                # [note: self.currentFrame is maintained independently of a similar variable
                #  inside a lower-level moviefile-related object.]
            self.alist_and_moviefile = alist_and_moviefile( self.assy, self.alist, self.filename, curframe_in_alist = self.currentFrame)
                # if this detected an error in the file matching the alist, it stored this fact but didn't report it yet or fail #####@@@@@ doit
                # maybe it won't even check yet, until asked...
            we_set_alist_and_moviefile = True
            ok = self.alist_and_moviefile.valid()
        else:
            # we have an alist_and_moviefile but we need to recheck whether the alist still matches the file
            # (in case the file changed on disk).
            ok = self.alist_and_moviefile.recheck_valid() # in theory this might come up with a new larger totalFramesActual value (NIM)
        if not ok:
            # it emitted error messages already #####@@@@@ doit
            # reset what we set, in case user will try again later with altered file or different assy.part
            if we_set_alist_and_moviefile:
                self.alist_and_moviefile.destroy()
                self.alist_and_moviefile = None
            if we_set_alist:
                self.alist = None
            return False
        # change current part and/or arrange to warn if user does that? No, this is done later when we _play.
        return True

    def _controls(self, On = True): #bruce 050427 moved body of this into helper func in moviefile
        from movieMode import _controls
        _controls(self.assy.w, On)
        #e perhaps this belongs in our movieMode client code instead;
        # or perhaps we should not control dashboard directly from this object at all,
        # but rather have observers we can update
    
    def _setup(self, hflag = True):
        """Setup this movie for playing
        """
        # bruce 050427 comment:
        # what it did before today:
        # - figure out part to use for movie file (this is wrong and needs changing).
        # - check movie file for validity re that part (on error, print message and return nonzero error code)
        # - freeze atoms (making some other operations on them illegal, I think, in the present code)
        # - possibly save frame 0 positions -- only if self.currentFrame is 0
        # - open movie file, read header
        # - update dashboard frame number info (SB, SL, label)
        # - history info: if hflag: self._info()
        # - self.startFrame = self.currentFrame
        if DEBUG1: print "movie._setup() called. filename = [" + self.filename + "]"

        if self.isOpen and platform.atom_debug:
            self.history.message( redmsg( "atom_debug: redundant _setup? bug if it means atoms are still frozen"))

        kluge_ensure_natoms_correct( self.assy.part) # matters for some warn_if_other_part messages, probably not for anything else
        
        ok = self._setup_check()
        if not ok:
            # bruce 050427 doing the following disable under more circumstances than before
            # (since old code's errcode 'r' 1 or 2 no longer distinguished here) -- ok?
            self._controls(0) # Disable movie control buttons.
            self.isOpen = False #bruce 050427 added this
            return 1020102 # was sometimes 1 and sometimes 2... callers only care whether nonzero.
            
        self._controls(1) # Enable movie control buttons.

        #bruce 050427 extensively rewrote the following (and moved some of what was here into OldFormatMovieFile_startup)

        self.alist_and_moviefile.own_atoms() # older related terms: self.movsetup(), freeze the atoms
        self.isOpen = True

        self.totalFramesActual = self.alist_and_moviefile.get_totalFramesActual() # needed for dashboard controls
        self.natoms = len(self.alist) # needed for _info

        self.update_dashboard_frame_controls() #bruce 050427 split this out

        if hflag:
            self._info() # prints info to history
        
        # startframe and currentframe are compared in _close to determine if the assy has changed due to playing this movie. ###k
        self.startFrame = self.currentFrame
        
        return 0
        
        # Debugging Code [to enable, remove prior 'return' statement]
        if DEBUG1:
            msg = "Movie Ready: Number of Frames: " + str(self.totalFramesActual) + \
                    ", Current Frame:" +  str(self.currentFrame) +\
                    ", Number of Atoms:" + str(self.natoms)
            self.history.message(msg)

            ## filepos = self.fileobj.tell() # Current file position
            msg = "Current frame:" + str(self.currentFrame) ## + ", filepos =" + str(filepos)
            self.history.message(msg)
        
    def update_dashboard_currentFrame(self):
        "update dashboard controls which show self.currentFrame, except for the ones being used to change it"
        #bruce 050428 split this out too, added all conditions/flags; ##e it should become a method of movieDashboardSlotsMixin
        old = self.win._movieDashboard_ignore_slider_and_spinbox # not sure if this is ever True here
        self.win._movieDashboard_ignore_slider_and_spinbox = True
        try:
            dont_update_slider = self.win._movieDashboard_in_valuechanged_SL
            dont_update_spinbox = self.win._movieDashboard_in_valuechanged_SB
            if not dont_update_slider:
                self.win.frameNumberSL.setValue(self.currentFrame) # SL = Slider
            if not dont_update_spinbox:
                self.win.frameNumberSB.setValue(self.currentFrame) # Spinbox
        finally:
            self.win._movieDashboard_ignore_slider_and_spinbox = old
        return
    
    def update_dashboard_frame_controls(self): #bruce 050427 split this out of _setup; ##e it should become a method of movieDashboardSlotsMixin
        "update dashboard controls which show self.currentFrame or self.totalFramesActual"
        self.win.frameNumberSL.setMaxValue(self.totalFramesActual)      

#        self.win.movieProgressBar.setTotalSteps(self.totalFramesActual) # Progress bar
#        self.win.movieProgressBar.setProgress(self.currentFrame)

        self.win.frameNumberSB.setMaxValue(self.totalFramesActual)

        self.update_dashboard_currentFrame()

        flabel = "Frame (" + str(self.totalFramesActual) + " total):"
        self.win.frameLabel.setText(flabel) # Spinbox label
        return

    # ==

    def warn_if_other_part(self, part): #bruce 050427; to call when play is pressed, more or less...
        "warn the user if playing this movie won't move any (or all) atoms in the given part (or about other weird conditions too)."
        if self.alist is None:
            return
        # like .touches_part() in a subobject, but can be called sooner...
        yes = 0 # counts the ones we'll move
        other = killed = False
        for atm in self.alist:
            if atm.molecule.part == part:
                yes += 1
            elif atm.molecule.part:
                other = True
            else:
                killed = True
        if not (yes or other):
            if not killed:
                # should never happen, I think
                self.warning( "this movie has no atoms. Playing it anyway (no visible effect).")
            else:
                self.warning( "all of this movie's atoms have been deleted. Playing it anyway (no visible effect).")
        else:
            if not yes:
                self.warning( "to see this movie playing, you must display a different Part.") #e which one, or ones?
            elif other or killed:
                if killed:
                    self.warning( "some of this movie's atoms have been deleted. (Playing it still moves the remaining atoms.)")
                if other:
                    self.warning( "some of this movie's atoms have been moved to another Part (maybe one on the clipboard). " \
                                  "Playing it moves its atoms in whichever Parts they reside in." )
                if yes < part.natoms:
                    # (this assumes part.natoms has been properly updated by the caller; _setup does this.)
                    self.warning( "some displayed atoms are not in this movie, and stay fixed while it plays.")
        return

    def warning(self, text):
        self.history.message( orangemsg( "Warning: " + text))
        
    def _close(self):
        """Close movie file and adjust atom positions.
        """
        #bruce 050427 comment: what this did in old code:
        # - if already closed, noop.
        # - pause (sets internal play-state variables, updates dashboard ###k)
        # - close file.
        # - unfreeze atoms.
        # - if frame moved while movie open this time, self.assy.changed()
        # - wanted to delete saved frame 0 but doesn't (due to crash during devel)
        if DEBUG1: print_compact_stack( "movie._close() called. self.isOpen = %r" % self.isOpen)
        if not self.isOpen: return
        self._pause(0) 
        ## self.fileobj.close() # Close the movie file.
        self.alist_and_moviefile.release_atoms() #bruce 050427
        self.alist_and_moviefile.close_file() #bruce 050427
        self.isOpen = False #bruce 050425 guess: see if this fixes some bugs
        if DEBUG1: print "self.isOpen = False #bruce 050425 guess: see if this fixes some bugs" ###@@@
        ## self.movend() # Unfreeze atoms.
        if self.startFrame != self.currentFrame:
            self.assy.changed()
                #bruce 050427 comment: this only helps if nothing else in playing a movie does this...
                # I'm not sure if that's still true (or if it was in the older code, either).
        return
        
    def _play(self, direction = FWD):
        """Start playing movie from the current frame.
        """
        #bruce 050427 comment: not changing this much
        
        if DEBUG0: print "movie._play() called.  Direction = ", playDirection[ direction ]

        if not self.isOpen: #bruce 050428 not sure if this is the best condition to use here ###@@@
            if (not self.might_be_playable()) and 0: ## self.why_not_playable:
                msg = "Movie file is not presently playable: %s." ## % (self.why_not_playable,)
            else:
                msg = "Movie file is not presently playable." ###e needs more detail, especially when error happened long before.
            self.history.message( redmsg( msg )) #bruce 050425 mitigates bug 519 [since then, it got fixed -- bruce 050428]
            return
        
        if direction == FWD and self.currentFrame == self.totalFramesActual: return
        if direction == REV and self.currentFrame == 0: return
        
        self.playDirection = direction
        
        if self.currentFrame == 0: 
            self.history.message("Playing movie file [" + self.filename + "]")
            self._continue(0)
        else:
            self._continue()

    # josh 050815.
    # Changed name from _writeas to _write_povray_series.  mark 050908.
    # I plan to write a special Movie Maker dialog that would call this with arguments.
    # Mark 050908
    def _write_povray_series(self, name):
        """Writes the movie out as a series of POV-Ray files, starting with the current frame
        until the last frame, skipping frames using the "Skip" value from the dashboard.
        
        If your trajectory file was foobar.dpb, this will write, e.g., foobar.000000.pov thru 
        foobar.000999.pov (assuming your movie has 1000 frames).
        If you have bash, you may then run:
            for FN in foobar.000*.pov; { povray +W800 +H600 +A -D $FN; } &> /dev/null &
        to generate the .png files. 
        This is not to be done under nE1 because it typically takes several hours
        and will be best done on a renderfarm with commands appropriate to the renderfarm.
        you may then make a move of it with:
            mencoder "mf://*.png" -mf fps=25 -o output.avi -ovc lavc -lavcopts vcodec=mpeg4
        """
        from fileIO import writepovfile
        
        if not self.isOpen: #bruce 050428 not sure if this is the best condition to use here ###@@@
            if (not self.might_be_playable()) and 0: ## self.why_not_playable:
                msg = "Movie file is not presently playable: %s." ## % (self.why_not_playable,)
            else:
                msg = "Movie file is not presently playable." ###e needs more detail, especially when error happened long before.
            self.history.message( redmsg( msg )) #bruce 050425 mitigates bug 519 [since then, it got fixed -- bruce 050428]
            return

        self.playDirection = 1

        # Writes the POV-Ray series starting at the current frame until the last frame, 
        # skipping frames if "Skip" (on the dashboard) is != 0.  Mark 050908
        nfiles = 0
        for i in range(self.currentFrame, self.totalFramesActual+1, self.win.skipSB.value()+1):
            self.alist_and_moviefile.play_frame(i)
            filename = "%s.%06d.pov" % (name,i)
            self.history.message( "Writing file: " + filename )
            writepovfile(self.assy, filename)
            nfiles += 1
        
        msg = platform.fix_plurals("%d file(s) written. Done." % nfiles)
        self.history.message( greenmsg( msg))
             
        
    def _continue(self, hflag = True): # [bruce 050427 comment: only called from self._play]
        """Continue playing movie from current position.
        hflag - if True, print history message
        """
        if DEBUG0: print "movie._continue() called. Direction = ", playDirection[ self.playDirection ]
        
        # In case the movie is already playing (usually the other direction).
        self._pause(0) 
        
        if hflag: self.history.message("Movie continued: " + playDirection[ self.playDirection ])

        self.warn_if_other_part(self.assy.part) #bruce 050427
        
        self.showEachFrame = True #bruce 050428 comment: this is the only set of this var to True.

        # Continue playing movie.
        if self.playDirection == FWD: self._playToFrame(self.totalFramesActual)
        else: self._playToFrame(0)

    def _pause(self, hflag = True):
        """Pause movie.
        hflag - if True, print history message
        """
        #bruce 050428 comment: I suspect it's required to call this in almost every event,
        # since it's the only place certain state variables gets reinitialized to default
        # values (e.g. showEachFrame to False). This should be analyzed and documented.
        if DEBUG0: print "movie._pause() called"
        self.debug_dump("_pause called, not done")
        # bruce 050427 comment: no isOpen check, hope that's ok (this has several calls)
        self.isPaused = True
        self.showEachFrame = False
        self.moveToEnd = False
        self.win.moviePlayActiveAction.setVisible(0)
        self.win.moviePlayAction.setVisible(1)
        self.win.moviePlayRevActiveAction.setVisible(0)
        self.win.moviePlayRevAction.setVisible(1)
#        self.update_dashboard_currentFrame()
        if hflag: self.history.message("Movie paused.")
        self.debug_dump("_pause call done")

    def debug_dump(self, heading = "debug_dump", **kws):
        if not DEBUG_DUMP: return # disable when not needed -- but it's useful and nicelooking output, so keep it around as an example
        if heading:
            print "\n  %s:" % heading
        print "    isPaused = %r, showEachFrame = %r, moveToEnd = %r, totalFramesActual = %r, currentFrame = %r, playDirection = %r" \
           % (self.isPaused, self.showEachFrame, self.moveToEnd, self.totalFramesActual, self.currentFrame, self.playDirection )
        if kws:
            print "  other args: %r" % kws
        print_compact_stack("    stack at that time: ", skip_innermost_n = 3) # skips this lineno and 2 internal ones (#e should revise meaning to -2)

    def _playToFrame(self, fnum, from_slider = False):
        #bruce 050428 renamed this from _playFrame, since it plays all frames from current to fnum.
        """Main method for movie playing.
        When called due to the user sliding the movie dashboard frame-number slider, from_slider should be True.
        If "self.showEachFrame = True", it will play each frame of the movie between "fnum" and "currentFrame"
        (except for skipped frames due to the skip control on the dashboard).
        If "self.showEachFrame = False", it will advance to "fnum" from "currentFrame".
        fnum - frame number to play to in the movie.
        """
        #bruce 050427 revised docstring, added from_slider arg, merged most of _playSlider into this method.
        # I faithfully added conditions on from_slider to imitate the old code, though some of them might not
        # be needed or might even be bugs (if so, then presumably the non-from_slider cases are more correct).
        # If the differences are correct, it's probably better to separate the methods again;
        # the reason I merged them for now is to facilitate comparison so I (or Mark) can eventually review
        # whether the diffs are correct.

        if DEBUG0: print "movie._playToFrame() called: from fnum = ", fnum, ", to currentFrame =", self.currentFrame

        #bruce 050427 comment: added an isOpen check, in case of bugs in callers (this has lots of calls)
        if not self.isOpen:
            return
        
        if not from_slider: #bruce 050427 comment: I'm suspicious of this condition.
            self.isPaused = False
            self.debug_dump()
        
        # Return immediately if already at desired frame.
        if fnum == self.currentFrame:
            if not from_slider: #bruce 050427 comment: I'm suspicious of this condition.
                self.isPaused = True # May not be needed.  Doing it anyway.
                self.debug_dump("fnum == self.currentFrame so paused", fnum = fnum)
            return
           
        # Don't let movie run out of bounds.
        if fnum < 0 or fnum > self.totalFramesActual:
            print "Warning: Slider or other fnum out of bounds.  fnum value =",fnum,", Number of frames =", self.totalFramesActual
            self.isPaused = True # May not be needed.  Doing it anyway.
            self.debug_dump("fnum out of range so paused", fnum = fnum)
            return

        # Reset movie to beginning (frame 0).  Executed when user types 0 in spinbox.
        #bruce 050427 comment: this might no longer be needed (it might be handled at a lower level). We'll see. ###@@@
        if not self.showEachFrame and fnum == 0 and not from_slider: 
            self._reset()
            return

        # "inc" is the frame increment (FWD = 1, REV = -1) .
        if fnum > self.currentFrame: 
            inc = FWD
            if not from_slider:
                self.win.moviePlayActiveAction.setVisible(1)
                self.win.moviePlayAction.setVisible(0)
        else: 
            inc = REV
            if not from_slider:
                self.win.moviePlayRevActiveAction.setVisible(1)
                self.win.moviePlayRevAction.setVisible(0)

        # This addresses the situation when the movie file is large (> 1000 frames)
        # and the user drags the slider quickly, creating a large delta between
        # fnum and currentFrame.  Issue: playing this long of a range of the movie 
        # may take some time.  We need to give feedback to the user as to what is happening:
        # 1). turn the cursor into WaitCursor (hourglass).
        # 2). print a history message letting the user know we are advancing the movie, but
        #       also let them know they can pause the movie at any time.
        #bruce 050427 comments:
        # - The above comment dates from the old code when this method didn't handle the slider,
        #   so my guess is, its reference to the slider is even older and is out of date.
        # - I'm now merging in _playSlider and adding "if from_slider" as needed for no change in behavior;
        #   no idea if the differences are good or bad.
        # - This might not be needed when we change to the new .dpb file format (NIM)
        #   or if we have cached enough frames in lower-level code (NIM). ###e
        waitCursor = False
        if not from_slider:
            if not self.showEachFrame:
                delta = abs(fnum - self.currentFrame)
                if delta != 1:
                    if delta > 1000:
                        waitCursor = True
                        self.history.message(playDirection[ inc ] + "ing to frame " + str(fnum) + ".  You may select Pause at any time.")
                    else:
                        self.history.message(playDirection[ inc ] + "ing to frame " + str(fnum))
        else:
            if abs(fnum - self.currentFrame) > 1000:
                self.history.message("Advancing to frame " + str(fnum) + ". Please wait...")
                waitCursor = True
        if waitCursor:
            self.waitCursor = True
            QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        
        if DEBUG0: print "BEGIN LOOP: fnum = ", fnum, ", currentFrame =", self.currentFrame, ", inc =",inc
    
        # This is the main loop to compute atom positions from the current frame to "fnum".
        # After this loop completes, we paint the model -- but also during it.
        # We also recursively process QEvents during it. [bruce 050427 revised this comment]
        # [bruce question 050516: do those events ever include movie dashboard slider
        #  or button events which call this method recursively?? ####@@@@]
        self.debug_dump("before playToFrame loop", fnum = fnum, inc = inc)
        if from_slider:
            # [bruce 050427: this case got a lot simpler.]
            self.currentFrame = fnum
            self.alist_and_moviefile.play_frame( self.currentFrame)
            self.debug_dump("just after play_frame for slider", fnum = fnum, inc = inc)
        # else...
        
        while self.currentFrame != fnum:

            self.debug_dump("top of while loop body", fnum = fnum, inc = inc)
            assert not from_slider
            
            if self.isPaused:
                break
                
            ## self.currentFrame += inc -- doing this below [bruce 050427]

            if DEBUG0: print "IN LOOP1: fnum = ", fnum, ", currentFrame =", self.currentFrame, ", inc =",inc

            #bruce 050427 totally revised the following in implem (not in behavior).
            # Note that we needn't worry about valid range of frames, since both currentFrame and fnum should be within range.
            # (Unless the surrounding code fails to check currentFrame well enough... I'm not sure! ###k)
            # We only need to worry about whether we reach fnum or not.

            skip_n = self.win.skipSB.value()
            if not self.showEachFrame:
                #bruce 050428 adding this to see if it speeds up "forward to end"
                ###e potential optim: increase skip, as long as time passed will not be too bad
                skip_n = max(19,skip_n) # seems ok, though value is surely too big for huge models and too small for tiny ones ###e
            delta_n = 1 + skip_n
            for ii in range(delta_n): # slowness should not be an issue compared to time it takes to scan file... until new file format??
                self.currentFrame += inc
                if self.currentFrame == fnum:
                    break

            # now self.currentFrame needs to be shown
            if 1: ## self.showEachFrame: ####@@@@ old code said if 1 for this... what's best? maybe update them every 0.1 sec?
                self.update_dashboard_currentFrame()
            if 1:
                self.alist_and_moviefile.play_frame( self.currentFrame) # doing this every time makes it a lot slower, vs doing nothing!
                ###e [bruce 050428 comments:]
                # potential optim: do we need to do this now, even if not drawing on glpane?
                # Warning: if we don't do it, the atom posns and self.currentFrame are out of sync;
                # at least this requires fixing the posns at the end (doing play_frame then),
                # but it might cause worse trouble, so really it's better to increase the "skip" above
                # (perhaps adaptively using time-measurements). The other updates could safely be
                # conditioned on how much time had passed, if they're always done at the end if needed.
            if self.showEachFrame:
                self.glpane.gl_update()

            ## bruce 050427: the following is useless since we just updated the dashboard above, in all cases!
            ## not sure if this is intended or not, but for now I'll remove it and be equivalent to old code.
##            # Updating MP dashboard widgets will slow down slider control.
##            # Only update when "Move To End" button 
##            if self.moveToEnd:
## ##                self.win.movieProgressBar.setProgress(self.currentFrame) # Progress bar
##                self.update_dashboard_currentFrame()
                        
            # Process queued events [bruce comment 050516: note that this will do a paintGL from our earlier gl_update above ####@@@@]
            qApp.processEvents()
                #e bruce 050427 comment: should we check to see if the user changed the controls,
                # and (if so) change the fnum we're heading for?? ###@@@
                
        # End of loop
        self.debug_dump("after playToFrame loop", fnum = fnum, inc = inc)
        
        # Update cursor, slider and show frame.
        if self.waitCursor: 
            QApplication.restoreOverrideCursor() # Restore the cursor
            self.waitCursor = False
        
        self.update_dashboard_currentFrame( )
            # [bruce 050428 comment: old code only updated slider here, but it did both SL and SB in loop above;
            #  now the update method decides which ones to update]
        self.glpane.gl_update() #e bruce 050427 comment: we should optimize and only do this if we didn't just do it in the loop

        if 1: ## if not from_slider:
            #bruce 050428 always do this, since Mark agrees it'd be good for moving the slider to pause the movie
            if DEBUG0: print "movie._playToFrame(): Calling _pause"
            self._pause(0) # Force pause. Takes care of variable and dashboard maintenance.
            if DEBUG0: print "movie._playToFrame(): BYE!"

        return # from _playToFrame

    def _playSlider(self, fnum):
        """Slot for movie slider control.
        It will advance the movie to "fnum" from "currentFrame".
        fnum - frame number to advance to.
        """

        if DEBUG0: print "movie._playSlider() called: fnum = ", fnum, ", currentFrame =", self.currentFrame
        self.debug_dump("_playSlider", fnum = fnum)
        self._playToFrame(fnum, from_slider = True) #bruce 050427 merged _playSlider into _playToFrame method, using from_slider arg

                
    def _reset(self):
        """Resets the movie to the beginning (frame 0).
        """
        if DEBUG0: "movie._reset() called"
        if self.currentFrame == 0: return
        
        #bruce 050427 comment: added an isOpen check, in case of bugs in callers
        if not self.isOpen:
            return
        
        self.currentFrame = 0

        # Restore atom positions.
        self.alist_and_moviefile.play_frame( self.currentFrame)
        
        self.update_dashboard_currentFrame()
        self._pause(0)
        self.glpane.gl_update()
        
    def _moveToEnd(self):
        """
        """
        if DEBUG0: print "movie._moveToEnd() called"
        if self.currentFrame == self.totalFramesActual: return

        #bruce 050427 comment: added an isOpen check, in case of bugs in callers
        if not self.isOpen:
            return
        
        self._pause(0)
        self.moveToEnd = True
        self._playToFrame(self.totalFramesActual)

    # ==
    
    def _info(self):
        """Print info about movie
        """
        if DEBUG0: print "movie._info() called."
        if not self.filename:
            self.history.message("No movie file loaded.")
            return
        self.history.message("Filename: [" + self.filename + "]")
        msg = "Number of Frames: " + str(self.totalFramesActual) + ".  Number of Atoms: " + str(self.natoms)
        self.history.message(msg)
#        self.history.message("Temperature:" + str(self.temp) + "K")
#        self.history.message("Steps per Frame:" + str(self.stepsper))
#        self.history.message("Time Step:" + str(self.stepsper))

    def get_trace_filename(self):
        """Returns the trace filename for the current movie.
        """
        fullpath, ext = os.path.splitext(self.filename)
        if ext == '.xyz':
            #bruce 050407 new feature: ensure tracefilename differs when filename does
            # (see comment next to our caller in runSim.py for why this matters)
            suffix = "-xyztrace.txt"
        else:
            suffix = "-trace.txt"
        return fullpath + suffix
        
    def get_GNUplot_filename(self):
        """Returns the GNUplot filename for the current movie.
        """
        fullpath, ext = os.path.splitext(self.filename)
        return fullpath + "-plot.txt"
    
    def moveAtoms(self, newPositions): # used when reading xyz files
        """Huaicai 1/20/05: Move a list of atoms to newPosition. After 
            all atoms moving, bond updated, update display once.
           <parameter>newPosition is a list of atom absolute position,
           the list order is the same as self.alist
        """   
        if len(newPositions) != len(self.alist):
            #bruce 050225 added some parameters to this error message
            #bruce 050406 comment: but it probably never comes out, since readxyz checks this,
            # so I won't bother to print it to history here. But leaving it in is good for safety.
            print "moveAtoms: The number of atoms from XYZ file (%d) is not matching with that of the current model (%d)" % \
                  (len(newPositions), len(self.alist))
            return
        for a, newPos in zip(self.alist, newPositions):
            #bruce 050406 this needs a special case for singlets, in case they are H in the xyz file
            # (and therefore have the wrong distance from their base atom).
            # Rather than needing to know whether or not they were H during the sim,
            # we can just regularize the singlet-baseatom distance for all singlets.
            # For now I'll just use setposn to set the direction and snuggle to fix the distance.
            #e BTW, I wonder if it should also regularize the distance for H itself? Maybe only if sim value
            # is wildly wrong, and it should also complain. I won't do this for now.
            a.setposn_batch(A(newPos)) #bruce 050513 try to optimize this
            if a.is_singlet(): # same code as in movend()
                a.snuggle() # includes a.setposn; no need for that to be setposn_batch [bruce 050516 comment]
        self.glpane.gl_update()
        return

##    def debug_print_movie_info(self, msg = None): #bruce, sometime before 050427
##        if not msg:
##            msg = "debug_print_movie_info"
##        print_compact_stack( msg + "\n")
##        alist = self.alist
##        if not alist:
##            alist_report = "alist false (%r)" % alist
##        elif len(alist) <= 30:
##            alist_report = "alist len %d contains %r" % (len(alist), alist)
##        else:
##            alist_report = "alist len %d starts %r..." % (len(alist), alist[0:30])
##        if self.__dict__.has_key( 'part'): # hasattr isn't safe or correct here -- it calls getattr and recurses!
##            part_report = "self.part is already set to %r" % (self.part,)
##        else:
##            part_report = "self.part is unset"
##        print "\natom_debug: movie %r:\n%s\n%s\nfilename [%s]\n" % (self, alist_report, part_report, self.filename)
##        return

    pass # end of class Movie

# ==

class MovableAtomList: #bruce 050426 splitting this out of class Movie... except it's entirely new code, as it turns out.
    """A list of atoms within an assy (perhaps in more than one Part or even including killed atoms),
    with methods for quickly and safely changing all their positions at once, updating their display,
    for "owning" those atoms or their chunks as needed to make it safe to reset their positions,
    and for tracking external changes to their structure relevant to safety and validity of resetting
    their positions. [For Alpha5 we're mainly worrying about safety from tracebacks rather than validity.]
       [Not yet handled here: ability to be told to move an H to one position, but to actually move a singlet
    into a different position computed from that (re bug 254). Caller might help by ordering singlets after
    their base atoms, or even by doing this work itself (none of that is decided yet). #e]
    """
    #e the plan is to later optimize this greatly
    # by making it totally own the involved atoms' posns and do its own fast redisplay.
    
    def __init__(self, assy, alist):
        self.assy = assy
        self.glpane = assy.o
        self.alist = list(alist) # use A()?
            # is alist a public attribute? (if so, no need for methods to prune its atoms by part or killedness, etc)
        self.natoms = len(self.alist)

    def get_posns(self):
        """Return an Array (mutable and owned by caller) of current positions of our atoms
        (This must work even if some of our atoms have been killed, or moved into different Parts,
        since we were made, though the positions returned for killed atoms probably don't matter (#k not sure).)
        """
        res = map( lambda a: a.posn(), self.alist )
        return A(res)
            
    def set_posns(self, newposns):
        """set our atoms' positions (even killed ones) to those in the given array;
        do all required invals but no redisplay
        [#e someday we might have a version which only does this for the atoms now in a given Part]
        """
        #e later we'll optimize this by owning atoms and speeding up or eliminating invals
        for atm, pos in zip(self.alist, newposns):
            atm.setposn_batch( pos) #bruce 050513 try to optimize this

    set_posns_no_inval = set_posns #e for now... later this can be faster, and require own/release around it

    def own_atoms(self): #bruce 050427 made this from movsetup
        # "freeze" our atoms' chunks (i.e. make their basepos and curpos the same object,
        # to optimize atm.setposn for their atoms). This probably makes some operations
        # by outside code on those chunks illegal (though I'm not sure if this is still
        # true now that setposn handles frozen chunks). Note that far better optimizations
        # would be possible (avoiding invals, using Numeric to redraw), and other improvements
        # (using Numeric to continuously snuggle the singlets). [bruce 050427]
        moldict = {}
        for a in self.alist:
            m = a.molecule
            moldict[id(m)] = m
        self.molecules = moldict.values()
        ## self.part = part = self.molecules[0].part
##        parts = {}
##        for m in self.molecules:
##            p = m.part
##            parts[id(p)] = p
##        self.parts = parts.values() # includes None if any mols are killed ###k I assume this works for _nullMol too, for killed atoms?
##        del parts
##        if 0: #e do we want this? maybe as a warning?
##            # check them all before freezing any (does this cover killed atoms too? I think so.)
##            if len(self.parts) > 1 or self.parts[0] is None: #revised 050513
##                self.history.message( redmsg( "Can't play movie, since not all its atoms are still in the same Part, or some have been deleted" ))
##                assert 0 # not sure how well this will be caught... #e should use retval, fix caller ####@@@@
##            part = self.parts[0] # only ok if we don't keep going above when >1 part...
##            self.assy.set_current_part(part) #obs comment: ###@@@ ok here?? should also do this whenever movie dashboard is used, i think...
        for m in self.molecules:
            if m.part is not None: # not for killed ones!
                m.freeze()        
        return
    
##    def atoms_are_owned(self):
##        } pass
    
    def release_atoms(self): #bruce 050427 made this from movend
        # terrible hack for singlets in simulator, which treats them as H
        for a in self.alist:
            if a.is_singlet() and a.bonds: # could check a.molecule.part instead, but a.bonds is more to the point and faster
                #bruce 050428 exclude killed atoms (a.killed() is too slow [not anymore, bruce 050702, but this check is better anyway])
                a.snuggle() # same code as in moveAtoms() except for killed-atom check
            #e could optimize this (enough to do it continuously) by using Numeric to do them all at once
        for m in self.molecules:
            # should be ok even if some atoms moved into other mols since this was made [bruce 050516 comment]
            if m.part is not None: # not for killed ones! (even if killed since own_atoms was called)
                m.unfreeze()
        self.glpane.gl_update() # needed because of the snuggle above
        return

##    def parts_touched(self): ###@@@ redundant with code in own_atoms; also not currently used, I think
##        """Scan our atoms and report a list of the Parts they're currently in, using None for killed atoms;
##        callers can use this to decide which Part to show or whether they want to keep using us at all.
##        """
##        #e in future, will caller know when this needs doing (re invals of these atoms' parts), or will we track that?
##        res = {}
##        for atm in self.alist:
##            part = atm.molecule.part # can this fail for a killed atom?? is it None for a killed atom, as it should be?
##            res[part] = part
##        return res.values()
##
##    def touches_part(self, part): ###@@@ not currently used, I think
##        for atm in self.alist:
##            if part is atm.molecule.part: #revised 050513
##                return True
##        return False
        
    def update_displays(self):
        ###@@@ should use same glpane as in self.glpane.gl_update code above (one or the other is wrong) [bruce 050516 guess/comment]
        self.assy.o.gl_update() #stub? someday might need to update the MT as well if it's showing animated icons for involved Parts...

    def destroy(self):
        self.alist = None

    pass # end of class MovableAtomList

# ==

class alist_and_moviefile:
    """Set up and maintain a corresponding MovableAtomList and a MovieFile,
    and be able to move the atoms using the moviefile
    and know the state of their relationship at all times.
    (But let the two subobjects we create do most of the work.)
       Assume that we know the current valid frame better than the atoms do...
    even if something else moves them (unless it's another copy of the same movie,
    which we assume won't happen)... but this will become wrong once there's an Undo feature!
    So then, we'd want to advise the atom-state of this value (keyed to this object's moviefile-contents),
    so it'd be a part of the undone state. I'm not sure if I'll do that, or ignore it for now. ###k
    Or I might do *both*, by designating this object as the way the atom's real owner (their assy) remembers that state!
    In other words, this "playable movie" is sitting in the atoms as a "slidable handle" (metaphorically at least)
    to let anything adjust their posns using it,
    including (example 1) the moviemode dashboard controls
    (once it decides which movie object it wants to display and adjust)
    or (example 2) various cmenu ops (or even MT-embedded sliders?) on movie nodes in the MT.
       This class might be small enough to use as a Jig for actually being in the MT...
    or it might still be better to let that be a separate object which represents one of these. #k
    """
    _valid = False
    def __init__(self, assy, alist, filename, curframe_in_alist = None):
        """Caller promises that filename exists. If it matches alist well enough to use with it,
        we set self.valid() true and fully init ourselves, i.e. set up the file/alist relationship
        and get ready to play specific frames (i.e. copy posns from file into alist's atoms) on request.
        If file doesn't match alist, we set self.valid() false and return early
        (but we might still be usable later if the file changes and some recheck method (NIM) is called (#e)).
           If provided, curframe_in_alist is the frame whose abs positions are the current positions of the atoms in alist,
        and caller is saying to use this to understand how to interpret a purely-differential moviefile.
        If the moviefile has its own abs positions, we can ignore this argument
        (#e but in future we might decide instead to check it, or to use it in some other way...).
        """
        self.alist = alist # needed for rechecking the match
        self.history = assy.w.history # not yet used, but probably will be used for error messages
        self.moviefile = MovieFile( filename, history = self.history)
        self.movable_atoms = None 
        if not self.moviefile:
            pass ## MovieFile will have emitted a history message (I hope)
            return
        self._valid = self.moviefile.matches_alist(alist) # this never emits a history message (for now)
        if not self._valid:
            # for now, we happen to know exactly why they're not valid... [bruce 050428]
            self.history.message( redmsg( "Movie file contents not valid for this Part (wrong number of atoms)."))
            self.moviefile.destroy()
            self.moviefile = None
            return # caller should check self.valid()
        self.movable_atoms = MovableAtomList( assy, alist)
        if curframe_in_alist is not None:
            n = curframe_in_alist
            frame_n = self.movable_atoms.get_posns()
            self.moviefile.donate_immutable_cached_frame( n, frame_n)
            self.current_frame = n
        else:
            self.current_frame = None # since it's unknown (#k ok for all callers?)
        return
    def destroy(self):
        try:
            if self.moviefile:
                self.moviefile.destroy()
            if self.movable_atoms:
                self.movable_atoms.destroy()
            self.alist = None
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: exception in alist_and_moviefile.destroy() ignored: ")
        return
##    why_not_playable = "" #e need to set this to actual reasons when possible
    def might_be_playable(self):
        return self.valid() # from the last time this was checked -- it's not re-checked now
    def valid(self):
        return self._valid
    def recheck_valid(self):
        self._valid = self.moviefile.recheck_matches_alist( self.alist)
        #e also check whether atoms are all in same part and not killed? No! We'll play even if these conditions are false.
        return self._valid
    def own_atoms(self):
        self.movable_atoms.own_atoms()
##    def atoms_are_owned(self):
##        return self.movable_atoms.atoms_are_owned()
    def release_atoms(self):
        self.movable_atoms.release_atoms()
    def play_frame(self, n):
        """Try to set atoms to positions in frame n.
        Return true if this works, false if n went beyond either end of moviefile.
        (For other errors, print some sort of error message and return false,
         or perhaps just raise an exception. #k)
        """
        mf = self.moviefile
        ma = self.movable_atoms
        if mf.frame_index_in_range(n):
            frame_n = mf.ref_to_transient_frame_n(n)
            #####@@@@@ bruce 050513
            ## print "not playing frame %d" % n
            ma.set_posns(frame_n) # now we no longer need frame_n
                # (note: set_posns did invals but not updates.)
            self.current_frame = n #k might not be needed -- our caller keeps its own version of this
            return True ###k does caller, or this method, need to update dashboards and glpanes that care?
        else:
            ## self.pause() ###k guess -- since we presumably hit the end... maybe return errcode instead, let caller decide??
            return False
        pass
    def get_totalFramesActual(self):
        return self.moviefile.get_totalFramesActual()
    def close_file(self):
        self.moviefile.close_file()
    pass # end of class alist_and_moviefile

# == helper functions

def find_saved_movie( assy, mfile):
    "look for a .dpb file of the given name; if found, return a Movie object for it"
    movie = Movie(assy)
    if movie.represent_this_moviefile( mfile):
        # succeeded
        return movie
    # otherwise it failed but did NOT already emit error messages about that (should it? in future, only it knows why it failed)
    return None

def _checkMovieFile(part, filename, history = None):
    """Returns 0 if filename is (or might be) a valid movie file for the specified part.
    Returns 1 if filename does not exist.
    Returns 2 if the movie file does not match the part.
    If history arg is provided, prints error messages to it
    (whenever return value is not zero).
    """
    #bruce 050427 comment: This should be merged with related code in moviefile.py,
    # but it looks correct, so I won't do this now. It's now only called from fileOpenMovie.
    #bruce 050324 made this a separate function, since it's not about a specific
    # Movie instance, just about a Part and a filename. Both args are now required,
    # and a new optional arg "history" is both where and whether to print errors
    # (both existing calls have been changed to pass it).
    # This function only checks number of atoms, and assumes all atoms of the Part
    # must be involved in the movie (in an order known to the Part, not checked,
    # though the order can easily be wrong).
    # It is not yet updated to handle the "new dpb format" (ie it doesn't get help
    # from either file keys or movie ids or atom positions) or movies made from
    # a possible future "simulate selection" operation.
    print_errors = not not history
    
    if DEBUG1: print "movie._checkMovieFile() function called. filename = ", filename
    
    assert filename #bruce 050324
    if not os.path.exists(filename):
        if print_errors:
            msg = redmsg("Cannot play movie file [" + filename + "]. It does not exist.")
            history.message(msg)
        return 1

    #bruce 050411: protect against no part (though better if caller does this); see bug 497.
    # Might be better to let part be unspecified and figure out from the moviefile
    # which available Part to use, but this is not
    # currently possible -- if parts have same contents, it's not even possible in principle
    # until we have new DPB format, and not clear how to do it even then (if we only have
    # persistent names for files rather than parts).
    if part is None:
        if platform.atom_debug:
            print_compact_stack( "atom_debug: possible bug: part is false (%r) in _checkMovieFile for %s" % (part,filename))
            ## can't do this, no movie arg!!! self.debug_print_movie_info()
        if print_errors:
            msg = redmsg("Movie file [" + filename + "] can't be played for current part.") # vaguer & different wording, since bug
            history.message(msg)
        return 2

    # start of code that should be moved into moviefile.py and merged with similar code there
    filesize = os.path.getsize(filename) - 4
    
    fp = open(filename,'rb')
    
    # Read header (4 bytes) from file containing the number of frames in the movie.
    nframes = unpack('i',fp.read(4))[0]
    fp.close()
    
    natoms = int(filesize/(nframes*3))
    # end of code that should be moved into moviefile.py

    kluge_ensure_natoms_correct( part)
    
    if natoms == part.natoms: ## bruce 050324 changed this from natoms == len(self.assy.alist)
        return 0
    else:
        if platform.atom_debug:
            print "atom_debug: not natoms == part.natoms, %d %d" % (natoms, part.natoms)
        if print_errors:
            msg = redmsg("Movie file [" + filename + "] not valid for the current part.")
            history.message(msg)
        return 2
    pass

def kluge_ensure_natoms_correct(part):
    ###@@@ kluge to work around bug in part.natoms not being invalidated enough
    part.natoms = None
    del part.natoms # force recompute when next needed
    return

# end
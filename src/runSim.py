# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
runSim.py

setting up and running the simulator, for Simulate or Minimize
(i.e. the same code that would change if the simulator interface changed),
and the user-visible commands for those operations.

$Id$

History: Mark created a file of this name, but that was renamed to SimSetup.py
by bruce on 050325.

Bruce 050324 pulled in lots of existing code for running the simulator
(and some code for reading its results) into this file, since that fits
its name. That existing code was mostly by Mark and Huaicai, and was
partly cleaned up by Bruce, who also put some of it into subclasses
of the experimental CommandRun class.

Bruce 050331 is splitting writemovie into several methods in more than
one subclass (eventually) of a new SimRunner class.

bruce 050901 and 050913 used env.history in some places.

bruce 051115 some comments and code cleanup; add #SIMOPT wherever a simulator executable command-line flag is hardcoded.

bruce 051231 partly-done code for using pyrex interface to sim; see use_dylib
'''

from debug import print_compact_traceback
import platform
from platform import fix_plurals
import os, sys
from math import sqrt
from SimSetup import SimSetup
from qt import QApplication, QCursor, Qt, QStringList, QProcess, QObject, SIGNAL
from movie import Movie
from HistoryWidget import redmsg, greenmsg, orangemsg
import env
from env import seen_before
from VQT import A, V
import re

# more imports lower down

debug_sim_exceptions = 0 # DO NOT COMMIT WITH 1 -- set this to reproduce a bug mostly fixed by Will today #bruce 060111

debug_all_frames = 0 # DO NOT COMMIT with 1
debug_all_frames_atom_index = 1 # index of atom to print in detail, when debug_all_frames

debug_sim = 0 # DO NOT COMMIT with 1
debug_pyrex_prints = 0 # prints to stdout the same info that gets shown transiently in statusbar
debug_timing_loop_on_sbar = 0

use_pyrex_sim = True 
    # Use pyrex sim by default.  Use debug menu to use the standalone sim. mark 060314.

if debug_sim_exceptions:
    debug_all_frames = 1

_FAILURE_ALREADY_DOCUMENTED = -10101

    
class SimRunner:
    "class for running the simulator [subclasses can run it in special ways, maybe]"
    #bruce 050330 making this from writemovie and maybe some of Movie/SimSetup; experimental,
    # esp. since i don't yet know how much to factor the input-file writing, process spawning,
    # file-growth watching, file reading, file using. Surely in future we'll split out file using
    # into separate code, and maybe file-growth watching if we run procs remotely
    # (or we might instead be watching results come in over a tcp stream, frames mixed with trace records).
    # So for now, let's make the minimal class for running the sim, up to having finished files to look at
    # but not looking at them, then the old writemovie might call this class to do most of its work
    # but also call other classes to use the results.

    # wware 060406 bug 1263 - provide a mechanism to be notified when the program is exiting
    # This is set to True in ops_files.py. This is a class (not instance) variable which matters
    # because ops_files.py can set this without a reference to the currently active SimRunner instance.
    PREPARE_TO_CLOSE = False
    
    def __init__(self, part, mflag, simaspect = None, use_dylib_sim = use_pyrex_sim, cmdname = "Simulator"):
            # [bruce 051230 added use_dylib_sim; revised 060102; 060106 added cmdname]
        "set up external relations from the part we'll operate on; take mflag since someday it'll specify the subclass to use"
        from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
        self.assy = assy = part.assy # needed?
        #self.tmpFilePath = assy.w.tmpFilePath
        self.win = assy.w  # might be used only for self.win.progressbar.launch
        self.part = part # needed?
        self.mflag = mflag # see docstring
        self.simaspect = simaspect # None for entire part, or an object describing what aspect of it to simulate [bruce 050404]
        self.errcode = 0 # public attr used after we're done; 0 or None = success (so far), >0 = error (msg emitted)
        self.said_we_are_done = False #bruce 050415
        self.pyrexSimInterrupted = False  #wware 060323, bug 1725, if interrupted we don't need so many warnings
        
        prefer_standalone_sim = debug_pref("force use of standalone sim", Choice_boolean_False,
                                      prefs_key = 'use-standalone-sim', non_debug = True)
        
        if prefer_standalone_sim:
            use_dylib_sim = False
        self.use_dylib_sim = use_dylib_sim #bruce 051230
            
        self.cmdname = cmdname
        if not use_dylib_sim:
            env.history.message(greenmsg("Using the standalone simulator (not the pyrex simulator)"))
        return
    
    def run_using_old_movie_obj_to_hold_sim_params(self, movie): #bruce 051115 removed unused 'options' arg
        self._movie = movie # general kluge for old-code compat (lots of our methods still use this and modify it)
        # note, this movie object (really should be a simsetup object?) does not yet know a proper alist (or any alist, I hope) [bruce 050404]
        self.errcode = self.set_options_errQ( ) # set movie alist, output filenames, sim executable pathname (verify it exists)
            #obs comment [about the options arg i removed?? or smth else?]
            # options include everything that affects the run except the set of atoms and the part
        if self.errcode: # used to be a local var 'r'
            # bruce 051115 comment: more than one reason this can happen, one is sim executable missing
            return
        self.sim_input_file = self.sim_input_filename() # might get name from options or make up a temporary filename
        self.set_waitcursor(True)
        
        # Disable some QActions (menu items/toolbar buttons) while the sim is running.
        self.win.disable_QActions_for_sim(True)
        
        try: #bruce 050325 added this try/except wrapper, to always restore cursor
            self.write_sim_input_file() # for Minimize, uses simaspect to write file; puts it into movie.alist too, via writemovie
            self.simProcess = None #bruce 051231
            self.spawn_process()
                # spawn_process is misnamed since it can go thru either interface (pyrex or exec OS process),
                # since it also monitors progress and waits until it's done,
                # and insert results back into part, either in realtime or when done.
                # result error code (or abort button flag) stored in self.errcode
        except:
            print_compact_traceback("bug in simulator-calling code: ")
            self.errcode = -11111
        self.set_waitcursor(False)
        self.win.disable_QActions_for_sim(False)
        
        if not self.errcode:
            return # success
        if self.errcode == 1: # User pressed Abort button in progress dialog.
            msg = redmsg("Aborted.")
            env.history.message(self.cmdname + ": " + msg)

            if self.simProcess: #bruce 051231 added condition (since won't be there when use_dylib)
                ##Tries to terminate the process the nice way first, so the process
                ## can do whatever clean up it requires. If the process
                ## is still running after 2 seconds (a kludge). it terminates the 
                ## process the hard way.
                #self.simProcess.tryTerminate()
                #QTimer.singleShot( 2000, self.simProcess, SLOT('kill()') )
                
                # The above does not work, so we'll hammer the process with SIGKILL.
                # This works.  Mark 050210
                self.simProcess.kill()
            
        elif not self.pyrexSimInterrupted and self.errcode != _FAILURE_ALREADY_DOCUMENTED:   # wware 060323 bug 1725
            # Something failed...
            msg = redmsg("Simulation failed: exit code or internal error code %r " % self.errcode) #e identify error better!
            env.history.message(self.cmdname + ": " + msg)
                #fyi this was 'cmd' which was wrong, it says 'Simulator' even for Minimize [bruce 060106 comment, fixed it now]
        self.said_we_are_done = True # since saying we aborted or had an error is good enough... ###e revise if kill can take time.
        return # caller should look at self.errcode
        # semi-obs comment? [by bruce few days before 050404, partly expresses an intention]
        # results themselves are a separate object (or more than one?) stored in attrs... (I guess ###k)
        # ... at this point the caller probably extracts the results object and uses it separately
        # or might even construct it anew from the filename and params
        # depending on how useful the real obj was while we were monitoring the progress
        # (since if so we already have it... in future we'll even start playing movies as their data comes in...)
        # so not much to do here! let caller care about res, not us.
    
    def set_options_errQ(self): #e maybe split further into several setup methods? #bruce 051115 removed unused 'options' arg
        """Set movie alist (from simaspect or entire part); debug-msg if it was already set (and always ignore old value).
        Figure out and set filenames, including sim executable path.
        All inputs and outputs are self attrs or globals or other obj attrs... except, return error code if sim executable missing
        or on other errors detected by subrs.
        
        old docstring:
        Caller should specify the options for this simulator run
        (including the output file name);
        these might affect the input file we write for it
        and/or the arguments given to the simulator executable.
        Temporary old-code compatibility: use self._movie
        for simsetup params and other needed params, and store new ones into it.
        """
        part = self.part
        movie = self._movie

        # set up alist (list of atoms for sim input and output files, in order)
        if movie.alist is not None:
            # this movie object is being reused, which is a bug. complain... and try to work around.
            if platform.atom_debug: # since I expect this is possible for "save movie file" until fixed... [bruce 050404] (maybe not? it had assert 0)
                print "BUG (worked around??): movie object being reused unexpectedly"
            movie.alist = None
        movie.alist_fits_entire_part = False # might be changed below
        if not self.simaspect:
            # No prescribed subset of atoms to minimize. Use all atoms in the part.
            # Make sure some chunks are in the part.
            if not part.molecules: # Nothing in the part to minimize.
                msg = redmsg("Can't create movie.  No chunks in part.")
                    ####@@@@ is this redundant with callers? yes for simSetup,
                    # don't know about minimize, or the weird fileSave call in MWsem.
                env.history.message(msg)
                return -1
            movie.set_alist_from_entire_part(part) ###@@@ needs improvement, see comments in it
            for atm in movie.alist:
                assert atm.molecule.part == part ###@@@ remove when works
            movie.alist_fits_entire_part = True # permits optims... but note it won't be valid
                # anymore if the part changes! it's temporary... not sure it deserves to be an attr
                # rather than local var or retval.
        else:
            # the simaspect should know what to minimize...
            alist = self.simaspect.atomslist()
            movie.set_alist(alist)
            for atm in movie.alist: # redundant with set_alist so remove when works
                assert atm.molecule.part == part

        # Set up filenames.
        # We use the process id to create unique filenames for this instance of the program
        # so that if the user runs more than one program at the same time, they don't use
        # the same temporary file names.
        # We now include a part-specific suffix [mark 051030]]
        # [This will need revision when we can run more than one sim process
        #  at once, with all or all but one in the "background" [bruce 050401]]
        
        # simFilesPath = "~/Nanorex/SimFiles". Mark 051028.
        from platform import find_or_make_Nanorex_subdir
        simFilesPath = find_or_make_Nanorex_subdir('SimFiles')
        
        # Create temporary part-specific filename.  Example: "partname-minimize-pid1000"
        # We'll be appending various extensions to tmp_file_prefix to make temp file names
        # for sim input and output files as needed (e.g. mmp, xyz, etc.)
        from movieMode import filesplit
        junk, basename, ext = filesplit(self.assy.filename)
        if not basename: # The user hasn't named the part yet.
            basename = "Untitled"
        self.tmp_file_prefix = os.path.join(simFilesPath, "%s-minimize-pid%d" % (basename, os.getpid()))
            
        r = self.old_set_sim_output_filenames_errQ( movie, self.mflag)
        if r: return r
        # don't call sim_input_filename here, that's done later for some reason

        # prepare to spawn the process later (and detect some errors now)
        bin_dir = self.sim_bin_dir_path()
        
        # Make sure the simulator exists (as dylib or as standalone program)
        if self.use_dylib_sim:
            #bruce 051230 experimental code
            self.dylib_path = bin_dir
                # this works for developers if they set up symlinks... might not be right...
            worked = self.import_dylib_sim(self.dylib_path)
            if not worked:
                # The dylib filename on Windows can be either sim.dll or sim.pyd -- should we mention them both?
                # If the imported name is not the usual one, or if two are present, should we print a warning?
                ##e Surely this message text (and the other behavior suggested above) should depend on the platform
                # and be encapsulated in some utility function for loading dynamic libraries. [bruce 060104]
                msg = redmsg("The simulator dynamic library [sim.so or sim.dll, in " + self.dylib_path +
                             "] is missing or could not be imported. Trying command-line simulator.")
                env.history.message(self.cmdname + ": " + msg)
                ## return -1
                self.use_dylib_sim = False
                ####@@@@ bug report: even after this, it will find tracefile from prior run (if one exists) and print its warnings.
                # probably we should remove that before this point?? [bruce 051230] [hmm, did my later removal of the old tracefile
                # fix this, or is it not removed until after this point?? bruce question 060102]

        if not self.use_dylib_sim:
            # "program" is the full path to the simulator executable. 
            if sys.platform == 'win32': 
                program = os.path.join(bin_dir, 'simulator.exe')
            else:
                program = os.path.join(bin_dir, 'simulator')
            if not os.path.exists(program):
                msg = redmsg("The simulator program [" + program + "] is missing.  Simulation aborted.")
                env.history.message(self.cmdname + ": " + msg)
                return -1
            self.program = program
        
        return None # no error
        
    def sim_bin_dir_path(self): #bruce 060102 split this out
        """Return pathname of bin directory that ought to contain simulator executable and/or dynamic library.
        (Doesn't check whether it exists.)
        """
        # filePath = the current directory NE-1 is running from.
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.normpath(filePath + '/../bin')

    def import_dylib_sim(self, dylib_path): #bruce 051230 experimental code
        """Try to import the dynamic library version of the simulator, under the module name 'sim',
        located in dylib_path. Return a success flag.
        """
        import sys
        if not sys.modules.has_key('sim'):
            oldpath = sys.path
            sys.path = [dylib_path] + oldpath
                ##k Do we need to include oldpath here? if not, we get better error detection if we leave it out.
                # But we might need to (in principle), if this import has to do another one behind the scenes for some reason.
                ##e maybe for some errors we should remove this invalid module so we can try the import again later??
                # This might never work, since maybe Python removes it unless it got too far to try again;
                # if it does ever import it it won't do more (even with reload) until you rerun the app.
                # So it's probably not worth improving this error handling code.
            try:
                import sim
                assert sys.modules.has_key('sim')
                worked = True
            except:
                print_compact_traceback("error trying to import dylib sim: ")
                worked = False
                #e should we worry about whether sys.modules.has_key('sim') at this point? Might depend on how it failed.
            sys.path = oldpath
        else:
            worked = True # optimistic
        if worked:
            try:
                from sim import Minimize, Dynamics # the two constructors we might need to use
            except:
                worked = False
                print_compact_traceback("error trying to import Minimize and Dynamics from dylib sim: ")
        return worked
    
    def old_set_sim_output_filenames_errQ(self, movie, mflag):
        """Old code, not yet much cleaned up. Uses and/or sets movie.filename,
        with movie serving to hold desired sim parameters
        (more like a SimSetup object than a Movie object in purpose).
        Stores shell command option for using tracefile (see code, needs cleanup).
        Returns error code (nonzero means error return needed from entire SimRunner.run,
         and means it already emitted an error message).
        """
        # figure out filename for trajectory or final-snapshot output from simulator
        # (for sim-movie or minimize op), and store it in movie.moviefile
        # (in some cases it's the name that was found there).
        
        if mflag == 1: # single-frame XYZ file
            if movie.filename and platform.atom_debug:
                print "atom_debug: warning: ignoring filename %r, bug??" % movie.filename
            movie.filename = self.tmp_file_prefix + ".xyz"  ## "sim-%d.xyz" % pid
            
        if mflag == 2: #multi-frame DPB file
            if movie.filename and platform.atom_debug:
                print "atom_debug: warning: ignoring filename %r, bug??" % movie.filename
            movie.filename = self.tmp_file_prefix + ".dpb"  ## "sim-%d.dpb" % pid
        
        if movie.filename: 
            moviefile = movie.filename
        else:
            msg = redmsg("Can't create movie.  Empty filename.")
            env.history.message(self.cmdname + ": " + msg)
            return -1
            
        # Check that the moviefile has a valid extension.
        ext = moviefile[-4:]
        if ext not in ['.dpb', '.xyz']:
            # Don't recognize the moviefile extension.
            msg = redmsg("Movie [" + moviefile + "] has unsupported extension.")
            env.history.message(self.cmdname + ": " + msg)
            print "writeMovie: " + msg
            return -1
        movie.filetype = ext #bruce 050404 added this

        # Figure out tracefile name, store in self.traceFileName,
        # and come up with sim-command argument for it, store that in self.traceFileArg.
        if mflag:
            #bruce 050407 comment: mflag true means "minimize" (value when true means output filetype).
            # Change: Always write tracefile, so Minimize can see warnings in it.
            # But let it have a different name depending on the output file extension,
            # so if you create xxx.dpb and xxx.xyz, the trace file names differ.
            # (This means you could save one movie and one minimize output for the same xxx,
            #  and both trace files would be saved too.) That change is now in movie.get_trace_filename().
            self.traceFileName = movie.get_trace_filename()
                # (same as in other case, but retval differs due to movie.filetype)
        else:
            # The trace filename will be the same as the movie filename, but with "-trace.txt" tacked on.
            self.traceFileName = movie.get_trace_filename() # presumably uses movie.filename we just stored
                # (I guess this needn't know self.tmp_file_prefix except perhaps via movie.filename [bruce 050401])

        if self.traceFileName:
            self.traceFileArg = "-q" + self.traceFileName #SIMOPT
        else:
            self.traceFileArg = ""
                
        # This was the old tracefile - obsolete as of 2005-03-08 - Mark
        ## traceFileArg = "-q"+ os.path.join(self.tmpFilePath, "sim-%d-trace.txt" % pid) #SIMOPT

        return None # no error

    def sim_input_filename(self):
        """Figure out the simulator input filename
        (previously set options might specify it or imply how to make it up;
         if not, make up a suitable temp name)
        and return it; don't record it (caller does that),
        and no need to be deterministic (only called once if that matters).
        """         
        # We always save the current part to an MMP file before starting
        # the simulator.  In the future, we may want to check if assy.filename
        # is an MMP file and use it if not assy.has_changed().
        # [bruce 050324 comment: our wanting this is unlikely, and becomes more so as time goes by,
        #  and in any case would only work for the main Part (assy.tree.part).]
        return self.tmp_file_prefix + ".mmp" ## "sim-%d.mmp" % pid
    
    def write_sim_input_file(self):
        """Write the appropriate data from self.part (as modified by self.simaspect)
        to an input file for the simulator (presently always in mmp format)
        using the filename self.sim_input_file
        (overwriting any existing file of the same name).
        """
        part = self.part
        mmpfile = self.sim_input_file # the filename to write to
        movie = self._movie # old-code compat kluge
        assert movie.alist is not None #bruce 050404
        
        if not self.simaspect: ## was: if movie.alist_fits_entire_part:
            if debug_sim: #bruce 051115 added this
                print "part.writemmpfile(%r)" % (mmpfile,)
            stats = {}
            part.writemmpfile( mmpfile, leave_out_sim_disabled_nodes = True, sim = True, dict_for_stats = stats)
                #bruce 051209 added options  (used to be hardcoded in files_mpp, see below), plus a new one, dict_for_stats
                # As of 051115 this is still called for Run Sim.
                # As of 050412 this didn't yet turn singlets into H;
                # but as of long before 051115 it does (for all calls -- so it would not be good to use for Save Selection!).
                #
                #bruce 051209 addendum:
                # It did this [until today] via these lines in files_mmp (copied here so text searches can find them):
                #   mapping = writemmp_mapping(assy, leave_out_sim_disabled_nodes = True, sim = True)
                #       #bruce 050811 added sim = True to fix bug 254 for sim runs, for A6.
                # It would be better if it did this by passing its own (better-named) options to this writing method.
                # So I made that change now, and I'll also pass a place to accumulate stats into,
                # so I can complete the fix to bug 254 (by printing messages about X->H, albeit by copying similar code
                #  and figuring out the count differently) without making the klugetower even worse.
            nsinglets_H = stats.get('nsinglets_H', 0)
            if nsinglets_H: #bruce 051209 this message code is approximately duplicated elsewhere in this file
                info = fix_plurals( "(Treating %d bondpoint(s) as Hydrogens, during simulation)" % nsinglets_H )
                env.history.message( info)
        else:
            #bruce 051209 comment: I believe this case can never run (and is obs), but didn't verify this.
            if debug_sim: #bruce 051115 added this
                print "simaspect.writemmpfile(%r)" % (mmpfile,)
            # note: simaspect has already been used to set up movie.alist; simaspect's own alist copy is used in following:
            self.simaspect.writemmpfile( mmpfile) # this also turns singlets into H
            # obs comments:
            # can't yet happen (until Minimize Selection) and won't yet work 
            # bruce 050325 revised this to use whatever alist was asked for above (set of atoms, and order).
            # But beware, this might only be ok right away for minimize, not simulate (since for sim it has to write all jigs as well).
        
        ## movie.natoms = natoms = len(movie.alist) # removed by bruce 050404 since now done in set_alist etc.
        ###@@@ why does that trash a movie param? who needs that param? it's now redundant with movie.alist
        return
    
    def set_waitcursor(self, on_or_off):
        """For on_or_off True, set the main window waitcursor.
        For on_or_off False, revert to the prior cursor.
        [It might be necessary to always call it in matched pairs, I don't know [bruce 050401]. #k]
        """
        if on_or_off:
            # == Change cursor to Wait (hourglass) cursor
            
            ##Huaicai 1/10/05, it's more appropriate to change the cursor
            ## for the main window, not for the progressbar window
            QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
            #oldCursor = QCursor(win.cursor())
            #win.setCursor(QCursor(Qt.WaitCursor) )
        else:
            QApplication.restoreOverrideCursor() # Restore the cursor
            #win.setCursor(oldCursor)
        return
    
    def spawn_process(self): # misnamed, since (1) also includes monitor_progress, and (2) doesn't always use a process
        """Actually spawn the process [or the extension class object],
        making its args [or setting its params] based on some of self's attributes.
        Wait til we're done with this simulation, then record results in other self attributes.
        """
        if debug_sim: #bruce 051115 added this; confirmed this is always called for any use of sim (Minimize or Run Sim)
            print "calling spawn_process" 
        # First figure out process arguments
        # [bruce 050401 doing this later than before, used to come before writing sim-input file]
        self.setup_sim_args() # stores them in an attribute, whose name and value depends on self.use_dylib_sim
        # Now run the sim to completion (success or fail or user abort),
        # as well as whatever updates we do at the same time in the cad code
        # (progress bar, showing movie in realtime [nim but being added circa 051231], ...)
        if self.use_dylib_sim:
            self.sim_loop_using_dylib() #bruce 051231 wrote this anew
        else:
            self.sim_loop_using_standalone_executable() #bruce 051231 made this from last part of old spawn_process code
        return

    def setup_sim_args(self): #bruce 051231 split this out of spawn_process, added dylib case
        """Set up arguments for the simulator, using one of two different interfaces:
        either constructing a command line for the standalone executable simulator,
        or creating and setting up an instance of an extension class defined in the
        sim module (a dynamic library). (But don't start it running.)
           We use the same method to set up both kinds of interface, so that it will
        be easier to keep them in sync as the code evolves.
           WARNING: We also set a few attributes of self which cause side effects later;
        in one case, the attribute looks just like a sim-executable command line option
        (purely for historical reasons).
        """
        # set one of the sim-interface-format flags
        use_dylib = self.use_dylib_sim
        use_command_line = not self.use_dylib_sim
        # (The rest of this method would permit both of these flags to be set together, if desired;
        #  that might be useful if we want to try one interface, and if it fails, try the other.)
        
        movie = self._movie # old-code compat kluge
        self.totalFramesRequested = movie.totalFramesRequested
        moviefile = movie.filename
        if use_command_line:
            program = self.program
            outfileArg = "-o%s" % moviefile #SIMOPT
            traceFileArg = self.traceFileArg
        infile = self.sim_input_file

        ext = movie.filetype #bruce 050404 added movie.filetype
        mflag = self.mflag
        
        # "formarg" = File format argument -- we need this even when use_dylib,
        # since it's also used as an internal flag via self._formarg
        if ext == ".dpb": formarg = ''
        elif ext == ".xyz": formarg = "-x" #SIMOPT (value also used as internal flag)
        else: assert 0
        self._formarg = formarg # kluge
        # the use_dylib code for formarg is farther below

        self._simopts = self._simobj = self._arguments = None # appropriate subset of these is set below
        
        if use_command_line:
            # "args" = arguments for the simulator.
            #SIMOPT -- this appears to be the only place the entire standalone simulator command line is created.
            if mflag:
                # [bruce 05040 infers:] mflag true means minimize; -m tells this to the sim.
                # (mflag has two true flavors, 1 and 2, for the two possible output filetypes for Minimize.)
                # [later, bruce 051231: I think only one of the two true mflag values is presently supported.]
                args = [program, '-m', str(formarg), traceFileArg, outfileArg, infile] #SIMOPT
            else: 
                # THE TIMESTEP ARGUMENT IS MISSING ON PURPOSE.
                # The timestep argument "-s + (movie.timestep)" is not supported for Alpha. #SIMOPT
                args = [program, 
                            '-f' + str(movie.totalFramesRequested), #SIMOPT
                            '-t' + str(movie.temp),  #SIMOPT
                            '-i' + str(movie.stepsper),  #SIMOPT
                            '-r', #SIMOPT
                            str(formarg),
                            traceFileArg,
                            outfileArg,
                            infile]
            if debug_sim:
                print  "program = ",program
                print  "Spawnv args are %r" % (args,) # note: we didn't yet remove args equal to "", that's done below
            arguments = QStringList()
            for arg in args:
                # wware 051213  sim's getopt doesn't like empty arg strings
                if arg != "":
                    arguments.append(arg)
            self._arguments = arguments
            del args, arguments
        if use_dylib:
            import sim # whether this will work was checked by a prior method
            if mflag:
                clas = sim.Minimize
            else:
                clas = sim.Dynamics
            simobj = clas(infile)
            # order of set of remaining options should not matter;
            # for correspondence see sim/src files sim.pyx, simhelp.c, and simulator.c
            simopts = simobj # for now, use separate variable names to access params vs methods, in case this changes again [b 060102]
            if formarg == '-x':
                simopts.DumpAsText = 1 # xyz rather than dpb, i guess
            else:
                assert formarg == ''
                simopts.DumpAsText = 0
            if self.traceFileName:
                simopts.TraceFileName = self.traceFileName # note spelling diff, 'T' vs 't' (I guess I like this difference [b 060102])
                #k not sure if this would be ok to do otherwise, since C code doesn't turn "" into NULL and might get confused
            simopts.OutFileName = moviefile
            if not mflag:
                # The timestep argument "-s + (movie.timestep)" or Dt is not supported for Alpha...
                simopts.NumFrames = movie.totalFramesRequested   # SIMPARAMS
                simopts.Temperature = movie.temp
                simopts.IterPerFrame = movie.stepsper
                simopts.PrintFrameNums = 0
            #e we might need other options to make it use Python callbacks (nim, since not needed just to launch it differently);
            # probably we'll let the later sim-start code set those itself.
            self._simopts = simopts
            self._simobj = simobj
        # wware 060406 bug 1471 - don't need a real movie, just need to hold the sim parameters
        # If the sim parameters change, they need to be updated everywhere a comment says "SIMPARAMS"
        # Movie.__init__ (movie.py), toward the end
        # SimSetup.setup (SimSetup.py)
        # FakeMovie.__init (runSim.py) and ~14 lines earlier
        class FakeMovie:
            def __init__(self, realmovie):
                self.totalFramesRequested = realmovie.totalFramesRequested
                self.temp = realmovie.temp
                self.stepsper = realmovie.stepsper
                self.watch_motion = realmovie.watch_motion
        self.assy.stickyParams = FakeMovie(movie)
        # return whatever results are appropriate -- for now, we stored each one in an attribute (above)
        return
        
    def sim_loop_using_standalone_executable(self): #bruce 051231 made this from part of spawn_process; compare to sim_loop_using_dylib
        "#doc"
        movie = self._movie
        arguments = self._arguments
        
        #bruce 050404 let simProcess be instvar so external code can abort it [this is still used as of 051231]
        self.simProcess = None
        try:
            self.remove_old_moviefile(movie.filename) # can raise exceptions #bruce 051230 split this out
            self.remove_old_tracefile(self.traceFileName)
            ## Start the simulator in a different process 
            self.simProcess = QProcess()
            simProcess = self.simProcess
            if debug_sim: #bruce 051115 revised this debug code
                # wware 060104  Create a shell script to re-run simulator
		outf = open("args", "w")
                # On the Mac, "-f" prevents running .bashrc
                # On Linux it disables filename wildcards (harmless)
                outf.write("#!/bin/sh -f\n")
                for a in arguments:
                    outf.write(str(a) + " \\\n")
                outf.write("\n")
                outf.close()
                def blabout():
                    print "stdout:", simProcess.readStdout()
                def blaberr():
                    print "stderr:", simProcess.readStderr()
                QObject.connect(simProcess, SIGNAL("readyReadStdout()"), blabout)
                QObject.connect(simProcess, SIGNAL("readyReadStderr()"), blaberr)
            simProcess.setArguments(arguments)
            if self._movie.watch_motion:
                env.history.message(orangemsg("(watch motion in realtime is only implemented for pyrex interface to simulator)"))
                # note: we have no plans to change that; instead, the pyrex interface will become the usual one
                # except for background or remote jobs. [bruce 060109]
            if not self._movie.create_movie_file:
                env.history.message(orangemsg("(option to not create movie file is not yet implemented)")) # for non-pyrex sim
                # NFR/bug 1286 not useful for non-pyrex sim, won't be implemented, this msg will be revised then
                # to say "not supported for command-line simulator"
            import time
            start = time.time() #bruce 060103 compute duration differently
            simProcess.start()
            # Launch the progress bar, and let it monitor and show progress and wait until
            # simulator is finished or user aborts it.
            self.monitor_progress_by_file_growth(movie) #bruce 060103 made this no longer help us compute duration
            duration = time.time() - start
            movie.duration = duration #bruce 060103 (more detailed comment in other place this occurs)

        except: # We had an exception.
            print_compact_traceback("exception in simulation; continuing: ")
            if simProcess:
                #simProcess.tryTerminate()
                simProcess.kill()
                simProcess = None
            self.errcode = -1 # simulator failure

        # now sim is done (or abort was pressed and it has not yet been killed)
        # and self.errcode is error code or (for a specific hardcoded value)
        # says abort was pressed.
        # what all cases have in common is that user wants us to stop now
        # (so we might or might not already be stopped, but we will be soon)
        # and self.errcode says what's going on.

        # [bruce 050407:]
        # For now:
        # Since we're not always stopped yet, we won't scan the tracefile
        # for error messages here... let the caller do that.
        # Later:
        # Do it continuously as we monitor progress (in fact, that will be
        # *how* we monitor progress, rather than watching the filesize grow).
        
        return

    def remove_old_moviefile(self, moviefile): #bruce 051230 split this out of spawn_process
        "remove the moviefile if it exists, after warning existing Movie objects that we'll do so; can raise exceptions"
        if os.path.exists(moviefile):
            #bruce 050428: do something about this being the moviefile for an existing open movie.
            try:
                ## print "calling apply2movies",moviefile
                self.assy.apply2movies( lambda movie: movie.fyi_reusing_your_moviefile( moviefile) )
                # note that this is only correct if we're sure it won't be called for the new Movie
                # we're making right now! For now, this is true. Later we might need to add an "except for this movie" arg.
            except:
                #e in future they might tell us to lay off this way... for now it's a bug, but we'll ignore it.
                print_compact_traceback("exception in preparing to reuse moviefile for new movie ignored: ")
                pass
            #bruce 050407 moving this into the try, since it can fail if we lack write permission
            # (and it's a good idea to give up then, so we're not fooled by an old file)
            if debug_sim:
                print "deleting moviefile: [",moviefile,"]"
            os.remove (moviefile) # Delete before spawning simulator.
        return        
        #bruce 051231: here is an old comment related to remove_old_moviefile;
        # I don't know whether it's obsolete regarding the bug it warns about:
        # delete old moviefile we're about to write on, and warn anything that might have it open
        # (only implemented for the same movie obj, THIS IS A BUG and might be partly new... ####@@@@)
    
    def remove_old_tracefile(self, tracefile): #bruce 060101
        "remove the tracefile if it exists, after warning anything that might care [nim]; can raise exceptions"
        if os.path.exists(tracefile):
            os.remove(tracefile) # can raise exception, e.g. due to directory permission error
        return
    
    def monitor_progress_by_file_growth(self, movie): #bruce 051231 split this out of sim_loop_using_standalone_executable
        filesize, pbarCaption, pbarMsg = self.old_guess_filesize_and_progbartext( movie)
            # only side effect: history message [bruce 060103 comment]
        # pbarCaption and pbarMsg are not used any longer.  [mark 060105 comment]
        # (but they or similar might be used again soon, eg for cmdname in tooltip -- bruce 060112 comment)
        from StatusBar import show_progressbar_and_stop_button
        self.errcode = show_progressbar_and_stop_button(
                            self.win,
                            filesize,
                            filename = movie.filename,
                            cmdname = self.cmdname, #bruce 060112
                            show_duration = 1 )
            # that 'launch' method is misnamed, since it also waits for completion;
            # its only side effects [as of bruce 060103] are showing/updating/hiding progress dialog, abort button, etc.
        return
    
    def old_guess_filesize_and_progbartext(self, movie):
        "#doc [return a triple of useful values for a progressbar, and emit a related history msg]"
        #bruce 060103 added docstring
        #bruce 050401 now calling this after spawn not before? not sure... note it emits a history msg.
        # BTW this is totally unclean, all this info should be supplied by the subclass
        # or caller that knows what's going on, not guessed by this routine
        # and the filesize tracking is bogus for xyz files, etc etc, should be
        # tracking status msgs in trace file. ###@@@
        formarg = self._formarg # old-code kluge
        mflag = self.mflag
        natoms = len(movie.alist)
        moviefile = movie.filename
        # We cannot determine the exact final size of an XYZ trajectory file.
        # This formula is an estimate.  "filesize" must never be larger than the
        # actual final size of the XYZ file, or the progress bar will never hit 100%,
        # even though the simulator finished writing the file.
        # - Mark 050105
        #bruce 050407: apparently this works backwards from output file file format and minimizeQ (mflag)
        # to figure out how to guess the filesize, and the right captions and text for the progressbar.
        if formarg == "-x": #SIMOPT (used as internal flag, review if we change how this is passed to sim executable!)
            # Single shot minimize.
            if mflag: # Assuming mflag = 2. If mflag = 1, filesize could be wrong.  Shouldn't happen, tho.
                filesize = natoms * 16 # single-frame xyz filesize (estimate)
                pbarCaption = "Minimize" # might be changed below
                    #bruce 050415: this string used to be tested in ProgressBar.py, so it couldn't have "All" or "Selection".
                    # Now it can have them (as long as it starts with Minimize, for now) --
                    # so we change it below (to caption from caller), or use this value if caller didn't provide one.
                pbarMsg = "Minimizing..."
            # Write XYZ trajectory file.
            else:
                filesize = movie.totalFramesRequested * ((natoms * 28) + 25) # multi-frame xyz filesize (estimate)
                pbarCaption = "Save File" # might be changed below
                pbarMsg = "Saving XYZ trajectory file " + os.path.basename(moviefile) + "..."
        else: 
            # Multiframe minimize
            if mflag:
                filesize = (max(100, int(sqrt(natoms))) * natoms * 3) + 4
                pbarCaption = "Minimize" # might be changed below
                pbarMsg = None #bruce 050401 added this
            # Simulate
            else:
                filesize = (movie.totalFramesRequested * natoms * 3) + 4
                pbarCaption = "Simulator" # might be changed below
                pbarMsg = "Creating movie file " + os.path.basename(moviefile) + "..."
                msg = "Simulation started: Total Frames: " + str(movie.totalFramesRequested)\
                        + ", Steps per Frame: " + str(movie.stepsper)\
                        + ", Temperature: " + str(movie.temp)
                env.history.message(self.cmdname + ": " + msg)
        #bruce 050415: let caller specify caption via movie object's _cmdname
        # (might not be set, depending on caller) [needs cleanup].
        # For important details see same-dated comment above.
        try:
            caption_from_movie = movie._cmdname
        except AttributeError:
            caption_from_movie = None
        if caption_from_movie:
            pbarCaption = caption_from_movie
        return filesize, pbarCaption, pbarMsg

#bruce 060103 pared this old comment down to its perhaps-useful parts:
##        handle abort button (in progress bar or maybe elsewhere, maybe a command key)
##        (btw abort or sim-process-crash does not imply failure, since there might be
##         usable partial results, even for minimize with single-frame output);
##        process other user events (or some of them) (maybe);
##        and eventually return when the process is done,
##        whether by abort, crash, or success to end;
##        return True if there are any usable results,
##        and have a results object available in some public attribute.

    def sim_loop_using_dylib(self): #bruce 051231; compare to sim_loop_using_standalone_executable
        # 051231 6:29pm: works, except no trace file is written so results in history come from prior one (if any)
        """#doc
        """
        movie = self._movie
        if platform.atom_debug and movie.duration:
            print "atom_debug: possible bug: movie.duration was already set to", movie.duration
        movie.duration = 0.0 #k hopefully not needed
        # provide a reference frame for later movie-playing (for complete fix of bug 1297) [bruce 060112]
        movie.ref_frame = (self.__frame_number,  A(map(lambda a: a.sim_posn(), movie.alist))) # see similar code in class Movie
            #e this could be slow, and the simobj already knows it, but I don't think getFrame has access to it [bruce 060112]
        simopts = self._simopts
        simobj = self._simobj
        if not self.mflag:
            # wware 060310, bug 1294
            numframes = simopts.NumFrames
            self.win.status_pbar.reset()
            self.win.status_pbar.setTotalSteps(numframes)
            self.win.status_pbar.setProgress(0)
            self.win.status_pbar.show()
        from StatusBar import AbortButtonForOneTask
            #bruce 060106 try to let pyrex sim share some abort button code with non-pyrex sim
        self.abortbutton_controller = abortbutton = AbortButtonForOneTask(self.cmdname)
        abortbutton.start()
        
        try:
            self.remove_old_moviefile(movie.filename) # can raise exceptions #bruce 051230 split this out
            self.remove_old_tracefile(self.traceFileName)

            if not self._movie.create_movie_file:
                env.history.message(orangemsg("(option to not create movie file is not yet implemented)")) # for pyrex sim
                # NFR/bug 1286; other comments describe how to implement it; it would need a warning
                # (esp if both checkboxes unchecked, since no frame output in that case, tho maybe tracef warnings alone are useful)
            editwarning = "Warning: editing structure during sim causes tracebacks; cancelling an abort skips some realtime display time"
            if not seen_before(editwarning): #bruce 060317 added this condition
                env.history.message(orangemsg( editwarning ))
            env.call_qApp_processEvents() # so user can see that history message

            ###@@@ SIM CLEANUP desired: [bruce 060102]
            # (items 1 & 2 & 4 have been done)
            # 3. if callback caller in C has an exception from callback, it should not *keep* calling it, but reset it to NULL

            import time
            # wware 060309, bug 1343
            self.startTime = start = time.time()
            
            if not abortbutton.aborting():
                # checked here since above processEvents can take time, include other tasks

                # do these before entering the "try" clause
                # note: we need the frame callback even if not self._movie.watch_motion,
                # since it's when we check for user aborts and process all other user events.
                frame_callback = self.sim_frame_callback
                trace_callback = self.tracefile_callback
                
                simgo = simobj.go

                minflag = movie.minimize_flag
                    ###@@@ should we merge this logic with how we choose the simobj class? [bruce 060112]
                
                self.tracefileProcessor = TracefileProcessor(self, minimize = minflag)
                    # so self.tracefile_callback does something [bruce 060109]

                from sim import SimulatorInterrupted #bruce 060112 - not sure this will work here vs outside 'def' ###k
                try:
                    simgo( frame_callback = frame_callback, trace_callback = trace_callback )
                        # note: if this calls a callback which raises an exception, that exception gets
                        # propogated out of this call, with correct traceback info (working properly as of sometime on 060111).
                        # If a callback sets simobj.Interrupted (but doesn't raise an exception),
                        # this is turned into an exception like "sim.SimulatorInterrupted: simulator was interrupted".
                        # It also generates a tracefile line "# Warning: minimizer run was interrupted "
                        # (presumably before that exception gets back to here,
                        #  which means a tracefile callback would presumably see it if we set one --
                        #  but as of 060111 there's a bug in which that doesn't happen since all callbacks
                        #  are turned off by Interrupted).
                    if platform.atom_debug:
                        print "atom_debug: pyrex sim: returned normally" ###@@@ remove this sometime
                except SimulatorInterrupted:
                    self.pyrexSimInterrupted = True   # wware 060323 bug 1725
                    # This is the pyrex sim's new usual exit from a user abort, as of sometime 060111.
                    # Before that it was RuntimeError, but that could overlap with exceptions raised by Python callbacks
                    # (in fact, it briefly had a bug where all such exceptions turned into RuntimeErrors).
                    #
                    # I didn't yet fully clean up this code for the new exception. [bruce 060112] ######@@@@@@
                    if debug_sim_exceptions: #bruce 060111
                        print_compact_traceback("fyi: sim.go aborted with this: ")
                    # following code is wrong unless this was a user abort, but I'm too lazy to test for that from the exception text,
                    # better to wait until it's a new subclass of RuntimeError I can test for [bruce 060111]
                    env.history.statusbar_msg("Aborted")
                    if platform.atom_debug:
                        print "atom_debug: pyrex sim: aborted" ###@@@ remove this sometime
                    if self.PREPARE_TO_CLOSE:
                        # wware 060406 bug 1263 - exiting the program is an acceptable way to leave this loop
                        self.errcode = -1
                    elif not abortbutton.aborting():
                        print "error: abort without abortbutton doing it (did a subtask intervene and finish it?)"
                        print " (or this can happen due to sim bug in which callback exceptions turn into RuntimeErrors)"####@@@@
                        from StatusBar import ABORTING #bruce 060111 9:16am PST bugfix of unreported bug
                        abortbutton.status = ABORTING ###@@@ kluge, should clean up, or at least use a method and store an error string too
                        assert abortbutton.aborting()
                    ## bug: this fails to cause an abort to be reported by history. might relate to bug 1303.
                    # or might only occur due to current bugs in the pyrex sim, since I think user abort used to work. [bruce 060111]
                    # Initial attempt to fix that -- need to improve errcode after reviewing them all
                    # (check for errorcode spelling error too? or rename it?) #######@@@@@@@
                    if not self.errcode:
                        print "self.errcode was not set, using -1"
                        self.errcode = -1 # simulator failure [wrong errorcode for user abort, fix this]
                    pass
                pass
            if 1: # even if aborting
                duration = time.time() - start
                #e capture and print its stdout and stderr [not yet possible via pyrex interface]
                movie.duration = duration #bruce 060103
            
        except: # We had an exception.
            print_compact_traceback("exception in simulation; continuing: ")
            ##e terminate it, if it might be in a different thread; destroy object; etc
            # show the exception message in the history window - wware 060314
            type, value, traceback = sys.exc_info()
            msg = redmsg("%s: %s" % (type, value))
            env.history.message(msg)
            self.errcode = _FAILURE_ALREADY_DOCUMENTED
            abortbutton.finish() # whether or not there was an exception and/or it aborted
            return

        if not self.mflag:
            # wware 060310, bug 1294
            self.win.status_pbar.setProgress(numframes)
            self.win.status_pbar.reset()
            self.win.status_pbar.hide()
        env.history.progress_msg("") # clear out elapsed time messages
        env.history.statusbar_msg("Done.") # clear out transient statusbar messages

        abortbutton.finish() # whether or not there was an exception and/or it aborted
        return

    __callback_time = -1 ###e we could easily optim our test by storing this plus __sim_work_time
    __frame_number = 0 # starts at 0 so incrementing it labels first frame as 1 (since initial frame is not returned)
        #k ought to verify that in sim code -- seems correct, looking at coords and total number of frames
        # note: we never need to reset __frame_number since this is a single-use object.
        # could this relate to bug 1297? [bruce 060110] (apparently not [bruce 060111])
    __sim_work_time = 0.05 # initial value -- we'll run sim_frame_callback_worker 20 times per second, with this value
    def sim_frame_callback(self): #bruce 060102
        "Per-frame callback function for simulator object."
        # some of these prints I commented out need to show up as fields in the progress bar instead...
        ## print "f",
        # This happened 3550 times for minimizing a small C3 sp3 hydrocarbon... better check the time first.
        #e Maybe we should make this into a lambda, or even code it in C, to optimize it. First make it work.
        from sim import SimulatorInterrupted
        if self.PREPARE_TO_CLOSE:
            # wware 060406 bug 1263 - if exiting the program, interrupt the simulator
            raise SimulatorInterrupted
        import time
        now = time.time() # should we use real time like this, or cpu time like .clock()??
        self.__frame_number += 1
        if debug_all_frames:
            from sim import getFrame
            if debug_sim_exceptions:
                # intentially buggy code
                print "frame %d" % self.__frame_number, self._simobj.getFrame() # this is a bug, that attr should not exist
            else:
                # correct code
                print "frame %d" % self.__frame_number, getFrame()[debug_all_frames_atom_index]
            pass
        ###e how to improve timing:
        # let sim use up most of the real time used, measuring redraw timing in order to let that happen. see below for more.
        # always show the last frame - wware 060314
        if debug_all_frames or self.__frame_number == self.totalFramesRequested or \
               now > self.__callback_time + self.__sim_work_time: # this probably needs coding in C or further optim
            simtime = now - self.__callback_time # for sbar
            if debug_pyrex_prints:
                print "sim hit frame %d in" % self.__frame_number, simtime
                    #e maybe let frame number be an arg from C to the callback in the future?
            self.__callback_time = now
            # Note that we don't only store this time, but the time *after* we do our other work here, in case redraw takes long.
            # i.e. we always let sim run for 0.05 sec even if our python loop body took longer.
            # maybe best to let sim run even longer, i.e. max(0.05, python loop body time), but no more than say 1 or 2 sec.
            ####@@@@ where i am - fill in loop body, right here. don't worry about progbar for now, or abort -- just movie.
            try:
                self.sim_frame_callback_worker( self.__frame_number) # might call self.abort_sim_run()
            except:
                print_compact_traceback("exception in sim_frame_callback_worker, aborting run: ")
                self.abort_sim_run("exception in sim_frame_callback_worker(%d)" % self.__frame_number ) # sets flag inside sim object
            self.__callback_time = time.time() # in case later than 'now' set earlier
            # use this difference to adjust 0.05 above, for the upcoming period of sim work;
            # note, in current code this also affects abortability
            pytime = self.__callback_time - now
            if debug_pyrex_prints:
                print "python stuff took", pytime
                # python stuff took 0.00386619567871 -- for when no real work done, just overhead; small real egs more like 0.03
            self.__sim_work_time = max(0.05, min(pytime * 4, 2.0))
            if debug_pyrex_prints:
                print "set self.__sim_work_time to", self.__sim_work_time
            # set status bar
            if debug_timing_loop_on_sbar:
                # debug: show timing loop properties
                msg = "sim took %0.3f, hit frame %03d, py took %0.3f, next simtime %0.3f" % \
                      (simtime, self.__frame_number, pytime, self.__sim_work_time)
                env.history.statusbar_msg(msg)
            else:
                # wware 060309, bug 1343
                msg = ""
                tp = self.tracefileProcessor
                if tp:
                    msg = tp.progress_text()
                if msg:
                    env.history.statusbar_msg(self.cmdname + ": " + msg)
        # wware 060310, bug 1343
        from platform import hhmmss_str
        msg = "Elapsed Time: " + hhmmss_str(int(time.time() - self.startTime))
        env.history.progress_msg(msg)
        if not self.mflag:
            # wware 060310, bug 1294
            self.win.status_pbar.setProgress(self.__frame_number)
        return

    def sim_frame_callback_worker(self, frame_number): #bruce 060102
        """Do whatever should be done on frame_callbacks that don't return immediately
           (due to not enough time passing).
           Might raise exceptions -- caller should protect itself from them until the sim does.
           + stuff new frame data into atom positions
             +? fix singlet positions, if not too slow
           + gl_update
           - update progress bar
           - tell Qt to process events
           - see if user aborted, if so, set flag in simulator object so it will 
             abort too 
           (but for now, separate code will also terminate the sim run in the usual way, 
            reading redundantly from xyz file)
        """
        from prefs_constants import watchRealtimeMinimization_prefs_key
        if 1: ### if not self.pyrex_sim_aborting(): ######@@@@@@ needs to be a method of a separated task-loop, like abortbutton itself has
            if self.abortbutton_controller.aborting():
                # extra space to distinguish which line got it -- this one is probably rarer, mainly gets it if nested task aborted(??)
                self.abort_sim_run("got real  abort at frame %d" % frame_number)######@@@@@@ also set self-aborting flag to be used above
            # mflag=1 -> minimize, user preference determines whether we watch it in realtime
            # mflag=0 -> dynamics, watch_motion (from movie setup dialog) determines realtime
            elif ((not self.mflag and self._movie.watch_motion) or
                  (self.mflag and env.prefs[watchRealtimeMinimization_prefs_key])):
                from sim import getFrame
                frame = getFrame()
                # stick the atom posns in, and adjust the singlet posns
                newPositions = frame
                movie = self._movie
                #bruce 060102 note: following code is approximately duplicated somewhere else in this file.
                try:
                    movie.moveAtoms(newPositions)
                except ValueError: #bruce 060108
                    # wrong number of atoms in newPositions (only catches a subset of possible model-editing-induced errors)
                    self.abort_sim_run("can't apply frame %d, model has changed" % frame_number)
                else:
                    if 1: #bruce 060108 part of fixing bug 1273
                        movie.realtime_played_framenumber = frame_number
                        movie.currentFrame = frame_number
                    self.part.changed() #[bruce 060108 comment: moveAtoms should do this ###@@@]
                    self.part.gl_update()
                # end of approx dup code

            #e update progress bar ####@@@@ later
            # tell Qt to process events (for progress bar, its abort button, user moving the dialog or window, changing display mode,
            #  and for gl_update)
            env.call_qApp_processEvents() 
            #e see if user aborted
            if self.abortbutton_controller.aborting():
                self.abort_sim_run("got real abort at frame %d" % frame_number)
                    ######@@@@@@ also set self-aborting flag to be used above
            # that's it!
        return

    def tracefile_callback(self, line): #bruce 060109, revised 060112; needs to be fast; should optim by passing step method to .go
        tp = self.tracefileProcessor
        if tp:
            tp.step(line)

    def abort_sim_run(self, why = "(reason not specified by internal code)" ): #bruce 060102
        "#doc"
        self._simopts.Interrupted = True
        if not self.errcode:
            self.errcode = -1
            #######@@@@@@@ temporary kluge in case of bugs in RuntimeError from that or its handler;
            # also needed until we clean up our code to use the new sim.SimulatorInterrupt instead of RuntimeError [bruce 060111]
        env.history.message( redmsg( "aborting sim run: %s" % why )) ######@@@@@@@ only if we didn't do this already
            #####@@@@@ current code (kluge) might do it 2 times even if sim behaves perfectly and no nested tasks (not sure)
        return

    tracefileProcessor = None
    
    def print_sim_warnings(self): #bruce 050407; revised 060109, used whether or not we're not printing warnings continuously
        """Print warnings and errors from tracefile (if this was not already done);
        then print summary/finishing info related to tracefile.
        Note: this might change self.said_we_are_done to False or True, or leave it alone.
        """
        # Note: this method is sometimes called after errors, and that is usually a bug but might sometimes be good;
        # caller needs cleanup about this.
        # Meanwhile, possible bug -- not sure revisions of 060109 (or prior state) is fully safe when called after errors.
        if not self.tracefileProcessor:
            # we weren't printing tracefile warnings continuously -- print them now
            self.tracefileProcessor = TracefileProcessor(self)
                # this might change self.said_we_are_done and/or use self.traceFileName, now and/or later
            try:
                tfile = self.traceFileName
            except AttributeError:
                return # sim never ran (not always an error, I suspect)
            if not tfile:
                return # no trace file was generated using a name we provide
                       # (maybe the sim wrote one using a name it made up... nevermind that here)
            try:
                ff = open(tfile, "rU") # "U" probably not needed, but harmless
            except:
                #bruce 051230 fix probably-unreported bug when sim program is missing
                # (tho ideally we'd never get into this method in that case)
                print_compact_traceback("exception opening trace file %r: " % tfile)
                env.history.message( redmsg( "Error: simulator trace file not found at [%s]." % tfile ))
                self.tracefileProcessor.mentioned_sim_trace_file = True #k not sure if this is needed or has any effect
                return
            lines = ff.readlines()
            ## remove this in case those non-comment lines matter for the summary (unlikely, so add it back if too slow) [bruce 060112]
##            lines = filter( lambda line: line.startswith("#"), lines )
##                # not just an optimization, since TracefileProcessor tracks non-# lines for status info
            ff.close()
            for line in lines:
                self.tracefileProcessor.step(line)
        # print summary/done
        self.tracefileProcessor.finish()
        return

    pass # end of class SimRunner

# ==

print_sim_comments_to_history = False

'''
Date: 12 Jan 2006 20:57:05 -0000
From: ericm
To: bruce
Subject: Minimize trace file format

Here\'s the code that writes the trace file during minimize:

    write_traceline("%4d %20f %20f %s %s\n", frameNumber, rms, max_force, callLocation, message);

You can count on the first three not changing.

Note that with some debugging flags on you get extra lines of this
same form that have other info in the same places.  I think you can
just use the rms value for progress and it will do strange things if
you have that debugging flag on.  If you want to ignore those lines,
you can only use lines that have callLocation=="gradient", and that
should work well.

-eric
'''

class TracefileProcessor: #bruce 060109 split this out of SimRunner to support continuous tracefile line processing
    findRmsForce = re.compile("rms ([0-9.]+) pN")
    findHighForce = re.compile("high ([0-9.]+) pN")
    "Helper object to filter tracefile lines and print history messages as they come and at the end"
    def __init__(self, owner, minimize = False):
        "store owner so we can later set owner.said_we_are_done = True; also start"
        self.owner = owner
        self.minimize = minimize # whether to check for line syntax specific to Minimize
        self.__last_plain_line_words = None # or words returned from string.split(None, 4)
        self.start() # too easy for client code to forget to do this
    def start(self):
        "prepare to loop over lines"
        self.seen = {} # whether we saw each known error or warning tracefile-keyword
        self.donecount = 0 # how many Done keywords we saw in there
        self.mentioned_sim_trace_file = False # public, can be set by client code
    def step(self, line): #k should this also be called by __call__ ? no, that would slow down its use as a callback.
        """do whatever should be done immediately with this line, and save things to do later;
        this bound method might be used directly as a trace_callback [but isn't, for clarity, as of 060109]
        """
        if not line.startswith("#"):
            # this happens a lot, needs to be as fast as possible
            if self.minimize:
                # check for "gradient" seems required based on current syntax (and will usually be true)
                # (as documented in email from ericm today) (if too slow, deferring until line used is tolerable,
                #  but might result in some missed lines, at least if sim internal debug flags are used) [bruce 060112]
                words = line.split(None, 4) # split in at most 4 places
                if len(words) >= 4 and words[3] == 'gradient': # 4th word -- see also self.progress_text()
                    self.__last_plain_line_words = words
                elif platform.atom_debug:
                    print "atom_debug: weird tracef line:", line ####@@@@ remove this?
            return 
        if print_sim_comments_to_history: #e add checkbox or debug-pref for this??
            env.history.message("tracefile: " + line)
        # don't discard initial "#" or "# "
        for start in ["# Warning:", "# Error:", "# Done:"]:
            if line.startswith(start):
                if start != "# Done:":
                    self.owner.said_we_are_done = False # not needed if lines come in their usual order
                    if not self.seen:
                        env.history.message( "Messages from simulator trace file:") #e am I right to not say this just for Done:?
                        self.mentioned_sim_trace_file = True
                    if start == "# Warning:":
                        cline = orangemsg(line)
                    else:
                        cline = redmsg(line)
                    env.history.message( cline) # leave in the '#' I think
                    self.seen[start] = True
                else:
                    # "Done:" line - emitted iff it has a message on it; doesn't trigger mention of tracefile name
                    # if we see high forces, color the Done message orange, bug 1238, wware 060323
                    foundRms = self.findRmsForce.search(line)
                    if foundRms: foundRms = float(foundRms.group(1))
                    foundHigh = self.findHighForce.search(line)
                    if foundHigh: foundHigh = float(foundHigh.group(1))
                    highForces = ((foundRms != None and foundRms > 2.0) or
                                  (foundHigh != None and foundHigh > 2.0))
                    self.donecount += 1
                    text = line[len(start):].strip()
                    if text:
                        if "# Error:" in self.seen:
                            line = redmsg(line)
                        elif highForces or ("# Warning:" in self.seen):
                            line = orangemsg(line)
                        env.history.message( line) #k is this the right way to choose the color?
                        ## I don't like how it looks to leave out the main Done in this case [bruce 050415]:
                        ## self.owner.said_we_are_done = True # so we don't have to say it again [bruce 050415]
        return
    def progress_text(self): ####@@@@ call this instead of printing that time stuff
        "Return some brief text suitable for periodically displaying on statusbar to show progress"
        words = self.__last_plain_line_words
        if not words:
            return ""
        if len(words) == 4: #k needed?
            words = list(words) + [""]
        try:
            frameNumber, rms, max_force, callLocation, message = words
            assert callLocation == 'gradient'
        except:
            return "?"
        return "frame %s: rms force = %s; high force = %s" % (frameNumber, rms, max_force)
            # 'high' instead of 'max' is to match Done line syntax (by experiment as of 060112)
    def finish(self):
        if not self.donecount:
            self.owner.said_we_are_done = False # not needed unless other code has bugs
            # Note [bruce 050415]: this happens when user presses Abort,
            # since we don't abort the sim process gently enough. This should be fixed.
            #bruce 051230 changed following from redmsg to orangemsg
            env.history.message( orangemsg( "Warning: simulator trace file should normally end with \"# Done:\", but it doesn't."))
            self.mentioned_sim_trace_file = True
        if self.mentioned_sim_trace_file:
            # sim trace file was mentioned; user might wonder where it is...
            # but [bruce 050415] only say this if the location has changed since last time we said it,
            # and only include the general advice once per session.
            global last_sim_tracefile
            tfile = self.owner.traceFileName #bruce 060110 try to fix bug 1299
            if last_sim_tracefile != tfile:
                preach = (last_sim_tracefile is None)
                last_sim_tracefile = tfile
                msg = "(The simulator trace file was [%s]." % tfile
                if preach:
                    msg += " It might be overwritten the next time you run a similar command."
                msg += ")"
                env.history.message( msg)
        return
        
    pass # end of class TracefileProcessor

# this global needs to preserve its value when we reload!
try:
    last_sim_tracefile
except:
    last_sim_tracefile = None
else:
    pass

# ==

# writemovie used to be here, but is now split into methods of class SimRunner above [bruce 050401]

# ... here's a compat stub... i guess ###doit

#obs comment:
# Run the simulator and tell it to create a dpb or xyz trajectory file.
# [bruce 050324 moved this here from fileIO.py. It should be renamed to run_simulator,
#  since it does not always try to write a movie, but always tries to run the simulator.
#  In fact (and in spite of not always making a movie file),
#  maybe it should be a method of the Movie object,
#  which is used before the movie file is made to hold the params for making it.
#  (I'm not sure how much it's used when we'll make an .xyz file for Minimize.)
#  If it's not made a Movie method, then at least it should be revised
#  to accept the movie to use as an argument; and, perhaps, mainly called by a Movie method.
#  For now, I renamed assy.m -> assy.current_movie, and never grab it here at all
#  but let it be passed in instead.] ###@@@
def writemovie(part, movie, mflag = 0, simaspect = None, print_sim_warnings = False, cmdname = "Simulator"):
        #bruce 060106 added cmdname
    """Write an input file for the simulator, then run the simulator,
    in order to create a moviefile (.dpb file), or an .xyz file containing all
    frames(??), or an .xyz file containing what would have
    been the moviefile's final frame.  The name of the file it creates is found in
    movie.filename (it's made up here for mflag != 0, but must be inserted by caller
    for mflag == 0 ###k). The movie is created for the atoms in the movie's alist,
    or the movie will make a new alist from part if it doesn't have one yet
    (for Minimize Selection, it will probably already have one when this is called ###@@@).
    (This should be thought of as a Movie method even though it isn't one yet.)
    DPB = Differential Position Bytes (binary file)
    XYZ = XYZ trajectory file (text file)
    mflag: [note: mflag is called mtype in some of our callers!]
        0 = default, runs a full simulation using parameters stored in the movie object.
        1 = run the simulator with -m and -x flags, creating a single-frame XYZ file.
        2 = run the simulator with -m flags, creating a multi-frame DPB moviefile.
    Return value: false on success, true (actually an error code but no caller uses that)
    on failure (error message already emitted).
      Either way (success or not), also copy errors and warnings from tracefile to history,
    if print_sim_warnings = True. Someday this should happen in realtime;
    for now [as of 050407] it happens once when we're done.
    """
    #bruce 050325 Q: why are mflags 0 and 2 different, and how? this needs cleanup.

    simrun = SimRunner( part, mflag, simaspect = simaspect, cmdname = cmdname)
        #e in future mflag should choose subclass (or caller should)
    movie._simrun = simrun #bruce 050415 kluge... see also the related movie._cmdname kluge
    movie.currentFrame = 0 #bruce 060108 moved this here, was in some caller's success cases
    movie.realtime_played_framenumber = 0 #bruce 060108
    movie.minimize_flag = not not mflag # whether we're doing some form of Minimize [bruce 060112]
    simrun.run_using_old_movie_obj_to_hold_sim_params(movie)
    if 1:
        #bruce 060108 part of fixing bug 1273
        fn = movie.realtime_played_framenumber
        if fn:
            if not movie.minimize_flag: #bruce 060112
                #e a more accurate condition would be something like "if we made a movie file and bragged about it"
                env.history.message(greenmsg("(current atom positions correspond to movie frame %d)" % fn))
        assert movie.currentFrame == fn
    if print_sim_warnings and simrun.errcode != _FAILURE_ALREADY_DOCUMENTED:
        # If there was a clear error then don't print a lot of lower-priority less urgent stuff
        # after the bright red error message.
        try:
            simrun.print_sim_warnings()
                #bruce 051230 comment: this runs even if sim executable was not found; why?? #####@@@@@
                # guess: need to check error code from run_using_old_movie_obj_to_hold_sim_params;
                # that's done by checking simrun.errcode, but I wonder if for some values (like user aborted sim)
                # we should still print the warnings? So I'll refrain from not trying to print them on errcode, for now.
                # Instead I made it (print_sim_warnings) handle the error of not finding the trace file,
                # instead of raising an exception then.
        except:
            print_compact_traceback("bug in print_sim_warnings, ignored: ")
    return simrun.errcode

# ==

#bruce 050324 moved readxyz here from fileIO, added filename and alist args,
# removed assy arg (though soon we'll need it or a history arg),
# standardized indentation, revised docstring [again, 050404] and some comments.
#bruce 050404 reworded messages & revised their printed info,
# and changed error return to return the error message string
# (so caller can print it to history if desired).
# The original in fileIO was by Huaicai shortly after 050120.
#bruce 050406 further revisions (as commented).
def readxyz(filename, alist):
    """Read a single-frame XYZ file created by the simulator, typically for
    minimizing a part. Check file format, check element types against those
    in alist (the number of atoms and order of their elements must agree).
    [As of 050406, also permit H in the file to match a singlet in alist.]
       This test will probably fail unless the xyz file was created
    using the same atoms (in the same order) as in alist. If the atom set
    is the same (and the same session, or the same chunk in an mmp file,
    is involved), then the fact that we sort atoms by key when creating
    alists for writing sim-input mmp files might make this order likely to match.
       On error, print a message to stdout and also return it to the caller.
       On success, return a list of atom new positions
    in the same order as in the xyz file (hopefully the same order as in alist).
    """
    xyzFile = filename ## was assy.m.filename
    lines = open(xyzFile, "rU").readlines()
    
    if len(lines) < 3: ##Invalid file format
        msg = "readxyz: %s: File format error (fewer than 3 lines)." % xyzFile
        print msg
        return msg
    
    atomList = alist ## was assy.alist, with assy passed as an arg
        # bruce comment 050324: this list or its atoms are not modified in this function
    ## stores the new position for each atom in atomList
    newAtomsPos = [] 
    
    try:     
        numAtoms = int(lines[0]) # bruce comment 050324: numAtoms is not used
        rms = float(lines[1][4:]) # bruce comment 050324: rms is not used
    except ValueError:
        msg = "readxyz: %s: File format error in Line 1 and/or Line 2" % xyzFile
        print msg
        return msg
    
    atomIndex = 0
    for line in lines[2:]:
        words = line.split()
        if len(words) != 4:
            msg = "readxyz: %s: Line %d format error." % (xyzFile, lines.index(line) + 1)
                #bruce 050404 fixed order of printfields, added 1 to index
            print msg
            return msg
        try:        
            if words[0] != atomList[atomIndex].element.symbol:
                if words[0] == 'H' and atomList[atomIndex].element == Singlet:
                    #bruce 050406 permit this, to help fix bug 254 by writing H to sim for Singlets in memory
                    pass
                else:
                    msg = "readxyz: %s: atom %d (%s) has wrong element type." % (xyzFile, atomIndex+1, atomList[atomIndex])
                        #bruce 050404: atomIndex is not very useful, so I added 1
                        # (to make it agree with likely number in mmp file)
                        # and the atom name from the model.
                        ###@@@ need to fix this for H vs singlet (then do we revise posn here or in caller?? probably in caller)
                    print msg
                    return msg
            newAtomsPos += [map(float, words[1:])]
        except ValueError:
            msg = "readxyz: %s: atom %d (%s) position number format error." % (xyzFile, atomIndex+1, atomList[atomIndex])
                #bruce 050404: same revisions as above.
            print msg
            return msg
        except:
            #bruce 060108 added this case (untested) since it looks necessary to catch atomList[atomIndex] attributeerrors 
            msg = "readxyz: %s: error (perhaps fewer atoms in model than in xyz file)" % (xyzFile,)
            print msg
            return msg
        
        atomIndex += 1
    
    if (len(newAtomsPos) != len(atomList)): #bruce 050225 added some parameters to this error message
        msg = "readxyz: The number of atoms from %s (%d) is not matching with the current model (%d)." % \
              (xyzFile, len(newAtomsPos), len(atomList))
        print msg
        return msg #bruce 050404 added error return after the above print statement; not sure if its lack was new or old bug
    
    return newAtomsPos

# == user-visible commands for running the simulator, for simulate or minimize

from qt import QMimeSourceFactory

class CommandRun: # bruce 050324; mainly a stub for future use when we have a CLI
    """Class for single runs of commands.
    Commands themselves (as opposed to single runs of them)
    don't yet have objects to represent them in a first-class way,
    but can be coded and invoked as subclasses of CommandRun.
    """
    def __init__(self, win, *args):
        self.win = win
        self.args = args # often not needed; might affect type of command (e.g. for Minimize)
        self.assy = win.assy
        self.part = win.assy.part
            # current Part (when the command is invoked), on which most commands will operate
        self.glpane = win.assy.o #e or let it be accessed via part??
        return
    # end of class CommandRun

class simSetup_CommandRun(CommandRun):
    """Class for single runs of the simulator setup command; create it
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
            return
        
        env.history.message(self.cmdname + ": " + "Enter simulation parameters and select <b>Run Simulation.</b>")

        ###@@@ we could permit this in movie player mode if we'd now tell that mode to stop any movie it's now playing
        # iff it's the current mode.

        previous_movie = self.assy.current_movie # problem: hides it from apply2movies. [solved below] do we even still need this?
            # might be None; will be used only for default param values for new Movie
        ## bruce 050428 don't do this so it's not hidden from apply2movies and since i think it's no longer needed:
        ## self.assy.current_movie = None # (this is restored on error)

        # wware 060406 bug 1471 - check for sticky parameters from previous sim run
        if previous_movie is None and hasattr(self.assy, "stickyParams"):
            previous_movie = self.assy.stickyParams

        self.movie = None
        r = self.makeSimMovie( previous_movie) # will store self.movie as the one it made, or leave it as None if cancelled
        movie = self.movie
        self.assy.current_movie = movie or previous_movie # (this restores assy.current_movie if there was an error)

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
                from platform import hhmmss_str
                estr = hhmmss_str(duration)
                msg = "Total time to create movie file: " + estr + ", Seconds/frame = " + spf
                env.history.message(self.cmdname + ": " + msg) 
            msg = "Movie written to [" + movie.filename + "]."\
                        "To play movie, click on the <b>Movie Player</b> <img source=\"movieicon\"> icon " \
                        "and press Play on the Movie Mode dashboard." #bruce 050510 added note about Play button.
            # This makes a copy of the movie tool icon to put in the HistoryWidget.
            #e (Is there a way to make that act like a button, so clicking on it in history plays that movie?
            #   If so, make sure it plays the correct one even if new ones have been made since then!)
            QMimeSourceFactory.defaultFactory().setPixmap( "movieicon", 
                        self.win.simMoviePlayerAction.iconSet().pixmap() )
            env.history.message(self.cmdname + ": " + msg)
            self.win.simMoviePlayerAction.setEnabled(1) # Enable "Movie Player"
            self.win.simPlotToolAction.setEnabled(1) # Enable "Plot Tool"
            #bruce 050324 question: why are these enabled here and not in the subr or even if it's cancelled? bug? ####@@@@
        else:
            assert not movie
            # Don't allow uninformative messages to obscure informative ones - wware 060314
            if r == _FAILURE_ALREADY_DOCUMENTED:
                env.history.message(self.cmdname + ": " + "Cancelled.")
                # (happens for any error; more specific message (if any) printed earlier)
        return

    def makeSimMovie(self, previous_movie): ####@@@@ some of this should be a Movie method since it uses attrs of Movie...
        #bruce 050324 made this from the Part method makeSimMovie.
        # It's called only from self.run() above; not clear it should be a separate method,
        # or if it is, that it's split from the caller at the right boundary.
        suffix = self.part.movie_suffix()
        if suffix is None: #bruce 050316 temporary kluge
            msg = redmsg( "Simulator is not yet implemented for clipboard items.")
            env.history.message(self.cmdname + ": " + msg)
            return -1
        ###@@@ else use suffix below!
        
        self.simcntl = SimSetup(self.part, previous_movie, suffix) # Open SimSetup dialog [and run it until user dismisses it]
            # [bruce 050325: this now uses previous_movie for params and makes a new self.movie,
            #  never seeing or touching assy.current_movie]
        movie = self.simcntl.movie # always a Movie object, even if user cancelled the dialog
        
        if movie.cancelled:
            # user hit Cancel button in SimSetup Dialog. No history msg went out; caller will do that.
            movie.destroy()
            return -1
        r = writemovie(self.part, movie, print_sim_warnings = True, cmdname = self.cmdname) # not passing mtype means "run dynamic sim (not minimize), make movie"
            ###@@@ bruce 050324 comment: maybe should do following in that function too
        if not r: 
            # Movie file created. Initialize. ###@@@ bruce 050325 comment: following mods private attrs, needs cleanup.
            movie.IsValid = True # Movie is valid.###@@@ bruce 050325 Q: what exactly does this (or should this) mean?
                ###@@@ bruce 050404: need to make sure this is a new obj-- if not always and this is not init False, will cause bugs
            self.movie = movie # bruce 050324 added this
            # it's up to caller to store self.movie in self.assy.current_movie if it wants to.
        return r

    pass # end of class simSetup_CommandRun


MIN_ALL, LOCAL_MIN, MIN_SEL = range(3) # internal codes for minimize command subtypes (bruce 051129)
    # this is a kluge compared to using command-specific subclasses, but better than testing something else like cmdname
    
class Minimize_CommandRun(CommandRun):
    """Class for single runs of the Minimize Selection or Minimize All commands
    (which one is determined by an __init__ arg, stored in self.args by superclass);
    create it when the command is invoked, to prep to run the command once;
    then call self.run() to actually run it.
    [#e A future code cleanup might split this into a Minimize superclass
    and separate subclasses for 'All' vs 'Sel' -- or it might not.
    As of 050412 the official distinction is stored in entire_part.]
    """
    def run(self):
        """Minimize the Selection or the current Part"""
        #bruce 050324 made this method from the body of MWsemantics.modifyMinimize
        # and cleaned it up a bit in terms of how it finds the movie to use.
        
        #bruce 050412 added 'Sel' vs 'All' now that we have two different Minimize buttons.
        # In future the following code might become subclass-specific (and cleaner):
        
        ## fyi: this old code was incorrect, I guess since 'in' works by 'is' rather than '==' [not verified]:
        ## assert self.args in [['All'], ['Sel']], "%r" % (self.args,)

        #bruce 051129 revising this to clarify it, though command-specific subclasses would be better
        assert len(self.args) >= 1
        cmd_subclass_code = self.args[0]
        
        assert cmd_subclass_code in ['All','Sel','Atoms'] #e and len(args) matches that?
        
        entire_part = (cmd_subclass_code == 'All')
            # (a self attr for entire_part is not yet needed)
            #e someday, entire_part might also be set later if selection happens to include everything, to permit optims,
            # but only for internal use, not for messages to user distinguishing the two commands.
            # Probably that would be a bad idea. [bruce 051129 revised this comment]
        if cmd_subclass_code == 'All':
            cmdtype = MIN_ALL
            cmdname = "Minimize All"
        elif cmd_subclass_code == 'Atoms':
            #bruce 051129 added this case for Local Minimize (extending a kluge -- needs rewrite to use command-specific subclass)
            cmdtype = LOCAL_MIN
            cmdname = "Local Minimize"
            # self.args is parsed later
        else:
            assert cmd_subclass_code == 'Sel'
            cmdtype = MIN_SEL
            cmdname = "Minimize Selection"
        self.cmdname = cmdname #e in principle this should come from a subclass for the specific command [bruce 051129 comment]
        startmsg = cmdname + ": ..."
        del cmd_subclass_code

        # Make sure some chunks are in the part.
        # (Valid for all cmdtypes -- Minimize only moves atoms, even if affected by jigs.)
        if not self.part.molecules: # Nothing in the part to minimize.
            env.history.message(greenmsg(cmdname + ": ") + redmsg("Nothing to minimize."))
            return

        if cmdtype == MIN_SEL:
            selection = self.part.selection_from_glpane() # compact rep of the currently selected subset of the Part's stuff
            if not selection.nonempty():
                msg = greenmsg(cmdname + ": ") + redmsg("Nothing selected. (Use Minimize All to minimize entire Part.)")
                env.history.message( msg) #bruce 051129 changed this from redmsg( msg) to msg since msg already includes colors above
                return
        elif cmdtype == LOCAL_MIN:
            from ops_select import selection_from_atomlist
            junk, atomlist, ntimes_expand = self.args
            selection = selection_from_atomlist( self.part, atomlist) #e in cleaned up code, selection object might come from outside
            selection.expand_atomset(ntimes = ntimes_expand) # ok if ntimes == 0
        else:
            assert cmdtype == MIN_ALL
            selection = self.part.selection_for_all()
                # like .selection_from_glpane() but for all atoms presently in the part [bruce 050419]
            # no need to check emptiness, this was done above
        
        self.selection = selection #e might become a feature of all CommandRuns, at some point

        # At this point, the conditions are met to try to do the command.
        env.history.message(greenmsg( startmsg)) #bruce 050412 doing this earlier
        
        # Disable some QActions (menu items/toolbar buttons) during minimize.
        self.win.disable_QActions_for_sim(True)
        try:
            simaspect = sim_aspect( self.part, selection.atomslist(), cmdname_for_messages = cmdname ) #bruce 051129 passing cmdname
                # note: atomslist gets atoms from selected chunks, not only selected atoms
                # (i.e. it gets atoms whether you're in Select Atoms or Select Chunks mode)
            # history message about singlets written as H (if any);
            #bruce 051115 updated comment: this is used for both Minimize All and Minimize Selection as of long before 051115;
            # for Run Sim this code is not used (so this history message doesn't go out for it, though it ought to)
            # but the bug254 X->H fix is done (though different code sets the mapping flag that makes it happen).
            nsinglets_H = simaspect.nsinglets_H()
            if nsinglets_H: #bruce 051209 this message code is approximately duplicated elsewhere in this file
                info = fix_plurals( "(Treating %d bondpoint(s) as Hydrogens, during minimization)" % nsinglets_H )
                env.history.message( info)
            nsinglets_leftout = simaspect.nsinglets_leftout()
            assert nsinglets_leftout == 0 # for now
            # history message about how much we're working on; these atomcounts include singlets since they're written as H
            nmoving = simaspect.natoms_moving()
            nfixed  = simaspect.natoms_fixed()
            info = fix_plurals( "(Minimizing %d atom(s)" % nmoving)
            if nfixed:
                them_or_it = (nmoving == 1) and "it" or "them"
                info += fix_plurals(", holding %d atom(s) fixed around %s" % (nfixed, them_or_it) )
            info += ")"
            env.history.message( info) 
            self.doMinimize(mtype = 1, simaspect = simaspect) # 1 = single-frame XYZ file. [this also sticks results back into the part]
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
        """Minimize self.part (if simaspect is None -- no longer used)
        or its given simaspect (simulatable aspect) (used for both Minimize Selection and Minimize All),
        generating and showing a movie (no longer asked for) or generating and applying to part an xyz file.
           The mtype flag means:
            1 = tell writemovie() to create a single-frame XYZ file.
            2 = tell writemovie() to create a multi-frame DPB moviefile. [###@@@ not presently used, might not work anymore]
        """
        assert mtype == 1 #bruce 051115
        assert simaspect is not None #bruce 051115
        #bruce 050324 made this from the Part method makeMinMovie.
        suffix = self.part.movie_suffix()
        if suffix is None: #bruce 050316 temporary kluge; as of circa 050326 this is not used anymore
            env.history.message( redmsg( "Minimize is not yet implemented for clipboard items."))
            return
        #e use suffix below? maybe no need since it's ok if the same filename is reused for this.

        # bruce 050325 change: don't use or modify self.assy.current_movie,
        # since we're not making a movie and don't want to prevent replaying
        # the one already stored from some sim run.
        # [this is for mtype == 1 (always true now) and might affect writemovie ###@@@ #k.]

        # NOTE: the movie object is used to hold params and results from minimize, even if it makes an xyz file rather than a movie file.
        # And at the moment it never makes a movie file when called from this code. [bruce 051115 comment about months-old situation]
        
        movie = Movie(self.assy) # do this in writemovie? no, the other call of it needs it passed in from the dialog... #k
            # note that Movie class is misnamed since it's really a SimRunnerAndResultsUser... which might use .xyz or .dpb results
            # (maybe rename it SimRun? ###e also, it needs subclasses for the different kinds of sim runs and their results...
            #  or maybe it needs a subobject which has such subclasses -- not yet sure. [bruce 050329])

        self._movie = movie #bruce 050415 kluge; note that class SimRun does the same thing.
            # Probably it means that this class, SimRun, and this way of using Movie should all be the same,
            # or at least have more links than they do now. ###@@@

        # semi-obs comment, might still be useful [as of 050406]:
        # Minimize Selection [bruce 050330] (ought to be a distinct command subclass...)
        # this will use the spawning code in writemovie but has its own way of writing the mmp file.
        # to make this clean, we need to turn writemovie into more than one method of a class
        # with more than one subclass, so we can override one of them (writing mmp file)
        # and another one (finding atom list). But to get it working I might just kluge it
        # by passing it some specialized options... ###@@@ not sure

        movie._cmdname = self.cmdname #bruce 050415 kluge so writemovie knows proper progress bar caption to use
            # (not really wrong -- appropriate for only one of several
            # classes Movie should be split into, i.e. one for the way we're using it here, to know how to run the sim,
            # which is perhaps really self (a SimRunner), once the code is fully cleaned up.

        r = writemovie(self.part, movie, mtype, simaspect = simaspect, print_sim_warnings = True, cmdname = self.cmdname) # write input for sim, and run sim
            # this also sets movie.alist from simaspect
        if r:
            # We had a problem writing the minimize file.
            # Simply return (error message already emitted by writemovie). ###k
            return
        
        if mtype == 1:  # Load single-frame XYZ file.
            newPositions = readxyz( movie.filename, movie.alist ) # movie.alist is now created in writemovie [bruce 050325]
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
            # If _setup() returns a non-zero value, something went wrong loading the movie.
            if movie._setup(): return
            movie._play()
            movie._close()
        return
    pass # end of class Minimize_CommandRun

# ==

def LocalMinimize_function( atomlist, nlayers ): #bruce 051207
    win = atomlist[0].molecule.part.assy.w # kluge!
    #e should probably add in monovalent real atom neighbors -- but before finding neighbors layers, or after?
    # (note that local min will always include singlets... we're just telling it to also treat attached H the same way.
    #  that would suggest doing it after, as an option to Minimize. Hmm, should even Min Sel do it? Discuss.)
    cmdrun = Minimize_CommandRun( win, 'Atoms', atomlist, nlayers)
    cmdrun.run()
    return

# == helper code for Minimize Selection [by bruce, circa 050406] [also used for Minimize All, probably as of 050419, as guessed 051115]

from elements import Singlet

#obs comment:
###@@@ this will be a subclass of SimRun, like Movie will be... no, that's wrong.
# Movie will be subclass of SimResults, or maybe not since those need not be a class
# it's more like an UnderstoodFile and also an UndoableContionuousOperation...
# and it needn't mix with simruns not related to movies.
# So current_movie maybe split from last_simrun? might fix some bugs from aborted simruns...
# for prefs we want last_started_simrun, for movies we want last_opened_movie (only if valid? not sure)...

def atom_is_anchored(atm):
    "is an atm anchored in space, when simulated?"
    ###e refile as atom method?
    #e permit filtering set of specific jigs (instances) that can affect it?
    #e really a Part method??
    res = False
    for jig in atm.jigs:
        if jig.anchors_atom(atm): # as of 050321, true only for Anchor jigs
            res = True # but continue, so as to debug this new method anchors_atom for all jigs
    return res
    
class sim_aspect: # as of 051115 this is used for Min Sel and Min All but not Run Sim; verified by debug_sim output.
    # warning: it also assumes this internally -- see comment below about "min = True".
    """Class for a "simulatable aspect" of a Part.
    For now, there's only one kind (a subset of atoms, some fixed in position),
    so we won't split out an abstract class for now.
    Someday there would be other kinds, like when some chunks were treated
    as rigid bodies or jigs and the sim was not told about all their atoms.
    """
    def __init__(self, part, atoms, cmdname_for_messages = "Minimize" ): #bruce 051129 passing cmdname_for_messages
        """atoms is a list of atoms within the part (e.g. the selected ones,
        for Minimize Selection); we copy it in case caller modifies it later.
        [Note that this class has no selection object and does not look at
        (or change) the "currently selected" state of any atoms,
        though some of its comments are worded as if it did.]
           We become a simulatable aspect for simulating motion of those atoms
        (and of any singlets bonded to them, since user has no way to select
        those explicitly),
        starting from their current positions, with a "boundary layer" of other
        directly bonded atoms (if any) held fixed during the simulation.
        [As of 050408 this boundary will be changed from thickness 1 to thickness 2
         and its own singlets, if any, will also be grounded rather than moving.
         This is because we're approximating letting the entire rest of the Part
         be grounded, and the 2nd layer of atoms will constrain bond angles on the
         first layer, so leaving it out would be too different from what we're
         approximating.]
        (If any given atoms have Anchor jigs, those atoms are also treated as
        boundary atoms and their own bonds are only explored to an additional depth
        of 1 (in terms of bonds) to extend the boundary.
        So if the user explicitly selects a complete boundary of Anchored atoms,
        only their own directly bonded real atoms will be additionally grounded.)
           All atoms not in our list or its 2-thick boundary are ignored --
        so much that our atoms might move and overlap them in space.
           We look at jigs which attach to our atoms,
        but only if we know how to sim them -- we might not, if they also
        touch other atoms. For now, we only look at Anchor jigs (as mentioned
        above) since this initial implem is only for Minimize. When we have
        Simulate Selection, this will need revisiting. [Update: we also look at
        other jigs, now that we have Enable In Minimize for motors.]
           If we ever need to emit history messages
        (e.g. warnings) we'll do it using a global history variable (NIM)
        or via part.assy. For now [050406] none are emitted.
        """
        if debug_sim: #bruce 051115 added this
            print "making sim_aspect for %d atoms (maybe this only counts real atoms??)" % len(atoms) ###@@@ only counts real atoms??
        self.part = part
        self.cmdname_for_messages = cmdname_for_messages
        self.moving_atoms = {}
        self.boundary1_atoms = {}
        self.boundary2_atoms = {}
        assert atoms, "no atoms in sim_aspect"
        for atm in atoms:
            assert atm.molecule.part == part
            assert atm.element != Singlet # when singlets are selectable, this whole thing needs rethinking
            if atom_is_anchored(atm):
                self.boundary1_atoms[atm.key] = atm
            else:
                self.moving_atoms[atm.key] = atm
            # pretend that all singlets of selected atoms were also selected
            # (but were not grounded, even if atm was)
            for sing in atm.singNeighbors():
                self.moving_atoms[sing.key] = sing
        del atoms
        # now find the boundary1 of the moving_atoms
        for movatm in self.moving_atoms.values():
            for atm2 in movatm.realNeighbors():
                # (not covering singlets is just an optim, since they're already in moving_atoms)
                # (in fact, it's probably slower than excluding them here! I'll leave it in, for clarity.)
                if atm2.key not in self.moving_atoms:
                    self.boundary1_atoms[atm2.key] = atm2 # might already be there, that's ok
        # now find the boundary2 of the boundary1_atoms;
        # treat singlets of boundary1 as ordinary boundary2 atoms (unlike when we found boundary1);
        # no need to re-explore moving atoms since we already covered their real and singlet neighbors
        for b1atm in self.boundary1_atoms.values():
            for atm2 in b1atm.neighbors():
                if (atm2.key not in self.moving_atoms) and (atm2.key not in self.boundary1_atoms):
                    self.boundary2_atoms[atm2.key] = atm2 # might be added more than once, that's ok
        # no need to explore further -- not even for singlets on boundary2 atoms.

        # Finally, come up with a global atom order, and enough info to check our validity later if the Part changes.
        # We include all atoms (real and singlet, moving and boundary) in one list, sorted by atom key,
        # so later singlet<->H conversion by user wouldn't affect the order.
        items = self.moving_atoms.items() + self.boundary1_atoms.items() + self.boundary2_atoms.items()
        items.sort()
        self._atoms_list = [atom for key, atom in items]
            # make that a public attribute? nah, use an access method
        for i in range(1,len(self._atoms_list)):
            assert self._atoms_list[i-1] != self._atoms_list[i]
            # since it's sorted, that proves no atom or singlet appears twice
        # anchored_atoms alone (for making boundary jigs each time we write them out)
        items = self.boundary1_atoms.items() + self.boundary2_atoms.items()
        items.sort()
        self.anchored_atoms_list = [atom for key, atom in items]
        #e validity checking info is NIM, except for the atom lists themselves
        return
    def atomslist(self):
        return list(self._atoms_list)
    def natoms_moving(self):
        return len(self._atoms_list) - len(self.anchored_atoms_list)
    def natoms_fixed(self):
        return len(self.anchored_atoms_list)
    def nsinglets_H(self):
        "return number of singlets to be written as H for the sim"
        singlets = filter( lambda atm: atm.is_singlet(), self._atoms_list )
        return len(singlets)
    def nsinglets_leftout(self):
        "return number of singlets to be entirely left out of the sim input file"
        return 0 # for now
    def writemmpfile(self, filename):
        #bruce 050404 (for most details). Imitates some of Part.writemmpfile aka files_mmp.writemmpfile_part.
        #e refile into files_mmp so the mmp format code is in the same place? maybe just some of it.
        # in fact the mmp writing code for atoms and jigs is not in files_mmp anyway! tho the reading code is.
        """write our data into an mmp file; only include just enough info to run the sim
        [###e Should we make this work even if the atoms have moved but not restructured since we were made? I think yes.
         That means the validity hash is really made up now, not when we're made.]
        """
        ## do we need to do a part.assy.update_parts() as a precaution?? if so, have to do it earlier, not now.
        from files_mmp import writemmp_mapping
        assy = self.part.assy
        fp = open(filename, "w")
        mapping = writemmp_mapping(assy, min = True)
            #e rename min option? (for minimize; implies sim as well;
            #   affects mapping attrnames in chem.py atom.writemmp)
            #bruce 051031 comment: it seems wrong that this class assumes min = True (rather than being told this in __init__). ###@@@
        mapping.set_fp(fp)    
        # note that this mmp file doesn't need any grouping or chunking info at all.
        try:
            mapping.write_header() ###e header should differ in this case
            ## node.writemmp(mapping)
            self.write_atoms(mapping)
            self.write_grounds(mapping)
            self.write_minimize_enabled_jigs(mapping)
            mapping.write("end mmp file for %s (%s)\n" % (self.cmdname_for_messages, assy.name) ) #bruce 051129 revised this
                # sim & cad both ignore text after 'end'
                #bruce 051115: fixed this file comment, since this code is also used for Minimize All.
        except:
            mapping.close(error = True)
            raise
        else:
            mapping.close()
        return
    def write_atoms(self, mapping):
        assert mapping.sim
        for atm in self._atoms_list: # includes both real atoms and singlets, both moving and anchored, all sorted by key
            atm.writemmp( mapping) # mapping.sim means don't include any info not relevant to the sim
                # note: this method knows whether & how to write a Singlet as an H (repositioned)!
    def write_grounds(self, mapping):
        from jigs import fake_Anchor_mmp_record
        atoms = self.anchored_atoms_list
        nfixed = len(atoms)
        max_per_jig = 20
        for i in range(0, nfixed, max_per_jig): # starting indices of jigs for fixed atoms
            indices = range( i, min( i + max_per_jig, nfixed ) )
            if debug_sim:
                print "debug_sim: writing Anchor for these %d indices: %r" % (len(indices), indices)
            # now write a fake Anchor which has just the specified atoms
            these_atoms = [atoms[i] for i in indices]
            line = fake_Anchor_mmp_record( these_atoms, mapping) # includes \n at end
            mapping.write(line)
            if debug_sim:
                print "debug_sim: wrote %r" % (line,)           
        return
        
    def write_minimize_enabled_jigs(self, mapping): # Mark 051006
        '''Writes any jig to the mmp file which has the attr "enable_minimize"=True
        '''
        assert mapping.min #bruce 051031; detected by writemmp call, below; this scheme is a slight kluge
        
        from jigs import Jig
        def func_write_jigs(nn):
            if isinstance(nn, Jig) and nn.enable_minimize:
                #bruce 051031 comment: should we exclude the ones written by write_grounds?? doesn't matter for now. ####@@@@
                if debug_sim:
                    print "The jig [", nn.name, "] was written to minimize MMP file.  It is enabled for minimize."
                nn.writemmp(mapping)
            return # from func_write_jigs only
            
        self.part.topnode.apply2all( func_write_jigs)
        return
        
    pass # end of class sim_aspect

# end

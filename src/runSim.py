# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
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
'''

from debug import print_compact_traceback
import platform
import os, sys
from math import sqrt
from SimSetup import SimSetup
from qt import QApplication, QCursor, Qt, QStringList, QProcess
from movie import Movie
# more imports lower down

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
    
    def __init__(self, part, mflag):
        "set up external relations from the part we'll operate on; take mflag since someday it'll specify the subclass to use"
        self.assy = assy = part.assy # needed?
        self.tmpFilePath = assy.w.tmpFilePath
        self.history = assy.w.history
        self.win = assy.w  # might be used only for self.win.progressbar.launch
        self.part = part # needed?
        self.mflag = mflag # see docstring
        self.errcode = 0 # public attr used after we're done; 0 or None = success (so far), >0 = error (msg emitted) ###@@@DOIT
        return
    
    def run_using_old_movie_obj_to_hold_sim_params(self, movie, options, part_or_simaspect):
        self._movie = movie # general kluge for old-code compat (lots of our methods still use this and modify it)
        self.errcode = self.set_options_errQ( options) # options include everything that affects the run except the set of atoms and the part
        if self.errcode: # used to be a local var 'r'
            return
##        self.run_in_foreground = True # all we have for now [050401]
        self.sim_input_file = self.sim_input_filename() # might get name from options or make up a temporary filename
        self.set_waitcursor(True)
        try: #bruce 050325 added this try/except wrapper, to always restore cursor
            self.write_sim_input_file( part_or_simaspect )
                #e also save that arg? or do that in this subr if nec? or not?
                # maybe the next use of it (to interpret the result file) is in other code, not this class.
            self.spawn_process() ##also includes monitor_progress, for now; result error code (or abort button flag) in self.errcode
##            if self.run_in_foreground:
##                self.monitor_progress() # and wait for it to be done or for abort to be requested and done
        except:
            print_compact_traceback("bug in simulator-calling code: ")
            self.errcode = -11111
        self.set_waitcursor(False)
        if not self.errcode:
            return # success
        history = self.history
        if self.errcode == 1: # User pressed Abort button in progress dialog.
            msg = redmsg("Simulator: Aborted.")
            history.message(msg)         
            
            ##Tries to terminate the process the nice way first, so the process
            ## can do whatever clean up it requires. If the process
            ## is still running after 2 seconds (a kludge). it terminates the 
            ## process the hard way.
            #self.simProcess.tryTerminate()
            #QTimer.singleShot( 2000, self.simProcess, SLOT('kill()') )
            
            # The above does not work, so we'll hammer the process with SIGKILL.
            # This works.  Mark 050210
            assert self.simProcess
            self.simProcess.kill()
            
        else: # Something failed...
            msg = redmsg("Simulation failed: exit code or internal error code %r " % self.errcode) #e identify error better!
            history.message(msg)
        return # caller should look at self.errcode
        # semi-obs comment? [by bruce few days before 050404, partly expresses an intention]
        # results themselves are a separate object (or more than one?) stored in attrs... (I guess ###k)
        # ... at this point the caller probably extracts the results object and uses it separately
        # or might even construct it anew from the filename and params
        # depending on how useful the real obj was while we were monitoring the progress
        # (since if so we already have it... in future we'll even start playing movies as their data comes in...)
        # so not much to do here! let caller care about res, not us.
    
    def set_options_errQ(self, options): #e maybe split further into several setup methods?
        """Caller should specify the options for this simulator run
        (including the output file name);
        these might affect the input file we write for it
        and/or the arguments given to the simulator executable.
        Temporary old-code compatibility: use self._movie
        for simsetup params and other needed params, and store new ones into it.
        """
        part = self.part
        movie = self._movie

        # set up alist (list of atoms for sim input and output files, in order)
        movie.alist_fits_entire_part = False # might be changed below
        if not movie.alist:
            # we don't yet know what atoms to minimize. Use the ones in part.
            # in future this might be different or always be done by caller...
            # Make sure some chunks are in the part.
            if not part.molecules: # Nothing in the part to minimize.
                msg = redmsg("Can't create movie.  No chunks in part.")
                    #####@@@@@ is this redundant with callers? yes for simSetup,
                    # don't know about minimize, or the weird fileSave call in MWsem.
                self.history.message(msg)
                return -1
            movie.set_alist_from_entire_part(part) ###@@@ needs improvement, see comments in it
            for atm in movie.alist:
                assert atm.molecule.part == part ###@@@ remove when works
            movie.alist_fits_entire_part = True # permits optims... but note it won't be valid
                # anymore if the part changes! it's temporary... not sure it deserves to be an attr
                # rather than local var or retval.
        else:
            # movie already knows what to minimize...
            # assert they're all in this Part.
            assert 0 # [might happen with mimimize selection, but doesn't yet happen - bruce 050325]
                # if this assert fails it might mean we reused this movie obj w/o meaning to...
                # should check that some other way even after this case can happen legit...
            for atm in movie.alist:
                assert atm.molecule.part == part

        # set up filenames
        # We use the PID (process id) to create unique filenames for this instance of the program,
        # so that if the user runs more than one program at the same time, they don't use
        # the same temporary file names.
        # [We don't yet make this include a Part-specific suffix [bruce 050325]]
        # [This will need revision when we can run more than one sim process
        #  at once, with all or all but one in the "background" [bruce 050401]]
        pid = os.getpid()
        self.tmp_file_prefix = os.path.join(self.tmpFilePath, "sim-%d" % pid)
            # we'll append various suffix.extensions to this, to make temp file names
            # for sim input and output files as needed
        r = self.old_set_sim_output_filenames_errQ( movie, self.mflag)
        if r: return r
        # don't call sim_input_filename here, that's done later for some reason

        # prepare to spawn the process later (and detect some errors now)
        # filePath = the current directory NE-1 is running from.
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        # "program" is the full path to the simulator executable. 
        if sys.platform == 'win32': 
            program = os.path.normpath(filePath + '/../bin/simulator.exe')
        else:
            program = os.path.normpath(filePath + '/../bin/simulator')
        # Make sure the simulator exists
        if not os.path.exists(program):
            msg = redmsg("The simulator program [" + program + "] is missing.  Simulation aborted.")
            self.history.message(msg)
            return -1
        self.program = program
        
        return None # no error
    
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
            self.history.message(msg)
            return -1
            
        # Check that the moviefile has a valid extension.
        ext = moviefile[-4:]
        if ext not in ['.dpb', '.xyz']:
            # Don't recognize the moviefile extension.
            msg = redmsg("Movie [" + moviefile + "] has unsupported extension.")
            self.history.message(msg)
            print "writeMovie: " + msg
            return -1
        movie.filetype = ext #bruce 050404 added this

        # Figure out tracefile name, come up with sim-command argument for it,
        # store that in self.traceFile [###e clean that up! split filename and cmd-option, rename this attr to self.traceFileOption...]
        
        # The trace file saves the simulation parameters and the output data for jigs.
        # Mark 2005-03-08
        if mflag: 
            # We currently don't need to write a tracefile when minimizing the part (mflag != 0).
            # [bruce comment 050324: but soon we will, to know better when the xyz file is finished or given up on. ###@@@]
            self.traceFile = ""
        else:
            # The trace filename will be the same as the movie filename, but with "-trace.txt" tacked on.
            self.traceFile = "-q" + movie.get_trace_filename() # presumably uses movie.filename we just stored
                # (I guess this needn't know self.tmp_file_prefix except perhaps via movie.filename [bruce 050401])
                
        # This was the old tracefile - obsolete as of 2005-03-08 - Mark
        ## traceFile = "-q"+ os.path.join(self.tmpFilePath, "sim-%d-trace.txt" % pid)

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
    
    def write_sim_input_file(self, part_or_simaspect):
        """Write the appropriate data from part_or_simaspect
        to an input file for the simulator (presently always in mmp format)
        using the filename self.sim_input_file
        (overwriting any existing file of the same name).
        """
        part = part_or_simaspect # only Parts are supported for now
        mmpfile = self.sim_input_file # the filename to write to
        movie = self._movie # old-code compat kluge
        
        # Tell user we're creating the movie file...
    #    msg = "Creating movie file [" + moviefile + "]"
    #    history.message(msg)

        if movie.alist_fits_entire_part:
            part.writemmpfile( mmpfile)
        else:
            assert 0 # can't yet happen (until minimize selection) and won't yet work 
            # bruce 050325 revised this to use whatever alist was asked for above (set of atoms, and order).
            # But beware, this might only be ok right away for minimize, not simulate (since for sim it has to write all jigs as well).
            write_mmpfile_for_sim( movie.alist, mmpfile) ###e new func below? won't yet work for clips with jigs, i think...

##        # READ THIS IF YOU PLAN TO CHANGE ANY CODE FOR writemovie()!
##        # writemmp must come before computing "natoms".  This ensures that writemovie
##        # will work when creating a movie for a file without an assy.alist.  Examples of this
##        # situation include:
##        # 1)  The part is a PDB file.
##        # 2) We have chunks, but no assy.alist.  This happens when the user opens a 
##        #      new part, creates something and simulates before saving as an MMP file.
##        # 
##        # I do not know if it was intentional, but assy.alist is not created until an mmp file 
##        # is created.  We are simply taking advantage of this "feature" here.
##        # - Mark 050106
##
##    ##    writemmp(assy, mmpfile, False) ###@@@ this should be the Part in this function, not assy -- will be changed.

        movie.natoms = natoms = len(movie.alist)
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
    
    def spawn_process(self): # also includes monitor_progress, for now
        """Actually spawn the process, making its args based on the given options
        (and/or on other options we've specified earlier to this class?)
        and with other args telling it to use the previously written input files.
        ###retval? or record some info?
        ### do we wait? no, we want to watch the files grow -- caller does that separately.
        """
        # figure out process arguments
        # [bruce 050401 doing this later than before, used to come before writing sim-input file]
        
        movie = self._movie # old-code compat kluge
        moviefile = movie.filename
        outfile = "-o%s" % moviefile
        infile = self.sim_input_file
        program = self.program
        traceFile = self.traceFile #e rename, revise

        ext = movie.filetype #bruce 050404 added movie.filetype
        mflag = self.mflag
        
        # "formarg" = File format argument
        if ext == ".dpb": formarg = ''
        elif ext == ".xyz": formarg = "-x"
        else: assert 0
        
        # "args" = arguments for the simulator.
        if mflag: 
            args = [program, '-m', str(formarg), traceFile, outfile, infile]
        else: 
            # THE TIMESTEP ARGUMENT IS MISSING ON PURPOSE.
            # The timestep argument "-s + (movie.timestep)" is not supported for Alpha.
            args = [program, 
                        '-f' + str(movie.totalFramesRequested),
                        '-t' + str(movie.temp), 
                        '-i' + str(movie.stepsper), 
                        '-r',
                        str(formarg),
                        traceFile,
                        outfile,
                        infile]
        self._args = args # needed??
        self._formarg = formarg # old-code kluge

        # delete old moviefile we're about to write on, and warn anything that might have it open
        # (only implemented for the same movie obj, THIS IS A BUG and might be partly new... ####@@@@)

        # We can't overwrite an existing moviefile, so delete it if it exists.
        if os.path.exists(moviefile):
            # [bruce 050401 comment:]
            # and make sure the movie obj is not still trying to use the file, first!
            # this is an old-code kluge... but necessary. In future we probably need
            # to inform *all* our current sims and movies that we're doing this
            # (deleting or renaming some file they might care about). ###@@@
            # BTW this stuff should be a method of movie, it uses private attrs...
            # and it might not be correct/safe in all cases either... [not reviewed]
            print "movie.isOpen =",movie.isOpen
            if movie.isOpen: 
                print "closing moviefile"
                movie.fileobj.close()
                movie.isOpen = False
                print "writemovie(): movie.isOpen =", movie.isOpen
            
            print "deleting moviefile: [",moviefile,"]"
            os.remove (moviefile) # Delete before spawning simulator.

        # These are useful when debugging the simulator.     
        print  "program = ",program
        print  "Spawnv args are %r" % (args,) # this %r remains (see above)

        arguments = QStringList()
        for arg in args:
            arguments.append(arg)
        
        #bruce 050404 let simProcess be instvar so external code can abort it
        self.simProcess = None
        try:
            ## Start the simulator in a different process 
            self.simProcess = QProcess()
            simProcess = self.simProcess
            simProcess.setArguments(arguments)
            simProcess.start()
            
            # Launch the progress bar. Wait until simulator is finished
                        ####@@@@ move this part into separate method??
            filesize, pbarCaption, pbarMsg = self.old_guess_filesize_and_progbartext( movie)
                # also emits a history message...
            self.errcode = self.win.progressbar.launch( filesize,
                            moviefile, 
                            pbarCaption, 
                            pbarMsg, 
                            1)
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
        return

    def old_guess_filesize_and_progbartext(self, movie): # also emits history msg
        "..."
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
        if formarg == "-x":
            # Single shot minimize.
            if mflag: # Assuming mflag = 2. If mflag = 1, filesize could be wrong.  Shouldn't happen, tho.
                filesize = natoms * 16 # single-frame xyz filesize (estimate)
                pbarCaption = "Minimize"
                pbarMsg = "Minimizing..."
            # Write XYZ trajectory file.
            else:
                filesize = movie.totalFramesRequested * ((natoms * 28) + 25) # multi-frame xyz filesize (estimate)
                pbarCaption = "Save File"
                pbarMsg = "Saving XYZ trajectory file " + os.path.basename(moviefile) + "..."
        else: 
            # Multiframe minimize
            if mflag:
                filesize = (max(100, int(sqrt(natoms))) * natoms * 3) + 4
                pbarCaption = "Minimize"
                pbarMsg = None #bruce 050401 added this
            # Simulate
            else:
                filesize = (movie.totalFramesRequested * natoms * 3) + 4
                pbarCaption = "Simulator"
                pbarMsg = "Creating movie file " + os.path.basename(moviefile) + "..."
                msg = "Simulation started: Total Frames: " + str(movie.totalFramesRequested)\
                        + ", Steps per Frame: " + str(movie.stepsper)\
                        + ", Temperature: " + str(movie.temp)
                self.history.message(msg)
        return filesize, pbarCaption, pbarMsg

    # seperate monitor routines not yet split out from spawn_process, not yet called ###@@@doit
    def monitor_progress(self): #e or monitor_some_progress, to be called in a loop with a sleep or show-frame, also by movie player?
        """Put up a progress bar (if suitable);
        watch the growing trace and trajectory files,
        displaying warnings and errors in history widget,
        progress-guess in progress bar,
        and perhaps in a realtime-playing movie in future;
        handle abort button (in progress bar or maybe elsewhere, maybe a command key)
        (btw abort or sim-process-crash does not imply failure, since there might be
         usable partial results, even for minimize with single-frame output);
        process other user events (or some of them) (maybe);
        and eventually return when the process is done,
        whether by abort, crash, or success to end;
        return True if there are any usable results,
        and have a results object available in some public attribute.
        """
        while not self.monitor_some_progress_doneQ(): # should store self.res I guess??
            time.sleep(0.1)
        return self.res
    def monitor_some_progress_doneQ(self):
        "..."
        pass
    pass # end of class SimRunner
    
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
def writemovie(part, movie, mflag = 0):
    """Write an input file for the simulator, then run the simulator,
    in order to create a moviefile (.dpb file), or an .xyz file containing all
    frames(??), or an .xyz file containing what would have
    been the moviefile's final frame.  The name of the file it creates is found in
    movie.filename (it's made up here for mflag != 0, but must be inserted by caller
    for mflag == 0 ###k). The movie is created for the atoms in the movie's alist,
    or the movie will make a new alist from part if it doesn't have one yet
    (for minimize selection, it will probably already have one when this is called ###@@@).
    (This should be thought of as a Movie method even though it isn't one yet.)
    DPB = Differential Position Bytes (binary file)
    XYZ = XYZ trajectory file (text file)
    mflag:
        0 = default, runs a full simulation using parameters stored in the movie object.
        1 = run the simulator with -m and -x flags, creating a single-frame XYZ file.
        2 = run the simulator with -m flags, creating a multi-frame DPB moviefile.
    Return value: false on success, true (actually an error code but no caller uses that)
    on failure (error message already emitted).
    """
    #bruce 050325 Q: why are mflags 0 and 2 different, and how? this needs cleanup.

    simrun = SimRunner( part, mflag) #e in future mflag should choose subclass (or caller should)
    options = "not used i think"
    simrun.run_using_old_movie_obj_to_hold_sim_params(movie, options, part)
        # messes needing cleanup: part passed twice, once might be simaspect; options useless now
    return simrun.errcode

# ==

#bruce 050324 moved readxyz here from fileIO, added filename and alist args,
# removed assy arg (though soon we'll need it or a history arg),
# standardized indentation, revised docstring and some comments.
# Didn't yet change prints to history messages, etc. ###@@@
# The original in fileIO was by Huaicai shortly after 050120.
def readxyz(filename, alist):
    """Read a single-frame XYZ file created by the simulator, typically for
    minimizing a part. Check file format, check element types against those
    in alist (the number and order of atoms must agree). Return a list of atom new positions
    in the same order as alist (assuming that's the order in the xyz file).
    """
    xyzFile = filename ## was assy.m.filename
    lines = open(xyzFile, "rU").readlines()
    
    if len(lines) < 3: ##Invalid file format
        print "%s: File format error." % xyzFile
        return
    
    atomList = alist ## was assy.alist, with assy passed as an arg
        # bruce comment 050324: this list or its atoms are not modified in this function
    ## stores the new position for each atom in atomList
    newAtomsPos = [] 
    
    try:     
        numAtoms = int(lines[0]) # bruce comment 050324: numAtoms is not used
        rms = float(lines[1][4:]) # bruce comment 050324: rms is not used
    except ValueError:
        print "%s: File format error in Line 1 and/or Line 2" % xyzFile
        return
    
    atomIndex = 0
    for line in lines[2:]:
        words = line.split()
        if len(words) != 4:
            print "%s: Line %d format error." % (lines.index(line), xyzFile)
            return
        try:        
            if words[0] != atomList[atomIndex].element.symbol:
                print "%s: atom %d is not matching." % (xyzFile, atomIndex)
                return
            
            newAtomsPos += [map(float, words[1:])]
        except ValueError:
            print "%s: atom %d position number format error." % (xyzFile, atomIndex)
            return
        
        atomIndex += 1
    
    if (len(newAtomsPos) != len(atomList)): #bruce 050225 added some parameters to this error message
        print "readxyz: The number of atoms from %s (%d) is not matching with the current model (%d)." % \
              (xyzFile, len(newAtomsPos), len(atomList))
    
    return newAtomsPos

# == user-visible commands for running the simulator, for simulate or minimize

from HistoryWidget import redmsg, greenmsg
from qt import QMimeSourceFactory

class CommandRun: # bruce 050324; mainly a stub for future use when we have a CLI
    """Class for single runs of commands.
    Commands themselves (as opposed to single runs of them)
    don't yet have objects to represent them in a first-class way,
    but can be coded and invoked as subclasses of CommandRun.
    """
    def __init__(self, win):
        self.win = win
        self.assy = win.assy
        self.part = win.assy.part
            # current Part (when the command is invoked), on which most commands will operate
        self.history = win.history # where this command can write history messages
        self.glpane = win.assy.o #e or let it be accessed via part??
        return
    # end of class CommandRun

class simSetup_CommandRun(CommandRun):
    """Class for single runs of the simulator setup command; create it
    when the command is invoked, to prep to run the command once;
    then call self.run() to actually run it.
    """
    def run(self):
        #bruce 050324 made this method from the body of MWsemantics.simSetup
        # and cleaned it up a bit in terms of how it finds the movie to use.
        if not self.part.molecules: # Nothing in the part to simulate.
            self.history.message(redmsg("Simulator: Nothing to simulate."))
            return
        
        self.history.message(greenmsg("Simulator:"))

        ###@@@ we could permit this in movie player mode if we'd now tell that mode to stop any movie it's now playing
        # iff it's the current mode.

        previous_movie = self.assy.current_movie
            # might be None; will be used only for default param values for new Movie
        self.assy.current_movie = None # (this is restored on error)

        self.movie = None
        r = self.makeSimMovie( previous_movie) # will store self.movie as the one it made, or leave it as None if cancelled
        movie = self.movie
        self.assy.current_movie = movie or previous_movie # (this restores assy.current_movie if there was an error)

        if not r: # Movie file saved successfully; movie is a newly made Movie object just for the new file
            assert movie
            # if duration took at least 10 seconds, print msg.
            self.progressbar = self.win.progressbar
            if self.progressbar.duration >= 10.0: 
                spf = "%.2f" % (self.progressbar.duration / movie.totalFramesRequested)
                    ###e bug in this if too few frames were written; should read and use totalFramesActual
                estr = self.progressbar.hhmmss_str(self.progressbar.duration)
                msg = "Total time to create movie file: " + estr + ", Seconds/frame = " + spf
                self.history.message(msg) 
            msg = "Movie written to [" + movie.filename + "]."\
                        "To play movie, click on the <b>Movie Player</b> <img source=\"movieicon\"> icon."
            # This makes a copy of the movie tool icon to put in the HistoryWidget.
            #e (Is there a way to make that act like a button, so clicking on it in history plays that movie?
            #   If so, make sure it plays the correct one even if new ones have been made since then!)
            QMimeSourceFactory.defaultFactory().setPixmap( "movieicon", 
                        self.win.toolsMoviePlayerAction.iconSet().pixmap() )
            self.history.message(msg)
            self.win.simMoviePlayerAction.setEnabled(1) # Enable "Movie Player"
            self.win.simPlotToolAction.setEnabled(1) # Enable "Plot Tool"
            #bruce 050324 question: why are these enabled here and not in the subr or even if it's cancelled? bug? ####@@@@
        else:
            assert not movie
            self.history.message("Cancelled.") # (happens for any error; more specific message (if any) printed earlier)
        return

    def makeSimMovie(self, previous_movie): #####@@@@@@ some of this should be a Movie method since it uses attrs of Movie...
        #bruce 050324 made this from the Part method makeSimMovie.
        # It's called only from self.run() above; not clear it should be a separate method,
        # or if it is, that it's split from the caller at the right boundary.
        suffix = self.part.movie_suffix()
        if suffix == None: #bruce 050316 temporary kluge
            self.history.message( redmsg( "Simulator is not yet implemented for clipboard items."))
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
        r = writemovie(self.part, movie) ###@@@ bruce 050324 comment: maybe should do following in that function too
        if not r: 
            # Movie file created. Initialize. ###@@@ bruce 050325 comment: following mods private attrs, needs cleanup.
            movie.IsValid = True # Movie is valid.###@@@ bruce 050325 Q: what exactly does this (or should this) mean?
                ###@@@ bruce 050404: need to make sure this is a new obj-- if not always and this is not init False, will cause bugs
            movie.currentFrame = 0
            self.movie = movie # bruce 050324 added this
            # it's up to caller to store self.movie in self.assy.current_movie if it wants to.
        return r

    pass # end of class simSetup_CommandRun


class Minimize_CommandRun(CommandRun):
    """Class for single runs of the Minimize command; create it
    when the command is invoked, to prep to run the command once;
    then call self.run() to actually run it.
    """
    def run(self):
        """Minimize the current Part""" #e in future this will only minimize the selection...
        #bruce 050324 made this method from the body of MWsemantics.modifyMinimize
        # and cleaned it up a bit in terms of how it finds the movie to use.

        # Make sure some chunks are in the part.
        if not self.part.molecules: # Nothing in the part to minimize.
            self.history.message(redmsg("Minimize: Nothing to minimize."))
            return
        
        # Disable Minimize, Simulator and Movie Player during the minimize function.
        self.win.modifyMinimizeAction.setEnabled(0) # Disable "Minimize"
        self.win.simSetupAction.setEnabled(0) # Disable "Simulator" 
        self.win.simMoviePlayerAction.setEnabled(0) # Disable "Movie Player"     
        try:
            self.history.message(greenmsg("Minimize..."))
            self.makeMinMovie(mtype = 1) # 1 = single-frame XYZ file. [this also sticks results back into the part]
            #self.makeMinMovie(mtype = 2) # 2 = multi-frame DPB file.
        finally:
            self.win.modifyMinimizeAction.setEnabled(1) # Enable "Minimize"
            self.win.simSetupAction.setEnabled(1) # Enable "Simulator"
            self.win.simMoviePlayerAction.setEnabled(1) # Enable "Movie Player"     
        self.history.message("Done")
        return
    def makeMinMovie(self, mtype = 1):
        """Minimize self.part and display the results.
        mtype:
            1 = tell writemovie() to create a single-frame XYZ file.
            2 = tell writemovie() to create a multi-frame DPB moviefile. [###@@@ not presently used, might not work anymore]
        """
        #bruce 050324 made this from the Part method makeMinMovie.
        suffix = self.part.movie_suffix()
        if suffix == None: #bruce 050316 temporary kluge; as of circa 050326 this is not used anymore
            self.w.history.message( redmsg( "Minimize is not yet implemented for clipboard items."))
            return
        #e use suffix below? maybe no need since it's ok if the same filename is reused for this.

        # bruce 050325 change: don't use or modify self.assy.current_movie,
        # since we're not making a movie and don't want to prevent replaying
        # the one already stored from some sim run.
        # [this is for mtype == 1 (always true now) and might affect writemovie ###@@@ #k.]
        
        movie = Movie(self.assy) # do this in writemovie? no, the other call of it needs it passed in from the dialog... #k
            # note that Movie class is misnamed since it's really a SimRunnerAndResultsUser... which might use .xyz or .dpb results
            # (maybe rename it SimRun? ###e also, it needs subclasses for the different kinds of sim runs and their results...
            #  or maybe it needs a subobject which has such subclasses -- not yet sure. [bruce 050329])

        ## if minsel: pass
            # minimize selection [bruce 050330] (ought to be a distinct command subclass...)
            # this will use the spawning code in writemovie but has its own way of writing the mmp file.
            # to make this clean, we need to turn writemovie into more than one method of a class
            # with more than one subclass, so we can override one of them (writing mmp file)
            # and another one (finding atom list). But to get it working I might just kluge it
            # by passing it some specialized options... ###@@@ not sure
            
        
        r = writemovie(self.part, movie, mtype) # write input for sim, and run sim
        if r:
            # We had a problem writing the minimize file.
            # Simply return (error message already emitted by writemovie). ###k
            return
        
        if mtype == 1:  # Load single-frame XYZ file.
            newPositions = readxyz( movie.filename, movie.alist ) # movie.alist is now created in writemovie [bruce 050325]
            if newPositions:
                movie.moveAtoms(newPositions)
                # bruce 050311 hand-merged mark's 1-line bugfix in assembly.py (rev 1.135):
                self.part.changed() # Mark - bugfix 386
                self.part.gl_update()
            else:
                pass #e print error message; or make readxyz do so ###@@@
        else: # Play multi-frame DPB movie file.
            ###@@@ bruce 050324 comment: can this still happen? [no] is it correct [probably not]
            # (what about changing mode to movieMode, does it ever do that?) [don't know]
            # I have not reviewed this and it's obviously not cleaned up (since it modifies private movie attrs).
            # But I will have this change the current movie, which would be correct in theory, i think, and might be needed
            # before trying to play it (or might be a side effect of playing it, this is not reviewed either).
            self.assy.current_movie = movie
            movie.currentFrame = 0
            # If _setup() returns a non-zero value, something went wrong loading the movie.
            if movie._setup(): return
            movie._play()
            movie._close()
        return
    pass # end of class Minimize_CommandRun

# ==

##write_mmpfile_for_sim( alist, filename): #bruce 050325 #####@@@@@ need this, not done, review calls and all code after calls...
##    """Write an MMP file specifically for the simulator,
##    containing only the atoms in alist
##    (which should all be in the same Part, but this might not be checked),
##    and containing only the jigs which attach to those atoms
##    (which must each be splittable if they also attach to other atoms).
##       For now [050325], this might not be fully implemented,
##    so we might fall back to writing the full assy (only ok for the MainPart)
##    or emit a redmsg saying we can't do this for this Part,
##    and then raise an exception (since we have no retval).
##    """
##    part = alist[0].molecule.part
##    part.write_mmpfile_for_sim( alist, filename) # works differently in diff part classes, perhaps (more reliable in main part?)
##    return

# end


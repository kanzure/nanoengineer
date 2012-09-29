# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
runSim.py -- setting up and running the simulator, for Simulate or Minimize
(i.e. the same code that would change if the simulator interface changed),
and part of the implementation of user-visible commands for those operations.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Mark created a file of this name, but that was renamed to SimSetup.py
by bruce on 050325.

Bruce 050324 pulled in lots of existing code for running the simulator
(and some code for reading its results) into this file, since that fits
its name. That existing code was mostly by Mark and Huaicai, and was
partly cleaned up by Bruce, who also put some of it into subclasses
of the experimental CommandRun class. (CommandRun and its subclasses
were subsequently moved into another file, sim_commandruns.py.)

Bruce 050331 is splitting writemovie into several methods in more than
one subclass (eventually) of a new SimRunner class.

Bruce 051115 some comments and code cleanup; add #SIMOPT wherever a
simulator executable command-line flag is hardcoded.

Bruce 051231 partly-done code for using pyrex interface to sim; see use_dylib

[and much more, by many developers, not recorded]

Bruce 080321 split out sim_commandruns.py and sim_aspect.py into their
own files.
"""

from utilities.debug import print_compact_traceback
import widgets.DebugMenuMixin as DebugMenuMixin
    # DebugMenuMixin needs refactoring
    # to move this variable (sim_params_set) (and related code?) out of it;
    # see its module docstring for more info [bruce 080104 comment]
from utilities import debug_flags
from platform_dependent.PlatformDependent import fix_plurals
from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
from platform_dependent.PlatformDependent import hhmmss_str
from platform_dependent.PlatformDependent import find_plugin_dir
import os, sys, time
from math import sqrt
from time import sleep
from datetime import datetime
from PyQt4.Qt import QApplication, QCursor, Qt, QStringList
from PyQt4.Qt import QProcess, QObject, QFileInfo, SIGNAL
from utilities.Log import redmsg, greenmsg, orangemsg, quote_html, _graymsg
import foundation.env as env
from foundation.env import seen_before
from geometry.VQT import A, vlen
import re
from model.chunk import Chunk
from model.elements import Singlet
from utilities.debug_prefs import debug_pref, Choice, Choice_boolean_True, Choice_boolean_False
from utilities.constants import filesplit
from processes.Process import Process
from processes.Plugins import checkPluginPreferences, verifyExecutable
from widgets.StatusBar import AbortHandler, FileSizeProgressReporter
from simulation.PyrexSimulator import thePyrexSimulator
from simulation.SimulatorParameters import SimulatorParameters
from simulation.YukawaPotential import YukawaPotential
from simulation.GromacsLog import GromacsLog

from utilities.prefs_constants import electrostaticsForDnaDuringAdjust_prefs_key
from utilities.prefs_constants import electrostaticsForDnaDuringMinimize_prefs_key
from utilities.prefs_constants import electrostaticsForDnaDuringDynamics_prefs_key
from utilities.prefs_constants import neighborSearchingInGromacs_prefs_key

from utilities.prefs_constants import gromacs_enabled_prefs_key
from utilities.prefs_constants import gromacs_path_prefs_key
from utilities.prefs_constants import cpp_enabled_prefs_key
from utilities.prefs_constants import cpp_path_prefs_key
from utilities.prefs_constants import nv1_enabled_prefs_key
from utilities.prefs_constants import nv1_path_prefs_key

from utilities.GlobalPreferences import pref_create_pattern_indicators

# some non-toplevel imports too (of which a few must remain non-toplevel)

# ==

debug_sim_exceptions = 0 # DO NOT COMMIT WITH 1 -- set this to reproduce a bug mostly fixed by Will today #bruce 060111

debug_all_frames = 0 # DO NOT COMMIT with 1
debug_all_frames_atom_index = 1 # index of atom to print in detail, when debug_all_frames

DEBUG_SIM = False # DO NOT COMMIT with True
debug_pyrex_prints = 0 # prints to stdout the same info that gets shown transiently in statusbar
debug_timing_loop_on_sbar = 0

_USE_PYREX_SIM = True
    # Use pyrex sim by default.  Use debug menu to use the standalone sim. mark 060314.

if debug_sim_exceptions:
    debug_all_frames = 1

FAILURE_ALREADY_DOCUMENTED = -10101

# ==

def _timestep_flag_and_arg( mflag = False): #bruce 060503
    timestep_fs_str = debug_pref("dynamics timestep (fs)",
                                 Choice(["0.1", "0.2", "0.5", "1.0"]),
                                 non_debug = True )
    timestep_fs = float(timestep_fs_str)
        # kluge: we use a string in the menu, since float 0.1 shows up in
        # menu text as 0.100000000000000001 or so
    timestep = timestep_fs * 1e-15
    use_timestep_arg = (timestep_fs != 0.1) and not mflag
        # only supply the arg if not minimizing,
        # and if a non-default value is chosen
        # (in case the code to supply it has a bug,
        # or supplies it to the sim in the wrong format)
    return use_timestep_arg, timestep

##_timestep_flag_and_arg()
##    # Exercise the debug_pref so it shows up in the debug menu
##    # before the first sim/min run...
##    # Oops, this doesn't work from here, since this module is not imported
##    # until it's needed! Never mind for now, since it won't be an issue
##    # later when timestep is again supported as a movie attribute.

def _verifyGromppAndMdrunExecutables(gromacs_plugin_path):
    gromacs_bin_dir, junk_exe = os.path.split(gromacs_plugin_path)
    if (sys.platform == 'win32'):
        dot_exe = ".exe"
    else:
        dot_exe = ""
    grompp = os.path.join(gromacs_bin_dir, "grompp%s" % dot_exe)
    message = verifyExecutable(grompp)
    if (message):
        return message
    mdrun = os.path.join(gromacs_bin_dir, "mdrun%s" % dot_exe)
    message = verifyExecutable(mdrun)
    if (message):
        return message
    return None

# ==

#class GromacsProcess(Process):
#    verboseGromacsOutput = False
#
#    def standardOutputLine(self, line):
#        Process.standardOutputLine(self, line)
#        if (self.verboseGromacsOutput):
#            if (self.runningGrompp and False):
#                print "grompp stdout: " + line.rstrip()
#            if (self.runningMdrun and False):
#                print "mdrun stdout: " + line.rstrip()
#
#    def standardErrorLine(self, line):
#        Process.standardErrorLine(self, line)
#        if (self.verboseGromacsOutput):
#            if (self.runningGrompp and False):
#                print "grompp stderr: " + line.rstrip()
#            if (self.runningMdrun):
#                print "mdrun stderr: " + line.rstrip()
#        if (line.startswith("ERROR:")):
#            msg = redmsg("Gromacs " + line.rstrip().rstrip("-"))
#            env.history.message(msg)
#
#    def prepareForGrompp(self):
#        self.runningGrompp = True
#        self.runningMdrun = False
#
#    def prepareForMdrun(self):
#        self.runningGrompp = False
#        self.runningMdrun = True
import mock
GromacsProcess = mock.Mock()

class SimRunner:
    """
    Class for running the simulator.
    [subclasses can run it in special ways, maybe]
    """
    #bruce 050330 making this from writemovie and maybe some of Movie/SimSetup;
    # experimental, esp. since i don't yet know how much to factor the
    # input-file writing, process spawning, file-growth watching, file reading,
    # file using. Surely in future we'll split out file using into separate
    # code, and maybe file-growth watching if we run processes remotely
    # (or we might instead be watching results come in over a tcp stream,
    # frames mixed with trace records).
    # So for now, let's make the minimal class for running the sim,
    # up to having finished files to look at but not looking at them;
    # then the old writemovie might call this class to do most of its work
    # but also call other classes to use the results.

    # wware 060406 bug 1263 - provide a mechanism to be notified when the
    # program is exiting. This is set to True in ops_files.py. This is a class
    # (not instance) variable, which matters because ops_files.py can set this
    # without a reference to the currently active SimRunner instance.
    PREPARE_TO_CLOSE = False

    used_atoms = None

    def __init__(self, part, mflag,
                 simaspect = None,
                 use_dylib_sim = _USE_PYREX_SIM,
                 cmdname = "Simulator",
                 cmd_type = 'Minimize',
                 useGromacs = False,
                 background = False,
                 hasPAM = False,
                 useAMBER = False,
                 typeFeedback = False):
            # [bruce 051230 added use_dylib_sim; revised 060102; 060106 added cmdname]
        """
        set up external relations from the part we'll operate on;
        take mflag arg, since someday it'll specify the subclass to use.
        """
        self.assy = assy = part.assy # needed?
        #self.tmpFilePath = assy.w.tmpFilePath
        self.win = assy.w  # might be used only for self.win.progressbar.launch
        self.part = part # needed?
        self.mflag = mflag # see docstring
        self.simaspect = simaspect # None for entire part, or an object describing
            # what aspect of it to simulate [bruce 050404]
        self.errcode = 0 # public attr used after we're done;
            # 0 or None = success (so far), >0 = error (msg emitted)
        self.said_we_are_done = False #bruce 050415
        self.pyrexSimInterrupted = False
            #wware 060323, bug 1725, if interrupted we don't need so many warnings
        self.useGromacs = useGromacs
        self.background = background
        self.hasPAM = hasPAM
        self.useAMBER = useAMBER
        self.typeFeedback = typeFeedback
        self.gromacsLog = None
        self.tracefileProcessor = None

        prefer_standalone_sim = \
            debug_pref("force use of standalone sim",
                       Choice_boolean_False,
                       prefs_key = 'use-standalone-sim',
                       non_debug = True )
        if prefer_standalone_sim:
            use_dylib_sim = False
        self.use_dylib_sim = use_dylib_sim #bruce 051230

        self.cmdname = cmdname
        self.cmd_type = cmd_type #060705
        if not use_dylib_sim:
            msg = "Using the standalone simulator (not the pyrex simulator)"
            env.history.message(greenmsg(msg))
        return

    def verifyNanoVision1Plugin(self):
        """
        Verify NanoVision-1 plugin.

        @return: True if NanoVision-1 is properly enabled.
        @rtype: boolean
        """

        plugin_name = "NanoVision-1"
        plugin_prefs_keys = (nv1_enabled_prefs_key, nv1_path_prefs_key)

        errorcode, errortext_or_path = \
                 checkPluginPreferences(plugin_name, plugin_prefs_keys,
                                        insure_executable = True)
        if errorcode:
            msg = redmsg("Verify Plugin: %s (code %d)" % (errortext_or_path, errorcode))
            env.history.message(msg)
            return False

        self.nv1_executable_path = errortext_or_path

        return True

    def verifyGromacsPlugin(self):
        """
        Verify GROMACS plugin.

        @return: True if GROMACS is properly enabled.
        @rtype: boolean
        """

        plugin_name = "GROMACS"
        plugin_prefs_keys = (gromacs_enabled_prefs_key, gromacs_path_prefs_key)

        errorcode, errortext_or_path = \
                 checkPluginPreferences(plugin_name, plugin_prefs_keys,
                                        extra_check = _verifyGromppAndMdrunExecutables)
        if errorcode:
            msg = redmsg("Verify Plugin: %s (code %d)" % (errortext_or_path, errorcode))
            env.history.message(msg)
            return False

        program_path = errortext_or_path

        self.gromacs_bin_dir, junk_exe = os.path.split(program_path)

        plugin_name = "CPP"
        plugin_prefs_keys = (cpp_enabled_prefs_key, cpp_path_prefs_key)

        errorcode, errortext_or_path = \
                 checkPluginPreferences(plugin_name, plugin_prefs_keys,
                                        insure_executable = True)
        if errorcode:
            msg = redmsg("Verify Plugin: %s (code %d)" % (errortext_or_path, errorcode))
            env.history.message(msg)
            return False

        self.cpp_executable_path = errortext_or_path

        return True

    def mdrunPollFunction(self):
        if (not self.mdrunLogFile):
            try:
                logFile = open(self.mdrunLogFileName, 'rU')
            except IOError:
                # file hasn't been created by mdrun yet, just try
                # again next time around.
                return
            self.mdrunLogFile = logFile
            self.mdrunLogLineBuffer = ""
        if (self.mdrunLogFile):
            while (True):
                line = self.mdrunLogFile.readline()
                if (not line):
                    return
                self.mdrunLogLineBuffer = self.mdrunLogLineBuffer + line
                if (self.mdrunLogLineBuffer.endswith('\n')):
                    self.gromacsLog.addLine(self.mdrunLogLineBuffer)
                self.mdrunLogLineBuffer = ""


    def run_using_old_movie_obj_to_hold_sim_params(self, movie):
        self._movie = movie # general kluge for old-code compat
            # (lots of our methods still use this and modify it)
        # note, this movie object (really should be a simsetup object?)
        # does not yet know a proper alist (or any alist, I hope) [bruce 050404]
        self.errcode = self.set_options_errQ( )
            # set movie alist, output filenames, sim executable pathname (verify it exists)
            #obs comment [about the options arg i removed?? or smth else?]
            # options include everything that affects the run except the set of atoms and the part
        if self.errcode: # used to be a local var 'r'
            # bruce 051115 comment: more than one reason this can happen;
            # one is sim executable missing
            return
        self.sim_input_file = self.sim_input_filename()
            # might get name from options or make up a temporary filename

        launchNV1 = debug_pref("GROMACS: Launch NV1", Choice_boolean_False)
        if (self.mflag == 1 and self.useGromacs):
            if (not self.verifyGromacsPlugin()):
                self.errcode = FAILURE_ALREADY_DOCUMENTED
                return
            if (self.background and launchNV1):
                if (not self.verifyNanoVision1Plugin()):
                    self.errcode = FAILURE_ALREADY_DOCUMENTED
                    return
        self.set_waitcursor(True)
        progressBar = self.win.statusBar().progressBar

        # Disable some QActions (menu items/toolbar buttons) while the sim is running.
        self.win.disable_QActions_for_sim(True)

        try: #bruce 050325 added this try/except wrapper, to always restore cursor
            self.write_sim_input_file()
                # for Minimize, this uses simaspect to write file;
                # puts it into movie.alist too, via writemovie
            self.simProcess = None #bruce 051231
            sp = SimulatorParameters()
            self.yukawaRCutoff = sp.getYukawaRCutoff()
            self.spawn_process()
                # spawn_process is misnamed since it can go thru either
                # interface (pyrex or exec OS process), since it also monitors
                # progress and waits until it's done, and insert results back
                # into part, either in real time or when done.
                # result error code (or abort button flag) stored in self.errcode
            if (self.mflag == 1 and self.useGromacs):
                ok, gromacs_plugin_path = find_plugin_dir("GROMACS")
                if (not ok):
                    msg = redmsg(gromacs_plugin_path)
                    env.history.message(self.cmdname + ": " + msg)
                    self.errcode = -11112
                    return
                progressBar.setRange(0, 0)
                progressBar.reset()
                progressBar.show()
                if (sys.platform == 'win32'):
                    dot_exe = ".exe"
                else:
                    dot_exe = ""
                sim_bin_dir = self.sim_bin_dir_path()
                grompp = \
                    os.path.join(self.gromacs_bin_dir, "grompp%s" % dot_exe)
                mdrun = os.path.join(self.gromacs_bin_dir, "mdrun%s" % dot_exe)

                gromacsFullBaseFileName = self._movie.filename
                gromacsFullBaseFileInfo = QFileInfo(gromacsFullBaseFileName)
                gromacsWorkingDir = gromacsFullBaseFileInfo.dir().absolutePath()
                gromacsBaseFileName = gromacsFullBaseFileInfo.fileName()

                env.history.message("%s: GROMACS files at %s%s%s.*" %
                    (self.cmdname, gromacsWorkingDir, os.sep,
                     gromacsFullBaseFileInfo.completeBaseName()))

                gromacsProcess = GromacsProcess()
                gromacsProcess.setProcessName("grompp")
                gromacsProcess.prepareForGrompp()
                gromacsProcess.redirect_stdout_to_file("%s-grompp-stdout.txt" %
                    gromacsFullBaseFileName)
                gromacsProcess.redirect_stderr_to_file("%s-grompp-stderr.txt" %
                    gromacsFullBaseFileName)
                gromppArgs = [
                    "-f", "%s.mdp" % gromacsBaseFileName,
                    "-c", "%s.gro" % gromacsBaseFileName,
                    "-p", "%s.top" % gromacsBaseFileName,
                    "-n", "%s.ndx" % gromacsBaseFileName,
                    "-o", "%s.tpr" % gromacsBaseFileName,
                    "-po", "%s-out.mdp" % gromacsBaseFileName,
                    ]

                gromacsProcess.setWorkingDirectory(gromacsWorkingDir)

                gromacs_topo_dir = \
                    self.gromacs_bin_dir[0:len(self.gromacs_bin_dir) - 4]
                gromacs_topo_dir = \
                    os.path.join(gromacs_topo_dir, "share", "gromacs", "top")
                environmentVariables = gromacsProcess.environment()
                environmentVariables += "GMXLIB=%s" % gromacs_topo_dir
                gromacsProcess.setEnvironment(environmentVariables)

                abortHandler = AbortHandler(self.win.statusBar(), "grompp")
                errorCode = gromacsProcess.run(grompp, gromppArgs, False, abortHandler)
                abortHandler = None
                if (errorCode != 0):
                    msg = redmsg("Gromacs minimization failed, grompp returned %d" % errorCode)
                    env.history.message(self.cmdname + ": " + msg)
                    self.errcode = 2;
                else:
                    progressBar.setRange(0, 0)
                    progressBar.reset()
                    gromacsProcess.setProcessName("mdrun")
                    gromacsProcess.prepareForMdrun()

                    trajectoryOutputFile = None
                    if (self.background and launchNV1):
                        trajectoryOutputFile = "%s/%s.%s" % \
                            (gromacsFullBaseFileInfo.absolutePath(),
                             gromacsFullBaseFileInfo.completeBaseName(), "nh5")
                    else:
                        if (not self.background):
                            progressBar.show()
                            gromacsProcess.redirect_stdout_to_file("%s-mdrun-stdout.txt" %
                                                                   gromacsFullBaseFileName)
                            gromacsProcess.redirect_stderr_to_file("%s-mdrun-stderr.txt" %
                                                                   gromacsFullBaseFileName)
                        trajectoryOutputFile = \
                            "%s.%s" % (gromacsFullBaseFileName, "trr")

                    mdrunArgs = None
                    if (self.background):
                        fullBaseFilename = gromacsFullBaseFileName
                        if (sys.platform == 'win32'):
                            fullBaseFilename = "\"" + fullBaseFilename + "\""
                        mdrunArgs = [
                            os.path.join(gromacs_plugin_path, "mdrunner.bat"),
                            gromacs_topo_dir,
                            mdrun,
                            fullBaseFilename
                        ]
                    else:
                        self.mdrunLogFile = None
                        self.mdrunLogFileName = "%s-mdrun.log" % gromacsFullBaseFileName
                        try:
                            os.remove(self.mdrunLogFileName)
                        except:
                            # Ignore the error that it isn't there.  We just want it gone.
                            pass
                        mdrunArgs = [
                            "-s", "%s.tpr" % gromacsFullBaseFileName,
                            "-o", "%s" % trajectoryOutputFile,
                            "-e", "%s.edr" % gromacsFullBaseFileName,
                            "-c", "%s-out.gro" % gromacsFullBaseFileName,
                            "-g", self.mdrunLogFileName,
                            ]
                    if (self.hasPAM):
                        tableFile = "%s.xvg" % gromacsFullBaseFileName
                        yp = YukawaPotential(sp)
                        yp.writeToFile(tableFile)

                        mdrunArgs += [ "-table", tableFile,
                                       "-tablep", tableFile ]

                    if (self.background):
                        abortHandler = None
                        scriptSuffix = None
                        if (sys.platform == 'win32'):
                            scriptSuffix = "bat"
                        else:
                            scriptSuffix = "sh"
                        os.spawnv(os.P_NOWAIT,
                                  os.path.join(gromacs_plugin_path,
                                               "mdrunner.%s" % scriptSuffix),
                                  mdrunArgs);

                    else:
                        self.gromacsLog = GromacsLog()
                        abortHandler = \
                            AbortHandler(self.win.statusBar(), "mdrun")
                        errorCode = \
                                  gromacsProcess.run(mdrun, mdrunArgs,
                                                     self.background,
                                                     abortHandler,
                                                     self.mdrunPollFunction)
                    abortHandler = None
                    if (errorCode != 0):
                        msg = redmsg("GROMACS minimization failed, mdrun returned %d" % errorCode)
                        env.history.message(self.cmdname + ": " + msg)
                        self.errcode = 3;
                    if (self.background and errorCode == 0):
                        if (launchNV1):
                            hdf5DataStoreDir = \
                                gromacsWorkingDir + os.sep + \
                                gromacsFullBaseFileInfo.completeBaseName()
                            os.mkdir(hdf5DataStoreDir)

                        sleep(1) # Give GMX/HDF5 a chance to write basic info

                        # Determine the GMX process id (pid) for passing to nv1.
                        #
                        # (Py)QProcess.pid() doesn't return anything useable
                        # for new, non-child processes, read the pid from the
                        # mdrun log file.
                        mdrunLogFileName = \
                            "%s-mdrun.log" % gromacsFullBaseFileName
                        pid = None
                        fileOpenAttemptIndex = 0
                        while (fileOpenAttemptIndex < 3):
                            try:
                                logFile = open(mdrunLogFileName, 'r')
                                for line in logFile:
                                    index = line.find(" pid: ");
                                    if (index != -1):
                                        pid = line[index+6:]
                                        pid = pid.split(" ")[0];
                                        break
                                logFile.close()
                                fileOpenAttemptIndex = 99

                            except:
                                fileOpenAttemptIndex += 1
                                env.history.message(self.cmdname + ": Waiting for GROMACS process identifier availability...")
                                sleep(1)

                        # Write the input file into the HDF5 data store
                        # directory. (It is part of data store.)
                        if (launchNV1):
                            inputFileName = hdf5DataStoreDir + os.sep + "input.mmp"
                            env.history.message(self.cmdname + ": Writing input.mmp file to HDF5 data store directory.")
                            all_atoms = {}
                            self.part.writemmpfile(inputFileName,
                                                   add_atomids_to_dict = all_atoms)

                        # Write a file that maps the ids of the atoms actually
                        # used for simulation to the atom ids of the complete
                        # structure stored in the MMP file above.
                        if (launchNV1):
                            used_atoms = self.used_atoms
                            assert used_atoms is not None, \
                                   "self.used_atoms didn't get stored"
                            mapFilename = \
                                hdf5DataStoreDir + os.sep + "trajAtomIdMap.txt"
                            self.writeTrajectoryAtomIdMapFile(mapFilename,
                                                              used_atoms, all_atoms)

                        # Launch the NV1 process
                        if (launchNV1):
                            nv1 = self.nv1_executable_path
                            nv1Process = Process()
                            nv1Args = [
                                "-f", hdf5DataStoreDir + ".nh5",
                                "-p", "GMX", "%s" % pid,
                                ]
                            nv1Process.setStandardOutputPassThrough(True)
                            nv1Process.setStandardErrorPassThrough(True)
                            nv1Process.setProcessName("nv1")
                            env.history.message(self.cmdname + ": Launching NanoVision-1...")
                            nv1Process.run(nv1, nv1Args, True)
                        else:
                            if (pid != None):
                                env.history.message(self.cmdname + ": GROMACS process " + pid + " has been launched.")
                            else:
                                env.history.message(self.cmdname + ": GROMACS process has been launched; unable to determine its identifier.")
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

        elif not self.pyrexSimInterrupted and \
             self.errcode != FAILURE_ALREADY_DOCUMENTED: # wware 060323 bug 1725
            # Something failed...
            msg = "Simulation failed: exit code or internal error code %r " % \
                  self.errcode #e identify error better!
            env.history.message(self.cmdname + ": " + redmsg(msg))
                #fyi this was 'cmd' which was wrong, it says 'Simulator'
                # even for Minimize [bruce 060106 comment, fixed it now]
        self.said_we_are_done = True
            # since saying we aborted or had an error is good enough...
            ###e revise if kill can take time.
        return # caller should look at self.errcode

        # semi-obs comment? [by bruce few days before 050404, partly expresses an intention]
        # results themselves are a separate object (or more than one?) stored in attrs... (I guess ###k)
        # ... at this point the caller probably extracts the results object and uses it separately
        # or might even construct it anew from the filename and params
        # depending on how useful the real obj was while we were monitoring the progress
        # (since if so we already have it... in future we'll even start playing movies as their data comes in...)
        # so not much to do here! let caller care about res, not us.

    def set_options_errQ(self): #e maybe split further into several setup methods? #bruce 051115 removed unused 'options' arg
        """
        Set movie alist (from simaspect or entire part);
        debug-msg if it was already set (and always ignore old value).
        Figure out and set filenames, including sim executable path.
        All inputs and outputs are self attrs or globals or other obj attrs...
        except, return error code if sim executable missing
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
            # this movie object is being reused, which is a bug.
            # complain... and try to work around.
            if debug_flags.atom_debug:
                # since I expect this is possible for "save movie file" until fixed...
                # [bruce 050404] (maybe not? it had assert 0)
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
            for atom in movie.alist:
                assert atom.molecule.part == part ###@@@ remove when works
            movie.alist_fits_entire_part = True # permits optims... but note it won't be valid
                # anymore if the part changes! it's temporary... not sure it deserves to be an attr
                # rather than local var or retval.
        else:
            # the simaspect should know what to minimize...
            alist = self.simaspect.atomslist()
            movie.set_alist(alist)
            for atom in movie.alist: # redundant with set_alist so remove when works
                assert atom.molecule.part == part

        # Set up filenames.
        # We use the process id to create unique filenames for this instance of the program
        # so that if the user runs more than one program at the same time, they don't use
        # the same temporary file names.
        # We now include a part-specific suffix [mark 051030]]
        # [This will need revision when we can run more than one sim process
        #  at once, with all or all but one in the "background" [bruce 050401]]

        # simFilesPath = "~/Nanorex/SimFiles". Mark 051028.
        simFilesPath = find_or_make_Nanorex_subdir('SimFiles')

        # Create temporary part-specific filename, for example:
        # "partname-minimize-pid1000".
        # We'll be appending various extensions to tmp_file_prefix to make temp
        # file names for sim input and output files as needed (e.g. mmp, xyz,
        # etc.)
        junk, basename, ext = filesplit(self.assy.filename)
        if not basename: # The user hasn't named the part yet.
            basename = "Untitled"
        timestampString = ""
        if (self.background):
            # Add a timestamp to the pid so that multiple backgrounded
            # calculations don't clobber each other's files.
            timestamp = datetime.today()
            timestampString = timestamp.strftime(".%y%m%d%H%M%S")
        self.tmp_file_prefix = \
            os.path.join(simFilesPath,
                         "%s-minimize-pid%d%s" % (basename, os.getpid(),
                                                  timestampString))

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
        """
        Return pathname of bin directory that ought to contain simulator executable and/or dynamic library.
        (Doesn't check whether it exists.)
        """
        # filePath = the current directory NE-1 is running from.
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.normpath(filePath + '/../bin')

    def import_dylib_sim(self, dylib_path): #bruce 051230 experimental code
        """
        Try to import the dynamic library version of the simulator, under the module name 'sim',
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
                from sim import theSimulator
            except:
                worked = False
                print_compact_traceback("error trying to import Minimize and Dynamics from dylib sim: ")
        return worked

    def old_set_sim_output_filenames_errQ(self, movie, mflag):
        """
        Old code, not yet much cleaned up. Uses and/or sets movie.filename,
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
            if movie.filename and debug_flags.atom_debug:
                print "atom_debug: warning: ignoring filename %r, bug??" % movie.filename
            movie.filename = self.tmp_file_prefix + ".xyz"  ## "sim-%d.xyz" % pid

        if mflag == 2: #multi-frame DPB file
            if movie.filename and debug_flags.atom_debug:
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
        """
        Figure out the simulator input filename
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
        """
        Write the appropriate data from self.part (as modified by self.simaspect)
        to an input file for the simulator (presently always in mmp format)
        using the filename self.sim_input_file
        (overwriting any existing file of the same name).
        """
        part = self.part
        mmpfile = self.sim_input_file # the filename to write to
        movie = self._movie # old-code compat kluge
        assert movie.alist is not None #bruce 050404
        self.used_atoms = {} #bruce 080325 [review: redundant with movie.alist??]

        if not self.simaspect: ## was: if movie.alist_fits_entire_part:
            # note: as of 080325, this case certainly runs for Run Dynamics,
            # and probably runs for all whole-part Adjust, Minimize, or
            # Dynamics operations. [bruce 080325 comment]
            if DEBUG_SIM:
                print "part.writemmpfile(%r)" % (mmpfile,)
            stats = {}
            part.writemmpfile( mmpfile,
                               leave_out_sim_disabled_nodes = True,
                               sim = True,
                               dict_for_stats = stats,
                               add_atomids_to_dict = self.used_atoms
                              )
                #bruce 051209 added options (used to be hardcoded in files_mmp), plus a new one, dict_for_stats
                # As of 051115 this is still called for Run Sim [Run Dynamics].
                # As of 050412 this didn't yet turn singlets into H;
                # but as of long before 051115 it does (for all calls -- so it would not be good to use for Save Selection!).
                #bruce 050811 added sim = True to fix bug 254 for sim runs, for A6.
                # (and 051209, according to a longer comment now removed [by bruce 080321],
                #  added dict_for_stats to complete that fix)
            nsinglets_H = stats.get('nsinglets_H', 0)
            if nsinglets_H: #bruce 051209 this message code is approximately duplicated elsewhere in this file
                info = fix_plurals( "(Treating %d bondpoint(s) as Hydrogens, during simulation)" % nsinglets_H )
                env.history.message( info)
        else:
            # note: as of 080325, this case certainly runs for Adjust 1 atom
            # (from its glpane cmenu), and probably runs for all part-subset
            # Adjust, Minimize, or Dynamics operations. [bruce 080325 comment]
            if DEBUG_SIM:
                print "simaspect.writemmpfile(%r)" % (mmpfile,)
            # note: simaspect has already been used to set up movie.alist; simaspect's own alist copy is used in following:
            self.simaspect.writemmpfile( mmpfile, add_atomids_to_dict = self.used_atoms)
                # this also turns singlets into H
            # obs comments:
            # bruce 050325 revised this to use whatever alist was asked for above (set of atoms, and order).
            # But beware, this might only be ok right away for minimize, not simulate (since for sim it has to write all jigs as well).

        ## movie.natoms = natoms = len(movie.alist) # removed by bruce 050404 since now done in set_alist etc.
        ###@@@ why does that trash a movie param? who needs that param? it's now redundant with movie.alist
        return

    def set_waitcursor(self, on_or_off): # [WARNING: this code is now duplicated in at least one other place, as of 060705]
        """
        For on_or_off True, set the main window waitcursor.
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
        """
        Actually spawn the process [or the extension class object],
        making its args [or setting its params] based on some of self's attributes.
        Wait til we're done with this simulation, then record results in other self attributes.
        """
        if DEBUG_SIM:
            #bruce 051115 confirmed this is always called for any use of sim (Minimize or Run Sim)
            print "calling spawn_process"
        # First figure out process arguments
        # [bruce 050401 doing this later than before, used to come before writing sim-input file]
        self.setup_sim_args() # stores them in an attribute, whose name and value depends on self.use_dylib_sim
        # Now run the sim to completion (success or fail or user abort),
        # as well as whatever updates we do at the same time in the cad code
        # (progress bar, showing movie in real time [nim but being added circa 051231], ...)
        if self.use_dylib_sim:
            self.sim_loop_using_dylib() #bruce 051231 wrote this anew
        else:
            self.sim_loop_using_standalone_executable() #bruce 051231 made this from last part of old spawn_process code
        return

    def setup_sim_args(self): #bruce 051231 split this out of spawn_process, added dylib case
        """
        Set up arguments for the simulator, using one of two different interfaces:
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
        self.update_cond = movie.update_cond
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
        if ext == ".dpb":
            formarg = ''
        elif ext == ".xyz":
            formarg = "-x" #SIMOPT (value also used as internal flag)
        else:
            assert 0
        self._formarg = formarg # kluge
        # the use_dylib code for formarg is farther below

        self._simopts = self._simobj = self._arguments = None # appropriate subset of these is set below

        use_timestep_arg = False
        if 1: ##@@ bruce 060503: add debug_pref to let user vary simulator timestep
            # (we also read the value on import, in separate code above, to make sure it gets into the debug menu right away)
            use_timestep_arg, timestep = _timestep_flag_and_arg(mflag)
            # boolean and float (timestep in seconds)
            if use_timestep_arg:
                env.history.message(orangemsg("Note: using experimental non-default dynamics timestamp of %r femtoseconds" % (timestep * 1e15)))
        if use_command_line:
            # "args" = arguments for the simulator.
            #SIMOPT -- this appears to be the only place the entire standalone simulator command line is created.
            if mflag:
                #argument to enable or disable electrostatics
                electrostaticArg = '--enable-electrostatic='
                if self.cmd_type == 'Adjust' or self.cmd_type == 'Adjust Atoms':
                    electrostaticFlag = self.getElectrostaticPrefValueForAdjust()
                else:
                    electrostaticFlag = self.getElectrostaticPrefValueForMinimize()

##              electrostaticArg.append(str(electrostaticFlag))
                electrostaticArg += str(electrostaticFlag) #bruce 070601 bugfix

                if (self.useGromacs):
                    gromacsArgs = ["--write-gromacs-topology",
                                   moviefile,
                                   "--path-to-cpp",
                                   self.cpp_executable_path
                                   ]
                else:
                    gromacsArgs = []
                if (self.hasPAM):
                    # vdw-cutoff-radius in nm, and must match the
                    # user potential function table passed to
                    # mdrun.  See GROMACS user manual section
                    # 6.6.2
                    gromacsArgs += [ "--vdw-cutoff-radius=%f" % self.yukawaRCutoff ]

                # [bruce 05040 infers:] mflag true means minimize; -m tells this to the sim.
                # (mflag has two true flavors, 1 and 2, for the two possible output filetypes for Minimize.)
                # [later, bruce 051231: I think only one of the two true mflag values is presently supported.]
                args = [program, '-m', str(formarg),
                        traceFileArg, outfileArg,
                        electrostaticArg,
                        infile] + gromacsArgs #SIMOPT
            else:
                # THE TIMESTEP ARGUMENT IS MISSING ON PURPOSE.
                # The timestep argument "-s + (movie.timestep)" is not supported for Alpha. #SIMOPT

                electrostaticArg = '--enable-electrostatic='
                electrostaticFlag = self.getElectrostaticPrefValueForDynamics()
##              electrostaticArg.append(str(electrostaticFlag))
                electrostaticArg += str(electrostaticFlag) #bruce 070601 bugfix

                args = [program,
                        '-f' + str(movie.totalFramesRequested), #SIMOPT
                        '-t' + str(movie.temp),  #SIMOPT
                        '-i' + str(movie.stepsper),  #SIMOPT
                        '-r', #SIMOPT
                        electrostaticArg,
                        str(formarg),
                        traceFileArg,
                        outfileArg,
                        infile]
            if use_timestep_arg: #bruce 060503; I'm guessing that two separate arguments are needed for this, and that %f will work
                args.insert(1, '--time-step')
                args.insert(2, '%f' % timestep)
            args += [ "--system-parameters", self.system_parameters_file ]
            if DEBUG_SIM:
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
            sim = thePyrexSimulator()
            sim.setup(mflag, infile)
            simobj = sim.sim
            if DebugMenuMixin.sim_params_set:
                for attr, value in DebugMenuMixin.sim_param_values.items():
                    setattr(simobj, attr, value)
            simopts = simobj
            # order of set of remaining options should not matter;
            # for correspondence see sim/src files sim.pyx, simhelp.c, and simulator.c
            if formarg == '-x':
                simopts.DumpAsText = 1 # xyz rather than dpb, i guess
            else:
                assert formarg == ''
                simopts.DumpAsText = 0
            if movie.print_energy:
                simopts.PrintPotentialEnergy = 1
            if self.traceFileName:
                simopts.TraceFileName = self.traceFileName # note spelling diff, 'T' vs 't' (I guess I like this difference [b 060102])
                #k not sure if this would be ok to do otherwise, since C code doesn't turn "" into NULL and might get confused
            sim.setOutputFileName(moviefile)
            if not mflag:
                # The timestep argument "-s + (movie.timestep)" or Dt is not supported for Alpha...
                if use_timestep_arg: #bruce 060503
                    simopts.Dt = timestep
                simopts.NumFrames = movie.totalFramesRequested   # SIMPARAMS
                simopts.Temperature = movie.temp
                simopts.IterPerFrame = movie.stepsper
                simopts.PrintFrameNums = 0
                simopts.EnableElectrostatic = self.getElectrostaticPrefValueForDynamics()
            if mflag:
                self.set_minimize_threshhold_prefs(simopts)
                if self.cmd_type == 'Adjust' or self.cmd_type == 'Adjust Atoms':
                    simopts.EnableElectrostatic = self.getElectrostaticPrefValueForAdjust()
                    simopts.NeighborSearching = 0
                else:
                    simopts.EnableElectrostatic = self.getElectrostaticPrefValueForMinimize()
                    simopts.NeighborSearching = self.getNeighborSearchingPrefValue()

                if (self.useGromacs):
                    simopts.GromacsOutputBaseName = moviefile
                    simopts.PathToCpp = self.cpp_executable_path
                if (self.hasPAM):
                    # vdw-cutoff-radius in nm, and must match the
                    # user potential function table passed to
                    # mdrun.  See GROMACS user manual section
                    # 6.6.2
                    simopts.VanDerWaalsCutoffRadius = self.yukawaRCutoff
                if (self.useAMBER):
                    simopts.UseAMBER = self.useAMBER
                    simopts.TypeFeedback = self.typeFeedback

            #e we might need other options to make it use Python callbacks (nim, since not needed just to launch it differently);
            # probably we'll let the later sim-start code set those itself.
            self._simopts = simopts
            self._simobj = simobj
        # return whatever results are appropriate -- for now, we stored each one in an attribute (above)
        return # from setup_sim_args

    def getElectrostaticPrefValueForAdjust(self):
        #ninad20070509
        #int EnableElectrostatic =1 implies electrostatic is enabled
        #and 0 implies it is disabled. This sim arg is defined in sim.pyx in sim/src
        if self.useGromacs and env.prefs[electrostaticsForDnaDuringAdjust_prefs_key]:
            val = 1
        else:
            val = 0
        return val

    def getElectrostaticPrefValueForMinimize(self):
        #ninad20070509
        # int EnableElectrostatic =1 implies electrostatic is enabled
        #and 0 implies it is disabled. This sim arg is defined in sim.pyx in sim/src
        if self.useGromacs and env.prefs[electrostaticsForDnaDuringMinimize_prefs_key]:
            val = 1
        else:
            val = 0
        return val

    def getNeighborSearchingPrefValue(self):
        if env.prefs[neighborSearchingInGromacs_prefs_key]:
            val = 1
        else:
            val = 0
        return val


    def getElectrostaticPrefValueForDynamics(self):
        #ninad20070509
        # int EnableElectrostatic =1 implies electrostatic is enabled
        #and 0 implies it is disabled. This sim arg is defined in sim.pyx in sim/src
        if env.prefs[electrostaticsForDnaDuringDynamics_prefs_key]:
            val = 1
        else:
            val = 0
        return val

    def set_minimize_threshhold_prefs(self, simopts): #bruce 060628, revised 060705
        def warn(msg):
            env.history.message(orangemsg("Warning: ") + quote_html(msg))
        try:
            if env.debug():
                print "debug: running set_minimize_threshhold_prefs"
            ###obs design scratch:
            # we'll probably use different prefs keys depending on an arg that tells us which command-class to use,
            # Adjust, Minimize, or Adjust Atoms; maybe some function in prefs_constants will return the prefs_key,
            # so all the UI code can call it too. [bruce 060705]
            from utilities.prefs_constants import Adjust_endRMS_prefs_key, Adjust_endMax_prefs_key
            from utilities.prefs_constants import Adjust_cutoverRMS_prefs_key, Adjust_cutoverMax_prefs_key
            from utilities.prefs_constants import Minimize_endRMS_prefs_key, Minimize_endMax_prefs_key
            from utilities.prefs_constants import Minimize_cutoverRMS_prefs_key, Minimize_cutoverMax_prefs_key

            # kluge for A8 -- ideally these prefs keys or their prefs values
            # would be set as movie object attrs like all other sim params
            cmd_type = self.cmd_type
            if cmd_type == 'Adjust' or cmd_type == 'Adjust Atoms' or cmd_type == 'Check AtomTypes':
                endRMS_prefs_key = Adjust_endRMS_prefs_key
                endMax_prefs_key = Adjust_endMax_prefs_key
                cutoverRMS_prefs_key = Adjust_cutoverRMS_prefs_key
                cutoverMax_prefs_key = Adjust_cutoverMax_prefs_key
            elif cmd_type == 'Minimize':
                endRMS_prefs_key = Minimize_endRMS_prefs_key
                endMax_prefs_key = Minimize_endMax_prefs_key
                cutoverRMS_prefs_key = Minimize_cutoverRMS_prefs_key
                cutoverMax_prefs_key = Minimize_cutoverMax_prefs_key
            else:
                assert 0, "don't know cmd_type == %r" % (cmd_type,)

            # The following are partly redundant with the formulas,
            # which is intentional, for error checking of the formulas.
            # Only the first (endRMS) values are independent.
            if cmd_type == 'Adjust' or cmd_type == 'Check AtomTypes':
                defaults = (100.0, 500.0, 100.0, 500.0) # also hardcoded in prefs_constants.py
            elif cmd_type == 'Adjust Atoms':
                defaults = (50.0, 250.0, 50.0, 250.0)
            elif cmd_type == 'Minimize':
                defaults = (1.0, 5.0, 50.0, 250.0) # revised 060705, was (1.0, 10.0, 50.0, 300.0); also hardcoded in prefs_constants.py

            endRMS = env.prefs[endRMS_prefs_key]
            endMax = env.prefs[endMax_prefs_key]
            cutoverRMS = env.prefs[cutoverRMS_prefs_key]
            cutoverMax = orig_cutoverMax = env.prefs[cutoverMax_prefs_key]
            # -1 means left blank, use default; any 0 or negative value entered explicitly will have the same effect.
            # For an explanation of the logic of these formulas, see email from bruce to nanorex-all of 060619,
            # "test UI for minimizer thresholds". These are mainly for testing -- for final release (A8 or maybe A8.1)
            # we are likely to hide all but the first from the UI by default, with the others always being -1.
            #   Revising formulas for A8 release, bruce 060705.

            if cmd_type == 'Adjust Atoms':
                # kluge, because it doesn't have its own prefs values, and has its own defaults, but needs to be adjustable:
                # use fixed values, but if Adjust prefs are made stricter, let those limit these fixed values too
                endRMS = min( endRMS, defaults[0] )
                endMax = min( endMax, defaults[1] )
                cutoverRMS = min( cutoverRMS, defaults[2] )
                cutoverMax = min( cutoverMax, defaults[3] )

            if endRMS <= 0:
                endRMS = defaults[0] # e.g. 1.0; note, no other defaults[i] needs to appear in these formulas
            if endMax <= 0:
                endMax = 5.0 * endRMS # revised 060705 (factor was 10, now 5)
            elif endMax < endRMS:
                warn("endMax < endRMS is not allowed, using endMax = endRMS")
                endMax = endRMS # sim C code would use 5.0 * endRMS if we didn't fix this here
            if cutoverRMS <= 0:
                cutoverRMS = max( 50.0, endRMS ) # revised 060705
            if cutoverMax <= 0:
                cutoverMax = 5.0 * cutoverRMS # revised 060705, was 300.0
            if cutoverRMS < endRMS:
                warn("cutoverRMS < endRMS is not allowed, using cutoverRMS,Max = endRMS,Max")
                cutoverRMS = endRMS
                cutoverMax = endMax
            elif cutoverMax < endMax:
                warn("cutoverMax < endMax is not allowed, using cutoverRMS,Max = endRMS,Max")
                cutoverRMS = endRMS
                cutoverMax = endMax
            if cutoverMax < cutoverRMS:
                if orig_cutoverMax <= 0:
                    warn("cutoverMax < cutoverRMS is not allowed, using cutoverMax = 5.0 * cutoverRMS")
                        # revised 060705 (factor was 6, now 5)
                    cutoverMax = 5.0 * cutoverRMS # sim C code would use 5.0 * cutoverRMS if we didn't fix this here
                else:
                    warn("cutoverMax < cutoverRMS is not allowed, using cutoverMax = cutoverRMS")
                    cutoverMax = cutoverRMS # sim C code would use 5.0 * cutoverRMS if we didn't fix this here
            if (endRMS, endMax, cutoverRMS, cutoverMax) != defaults or env.debug():
                msg = "convergence criteria: endRMS = %0.2f, endMax = %0.2f, cutoverRMS = %0.2f, cutoverMax = %0.2f" % \
                    (endRMS, endMax, cutoverRMS, cutoverMax)
                if (endRMS, endMax, cutoverRMS, cutoverMax) == defaults:
                    msg += " (default values -- only printed since ATOM_DEBUG is set)"
                    msg = _graymsg( msg)
                env.history.message( msg)
            simopts.MinimizeThresholdEndRMS = endRMS # for sim.so, but also grabbed from here later by other code in this file
            simopts.MinimizeThresholdEndMax = endMax # ditto
            simopts.MinimizeThresholdCutoverRMS = cutoverRMS
            simopts.MinimizeThresholdCutoverMax = cutoverMax
##            # only some of the following are needed elsewhere; maybe they could be grabbed from simopts but I'm not sure
##            self.endRMS = endRMS
##            self.endMax = endMax
##            self.cutoverRMS = cutoverRMS
##            self.cutoverMax = cutoverMax
        except:
            print_compact_traceback("error in set_minimize_threshhold_prefs (the ones from the last run might be used): ")
            warn("internal error setting convergence criteria; the wrong ones might be used.")
            pass
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
            if DEBUG_SIM: #bruce 051115 revised this debug code
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
                ###BUG: the above line may have never been ported to Qt4; for me it's saying AttributeError: setArguments.
                # (One way to make it happen is to remove sim.so but leave the simulator executable accessible.)
                # [bruce 070601 comment]
            if self._movie.watch_motion:
                env.history.message(orangemsg("(watch motion in real time is only implemented for pyrex interface to simulator)"))
                # note: we have no plans to change that; instead, the pyrex interface will become the usual one
                # except for background or remote jobs. [bruce 060109]
            if not self._movie.create_movie_file:
                env.history.message(orangemsg("(option to not create movie file is not yet implemented)")) # for non-pyrex sim
                # NFR/bug 1286 not useful for non-pyrex sim, won't be implemented, this msg will be revised then
                # to say "not supported for command-line simulator"
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
            if DEBUG_SIM:
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
        statusBar = self.win.statusBar()
        progressReporter = FileSizeProgressReporter(movie.filename, filesize)
        self.errcode = statusBar.show_progressbar_and_stop_button(
            progressReporter,
            cmdname = self.cmdname, #bruce 060112
            showElapsedTime = True )
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
                pbarCaption = "Adjust" # might be changed below
                    #bruce 050415: this string used to be tested in ProgressBar.py, so it couldn't have "All" or "Selection".
                    # Now it can have them (as long as it starts with Minimize, for now) --
                    # so we change it below (to caption from caller), or use this value if caller didn't provide one.
                pbarMsg = "Adjusting..."
            # Write XYZ trajectory file.
            else:
                filesize = movie.totalFramesRequested * ((natoms * 28) + 25) # multi-frame xyz filesize (estimate)
                pbarCaption = "Save File" # might be changed below
                pbarMsg = "Saving XYZ trajectory file " + os.path.basename(moviefile) + "..."
        else:
            # Multiframe minimize
            if mflag:
                filesize = (max(100, int(sqrt(natoms))) * natoms * 3) + 4
                pbarCaption = "Adjust" # might be changed below
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
        """
        #doc
        """
        movie = self._movie
        if debug_flags.atom_debug and movie.duration:
            print "atom_debug: possible bug: movie.duration was already set to", movie.duration
        movie.duration = 0.0 #k hopefully not needed
        # provide a reference frame for later movie-playing (for complete fix of bug 1297) [bruce 060112]
        movie.ref_frame = (self.__frame_number,  A(map(lambda a: a.sim_posn(), movie.alist))) # see similar code in class Movie
            #e this could be slow, and the simobj already knows it, but I don't think getFrame has access to it [bruce 060112]
        simopts = self._simopts
        simobj = self._simobj

        if self.mflag:
            numframes = 0
        else:
            numframes = simopts.NumFrames
        progressBar = self.win.statusBar().progressBar
        progressBar.reset()
        progressBar.setRange(0, numframes)
        progressBar.setValue(0)
        progressBar.show()

        self.abortHandler = AbortHandler(self.win.statusBar(), self.cmdname)

        try:
            self.remove_old_moviefile(movie.filename) # can raise exceptions #bruce 051230 split this out
        except:
            #bruce 060705 do this here -- try not to prevent the upcoming sim
            print_compact_traceback("problem removing old moviefile, continuing anyway: ")
            env.history.message(orangemsg("problem removing old moviefile, continuing anyway"))

        try:
            self.remove_old_tracefile(self.traceFileName)
        except:
            #bruce 060705 do this here -- try not to prevent the upcoming sim
            print_compact_traceback("problem removing old tracefile, continuing anyway: ")
            env.history.message(orangemsg("problem removing old tracefile, continuing anyway"))

        try:
            if not self._movie.create_movie_file:
                env.history.message(orangemsg("(option to not create movie file is not yet implemented)")) # for pyrex sim
                # NFR/bug 1286; other comments describe how to implement it; it would need a warning
                # (esp if both checkboxes unchecked, since no frame output in that case, tho maybe tracef warnings alone are useful)
            editwarning = "Warning: editing structure while watching motion causes tracebacks; cancelling an abort skips some real time display time"
            if self._movie.watch_motion: #bruce 060705 added this condition
                if not seen_before(editwarning): #bruce 060317 added this condition
                    env.history.message(orangemsg( editwarning ))
            env.call_qApp_processEvents() # so user can see that history message

            ###@@@ SIM CLEANUP desired: [bruce 060102]
            # (items 1 & 2 & 4 have been done)
            # 3. if callback caller in C has an exception from callback, it should not *keep* calling it, but reset it to NULL

            # wware 060309, bug 1343
            self.startTime = start = time.time()

            if self.abortHandler.getPressCount() < 1:
                # checked here since above processEvents can take time, include other tasks

                # do these before entering the "try" clause
                # note: we need the frame callback even if not self._movie.watch_motion,
                # since it's when we check for user aborts and process all other user events.
                frame_callback = self.sim_frame_callback
                trace_callback = self.tracefile_callback

                minflag = movie.minimize_flag
                    ###@@@ should we merge this logic with how we choose the simobj class? [bruce 060112]

                self.tracefileProcessor = TracefileProcessor(self, minimize = minflag, simopts = simopts)
                    # so self.tracefile_callback does something [bruce 060109]

                from sim import SimulatorInterrupted #bruce 060112 - not sure this will work here vs outside 'def' ###k
                self.sim_frame_callback_prep()
                if DebugMenuMixin.sim_params_set:
                    for attr, expected in DebugMenuMixin.sim_param_values.items():
                        found = getattr(simobj, attr)
                        if found != expected:
                            env.history.message(orangemsg(attr + ' expected=' + str(expected) + ' found=' + str(found)))
                try:
                    thePyrexSimulator().run( frame_callback = frame_callback, trace_callback = trace_callback )
                        # note: if this calls a callback which raises an exception, that exception gets
                        # propogated out of this call, with correct traceback info (working properly as of sometime on 060111).
                        # If a callback sets simobj.Interrupted (but doesn't raise an exception),
                        # this is turned into an exception like "sim.SimulatorInterrupted: simulator was interrupted".
                        # It also generates a tracefile line "# Warning: minimizer run was interrupted "
                        # (presumably before that exception gets back to here,
                        #  which means a tracefile callback would presumably see it if we set one --
                        #  but as of 060111 there's a bug in which that doesn't happen since all callbacks
                        #  are turned off by Interrupted).
                    if debug_flags.atom_debug:
                        print "atom_debug: pyrex sim: returned normally"
                except SimulatorInterrupted:
                    self.pyrexSimInterrupted = True   # wware 060323 bug 1725
                    # This is the pyrex sim's new usual exit from a user abort, as of sometime 060111.
                    # Before that it was RuntimeError, but that could overlap with exceptions raised by Python callbacks
                    # (in fact, it briefly had a bug where all such exceptions turned into RuntimeErrors).
                    #
                    # I didn't yet fully clean up this code for the new exception. [bruce 060112] ####@@@@
                    if debug_sim_exceptions: #bruce 060111
                        print_compact_traceback("fyi: sim.go aborted with this: ")
                    # following code is wrong unless this was a user abort, but I'm too lazy to test for that from the exception text,
                    # better to wait until it's a new subclass of RuntimeError I can test for [bruce 060111]
                    env.history.statusbar_msg("Aborted")
                    if debug_flags.atom_debug:
                        print "atom_debug: pyrex sim: aborted"
                    if self.PREPARE_TO_CLOSE:
                        # wware 060406 bug 1263 - exiting the program is an acceptable way to leave this loop
                        self.errcode = -1
                    elif self.abortHandler.getPressCount() < 1:
                        if not debug_sim_exceptions:
                            #bruce 060712
                            print_compact_traceback("fyi: sim.go aborted with this: ")
                        msg3 = "possible bug in simulator: abort not caused by abortbutton"
                        env.history.message(redmsg(msg3)) #bruce 060712
                        print "error: abort without abortbutton doing it (did a subtask intervene and finish it?)"
                        print " (or this can happen due to sim bug in which callback exceptions turn into RuntimeErrors)"####@@@@
                        self.abortHandler.finish()
                        self.abortHandler = None
                    ## bug: this fails to cause an abort to be reported by history. might relate to bug 1303.
                    # or might only occur due to current bugs in the pyrex sim, since I think user abort used to work. [bruce 060111]
                    # Initial attempt to fix that -- need to improve errcode after reviewing them all
                    # (check for errorcode spelling error too? or rename it?) ####@@@@
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
            self.errcode = FAILURE_ALREADY_DOCUMENTED
            self.abortHandler.finish() # whether or not there was an exception and/or it aborted
            self.abortHandler = None
            return

        env.history.progress_msg("") # clear out elapsed time messages
        env.history.statusbar_msg("Done.") # clear out transient statusbar messages

        self.abortHandler.finish() # whether or not there was an exception and/or it aborted
        self.abortHandler = None
        return

    __last_3dupdate_time = -1
    __last_progress_update_time = -1
    __frame_number = 0 # starts at 0 so incrementing it labels first frame as 1 (since initial frame is not returned)
        #k ought to verify that in sim code -- seems correct, looking at coords and total number of frames
        # note: we never need to reset __frame_number since this is a single-use object.
        # could this relate to bug 1297? [bruce 060110] (apparently not [bruce 060111])
##    __sim_work_time = 0.05 # initial value -- we'll run sim_frame_callback_worker 20 times per second, with this value
    __last_3dupdate_frame = 0
    __last_pytime = 0.03 # guess (this is a duration)

    def sim_frame_callback_prep(self):
        self.__last_3dupdate_time = self.__last_progress_update_time = time.time()

    def sim_frame_callback_update_check(self, simtime, pytime, nframes):
        "[#doc is in SimSetup.py and in caller]"
        #bruce 060705 revised this, so self.update_cond of None is not an error, so it can be the usual way to say "never update"
        res = True # whether to update this time
        use_default_cond = False
        if self.update_cond == '__default__':
            use_default_cond = True
        elif self.update_cond:
            try:
                res = self.update_cond(simtime, pytime, nframes) # res should be a boolean value
            except:
                self.update_cond = '__default__' # was None
                print_compact_traceback("exception in self.update_cond ignored, reverting to default cond: ")
                use_default_cond = True
        else:
            res = False # was: use_default_cond = True
        if use_default_cond:
            try:
                res = (simtime >= max(0.05, min(pytime * 4, 2.0)))
            except:
                print_compact_traceback("exception in default cond, just always updating: ")
                res = True
##        if res and debug_flags.atom_debug: # DO NOT COMMIT THIS, even with 'if res' -- might print too often and slow it down
##            print "debug: %d sim_frame_callback_update_check returns %r, args" % (self.__frame_number,res), \
##                  simtime, pytime, nframes #bruce 060712
        return res

    def sim_frame_callback(self, last_frame):
        "Per-frame callback function for simulator object."
        from sim import SimulatorInterrupted
        if last_frame and env.debug():
            print "debug: last_frame is true" #bruce 060712
        # Note: this was called 3550 times for minimizing a small C3 sp3 hydrocarbon... better check the elapsed time quickly.
        #e Maybe we should make this into a lambda, or even code it in C, to optimize it.
        if self.PREPARE_TO_CLOSE:
            # wware 060406 bug 1263 - if exiting the program, interrupt the simulator
            from sim import SimulatorInterrupted
            raise SimulatorInterrupted
        self.__frame_number += 1
        if debug_all_frames:
            from sim import theSimulator
            if debug_sim_exceptions:
                # intentionally buggy code
                print "frame %d" % self.__frame_number, self._simobj.getTheFrame() # this is a bug, that attr should not exist
            else:
                # correct code
                print "frame %d" % self.__frame_number, theSimulator().getFrame()[debug_all_frames_atom_index]
            pass
        try:
            # Decide whether to update the 3D view and/or the progress indicators.
            # Original code: let sim use up most of the real time used, measuring redraw timing in order to let that happen.
            # see below for more info.
            #bruce 060530 generalizing this to ask self.update_cond how to decide.
            now = time.time() # real time
            simtime = now - self.__last_3dupdate_time # time the sim has been churning away since the last update was completed
            pytime = self.__last_pytime
            nframes = self.__frame_number - self.__last_3dupdate_frame
            update_3dview = self.sim_frame_callback_update_check( simtime, pytime, nframes ) # call this even if later code overrides it
            # always show the last frame - wware 060314
            if last_frame or debug_all_frames:
                update_3dview = True

            # now we know whether we want to update the 3d view (and save new values for the __last variables used above).
            if update_3dview:
                if debug_pyrex_prints:
                    print "sim hit frame %d in" % self.__frame_number, simtime
                        #e maybe let frame number be an arg from C to the callback in the future?
                self.__last_3dupdate_frame = self.__frame_number
                self.__last_3dupdate_time = now_start = now
                    # this gets set again below, and again [060712] after all time spent in this function when update_3dview is true;
                    # this set is probably not needed, but it may help with debugging or exceptions sometimes;
                    # the later intermediate one is the same, except it's more likely that it may help with those things.
                    # [bruce 060712 revised this comment & related code]
                try:
                    self.sim_frame_callback_worker( self.__frame_number) # might call self.abort_sim_run() or set self.need_process_events
                except:
                    print_compact_traceback("exception in sim_frame_callback_worker, aborting run: ")
                    self.abort_sim_run("exception in sim_frame_callback_worker(%d)" % self.__frame_number ) # sets flag inside sim object
                self.__last_3dupdate_time = time.time() # this will be set yet again (see comment above)
                # [following comment might be #obs, but I don't understand the claim of an effect on abortability -- bruce 060712]
                # use this difference to adjust 0.05 above, for the upcoming period of sim work;
                # note, in current code this also affects abortability

                # pytime code moved from here to end of method, bruce 060712, to fix bad logic bug introduced 060601,
                # which caused A8 watch realtime "as fast as possible" to be far slower than in A7, due to rendering time
                # being counted as simtime (which was because rendering was moved out of sim_frame_callback_worker on 060601)

                # update 'now' for use in progress_update decision
                now = self.__last_3dupdate_time
                pass

            if now >= self.__last_progress_update_time + 1.0 or update_3dview and now >= self.__last_progress_update_time + 0.2:
                # update progressbar [wware 060310, bug 1343]
                # [optim by bruce 060530 -- at most once per second when not updating 3d view, or 5x/sec when updating it often]
                self.need_process_events = True
                self.__last_progress_update_time = now
                msg = None
                # wware 060309, bug 1343, 060628, bug 1898
                tp = self.tracefileProcessor
                if tp:
                    pt = tp.progress_text()
                    if pt:
                        msg = self.cmdname + ": " + pt
                if msg is not None:
                    env.history.statusbar_msg(msg)
                if self.mflag:
                    # Minimization, give "Elapsed Time" message
                    msg = "Elapsed time: " + hhmmss_str(int(time.time() - self.startTime))
                else:
                    # Dynamics, give simulation frame number, total frames, and time, wware 060419
                    msg = (("Frame %d/%d, T=" % (self.__frame_number, self.totalFramesRequested)) +
                           hhmmss_str(int(time.time() - self.startTime)))
                env.history.progress_msg(msg)
                if self.mflag:
                    self.win.statusBar().progressBar.setValue(0)
                else:
                    self.win.statusBar().progressBar.setValue(self.__frame_number)
                pass

            # do the Qt redrawing for either the GLPane or the status bar (or anything else that might need it),
            # only if something done above set a flag requesting it
            self.sim_frame_callback_updates() # checks/resets self.need_process_events, might call call_qApp_processEvents
                #bruce 060601 bug 1970

            if update_3dview:
                #bruce 060712 fix logic bug introduced on 060601 [for Mac/Linux A8, though the bug surely affects Windows A8 too] --
                # measure pytime only now, so it includes GLPane redraw time as it needs to.
                # (This also means it includes sbar updates and redraw, but only when update_3dview occurred;
                #  that makes sense, since what it controls is the frequency of the redraws of all kinds that happen then,
                #  but not the frequency of the progress_update sbar redraws that sometimes happen not then (at most one per second).)
                self.__last_3dupdate_time = time.time() # this is the last time we set this, in this method run
                pytime = self.__last_3dupdate_time - now_start
                self.__last_pytime = pytime
                if debug_pyrex_prints:
                    print "python stuff when update_3dview took", pytime
                    # old results of that, before we did nearly so much sbar updating:
                    # python stuff took 0.00386619567871 -- for when no real work done, just overhead; small real egs more like 0.03
                if debug_timing_loop_on_sbar:
                    # debug: show timing loop properties on status bar
                    msg = "sim took %0.3f, hit frame %03d, py took %0.3f" % \
                        (simtime, self.__frame_number, pytime)
                    env.history.statusbar_msg(msg)
                pass
            pass

        except SimulatorInterrupted, e:
            # With the precautions on the sim side, in sim.pyx and simhelp.c, the only time we'll
            # ever get a SimulatorInterrupted exception is as the result of an actual interruption
            # of the simulator, not as a result of any exception thrown by a Python callback or by
            # any anomalous occurrence in the simulator C code. We don't want a traceback printed
            # for a simulator interruption so in this event, just ignore the exception.
            # wware, bug 2022, 060714
            pass
        except:
            #bruce 060530 -- ideally we'd propogate the exception up to our caller the sim,
            # and it would propogate it back to the python calling code in this object,
            # so there would be no need to print it here. But that seems to be broken now,
            # whether in the sim or in the calling Python I don't know, so I'll print it here too.
            # But then I'll reraise it for when that gets fixed, and since even now it does succeed
            # in aborting the sim.
            print_compact_traceback("exception in sim_frame_callback (will be propogated to sim): ")
            raise
        return # from sim_frame_callback

    aborting = False #bruce 060601
    need_process_events = False #bruce 060601

    def sim_frame_callback_worker(self, frame_number): #bruce 060102
        """
        Do whatever should be done on frame_callbacks that don't return immediately
        (due to not enough time passing), EXCEPT for Qt-related progress updates other than gl_update --
        caller must do those separately in sim_frame_callback_updates, if this method sets self.need_process_events.
        Might raise exceptions -- caller should protect itself from them until the sim does.
        + stuff new frame data into atom positions
          +? fix singlet positions, if not too slow
        + gl_update
        """
        if not self.aborting: #bruce 060601 replaced 'if 1'
            if self.abortHandler and self.abortHandler.getPressCount() > 0:
                # extra space to distinguish which line got it -- this one is probably rarer, mainly gets it if nested task aborted(??)
                self.abort_sim_run("got real  abort at frame %d" % frame_number) # this sets self.aborting flag
##            # mflag == 1 => minimize, user preference determines whether we watch it in real time
##            # mflag == 0 => dynamics, watch_motion (from movie setup dialog) determines real time
##            elif ((not self.mflag and self._movie.watch_motion) or
##                  (self.mflag and env.prefs[Adjust_watchRealtimeMinimization_prefs_key])):
            elif self._movie.watch_motion:
                from sim import theSimulator
                frame = theSimulator().getFrame()
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
                self.need_process_events = True #bruce 060601
        return

    def sim_frame_callback_updates(self): #bruce 060601 split out of sim_frame_callback_worker so it can be called separately
        """
        Do Qt-related updates which are needed after something has updated progress bar displays or done gl_update
        or printed history messages, if anything has set self.need_process_events to indicate it needs this
        (and reset that flag):
        - tell Qt to process events
        - see if user aborted, if so, set flag in simulator object so it will abort too
          (but for now, separate code will also terminate the sim run in the usual way,
           reading redundantly from xyz file)
        """
        if self.need_process_events:
            # tell Qt to process events (for progress bar, its abort button, user moving the dialog or window, changing display mode,
            #  and for gl_update)
            self.need_process_events = False
            env.call_qApp_processEvents()
            self.need_process_events = False # might not be needed; precaution in case of recursion
            #e see if user aborted
            if self.abortHandler and self.abortHandler.getPressCount() > 0:
                self.abort_sim_run("frame %d" % self.__frame_number) # this also sets self.aborting [bruce 06061 revised text]
        return

    def tracefile_callback(self, line): #bruce 060109, revised 060112; needs to be fast; should optim by passing step method to .go
        tp = self.tracefileProcessor
        if tp:
            tp.step(line)

    def abort_sim_run(self, why = "(reason not specified by internal code)" ): #bruce 060102
        "#doc"
        wasaborting = self.aborting
        self.aborting = True #bruce 060601
        self.need_process_events = True #bruce 060601 precaution; might conceivably improve bugs in which abort confirm dialog is not taken down
        self._simopts.Interrupted = True
        if not self.errcode:
            self.errcode = -1
            ####@@@@ temporary kluge in case of bugs in RuntimeError from that or its handler;
            # also needed until we clean up our code to use the new sim.SimulatorInterrupt instead of RuntimeError [bruce 060111]
        if not wasaborting: #bruce 060601 precaution
            env.history.message( redmsg( "aborting sim run: %s" % why ))
        return

    tracefileProcessor = None

    def print_sim_warnings(self): #bruce 050407; revised 060109, used whether or not we're not printing warnings continuously
        """
        Print warnings and errors from tracefile (if this was not already done);
        then print summary/finishing info related to tracefile.
        Note: this might change self.said_we_are_done to False or True, or leave it alone.
        """
        # Note: this method is sometimes called after errors, and that is usually a bug but might sometimes be good;
        # caller needs cleanup about this.
        # Meanwhile, possible bug -- not sure revisions of 060109 (or prior state) is fully safe when called after errors.
        if not self.tracefileProcessor:
            # we weren't printing tracefile warnings continuously -- print them now
            try:
                simopts = self._simopts
            except:
                # I don't know if this can happen, no time to find out, not safe for A8 to assume it can't [bruce 060705]
                print "no _simopts"
                simopts = None
            self.tracefileProcessor = TracefileProcessor(self, simopts = simopts)
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

    def writeTrajectoryAtomIdMapFile(self, filename, used_atoms, all_atoms):
        """
        Write a file that maps the ids of the atoms actually used for simulation
        (used_atoms) to the atom ids of the same atoms within the complete
        structure (a Part) as it was stored in an MMP file (all_atoms).

        @param filename: pathname of file to create and write to.

        @param used_atoms: dict of atoms used (atom.key -> atom id used for sim)

        @param all_atoms: dict of all atoms in one Part (atom.key -> atom id
                          used when writing the file for that Part)
        """
        #brian & bruce 080325
        print "writeTrajectoryAtomIdMapFile", filename, \
            len(used_atoms), len(all_atoms) # remove when works @@@@@
        try:
            fileHandle = open(filename, 'w')

            header1 = "# Format: simulation_atom_id mmp_file_atom_id\n"
                # format uses -1 for missing atom errors (should never happen)
            fileHandle.write(header1)

            header2 = "# (%d atoms used, %d atoms in all)\n" % \
                      ( len(used_atoms), len(all_atoms) )
            fileHandle.write(header2)

            # compute the data
            data = {}
            for key, used_atom_id in used_atoms.iteritems():
                all_atoms_id = all_atoms.get(key, -1)
                if all_atoms_id == -1:
                    print "error: atom %r is in used_atoms (id %r) " \
                          "but not all_atoms" % (key, used_atom_id)
                    # todo: if this ever happens, also print
                    # a red summary message to history
                data[used_atom_id] = all_atoms_id
                continue
            items = data.items()
            items.sort()

            # write the data
            for used_atom_id, all_atoms_id in items:
                fileHandle.write("%s %s\n" % (used_atom_id, all_atoms_id))

            fileHandle.write("# end\n")
            fileHandle.close()

        except:
            msg = self.cmdname + ": Failed to write [%s] " \
                  "(the simulation atom id to mmp file atom id map file)." % \
                  filename
            env.history.message(redmsg(msg))
        return

    pass # end of class SimRunner

# ==

_print_sim_comments_to_history = False

"""
Date: 12 Jan 2006
From: ericm
To: bruce
Subject: Minimize trace file format

Here's the code that writes the trace file during minimize:

    write_traceline("%4d %20f %20f %s %s\n", frameNumber, rms, max_force, callLocation, message);

You can count on the first three not changing.

Note that with some debugging flags on you get extra lines of this
same form that have other info in the same places.  I think you can
just use the rms value for progress and it will do strange things if
you have that debugging flag on.  If you want to ignore those lines,
you can only use lines that have callLocation=="gradient", and that
should work well.

-eric
"""

class TracefileProcessor: #bruce 060109 split this out of SimRunner to support continuous tracefile line processing
    """
    Helper object to filter tracefile lines and print history messages as they come and at the end
    """
    findRmsForce = re.compile("rms ([0-9.]+) pN")
    findHighForce = re.compile("high ([0-9.]+) pN")
    formattedCommentRegex = re.compile(r'^(# [^:]+:)(.*)')

    def __init__(self, owner, minimize = False, simopts = None):
        """
        store owner in self, so we can later set owner.said_we_are_done = True; also start
        """
        self.owner = owner
            # a SimRunner object; has attrs like part, _movie (with alist), used_atoms, ...
            # the ones we set or use here are said_we_are_done, traceFileName, _movie, part
        self.simopts = simopts #bruce 060705 for A8
        self.minimize = minimize # whether to check for line syntax specific to Minimize
        self.__last_plain_line_words = None # or words returned from string.split(None, 4)
        self.start() # too easy for client code to forget to do this
        self._pattern_atom_id_cache = {} # note: this cache and its associated methods
            # might be moved to another object, like self.owner
        return

    def start(self):
        """
        prepare to loop over lines
        """
        self.seen = {} # whether we saw each known error or warning tracefile-keyword
        self.donecount = 0 # how many Done keywords we saw in there
        self.mentioned_sim_trace_file = False # public, can be set by client code
        self.currentPatternName = ""
        self.PAM5_handles = []

    def step(self, line): #k should this also be called by __call__ ? no, that would slow down its use as a callback.
        """
        do whatever should be done immediately with this line, and save things to do later;
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
                elif debug_flags.atom_debug:
                    print "atom_debug: weird tracef line:", line ####@@@@ remove this? it happens normally at the end of many runs
            return
        if _print_sim_comments_to_history: #e add checkbox or debug-pref for this??
            env.history.message("tracefile: " + line)
        # don't discard initial "#" or "# "
        m = self.formattedCommentRegex.match(line)
        if (m):
            start = m.group(1)
            rest = m.group(2)
            if (start == "# Warning:" or start == "# Error:"):
                self.gotWarningOrError(start, line)
            elif start == "# Done:":
                self.gotDone(start, rest)
            elif start.startswith("# Pattern "):
                self.gotPattern(start, rest)
            ## else:
            ##     print "other formatted trace line: " + line.rstrip()
        return

    def gotWarningOrError(self, start, line):
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

    def gotDone(self, start, rest):
        # "Done:" line - emitted iff it has a message on it; doesn't trigger mention of tracefile name
        # if we see high forces, color the Done message orange, bug 1238, wware 060323
        if 1:
            #bruce 060705
            simopts = self.simopts
            try:
                endRMS = simopts.MinimizeThresholdEndRMS
            except AttributeError:
                print "simopts %r had no MinimizeThresholdEndRMS"
                endRMS = 1.0 # was 2.0
            try:
                endMax = simopts.MinimizeThresholdEndMax
            except AttributeError:
                print "simopts %r had no MinimizeThresholdEndMax"
                endMax = 5.0 # was 2.0
            epsilon = 0.000001 # guess; goal is to avoid orangemsg due to roundoff when printing/reading values
            pass
        foundRms = self.findRmsForce.search(rest)
        if foundRms:
            foundRms = float(foundRms.group(1))
        foundHigh = self.findHighForce.search(rest)
        if foundHigh:
            foundHigh = float(foundHigh.group(1))
        highForces = ((foundRms != None and foundRms > endRMS + epsilon) or
                      (foundHigh != None and foundHigh > endMax + epsilon))
        self.donecount += 1
        text = rest.strip()
        if text:
            line = start + " " + text
            if "# Error:" in self.seen:
                line = redmsg(line)
            elif highForces or ("# Warning:" in self.seen):
                line = orangemsg(line)
            env.history.message(line) #k is this the right way to choose the color?
            # but don't do this, we want the main Done too: [bruce 050415]:
            ## self.owner.said_we_are_done = True
        return

    def gotPattern(self, start, rest):
        """
        """

        if (start == "# Pattern match:"):
            self.gotPatternMatch(rest)
        elif (start == "# Pattern makeVirtualAtom:"):
            self.gotPatternMakeVirtualAtom(rest)
        elif (start == "# Pattern makeBond:"):
            self.gotPatternMakeBond(rest)
        elif (start == "# Pattern setStretchType:"):
            self.gotPatternSetStretchType(rest)
        elif (start == "# Pattern makeVanDerWaals:"):
            self.gotPatternMakeVanDerWaals(rest)
        elif (start == "# Pattern setType:"):
            self.gotPatternSetType(rest)
        else:
            print "gotPattern(): unknown type: ", start, rest

        # if debug_pref is set, create graphical indicators for it
        # (possibly using info created by the always-on processing of the line)
        if pref_create_pattern_indicators():
            self.createPatternIndicator( start, rest)
        return


    # Pattern match: [31] (PAM5-basepair-handle) 2 6 22 13
    # [match number]
    # (pattern name)
    # atoms matched...
    def gotPatternMatch(self, rest):
        line = rest.rstrip().split()
        # pattern match number = line[0]
        self.currentPatternName = line[1]
        # actual atoms matched follow

    # Pattern makeVirtualAtom: [5] {41} 3 1 5 20 11 x 0.814144 0.147775 0.000000
    # [match number]
    # {new atom id}
    # number of parent atoms
    # GROMACS function number
    # parent1, parent2, parent3, parent4
    # parameterA, parameterB, parameterC
    def gotPatternMakeVirtualAtom(self, rest):
        pass

    # Pattern makeBond: [5] {47} {48} 1.046850 834.100000
    # [match number]
    # atom1, atom2 ({} indicates atom created by ND1)
    # ks, r0
    def gotPatternMakeBond(self, rest):
        # note: similar code is present in createPatternIndicator
        line = rest.rstrip().split()
        if (self.currentPatternName == "(PAM5-basepair-handle)"):
            atom1 = self._atomID(line[1])
            atom2 = self._atomID(line[2])
            ks = float(line[3])
            r0 = float(line[4])
            self.PAM5_handles += [[atom1, atom2, ks, r0]]

    # Pattern setStretchType: [9] 12 11 1.000000 509.000000
    # [match number]
    # atom1, atom2 ({} indicates atom created by ND1)
    # ks, r0
    def gotPatternSetStretchType(self, rest):
        pass

    def gotPatternMakeVanDerWaals(self, rest):
        pass

    def gotPatternSetType(self, rest):
        line = rest.rstrip().split()
        atom = self.interpret_pattern_atom_id(line[1])
        atom.setOverlayText(line[2])

    def newAtomPositions(self, positions):
        for handle in self.PAM5_handles:
            atom1 = handle[0]
            atom2 = handle[1]
            ks = handle[2] # N/m
            r0 = handle[3] # pm
            pos1 = positions[atom1-1] # angstroms
            pos2 = positions[atom2-1] # angstroms
            delta = 100.0 * vlen(A(pos1) - A(pos2)) # pm
            force = abs((delta - r0) * ks) # pN
            env.history.message("Force on handle %d: %f pN" % (atom2, force))

    def _atomID(self, idString):
        if (idString.startswith("{")):
            s = idString[1:-1]
            return int(s)
        return int(idString)

    def progress_text(self): ####@@@@ call this instead of printing that time stuff
        """
        Return some brief text suitable for periodically displaying on statusbar to show progress
        """
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

    def createPatternIndicator( self, start, rest): #bruce 080520
        """
        """
        ### TODO: add exception protection to caller.

        # start looks like "# Pattern <patterntype>:"
        patterntype = start[:-1].strip().split()[2]

        assy = self.owner.part.assy

        if patterntype == "makeVirtualAtom":
            # for format details see:
            #
            # http://www.nanoengineer-1.net/mediawiki/index.php?title=Tracefile_pattern_lines
            #
            # which says:
            #
            #   rest looks like
            #
            #     [4] {22} 3 1 1 2 3 x -0.284437 0.710930 0.000000
            #
            #   i.e.
            #
            #     [match sequence] {atom ID} num_parents
            #     function_id parentID1 parentID2 parentID3 parentID4 A B C
            #
            #   In this case, there are only three parents, so parentID4 is "x"
            #   instead of a number.  Function_id 1 with 3 parents only uses two
            #   parameters (A and B), so C is zero.
            #
            #   For a three parent virtual site with function_id 1, here is how you
            #   find the location of the site:
            #
            #   Multiply the vector (parentID2 - parentID1) * A
            #   Multiply the vector (parentID3 - parentID1) * B
            #   Add the above two vectors to parentID1
            #
            #   This is the only style of virtual site currently in use.  See the
            #   GROMACS user manual for the definition of other types of virtual sites.
            words = rest.strip().split()
            ( matchseq, site_atom_id, num_parents, function_id,
              parentID1, parentID2, parentID3, parentID4,
              A, B, C, ) = words
            if 'killing old site_atoms before this point is nim': ####
                site_atom = self.interpret_pattern_atom_id( site_atom_id, ok_to_not_exist = True)
                if site_atom is not None:
                    site_atom.kill()
                    # review: will this automatically clear out the dict entry which maps site_atom_id to site_atom??
                pass
            num_parents = int(num_parents)
            function_id = int(function_id)
            parent_atoms = map( self.interpret_pattern_atom_id, \
                [parentID1, parentID2, parentID3, parentID4][:num_parents] )
            A, B, C = map(float, [A, B, C])
            if (num_parents, function_id) == (3, 1):
                # the only style of virtual site currently in use (as of 20080501)
                from model.virtual_site_indicators import add_virtual_site

                site_params = ( function_id, A, B)
                mt_name = "%s %s %0.2f %0.2f" % (matchseq, site_atom_id, A, B)
                site_atom = add_virtual_site(assy, parent_atoms, site_params,
                                             MT_name = mt_name
                                            )
                self.define_new_pattern_atom_id(site_atom_id, site_atom)
                assy.w.win_update() ### IMPORTANT OPTIM: do this only once, later (not in this method)
                ## self.needs_win_update = True -- how often to check this and do a real update??
            else:
                print "unrecognized kind of virtual site:", start + " " + rest.strip()
            pass
        elif patterntype == "makeBond":
            # note: similar code is present in gotPatternMakeBond
            #
            # Pattern makeBond: [5] {47} {48} 1.046850 834.100000
            # [match number]
            # atom1, atom2 ({} indicates atom created by ND1)
            # ks, r0
            words = rest.strip().split()
            ( matchseq, atom_id1, atom_id2, ks_s, r0_s, ) = words
            atom1 = self.interpret_pattern_atom_id(atom_id1)
            atom2 = self.interpret_pattern_atom_id(atom_id2)
            ks = float(ks_s) # N/m
            r0 = float(r0_s) # pm
            ## print "strut: r0: %f ks: %f" % (r0, ks), atom1, "-", atom2
            # create a strut between atom1 and atom2, length r0, stiffness ks.
            atoms = [atom1, atom2]
            bond_params = ( ks, r0 )
            mt_name = "%s %s-%s" % (matchseq, atom1, atom2) # ks and r0 too?
                # future: not always used, only used if atoms are not virtual sites
            from model.virtual_site_indicators import add_virtual_bond
            add_virtual_bond( assy, atoms, bond_params, MT_name = mt_name)
            pass

        return # from createPatternIndicator

    def interpret_pattern_atom_id(self, id_string, ok_to_not_exist = False):
        """
        Interpret a pattern atom id string of the form "23" or "{23}"
        as a real atom (using self.owner._movie.alist to map atom id number
        (as index in that list) to atom). Cache interpretations in self,
        for efficiency and so new atoms can be added without modifying alist.

        @return: the atom, or None if it doesn't exist and ok_to_not_exist.
        """
        # note: this method & its cache may need to be moved to another object.
        try:
            return self._pattern_atom_id_cache[ id_string ]
        except KeyError:
            atom_id_num = self._atomID( id_string)
            atom_id_index = atom_id_num - 1
            alist = self.owner._movie.alist
            if not (0 <= atom_id_index < len(alist)):
                # atom does not exist in alist
                if ok_to_not_exist:
                    return None
                else:
                    assert 0, "atom_id_num %d not found, only %d atoms" % \
                              ( atom_id_num, len(alist))
                    return None
                pass
            res = alist[atom_id_index]
            self._pattern_atom_id_cache[ id_string ] = res
            return res
        pass

    def define_new_pattern_atom_id( self, id_string, atom):
        if self._pattern_atom_id_cache.has_key( id_string ):
            old_atom = self._pattern_atom_id_cache[ id_string ]
            print "killing old_atom", old_atom # should not happen by the time we're done, maybe never
            old_atom.kill() ###k
        self._pattern_atom_id_cache[ id_string ] = atom
        print "defined", id_string, atom #####
        return

    pass # end of class TracefileProcessor

# this global needs to preserve its value when we reload!
try:
    last_sim_tracefile
except:
    last_sim_tracefile = None
else:
    pass

def part_contains_pam_atoms(part, kill_leftover_sim_feedback_atoms = False):
    """
    Returns non-zero if the given part contains any pam atoms.
    Returns less than zero if the part contains a mixture of pam and
    other atoms, or more than one type of pam atom.  Singlets
    and "sim feedback atoms" (role == 'virtual-site') don't count.

    @param kill_leftover_sim_feedback_atoms: if true, do that as a side effect.
    """
    # probably written by EricM
    #bruce 080520 added kill_leftover_sim_feedback_atoms option,
    # and made this function non-private
    from utilities.constants import MODEL_PAM5, MODEL_PAM3

    #             PAM3   PAM5  other
    contents = [ False, False, False ]
    kill_these = []

    def check_for_pam(n):
        if (isinstance(n, Chunk)):
            for a in n.atoms.itervalues():
                elt = a.element
                if (elt is Singlet):
                    continue
                if elt.role == 'virtual-site':
                    if kill_leftover_sim_feedback_atoms:
                        kill_these.append(a)
                elif (elt.pam == MODEL_PAM3):
                    contents[0] = True
                elif (elt.pam == MODEL_PAM5):
                    contents[1] = True
                else:
                    contents[2] = True

    part.topnode.apply2all(check_for_pam)

    # do this last, since it can't be done during apply2all:
    for atom in kill_these:
        atom.kill()

    if (contents[0]):     # has PAM3
        if (contents[1]): # has PAM5
            return -2     # mixture of PAM3 and PAM5
        if (contents[2]): # has other
            return -1     # mixture of PAM3 and other
        return 1          # just PAM3
    if (contents[1]):     # has PAM5
        if (contents[2]): # has other
            return -1     # mixture of PAM5 and other
        return 1          # just PAM5
    return 0              # just other (or empty)

# ==

# writemovie used to be here, but is now split into methods
# of class SimRunner above [bruce 050401]

# ... but here's a compatibility stub... i guess

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

def writemovie(part,
               movie,
               mflag = 0,
               simaspect = None,
               print_sim_warnings = False,
               cmdname = "Simulator",
               cmd_type = 'Minimize',
               useGromacs = False,
               background = False,
               useAMBER = False,
               typeFeedback = False):
        #bruce 060106 added cmdname
    """
    Write an input file for the simulator, then run the simulator,
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
    if print_sim_warnings = True. Someday this should happen in real time;
    for now [as of 050407] it happens once when we're done.
    """
    #bruce 050325 Q: why are mflags 0 and 2 different, and how? this needs cleanup.

    hasPAM = part_contains_pam_atoms(part)
        # POSSIBLE BUG: this check is done on entire Part
        # even if we're only minimizing a subset of it.
    if (hasPAM < 0):
        if (hasPAM < -1):
            msg = "calculations with mixed PAM3 and PAM5 atoms are not supported"
        else:
            msg = "calculations with mixed PAM and other atoms are not supported"
        env.history.message(orangemsg(msg))
        # note: no return statement (intentional?)
    hasPAM = not not hasPAM
    simrun = SimRunner(part,
                       mflag,
                       simaspect = simaspect,
                       cmdname = cmdname,
                       cmd_type = cmd_type,
                       useGromacs = useGromacs,
                       background = background,
                       hasPAM = hasPAM,
                       useAMBER = useAMBER,
                       typeFeedback = typeFeedback)
        #e in future mflag should choose subclass (or caller should)
    movie._simrun = simrun #bruce 050415 kluge... see also the related movie._cmdname kluge
    movie.currentFrame = 0 #bruce 060108 moved this here, was in some caller's success cases
    movie.realtime_played_framenumber = 0 #bruce 060108
    movie.minimize_flag = not not mflag # whether we're doing some form of Minimize [bruce 060112]
    # wware 060420 - disable atom/bond highlighting while simulating, improves simulator performance
    part.assy.o.is_animating = True
    simrun.run_using_old_movie_obj_to_hold_sim_params(movie)
    part.assy.o.is_animating = False
    if 1:
        #bruce 060108 part of fixing bug 1273
        fn = movie.realtime_played_framenumber
        if fn:
            if not movie.minimize_flag: #bruce 060112
                #e a more accurate condition would be something like "if we made a movie file and bragged about it"
                msg = "(current atom positions correspond to movie frame %d)" % fn
                env.history.message(greenmsg(msg))
        assert movie.currentFrame == fn
    if print_sim_warnings and simrun.errcode != FAILURE_ALREADY_DOCUMENTED:
        # If there was a clear error then don't print a lot of lower-priority less urgent stuff
        # after the bright red error message.
        try:
            simrun.print_sim_warnings()
                #bruce 051230 comment: this runs even if sim executable was not found; why?? ####@@@@
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
    """
    Read a single-frame XYZ file created by the simulator, typically for
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
    from model.elements import Singlet

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
        numAtoms_junk = int(lines[0])
        rms_junk = float(lines[1][4:])
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

def readGromacsCoordinates(filename, atomList, tracefileProcessor = None):
    """
    Read a coordinate file created by gromacs, typically for
    minimizing a part.
       On error, print a message to stdout and also return it to the caller.
       On success, return a list of atom new positions
    in the same order as in the xyz file (hopefully the same order as in alist).
    """
    translateFileName = None
    if (filename.endswith("-out.gro")):
        translateFileName = filename[:-8] + ".translate"
    elif (filename.endswith(".gro")):
        translateFileName = filename[:-4] + ".translate"

    try:
        translateFile = open(translateFileName, "rU")
        dX = float(translateFile.readline()) * 10.0
        dY = float(translateFile.readline()) * 10.0
        dZ = float(translateFile.readline()) * 10.0
        translateFile.close()
    except IOError:
        # Ok for file not to exist, assume no translation
        dX = 0.0
        dY = 0.0
        dZ = 0.0

    try:
        lines = open(filename, "rU").readlines()
    except IOError:
        msg = "readGromacsCoordinates: %s: Can't open or read file." % filename
        print msg
        return msg
    except:
        msg = "readGromacsCoordinates: %s: Exception opening or reading file" % filename
        print_compact_traceback(msg + ": ")
        return msg + " (see console prints)."

    if len(lines) < 3: ##Invalid file format
        msg = "readGromacsCoordinates: %s: File format error (fewer than 3 lines)." % filename
        print msg
        return msg

    newAtomsPos = []
    allAtomPositions = []

    try:
        numAtoms_junk = int(lines[1])
    except ValueError:
        msg = "readGromacsCoordinates: %s: File format error in Line 2" % filename
        print msg
        return msg

    atomIndex = 0
    for line in lines[2:-1]:
        #          1         2         3         4
        #01234567890123456789012345678901234567890123456789
        #    1xxx     A1    1   9.683   9.875   0.051
        xstr = line[20:28]
        ystr = line[28:36]
        zstr = line[36:44]
        extraString = line[44:]
        if (extraString.strip() != ""):
            return "GROMACS minimize returned malformed results (output overflow?)"
        if (xstr == "     nan" or ystr == "     nan" or zstr == "     nan"):
            return "GROMACS minimize returned undefined results"
        try:
            x = float(xstr) * 10.0 + dX
            y = float(ystr) * 10.0 + dY
            z = float(zstr) * 10.0 + dZ
        except ValueError, e:
            return "Error parsing GROMACS minimize results: [%s][%s][%s]" % (xstr, ystr, zstr)
        atomIndex += 1
        if (atomIndex <= len(atomList)):
            # coordinates of virtual sites are reported at end of
            # list, and we want to ignore them.
            newAtomsPos += [[x, y, z]]
        allAtomPositions += [[x, y, z]]
    if (len(newAtomsPos) != len(atomList)):
        msg = "readGromacsCoordinates: The number of atoms from %s (%d) is not matching with the current model (%d)." % \
            (filename, len(newAtomsPos), len(atomList))
        print msg
        return msg

    if (tracefileProcessor):
        tracefileProcessor.newAtomPositions(allAtomPositions)

    return newAtomsPos

# end

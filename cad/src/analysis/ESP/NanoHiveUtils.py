# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
NanoHiveUtils.py

@author: Brian, Mark
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Brian wrote the NH_Connection class.
Mark wrote everything else.

Module classification:

Mostly control & io code. Some model & ui code (via assy arg & assy.w).
Probably "simulation". [bruce 071214]
"""

import foundation.env as env, os, sys, time
from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
from utilities.prefs_constants import nanohive_path_prefs_key, nanohive_enabled_prefs_key
from PyQt4.Qt import Qt, QApplication, QCursor
from widgets.StatusBar import NanoHiveProgressReporter

def get_nh_simspec_filename(basename):
    """
    Return the full path of the Nano-Hive simulation specification file.
    """
    if basename:
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        fn = os.path.normpath(os.path.join(nhdir,str(basename)+"-sim.xml"))
        #print "get_nh_simspec_filename(): filename=", fn
        return fn
    else:
        return None

def get_nh_workflow_filename(basename):
    """
    Return the full path of the Nano-Hive workflow file.
    """
    if basename:
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        fn = os.path.normpath(os.path.join(nhdir,str(basename)+"-flow.tcl"))
        #print "get_nh_workflow_filename(): filename=", fn
        return fn
    else:
        return None

def get_nh_mmp_filename(basename):
    """
    Return the full path of the Nano-Hive MMP input file.
    """
    if basename:
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        fn = os.path.normpath(os.path.join(nhdir,str(basename)+".mmp"))
        #print "get_nh_mmp_filename(): filename=", fn
        return fn
    else:
        return None

def get_nh_espimage_filename(assy, jigname):
    """
    Returns the filename of the ESP Image's png given assy and ESP Image's jigname,
    to be stored in the ESP Image's MMP info record.
    The filename format is "assyname-jigname.png"
    """
    cwd = os.path.join(assy.get_cwd(), assy.name + "-" + jigname + ".png")
    return os.path.normpath(cwd)

def get_nh_home_ORIG():
    """
    Return the Nano-Hive home directory
    """
    nanohive_exe = env.prefs[nanohive_path_prefs_key]

    # On Windows, the default location of the Nano-Hive executable is
    # C:\Program Files\Nano-Hive\bin\win32-x86\NanoHive.exe
    # The home directory is retreived by stripping off the last two directories
    # from the Nano-Hive executable path, which is
    # C:\Program Files\Nano-Hive
    if sys.platform == 'win32':
        head, tail = os.path.split(nanohive_exe)
        head, tail = os.path.split(head)
        nh_home, tail = os.path.split(head)
    return nh_home

def get_nh_home():
    """
    Returns the Nano-Hive home (base) directory for each platform, if it exists. Otherwise, return None.
    """
    if sys.platform == "win32": # Windows
        basedir = "C:\Program Files\Nano-Hive"
    else: # Linux and MacOS
        basedir = "/usr/local/share/Nano-Hive"

    if not os.path.exists(basedir): return None
    return basedir

def get_nh_config_filename():
    """
    Return the full path of the Nano-Hive config.txt file.
    """
    if sys.platform == "win32": # Windows
        fn = os.path.normpath(get_nh_home() + "/conf/configs.txt")
    else: # Linxus and MacOS
        fn = os.path.normpath(os.path.expanduser("~/.Nano-Hive/conf/configs.txt"))

    if not os.path.exists(fn): return None
    return fn

def run_nh_simulation(assy, sim_id, sim_parms, sims_to_run, results_to_save):
    """
    Run a Nano-Hive simulation on the part (assy).  Only the MPQC_ESP plug-in
    used for creating an ESP Image file is supported in A7.

    sim_id is the simulation id of the simulation.  It is used to construct the
    basename of all the simulation files and is the name of the Nano-Hive simulation run.

    sims_to_run is a list of simulations to run, where:
        MPQC_ESP = MPQC ESP Plane
        MPQC_GD = MPQC Gradient Dynamics (not supported in A7)
        AIREBO = AIREBO (not supported in A7)

    results_to_save is a list of results to save, where:
        MEASUREMENTS = Measurements to file
        POVRAYVIDEO = POVRay Video
        NETCDF = NetCDF

    Return values:
        0 = successful
        1 = Nano-Hive plug-in not enabled
        2 = Nano-Hive plug-in path is empty
        3 = Nano-Hive plug-in path points to a file that does not exist
        4 = Nano-Hive plug-in is not Version 1.2b
        5 = Couldn't connect to Nano-Hive instance
        6 = "load" command failed
        7 = "run" command failed
        8 = Simulation aborted
    """
    if not sims_to_run:
        return # No simulations to run in the list.

    # Validate that the Nano-Hive plug-in is enabled.
    if not env.prefs[nanohive_enabled_prefs_key]:
        r = activate_nh_plugin(assy.w)

        if r:
            return 1 # Nano-Hive plug-in not enabled.

    if not env.prefs[nanohive_path_prefs_key]:
        return 2 # Nano-Hive plug-in path is empty

    if not os.path.exists(env.prefs[nanohive_path_prefs_key]):
        return 3 # Nano-Hive plug-in path points to a file that does not exist

    r = verify_nh_program()
    if r:
        return 4 # Nano-Hive plug-in is not Version 1.2b

    if not sim_id:
        sim_id = get_sim_id()

    output_dir = find_or_make_Nanorex_subdir("Nano-Hive") # ~/Nanorex/Nano-Hive

    # Put up the wait cursor.  The cursor will be restored by exit_nh().
    QApplication.setOverrideCursor( assy.w.ArrowWaitCursor )

    # 1. Try to connect to Nano-Hive, get socket.
    # 99% of the time, no socket will be returned since Nano-Hive hasn't been started yet.
    # Let's check, just in case this is a Nano-Hive instance running.
    nh_socket = connect_to_nh()

    if nh_socket:
        kill_nh = False
    else: # No Nano-Hive instance is running.  Start it.
        kill_nh = True
        r = start_nh() # Start Nano-Hive server (instance).

        if r:
            print "Nano-Hive startup aborted."

        # It may take a second or two to connect to the new Nano-Hive instance.
        # Keep trying until we get a socket.  Give up if we haven't connected within 4 seconds.
        start = time.time()
        while not nh_socket:
            time.sleep(0.25)
            nh_socket = connect_to_nh()
            duration = time.time() - start
            if duration > 4.0: # Give up after 4 seconds
                exit_nh(nh_socket, kill_nh) # Only restore's the cursor
                return 5 # Couldn't connect to Nano-Hive socket.

    # 2. Write the MMP file that Nano-Hive will use for the sim run.
    assy.writemmpfile(get_nh_mmp_filename(sim_id))

    # 3. Write the sim-spec file using the parameters from the Nano-Hive dialog widgets
    from analysis.ESP.files_nh import write_nh_simspec_file
    write_nh_simspec_file(sim_id, sim_parms, sims_to_run, results_to_save, output_dir)

    # 4. Write the Sim Workflow file
    from analysis.ESP.files_nh import write_nh_workflow_file
    write_nh_workflow_file(sim_id)

    # 5. Send commands to Nano-Hive.  There can be no spaces in partname.  Need to fix this.
    cmd = 'load simulation -f "' + get_nh_simspec_filename(sim_id) + '" -n ' + sim_id
    #print "NanoHiveUtils.run_nh_simulation(): N-H load command: ", cmd

    success, response = nh_socket.sendCommand(cmd) # Send "load" command.
    if not success:
        print success, response
        exit_nh(nh_socket, kill_nh)
        return 6 # "load" command failed

    cmd = "run " + sim_id
    #print "NanoHiveUtils.run_nh_simulation(): N-H run command: ", cmd

    success, response = nh_socket.sendCommand(cmd) # Send "run" command.
    if not success:
        print success, response
        exit_nh(nh_socket, kill_nh)
        return 7 # "run" command failed

    statusBar = assy.w.statusBar()
    progressReporter = NanoHiveProgressReporter(nh_socket, sim_id)
    r = statusBar.show_progressbar_and_stop_button(progressReporter, "NanoHive", True)

    if r:
        stop_nh_sim(sim_id)
        exit_nh(nh_socket, kill_nh)
        return 8 # simulation aborted

    exit_nh(nh_socket, kill_nh)

    return 0

def activate_nh_plugin(win):
    """
    Opens a message box informing the user that the Nano-Hive plugin
    needs to be enabled and asking if they wish to do so.
    win is the main window object.
    """
    from PyQt4.Qt import QMessageBox
    ret = QMessageBox.warning( win, "Activate Nano-Hive Plug-in",
        "Nano-Hive plug-in not enabled. Please select <b>OK</b> to \n" \
        "activate the Nano-Hive plug-in from the Preferences dialog.",
        "&OK", "Cancel", "",
        0, 1 )

    if ret == 0: # OK
        win.userPrefs.showDialog('Plug-ins') # Show Preferences | Plug-in.
        if not env.prefs[nanohive_enabled_prefs_key]:
            return 1 # Nano-Hive was not enabled by user.

    elif ret == 1: # Cancel
        return 1

    return 0

def verify_nh_program():
    """
    Returns 0 if nanohive_path_prefs_key is the path to the Nano-Hive v1.2b executable.
    Otherwise, returns 1.
    """
    vstring = "Nano-Hive version 1.2.0-beta-1 Copyright (C) 2004,2005 Nano-Hive, LLC"
    r = verify_program(env.prefs[nanohive_path_prefs_key], '-v', vstring)
    return r

# This is a general function that should be moved to utilities
def verify_program(program, version_flag, vstring):
    """
    Verifies a program by running it with the version_flag and matching the output to vstring.
    Returns 0 if there is a match.  Otherwise, returns 1
    """
    if not program:
        return 1

    if not os.path.exists(program):
        return 1

    args = [version_flag]

    from processes.Process import Process

    arguments = []
    for arg in args:
        if arg != "":
            arguments.append(arg)

    print
    print "arguments:", arguments

    p = Process()
    p.start(program, arguments)

    if not p.waitForFinished (10000): # Wait for 10000 milliseconds = 10 seconds
        return 1

    output = 'Not vstring'

    output = str(p.readAllStandardOutput())

    #print "output=", output
    #print "vstring=", vstring

    if output.find(vstring) == -1:
        return 1
    else:
        return 0 # Match found.

def start_nh():
    """
    Starts Nano-Hive server in the background.
    Returns 1 if Nano-Hive path is not set or if the path does not exist.
    Returns 2 if Nano-Hive config file does not exist.
    """
    # Get Nano-Hive executable path from the prefs db.
    nanohive_exe = env.prefs[nanohive_path_prefs_key]

    if not nanohive_exe:
        return 1

    if not os.path.exists(nanohive_exe):
        return 1

    nanohive_config = get_nh_config_filename()

    if not nanohive_config:
        return 2

    args = ['-f', nanohive_config]

    #print "start_nh(): args=", args

    from processes.Process import Process

    arguments = []
    for arg in args:
        if arg != "":
            arguments.append(arg)

    nhProcess = Process()
    nhProcess.start(nanohive_exe, args)

    return 0

def stop_nh_sim(nh_socket, sim_id=None):
    """
    Stops a running Nano-Hive simulation.
    <sim_id> - the id (name) of the simulator to stop.
    """
    if nh_socket:
        if sim_id:
            success, response = nh_socket.sendCommand("stop " + sim_id) # Send "stop" command.
    QApplication.restoreOverrideCursor() # Restore the cursor

def exit_nh(nh_socket, kill_nh):
    """
    Exits (kills) the Nano-Hive instance if kill_nh is True,
    closes the socket and restores the cursor."
    """
    if nh_socket:
        if kill_nh:
            success, response = nh_socket.sendCommand("exit") # Send "exit" command.
        nh_socket.close()
    QApplication.restoreOverrideCursor() # Restore the cursor

def connect_to_nh():
    """
    Connects to a Nano-Hive instance.
    Returns NH_Connection socket if successful, None if failure.
    """
    hostIP = "127.0.0.1"
    port = 3000 # Nano-Hive 1.2b uses port 3000, not 3002 as 1.2a did.  mark 2006-01-04.
    serverTimeout = 5.0
    clientTimeout = 30.0

    method = "NanoHiveUtils.connect_to_nh()"

    nh_conn = NH_Connection() # Obtain connection object

    # Try connecting the Nano-Hive instance.
    success, msg = nh_conn.connect(hostIP, port, serverTimeout, clientTimeout)

    if success:
        success, result = nh_conn.sendCommand("status 1") # Send status command.
        if success:
            msg = method + ": Success: " + str(success)  + "\nMessage: " + str(result)
            #env.history.message(msg)
            #print msg
            return nh_conn

        else:
            msg = method + ": Command Error:\nSuccess=" + str(success)  + "\nMessage: " + str(result)
            #env.history.message(msg)
            #print msg
            return None

    else:
        msg = method + ": Connection Failed:\nSuccess=" + str(success)  + "\nMessage: " + str(msg)
        #env.history.message(msg)
        #print msg
        return None


# Version 2

import socket

class NH_Connection:
    """
    A sockets connection to a Nano-Hive instance.
    """
    def connect(self, hostIP, port, serverTimeout, clientTimeout):
        """
        Connects to the specified N-H instance.

        Parameters:
            hostIP
                The IP address of the N-H host
            port
                The port listened to by the SocketsControl plugin of the N-H host
            serverTimeout
                A float specifying how long, in seconds, to give when reading
                from, and writing to, N-H
            clientTimeout
                A float specifying the timeout period of the SocketsControl
                plugin of the N-H host. Not implemented yet, but this will
                keep the N-H connection alive with "ping" commands

        Returns:
            success indicator
                A one if the N-H instance was successfully connected to, or a
                zero if an error occurred and connection failed
            error message
                If connection failed, describes the problem
        """
        try:
            self.connectionHandle = \
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connectionHandle.connect((hostIP, port))
            self.connectionHandle.settimeout(serverTimeout)

        except socket.error, errorMessage:
            return 0, errorMessage

        return 1, ""


    def close(self):
        """
        Closes the connection to the N-H instance.
        """
        self.connectionHandle.close()


    def sendCommand(self, command):
        """
        Sends a command to the N-H instance and returns the response.

        Parameters:
            command
                The command to send to the N-H instance

        Returns:
            success indicator
                A one if the command was successfully sent and a response was
                received
            response or error message
                If all was successful, the encoded N-H instance response, or a
                description of the error if unsuccessful. The encoded response
                can be decoded with the
                Nano-Hive/data/local/en_resultCodes.txt file
        """
        # Send command
        success = 1
        try:
            self.connectionHandle.send(command)

        except socket.error, errorMessage:
            success = 0

        # Read response length
        if success:
            try:
                responseLengthChars = self.connectionHandle.recv(4)

            except socket.error, errorMessage:
                success = 0

        if success:
            responseLength = ord(responseLengthChars[0])
            responseLength |= ord(responseLengthChars[1]) << 8
            responseLength |= ord(responseLengthChars[2]) << 16
            responseLength |= ord(responseLengthChars[3]) << 24;

            # Read response
            try:
                response = self.connectionHandle.recv(responseLength)

            except socket.error, errorMessage:
                success = 0

        if success:
            return 1, response
        else:
            return 0, errorMessage

# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
NanoHiveUtils.py

$Id$

History:
    
    Brian wrote the NH_Connection class
    Mark wrote everything else

'''
__author__ = "Brian"

import env, os
from platform import find_or_make_Nanorex_subdir
from constants import nanohive_path_prefs_key

def get_nh_simspec_filename(basename):
    '''Return the full path of the Nano-Hive simulation specification file.
    '''
    if basename:
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        return os.path.join(nhdir,str(basename)+"-sim.xml")
    else:
        return None

def get_nh_workflow_filename(basename):
    '''Return the full path of the Nano-Hive workflow file.
    '''
    if basename:
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        return os.path.join(nhdir,str(basename)+"-flow.tcl")
    else:
        return None

def get_nh_mmp_filename(basename):
    '''Return the full path of the Nano-Hive MMP input file.
    '''
    if basename:
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        return os.path.join(nhdir,str(basename)+".mmp")
    else:
        return None

def get_nh_home():    
    '''Return the Nano-Hive home directory'''
    
    # Retreive the Nano-Hive home directory by stripping off the last two directories
    # from the Nano-Hive executable path.
    nanohive_exe = env.prefs[nanohive_path_prefs_key]
    head, tail = os.path.split(nanohive_exe)
    head, tail = os.path.split(head)
    nh_home, tail = os.path.split(head)
    return nh_home

def run_nh_simulation(assy, sim_name, sim_parms, sims_to_run, results_to_save):
    '''Run a Nano-Hive simulation on the part (assy).
    
    sim_name is the name of the simulation.  It is used to construct the basename of all
    the simulation files and is the name of the Nano-Hive simulation run.
    
    sims_to_run is a list of simulations to run, where:
        MPQC_ESP = MPQC ESP Plane
        MPQC_GD = MPQC Gradient Dynamics
        AIREBO = AIREBO
        
    results_to_save is a list of results to save, where:
        MEASUREMENTS = Measurements to file
        POVRAYVIDEO = POVRay Video
        NETCDF = NetCDF

    Return values:
        0 = successful
        1 = couldn't connect to Nano-Hive instance
        2 = load command failed
        3 = run command failed
    '''
    
    if not sims_to_run:
        return # No simulations to run in the list.
        
    # Validate that the Nano-Hive executable exists.
    r = validate_nh_program(None)
    
    if r: # Nano-Hive program was not found/valid.
        return 1 # Simulation Cancelled.
    
    if not sim_name:
        sim_name = get_sim_name()   
        
    from platform import find_or_make_Nanorex_subdir
    output_dir = find_or_make_Nanorex_subdir("Nano-Hive") # ~/Nanorex/Nano-Hive
    
    # 1. Connect to Nano-Hive, get socket.
    nh_socket = connect_to_nanohive()
    
#    if not nh_socket: # Error connecting to Nano-Hive instance
#        return 1
        
    # 2. Write the MMP file that Nano-Hive will use for the sim run.
    assy.writemmpfile(get_nh_mmp_filename(sim_name))
        
    # 3. Write the sim-spec file using the parameters from the Nano-Hive dialog widgets
    from files_nh import write_nh_simspec_file
    write_nh_simspec_file(sim_name, sim_parms, sims_to_run, results_to_save, output_dir)
    
    # 4. Write the Sim Workflow file
    from files_nh import write_nh_workflow_file
    write_nh_workflow_file(sim_name)
    
    if not nh_socket: # Error connecting to Nano-Hive instance
        return 1
    
    # 5. Send commands to Nano-Hive.  There can be no spaces in partname.  Need to fix this.
    cmd = 'load simulation -f "' + get_nh_simspec_filename(sim_name) + '" -n ' + sim_name
    print "NanoHiveUtils.run_nh_simulation(): N-H load command: ", cmd
    
    success, result = nh_socket.sendCommand(cmd) # Send "load" command.
    if not success:
        print success, result
        return 2
    
    cmd = "run " + sim_name
    print "NanoHiveUtils.run_nh_simulation(): N-H run command: ", cmd
    
    success, result = nh_socket.sendCommand(cmd) # Send "run" command.
    if not success:
        print success, result
        return 3
    
    # All done.  Close the socket. 
    nh_socket.close()
    
    return 0

def validate_nh_program(parent):
    '''Checks that the Nano-Hive program path exists in the user pref database
    and that the file it points to exists.  If the Nano-Hive path does not exist, the
    user will be prompted with the file chooser to select the Nano-Hive executable.
    This function does not check whether the Nano-Hive path is actually Nano-Hive.
    
    parent is the parent Qt Window or Dialog.
    
    Returns:  0 = Valid
                    1 = Invalid
    '''
    # Get Nano-Hive executable path from the prefs db
    nanohive_exe = env.prefs[nanohive_path_prefs_key]
    
    if not nanohive_exe:
        msg = "The Nano-Hive executable path is not set.\n"
    elif os.path.exists(nanohive_exe):
        return 0
    else:
        msg = nanohive_exe + " does not exist.\n"
        
    # Nano-Hive Dialog is the parent for messagebox and file chooser.
    ret = QMessageBox.warning( parent, "Nano-Hive Executable Path",
        msg + "Please select OK to set the location of Nano-Hive for this computer.",
        "&OK", "Cancel", None,
        0, 1 )
            
    if ret==0: # OK
        #from UserPrefs import get_gamess_path
        #self.server.program = get_gamess_path(parent)
        from UserPrefs import get_filename_and_save_in_prefs
        nanohive_exe = \
            get_filename_and_save_in_prefs(parent, nanohive_path_prefs_key, 'Choose Nano-Hive Executable')
        if not nanohive_exe:
            return 1 # Cancelled from file chooser.
        
    elif ret==1: # Cancel
        return 1

    return 0

def connect_to_nanohive():
    '''Connects to a Nano-Hive instance.  
    Returns NH_Connection socket if successful, None if failure.
    '''

    import NanoHiveUtils

    hostIP = "127.0.0.1"
    port = 3002 # SpiderMonkey
    serverTimeout = 5.0
    clientTimeout = 30.0
    
    nh_conn = NanoHiveUtils.NH_Connection() # Obtain connection object
    
    # Try connecting the Nano-Hive instance.
    success, msg = nh_conn.connect(hostIP, port, serverTimeout, clientTimeout)
    
    if success:
        success, result = nh_conn.sendCommand("status 1") # Send status command.
        if success:
            msg = "Success: " + str(success)  + "\nMessage: " + str(result)
            env.history.message(msg)
            return nh_conn
            
        else:
            msg = "Command Error:\nSuccess=" + str(success)  + "\nMessage: " + str(result)
            env.history.message(msg)
            return None
        
    else:
        msg = " Connection Failed:\nSuccess=" + str(success)  + "\nMessage: " + str(msg)
        env.history.message(msg)
        return None


# Version 2

import socket


class NH_Connection:
        "A sockets connection to a Nano-Hive instance."
        
        
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
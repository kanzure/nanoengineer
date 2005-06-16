# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
SimServer.py

$Id$
'''
__author__ = "Mark"

import sys

class SimServer:
    '''a SimServer has all the attributes needed to connect to and run a SimJob'''
    
    server_parms = {
        'hostname':'localhost',
        'ipaddress':'127.0.0.1',
        'method':'Local access',
        'engine':'PC GAMESS',
        'program':'C:\\PCGAMESS\\gamess.exe',
        'tmpdir':'C:\\PCGAMESS\\',
        'platform':'Windows',
        'username':'nanorex',
        'password':''}
        
    def __init__(self):
        
        # The parameters (parms) for the SimServer object are provided in a dictionary in key:value pairs
        # For the Gamess Jig, the parms are defined in the jig_Gamess.py.
        #
        # The parms.keys are:
        # name: Server name
        # ipaddress: Server IP Address 
        # engine: Sim engine (GAMESS, nanoSIM-1)
        # program: Full path to the engine program
        # paltform: OS
        # username: User name
        # password: Password
        
        self.parms = SimServer.server_parms
        if sys.platform == 'linux2':
            self.parms['platform'] = 'Linux'
            self.parms['program'] = '/usr/bin/rumgms'
        elif sys.platform == 'darwin':
            self.parms['program'] = '/usr/bin/rumgms'
            self.parms['platform'] = 'Mac Os'
        
        self.parms.keys().sort() # Sort parms.
            
        # WARNING: Bugs will be caused if any of SimJob's own methods or 
        # instance variables had the same name as any of the parameter ('k') values.
        for k in self.parms:
             self.__dict__[k] = self.parms[k]        
                
        self.edit_cntl = None
    
    def __getstate__(self):
        """Called by pickle """
        return self.parms, self.edit_cntl
        
    
    def __setstate__(self, state):
        """Called by unPickle"""
        self.parms, self.edit_cntl = state
        self.set_parms(self.parms)     
    
    def write_parms(self, f):
        'Write server parms to file f'
        
        rem = self.get_comment_character()
            
        f.write (rem + '\n' + rem +  'Server Parameters\n' + rem + '\n')
        for k in self.parms:
            phrase = rem + k + ': ' + str(self.__dict__[k])
            f.write (phrase + '\n')
        f.write (rem+'\n')
    
    def set_parms(self, parms):
        self.parms = parms
        for k in parms:
             self.__dict__[k] = parms[k]        
   
    def get_comment_character(self):
        if sys.platform == 'win32':
            return 'REM ' # Batch file comment for Windows
        else:
            return '# ' # Script file comment for Linux and Mac
            
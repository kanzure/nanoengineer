# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
SimServer.py

$Id$
'''
__author__ = "Mark"

class SimServer:
    '''a SimServer has all the attributes needed to connect to and run a SimJob'''
    
    def __init__(self, parms):
        
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
        
        self.parms = parms.keys()
        self.parms.sort() # Sort parms.
        self.edit_cntl = None
        
        # WARNING: Bugs will be caused if any of SimJob's own methods or 
        # instance variables had the same name as any of the parameter ('k') values.

        for k in parms:
            self.__dict__[k] = parms[k]        
            
    def write_parms(self, f):
        'Write server parms to file f'
        
        rem = self.get_comment_character()
            
        f.write (rem + '\n' + rem +  'Server Parameters\n' + rem + '\n')
        for k in self.parms:
            phrase = rem + k + ': ' + str(self.__dict__[k])
            f.write (phrase + '\n')
        f.write (rem+'\n')
        
    def get_comment_character(self):
        if self.platform == 'win32':
            return 'REM ' # Batch file comment for Windows
        else:
            return '# ' # Script file comment for Linux and Mac
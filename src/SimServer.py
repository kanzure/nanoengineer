# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
SimServer.py

$Id$
'''
__author__ = "Mark"

import sys

class SimServer:
    '''a SimServer has all the attributes needed to connect to and run a SimJob. A lot of changes made by Huaicai.'''
    
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
        """Create a server with default parameters. If you want to change properties of the server, call set_parms() instead. """
        from preferences import prefs_context
        prefs = prefs_context()
        self.server_id = prefs.get('server_id')
        if not self.server_id: self.server_id = 66
        else: self.server_id += 1
        prefs['server_id'] = self.server_id
        
        self.parms = SimServer.server_parms
        if sys.platform == 'linux2':
            self.parms['platform'] = 'Linux'
            self.parms['program'] = '/home/huaicai/gamess/rungms'
            self.parms['engine'] = 'GAMESS'
        elif sys.platform == 'darwin':
            self.parms['program'] = 'rungms'
            self.parms['platform'] = 'Mac Os'
            self.parms['engine'] = 'GAMESS'
        
        self.parms.keys().sort() # Sort parms.
            
        # WARNING: Bugs will be caused if any of SimJob's own methods or 
        # instance variables had the same name as any of the parameter ('k') values.
        for k in self.parms:
             self.__dict__[k] = self.parms[k]        
                
        self.edit_cntl = None
    
    def __getstate__(self):
        """Called by pickle """
        return self.server_id, self.parms, self.edit_cntl
   
    def __setstate__(self, state):
        """Called by unPickle"""
        self.server_id, self.parms, self.edit_cntl = state
        self.set_parms(self.parms)     
    
    def set_parms(self, parms):
        self.parms = parms
        for k in parms:
             self.__dict__[k] = parms[k]     
             
    ######Note: The following method is deprecated #####  
    def write_parms(self, f):
        'Write server parms to file f'
        
        rem = self.get_comment_character()
            
        f.write (rem + '\n' + rem +  'Server Parameters\n' + rem + '\n')
        for k in self.parms:
            phrase = rem + k + ': ' + str(self.__dict__[k])
            f.write (phrase + '\n')
        f.write (rem+'\n')
    
    ###############################################        
# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""
SimServer.py - hold attributes needed to connect to and run a SimJob.
(Appears to be specific to GAMESS in some ways.)
[bruce 071217 guess at description]

@author: Mark
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.

History:

By Mark. A lot of changes made by Huaicai.

"""

import sys
import foundation.env as env

class SimServer:
    """
    a SimServer has all the attributes needed to connect to and run a SimJob.
    """
    server_parms = {
        'hostname'  : 'localhost',
        'ipaddress' : '127.0.0.1',
        'method'    : 'Local access',
        'engine'    : 'PC GAMESS',
        'program'   : 'C:\\PCGAMESS\\gamess.exe',
        'tmpdir'    : 'C:\\PCGAMESS\\',
        'platform'  : 'Windows',
        'username'  : 'nanorex',
        'password'  : '',
     }

    def __init__(self):
        """
        Create a server with default parameters.

        @note: If you want to change properties of the server,
        call set_parms() instead.
        """
        self.server_id = env.prefs.get('server_id')
        if not self.server_id:
            self.server_id = 66
        else:
            self.server_id += 1
        env.prefs['server_id'] = self.server_id

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

        ### WARNING: Bugs will be caused if any of SimJob's own methods or
        # instance variables had the same name as any of the parameter ('k') values.
        for k in self.parms:
             self.__dict__[k] = self.parms[k]

        self.edit_cntl = None

    def __getstate__(self):
        """
        Called by pickle
        """
        return self.server_id, self.parms, self.edit_cntl

    def __setstate__(self, state):
        """
        Called by unpickle
        """
        self.server_id, self.parms, self.edit_cntl = state
        self.set_parms(self.parms)

    def set_parms(self, parms):
        self.parms = parms
        for k in parms:
             self.__dict__[k] = parms[k]

    def write_parms(self, f): # deprecated method
        """
        [deprecated method]
        Write server parms to file f
        """
        rem = self.get_comment_character()

        f.write (rem + '\n' + rem +  'Server Parameters\n' + rem + '\n')
        for k in self.parms:
            phrase = rem + k + ': ' + str(self.__dict__[k])
            f.write (phrase + '\n')
        f.write (rem+'\n')

    pass

# end

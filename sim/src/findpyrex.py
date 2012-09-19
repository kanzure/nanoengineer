# Copyright 2006 Nanorex, Inc.  See LICENSE file for details.

__author__ = "Will"

import sys, os, Pyrex

def find_pyrexc():
    if sys.platform == 'darwin':

        # MacOS
        x = os.path.dirname(Pyrex.__file__).split('/')
        y = '/'.join(x[:-4] + ['bin', 'pyrexc'])
        if os.path.exists(y):
            return y
        elif os.path.exists('/usr/local/bin/pyrexc'):
            return '/usr/local/bin/pyrexc'
        raise Exception('cannot find Mac pyrexc')

    elif sys.platform == 'linux2':

        if os.path.exists('/usr/bin/pyrexc'):
            return '/usr/bin/pyrexc'
        if os.path.exists('/usr/local/bin/pyrexc'):
            return '/usr/local/bin/pyrexc'
        raise Exception('cannot find Linux pyrexc')

    else:
        # windows
        return 'python c:/Python' + sys.version[:3] + '/Scripts/pyrexc.py'

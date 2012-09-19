# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
Paths.py -- platform dependant filename paths

@author: Bruce, Mark, maybe others
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

import sys
import os

def get_default_plugin_path(win32_path, darwin_path, linux_path):
    """
    Returns the plugin (executable) path to the standard location for each platform
    (taken from the appropriate one of the three platform-specific arguments),
    but only if a file or dir exists there.
    Otherwise, returns an empty string.
    """
    if sys.platform == "win32": # Windows
        plugin_path = win32_path
    elif sys.platform == "darwin": # MacOS
        plugin_path = darwin_path
    else: # Linux
        plugin_path = linux_path
    if not os.path.exists(plugin_path):
        return ""
    return plugin_path

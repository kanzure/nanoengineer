#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""This addresses bug 1167, where if the BROWSER environment variable
is not set, nE-1 may not be able to find the web browser to do wiki
help. Let's see if we can resolve that issue without putting \"export
BROWSER\" in the .bashrc or /etc/bashrc file.

Originally observed this bug on Linux. Try to write a fix that works
on any platform.

Remember to type \"export BROWSER=\" before running this script,
otherwise if your bashrc file defines BROWSER, you'll get a successful
result for the wrong reason.
"""

import webbrowser

def register(pathname, key):
    webbrowser._tryorder += [ key ]
    webbrowser.register(key, None,
                        webbrowser.GenericBrowser("%s '%%s'" % pathname))

# In order of decreasing desirability. Browser names for different
# platforms can be mixed in this list. Where a browser is not
# normally found on the system path (like IE on Windows), give its
# full pathname.
for candidate in [
    'firefox',
    'safari',
    'opera',
    'netscape',
    'konqueror',
    'c:/Program Files/Internet Explorer/iexplore.exe'
    ]:
    import os.path
    if os.path.exists(candidate):
        # some candidateidates might have full pathnames
        register(candidate, candidate)
        continue
    for dir in os.environ['PATH'].split(':'):
        pathname = os.path.join(dir, candidate)
        if os.path.exists(pathname):
            register(pathname, candidate)
            continue

webbrowser.open("http://willware.net:8080")

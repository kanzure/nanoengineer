#! /usr/bin/python
# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.

"""
checkui.py

$Id$
"""

import sys
from commands import getoutput
import re
from StringIO import StringIO

isdef = re.compile("\s*def (\w*)\(self,?\W*([^)]*)\):")

if __name__ == '__main__':

    f = sys.argv[1]
    if f[-2:] == 'ui':
        foo = getoutput("pyuic " + sys.argv[1])
    else:
        foo = getoutput("cat " + sys.argv[1])
    bar = StringIO(foo)
    lis = []
    for l in bar.readlines():
        m = isdef.search(l)
        if m and not '__' == m.group(1)[:2]:
            if m.group(1) == 'languageChange':
                continue
            lis += [m.group(1) + '(' + m.group(2) + ')']
    lis.sort()
    for i in lis:
        print i

# end


# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
This script produces the sponsors.md5 file. It assumes the sponsors.xml file is
in the same directory as it is being run in.

Usage: python generateMD5.py
"""

import md5, base64

m = md5.new()
m.update(open('sponsors.xml').read())
digest = "md5:" + base64.encodestring(m.digest())
open('sponsors.md5', 'w').write(digest)


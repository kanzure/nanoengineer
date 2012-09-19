
# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
This script encodes the .png file piped in to text suitable for use in the
sponsors.xml file.

Usage: cat logo.png | python encodeLogo.py > logo.xml
"""

import base64, sys

if (__name__ == '__main__'):
    R = base64.encodestring(sys.stdin.read())
    lines = filter(lambda x: x, R.split('\n'))
    lines = map(lambda x: "    "+x, lines)
    lines[0] = lines[0][:4] + "<logo>" + lines[0][4:]
    lines[-1] += "</logo>"
    print """  <sponsor>
        <name>Sponsor name</name>
        <keywords>KeyWord</keywords>"""
    for L in lines:
        print L
    print """    <text>Text, including a URL</text>
        </sponsor>"""


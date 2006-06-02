# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
Plugins.py

$Id$

http://www.boddie.org.uk/python/XML_intro.html

Stuff to make plugins work. Start with reading metadata file.
"""

__author__ = "Will"

import os
import sys
import types
import xml.dom.minidom

# This is just a convenience function to see what's in the
# metadata file, and how to navigate it.
def printNode(node, indent=''):
    if node.nodeType == node.TEXT_NODE:
        print indent + repr(node.data)
    elif node.nodeType == node.ELEMENT_NODE:
        attrStr = ''
        attrs = node._attrs.keys()
        if attrs:
            for a in attrs:
                attrStr += ' ' + a + '="' + node.getAttribute(a) + '"'
        print indent + node.localName + attrStr
        includeText = True
        for child in node.childNodes:
            if child.nodeType != node.TEXT_NODE:
                includeText = False
                break
        for child in node.childNodes:
            if includeText or child.nodeType != node.TEXT_NODE:
                printNode(child, indent + '    ')
    elif node.nodeType == node.DOCUMENT_NODE:
        assert len(node.childNodes) == 1
        printNode(node.childNodes[0], indent)
    elif node.nodeType == node.COMMENT_NODE:
        pass
    else:
        print indent + '??? %d ???' % node.nodeType

########################################

# a non-recursive version
def getElementsByTagname(parent, name):
    rc = [ ]
    for node in parent.childNodes:
        if node.nodeType == node.ELEMENT_NODE and \
            (name == "*" or node.tagName == name):
            rc.append(node)
    return rc

def getXmlText(parent):
    rc = ''
    for node in parent.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc += node.data
    return rc

class Plugin:
    def __init__(self, path):
        xmlfile = os.path.join(path, 'metadata.xml')
        f = open(xmlfile)
        info = xml.dom.minidom.parse(f)
        f.close()
        assert info.nodeType == info.DOCUMENT_NODE
        assert len(info.childNodes) == 1
        self.plugindir = path
        self.root = root = getElementsByTagname(info, 'ne1_plugin')[0]
        self.name = getXmlText(getElementsByTagname(root, 'name')[0])
        self.version = getXmlText(getElementsByTagname(root, 'version')[0])
        self.description = getElementsByTagname(root, 'description')[0]
        self.files = getElementsByTagname(root, 'files')[0]
    def docs(self):
        lst = [ ]
        for f in self.files.childNodes:
            if f.localName == 'doc':
                lst.append(f.getAttribute('name'))
        return lst
    def executables(self, os=sys.platform):
        lst = [ ]
        for f in self.files.childNodes:
            if f.localName == 'executable':
                oslist = f.getAttribute('os').split(',')
                if os in oslist:
                    lst.append(f.getAttribute('name'))
        return lst
    def make(self):
        cmd = '(cd ' + self.plugindir
        for e in self.executables():
            # If we know anything special about building this executable,
            # this is the place to use that information.
            cmd += '; make ' + e
        cmd += ')'
        print cmd
        os.system(cmd)
    def makeClean(self):
        cmd = '(cd ' + self.plugindir + '; make clean)'
        print cmd
        os.system(cmd)

_plugindir = '../plugins/'
_plugins = [ ]

for d in os.listdir(_plugindir):
    if d != 'CVS':
        path = os.path.join(_plugindir, d)
        if os.path.isdir(path):
            p = Plugin(path)
            _plugins.append(p)
            p.makeClean()
            p.make()

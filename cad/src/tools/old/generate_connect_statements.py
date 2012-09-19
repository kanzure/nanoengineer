#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
import re
import os
import xml.dom.minidom

def find_children(node, criterion=None):
    kids = [ ]
    for e in node.childNodes:
        if (criterion is None or criterion(e)):
            kids.append(e)
    return kids

def first_text_node(node):
    return find_children(node, lambda e: e.nodeType is e.TEXT_NODE)[0]

def find_elements(node, criterion=None):
    def crit(e, criterion=criterion):
        if e.nodeType is not e.ELEMENT_NODE:
            return False
        return criterion is None or criterion(e)
    return find_children(node, crit)

def find_elements_by_localName(node, localName):
    def crit(e, localName=localName):
        if e.nodeType is not e.ELEMENT_NODE:
            return False
        return e.localName == localName
    return find_children(node, crit)

def blab(node, level=0):
    indent = level * '    '
    print indent + repr(node)
    for kid in find_children(node):
        blab(kid, level + 1)

def main():
    uifiles = map(lambda x: x[:-1],
                  os.popen('/bin/ls *.ui').readlines())

    for f in uifiles:
        rev = os.popen('cvs status ' + f).readlines()[3].split()[2]
        branchpoint = '.'.join(rev.split('.')[:2])
        print '==========================='
        print f, '     ', rev
        print '==========================='
        r = os.popen('cvs up -p -r ' + branchpoint + ' ' + f).read()
        doc = xml.dom.minidom.parseString(r)
        ui = find_elements(doc)[0]
        connections = find_elements_by_localName(ui, 'connections')[0]
        for conn in find_elements_by_localName(connections, 'connection'):
            sender = find_elements_by_localName(conn, 'sender')[0]
            sender = first_text_node(sender).wholeText
            receiver = find_elements_by_localName(conn, 'receiver')[0]
            receiver = first_text_node(receiver).wholeText
            signal = find_elements_by_localName(conn, 'signal')[0]
            signal = first_text_node(signal).wholeText
            slot = find_elements_by_localName(conn, 'slot')[0]
            slot = first_text_node(slot).wholeText
            print ('        self.connect(self.%s,SIGNAL("%s"),self.%s)' %
                   (sender, signal, re.sub('\(.*', '', slot)))

if (__name__ == '__main__'):
    main()

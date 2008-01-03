#!/usr/bin/env python
# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
packageData_checker.py - script for checking and reporting on packageData.py

Note: some of this code might be moved into packageData
if all users of that data should use this code to canonicalize it
before making other use of it (eg for import graphing).

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from packageData import packageMapping, layer_aliases, topic_mapping

# utils for looking at output of AllPyFiles, not yet used within this file

def source_path_parts(path):
    p1 = path.split('/')
    assert p1[0] == '.'
    return p1[1:]

def topmodule(pathparts):
    if not len(pathparts) == 1:
        return None
    module = pathparts[0]
    assert module.endswith('.py')
    return module[:-3]

#e should add routine to look for toplevel files not present in packageMapping

# ==

# flags for packageClassification
LAYER_ONLY = 'LAYER_ONLY'
TOPIC_ONLY = 'TOPIC_ONLY'
LAYER_AND_TOPIC = 'LAYER_AND_TOPIC'

def packageClassification(value, flags):
    """
    @param value: a string value from the packageMapping global variable,
                  e.g. "ui/propmgr|commands/BuildSomething" or "widget" or ...
                  which has a layer and an optional |topic
                  both of which might be word or word/word etc
    """
    parts = value.split('|')
    assert len(parts) in (1,2)
    if len(parts) == 1:
        layer = parts[0]
        topic = None
    else:
        layer, topic = parts
    layer = canonicalize(layer, layer_aliases)
    if topic is None:
        topic = layer # or, "dflt_" + layer??
    topic = canonicalize(topic, topic_mapping)
    if flags == LAYER_ONLY:
        return layer
    elif flags == TOPIC_ONLY:
        return topic
    else:
        # LAYER_AND_TOPIC
        if layer == topic:
            return layer
        return layer + "|" + topic
    pass

def canonicalize(value, dict1):
    """
    Canonicalize value by repeatedly doing value = dict1[value],
    but if this enters a cycle, report error and return original value.
    """
    orig_value = value
    prior_values = [value]
    while dict1.has_key(value):
        value = dict1[value]
        if value in prior_values:
            print >> sys.stderr, "error: canonicalize loop: %r" % (prior_values + [value])
            return orig_value
        prior_values.append(value)
    return value

def summarize_packageMapping( flags):

    counts = {}
    
    for basename, value in packageMapping.items():
        classification = packageClassification(value, flags)
        countnow = counts.setdefault(classification, 0)
        countnow += 1
        counts[classification] = countnow

    items = counts.items()
    items.sort() # by classification

    print
    print "classication: count (for %s)" % (flags,)
    print
    for classification, count in items:
        print "%s: %d" % (classification, count)
    return

def summarize_packageMapping_allflags():
    ## summarize_packageMapping( LAYER_ONLY)
    summarize_packageMapping( TOPIC_ONLY)
    # that's enough for now
    return

if __name__ == '__main__':    
    summarize_packageMapping_allflags()
    print
    print "done"

# end

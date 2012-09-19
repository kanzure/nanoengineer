# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: EricM
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.
"""

import types
import numpy.oldnumeric

cdef extern from "Python.h":
    int PyType_Check(obj)
    int PyCallable_Check(obj)
    int PyList_Check(obj)

cdef extern from "samevalshelp.c":
    int c_setArrayType(object atype)
    int c_setInstanceCopier(object copier)
    int c_setGeneralCopier(object copier)
    int c_setArrayCopier(object copier)
    int c_setInstanceLikeClasses(object classList)
    object c_same_vals(object o1, object o2)
    object c_copy_val(object obj)

class _old_style_class:
    pass

_old_style_instance = _old_style_class()

def same_vals(o1, o2):
    res = c_same_vals(o1, o2)

    # TODO: we need to fix a bug in c_same_vals exception handling,
    # in which it fails to properly handle an exception in its call to
    # PyObject_RichCompareBool (for example, a ValueError when it's used
    # on objects of type numpy.ndarray). Until that's fixed in the C code
    # (not just for ndarray but for any potential exception from that callback),
    # we work around that bug in c_same_vals here, by the following KLUGE --
    # this getattr will raise that unhandled exception from its own location
    # in this file, but will cause no harm (except a slowdown, of unknown
    # importance) if there is no unhandled exception.
    # TODO: also extend c_same_vals to correctly compare numpy.ndarray,
    # like the Python version (in utilities/Comparison.py) now does.
    # [bruce 081202]
    
    # disabled to get ubuntu 7.04 running again [bryan 2012-04-30]
    #getattr3(_old_style_instance, 'missingattr', None)
        # for doc of getattr3: http://www.cosc.canterbury.ac.nz/greg.ewing/python/Pyrex/version/Doc/Manual/basics.html

    return res

def copy_val(obj):
    return c_copy_val(obj)

def setArrayType(atype):
    if (PyType_Check(atype)):
        c_setArrayType(atype)
    else:
        raise TypeError, "argument must be a type"

def setInstanceCopier(copier):
    if (PyCallable_Check(copier)):
        c_setInstanceCopier(copier)
    else:
        raise TypeError, "argument must be callable"

def setGeneralCopier(copier):
    if (PyCallable_Check(copier)):
        c_setGeneralCopier(copier)
    else:
        raise TypeError, "argument must be callable"

def setArrayCopier(copier):
    if (PyCallable_Check(copier)):
        c_setArrayCopier(copier)
    else:
        raise TypeError, "argument must be callable"

def setInstanceLikeClasses(classList): # deprecated, bruce 090206
    if (PyList_Check(classList)):
        c_setInstanceLikeClasses(classList)
    else:
        raise TypeError, "argument must be a list"


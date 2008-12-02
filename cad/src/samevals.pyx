# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: EricM
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

import types
import Numeric

cdef extern from "Python.h":
    int PyType_Check(obj)
    int PyCallable_Check(obj)
    int PyList_Check(obj)

cdef extern from "samevalshelp.c":
    int c_setArrayType(object atype)
    int c_setInstanceCopier(object copier)
    int c_setArrayCopier(object copier)
    int c_setInstanceLikeClasses(object classList)
    object c_same_vals(object o1, object o2)
    object c_copy_val(object obj)

def same_vals(o1, o2):
    return c_same_vals(o1, o2)

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
        raise TypeError, "argument must be executable"

def setArrayCopier(copier):
    if (PyCallable_Check(copier)):
        c_setArrayCopier(copier)
    else:
        raise TypeError, "argument must be executable"

def setInstanceLikeClasses(classList):
    if (PyList_Check(classList)):
        c_setInstanceLikeClasses(classList)
    else:
        raise TypeError, "argument must be a list"


# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
qt4transition.py - Useful markers and messages for Qt 4 transition work.

@author: Will
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""

import sys
import traceback
import types

import utilities.debug_prefs as debug_prefs
import utilities.debug as debug

from utilities.objectBrowse import objectBrowse

__already = { }

def __linenum(always = False):
    try:
        raise Exception
    except:
        tb = sys.exc_info()[2]
        f = tb.tb_frame
        f = f.f_back
        f = f.f_back
        key = (f.f_code.co_filename, f.f_lineno)
        got_key = True
        if not __already.has_key(key):
            __already[key] = 1
            got_key = False
        if got_key and not always:
            return False
        else:
            print f.f_code.co_filename, f.f_code.co_name, f.f_lineno
            return True

def qt4here(msg = None, show_traceback = False):
    if show_traceback:
        traceback.print_stack(None, None, sys.stdout)
        if msg is not None:
            print 'Qt 4 HERE: ' + msg
        print
    else:
        __linenum(always = True)
        if msg is not None:
            print 'Qt 4 HERE: ' + msg

def qt4overhaul(msg):
    if __linenum():
        print 'Qt 4 MAJOR CONCEPTUAL OVERHAUL: ' + msg

def qt4message(msg, always = False):
    if debug_prefs.debug_pref("Enable QT4 TODO messages",
                      debug_prefs.Choice_boolean_False,
                      prefs_key = True):
        if __linenum(always):
            print 'Qt 4 MESSAGE: ' + msg

def qt4todo(msg):
    if debug_prefs.debug_pref("Enable QT4 TODO messages",
                      debug_prefs.Choice_boolean_False,
                      prefs_key = True):
        if __linenum():
            print 'Qt 4 TODO: ' + msg
    else:
        return

def multipane_todo(msg):
    if __linenum():
        print 'Multipane TODO: ' + msg

def qt4warning(msg):
    if debug_prefs.debug_pref("Enable QT4 WARNING messages",
                      debug_prefs.Choice_boolean_False,
                      prefs_key = True):
        if __linenum():
            print 'Qt 4 WARNING: ' + msg

def qt4skipit(msg):
    """
    Indicates something I don't think we need for Qt 4
    """
    if __linenum():
        print 'Qt 4 SKIP IT: ' + msg

__nomsg = '128931789ksadjfqwhrhlv128947890127408'

def qt4die(msg = __nomsg, browse = False):
    traceback.print_stack(file = sys.stdout)
    if msg == __nomsg:
        print 'Qt 4 DIE'
    elif browse:
        print 'Qt 4 DIE:', msg
        objectBrowse(msg, maxdepth = 1)
    else:
        if type(msg) is not types.StringType:
            msg = repr(msg)
        print 'Qt 4 DIE: ' + msg
    sys.exit(0)

def qt4exception(msg):
    """
    Indicates something I don't think we definitely shouldn't have for Qt 4
    """
    raise Exception('Qt 4: ' + msg)

def qt4info(msg, name = None, maxdepth = 1, browse = False):
    __linenum(always = True)
    if type(msg) is type('abc'):
        print 'Qt 4 INFO:', repr(msg)
    else:
        print 'Qt 4 INFO:',
        if name is not None: print name,
        print repr(msg)
        if browse:
            objectBrowse(msg, maxdepth = maxdepth, outf = sys.stdout)

def qt4warnDestruction(obj, name = ''):
    message = '* * * * '
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame
        f = f.f_back
        message += f.f_code.co_filename + (':%d' % f.f_lineno)
    if name:
        message += ' ' + name
    if debug_prefs.debug_pref("Enable QT4 WARNING messages",
                      debug_prefs.Choice_boolean_False,
                      prefs_key = True):
        print 'Setting up destruction warning', message
    def destruction(ignore, message = message):
        print 'OBJECT DESTROYED (exiting)', message #bruce 070521 revised message
        sys.exit(1)
    from PyQt4.Qt import QObject, SIGNAL
    QObject.connect(obj, SIGNAL("destroyed(QObject *)"), destruction)

def findDefiningClass(cls_or_method, method_name = None):
    """
    Find which base class defines this method

    >>> print findDefiningClass(DeepClass.foo)
    __main__.BaseClass
    >>> print findDefiningClass(ShallowClass.foo)
    __main__.Base2Class
    >>> print findDefiningClass(ShallowClass, 'foo')
    __main__.Base2Class
    >>> x = DeepClass()
    >>> print findDefiningClass(x.foo)
    __main__.BaseClass
    """
    if method_name is not None:
        if type(cls_or_method) is not types.ClassType:
            cls_or_method = cls_or_method.__class__
        method = getattr(cls_or_method, method_name)
    elif type(cls_or_method) is types.MethodType:
        method = getattr(cls_or_method.im_class, cls_or_method.im_func.func_name)
    else:
        method = cls_or_method
    assert method.im_self is None, "Method must be a class method, not an instance mthod"
    def hunt(klass, lst, depth, name = method.im_func.func_name, method = method):
        if hasattr(klass, name) and method.im_func is getattr(klass, name).im_func:
            lst.append((depth, klass))
        for base in klass.__bases__:
            hunt(base, lst, depth + 1)
    lst = [ ]
    hunt(method.im_class, lst, 0)
    lst.sort()
    return lst[-1][1]

def lineage(widget, die = True, depth = 0):
    """
    Trace the parental lineage of a Qt 4 widget: parent,
    grandparent... This is helpful in diagnosing "RuntimeError:
    underlying C/C++ object has been deleted" errors. It is frequently
    wise to kill the program at the first such deletion, so that is the
    default behavior (switchable with die = False).
    """
    if widget is not None:
        from PyQt4.Qt import QObject, SIGNAL
        print (depth * '    ') + repr(widget)
        def destruction(ignore, die = die, message = repr(widget) + " was just destroyed"):
            qt4here(message, show_traceback = True)
            if die:
                sys.exit(1)
        QObject.connect(widget, SIGNAL("destroyed(QObject *)"), destruction)
        lineage(widget.parent(), die, depth + 1)

# ==

if __name__ == '__main__':

    # classes used to test findDefiningClass
    class BaseClass:
        def foo(self):
            print 'bar'
    class Base2Class:
        def foo(self):
            print 'BAR'
    class MiddleClass(BaseClass):
        pass
    class DeepClass(MiddleClass, Base2Class):
        pass
    class ShallowClass(Base2Class, MiddleClass):
        pass

    import doctest
    doctest.testmod()

# end

"""
debug.py

Some useful debugging functions.

Copyright, License, and Warranty info:

Some of these functions were originally written by me (Bruce Smith) during 2003,
as a contractor on a project which was not "work for hire". According to the
US Copyright Act of 1976, those functions are therefore copyrightable only by me.
I (Bruce Smith, Sep 23 2004) hereby place those functions (listed below) into the
public domain.

The above applies to the functions compact_traceback_msg and
print_compact_traceback_and_continue, in their original form.

They have been further modified by me (Bruce Smith, 23 Sep 2004 and later)
as an employee of Nanorex. Those modifications are, of course,
Copyright 2004, Nanorex, Inc.

# BRUCE SMITH DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL BRUCE SMITH BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

from asyncore import compact_traceback

import sys

def compact_traceback_msg( prefix = 'error: ', newline = ' '):
    junk, ty, val, tbinfo = compact_traceback()
    tbinfo = tbinfo.replace( '] [', ']%s[' % newline)
    return '%s%s:%s %s%s' % ( prefix, ty, val, newline, tbinfo )

def print_compact_traceback_and_continue(prefix = 'ignoring this exception: ', newline = '\n', self_debug = 0):
    "#doc; above all else, cause no harm (ie continue even if unable to print any error message), unless self_debug = true"
    try:
        msg = compact_traceback_msg( prefix = prefix, newline = newline )
    except:
        if self_debug:
            raise
        msg = "... uh oh, exception in print_compact_traceback_and_continue, not printed, sorry"
    try:
        print >>sys.__stderr__, msg
    except:
        if self_debug:
            raise
        try:
            msg = "failed to print this to sys.__stderr__:\n" + msg
            print msg
        except:
            pass
    return

print_compact_traceback = print_compact_traceback_and_continue

# end

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
as an employee of Nanorex. Those modifications, and the other functions
in this file, are, of course, Copyright 2004, Nanorex, Inc.

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

# THE FOLLOWING MIGHT NOT EVEN BE GPL_COMPATIBLE, UNTIL REWRITTEN [040928]

def compact_stack_orig( newline = '\n', outer_first = 0, inner_del = 0 ): # not used, just for comparison
    """modified from compact_traceback( )
    """
    import inspect as _inspect
    tbinfo = [] #k array of (file, function, line) tuples
    for frame_rec in _inspect.stack(0): # arg is number of lines of context in list_of_lines
        (frame_object, filename, lineno, funcname, list_of_lines, index_of_current_line) = frame_rec
        del frame_object    
        tbinfo.append ((
            str(filename),
            str(funcname),
            str(lineno) # this str() is needed, the others are just for safety
            ))

    tbinfo = tbinfo[inner_del:]
    if outer_first:
        tbinfo.reverse()
    # after this it's almost the same as in compact_traceback
    info = '[' + (']' + newline + '[').join(map((lambda x: '|'.join(x)), tbinfo)) + ']'
    return info
del compact_stack_orig

# BUT WHATEVER IS NEW IN THIS VERSION OF IT IS OK

try:
    _next_frame_id
except:
    _next_frame_id = 1

def compact_stack( newline = '\n', outer_first = 0, inner_del = 0, add_frame_ids = 1 ): ####e add_frame_ids = 0 if turns out not safe
    """modified from compact_traceback( )
    add_frame_ids added 040928
    """
    import inspect as _inspect
    tbinfo = [] #k array of (file, function, line) tuples
    for frame_rec in _inspect.stack(0): # arg is number of lines of context in list_of_lines
        (frame_object, filename, lineno, funcname, list_of_lines, index_of_current_line) = frame_rec
        if add_frame_ids: #040928
            # record in each frame a unique id and a count of how many times we've returned it so far, for comparing successive stacktraces
            try:
                fid = frame_object.f_locals['__bruce_frame_id__']
            except KeyError:
                global _next_frame_id
                fid = _next_frame_id
                _next_frame_id += 1
                frame_object.f_locals['__bruce_frame_id__'] = fid
                usage = 1
                frame_object.f_locals['__bruce_frame_usage__'] = usage
            else:
                usage = frame_object.f_locals['__bruce_frame_usage__'] + 1
                frame_object.f_locals['__bruce_frame_usage__'] = usage
        else:
            fid = usage = -1 ###fix
        del frame_object  
        tbinfo.append ((
            str(filename),
            str(funcname),
            str(lineno), # this str() is needed, the others are just for safety
            str(fid),
            str(usage)
            ))

    tbinfo = tbinfo[inner_del:]
    if outer_first:
        tbinfo.reverse()
    # after this it's almost the same as in compact_traceback
    info = '[' + (']' + newline + '[').join(map((lambda x: '|'.join(x)), tbinfo)) + ']'
    return info

# end of stuff with nonstandard copyright status -- below this line it's normal

# ===

# import some things to make debugging commands more convenient ###e also qt, etc
import sys, os, time

# run python commands from various sorts of integrated debugging UIs (for users who are developers); used in GLPane.py.
# (moved here from GLPane.py by bruce 040928; docstring and messages maybe not yet fixed)

def debug_run_command(command, source = "user debug input"): #bruce 040913-16 in GLPane.py; modified 040928
    """Execute a python command, supplied by the user via some sort of debugging interface (named by source),
       in debug.py's globals. Return 1 for ok (incl empty command), 0 for any error.
       Caller should not print exception diagnostics -- this function does that
       (and does not reraise the exception).
    """
    #e someday we might record time, history, etc
    command = "" + command # i.e. assert it's a string
    #k what's a better way to do the following?
    while command and command[0] == '\n':
        command = command[1:]
    while command and command[-1] == '\n':
        command = command[:-1]
    if not command:
        print "empty command (from %s), nothing executed" % (source,)
        return 1
    if '\n' not in command:
        print "will execute (from %s): %s" % (source, command)
    else:
        nlines = command.count('\n')+1
        print "will execute (from %s; %d lines):\n%s" % (source, nlines, command)
    command = command + '\n' #k probably not needed
    try:
        exec command in globals()
    except:
        print_compact_traceback("exception from that: ")
        return 0
    else:
        print "did it!"
        return 1
    pass

def debug_runpycode_from_a_dialog( source = "some debug menu??"):
    title = "debug: run py code"
    label = "one line of python to exec in debug.py's globals()\n(or use @@@ to fake \\n for more lines)\n(or use execfile)"
    text, ok = QInputDialog.getText(title, label)
    if ok:
        # fyi: type(text) == <class '__main__.qt.QString'>
        command = str(text)
        command = command.replace("@@@",'\n')
        debug_run_command(command, source = source)
    else:
        print "run py code: cancelled"
    return

def print_compact_stack(msg = "", **kws): # newly written, 040928
    try:
        info = compact_stack(**kws)
    except:
        raise#####
        info = "(exception in compact_stack)"
    print >>sys.__stderr__, "stack: %s%s" % (msg, info)
    return

if __name__ == '__main__':
    def ff():
        print_compact_stack("test 1 in ff:\n")
        print_compact_stack("test 2 in ff:\n")
    ff()
    print_compact_stack("test 3:\n")
    print >>sys.__stderr__, "done"
    print "done, see __stderr__"
    
# end

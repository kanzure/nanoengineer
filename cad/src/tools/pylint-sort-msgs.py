#!/usr/bin/env python
"""
$Id$

parse messages like this

widgets/prefs_widgets.py:472: [W0511] TODO: try to make destroyable_Qt_connection a super of this class
widgets/prefs_widgets.py:39: [C0112, widget_destroyConnectionWithState] Empty docstring

and print them into files based on the W0511 part, named e.g. W0511.txt.

"""
import sys, os, time

files = {} ### REVIEW: can I have any number of open files at a time?

def open_file_for_message_type(mtype):
    if not files.has_key(mtype):
        filename = "%s.txt" % mtype
        files[mtype] = open(filename, "w")
    return files[mtype]

def close_files(): # maybe not needed, if normal exit does this??
    for key, val in files.items():
        val.close()
    return
    
def writeit(line, current_message_type):
    if current_message_type:
        file1 = open_file_for_message_type(current_message_type)
        file1.write(line)
    return

current_message_type = None

for line in sys.stdin.readlines():
    if not line[0].isspace():
        words = line.split()
        if len(words) >= 2 and words[1][0] == '[' and words[1][-1] in [ ']', ',' ]:
            message_type = words[1][1:-1]
            assert len(message_type) == 5
            assert message_type[0] in "WCERF", "unrecognized message: %r" % (message_type,)
            for char1 in message_type[1:]:
                assert char1 in "0123456789"
            current_message_type = message_type
    writeit(line, current_message_type)
    continue

# end

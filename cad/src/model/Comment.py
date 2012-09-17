# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
Comment.py - The Comment class.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

mark 060530 - Comment class moved here from Utility.py.

bruce 071019 - moved mmp reading code for Comment into this file;
registering it with files_mmp_registration instead of hardcoding it there
"""

from foundation.Utility import SimpleCopyMixin, Node
from utilities.icon_utilities import imagename_to_pixmap
from utilities.constants import gensym

from files.mmp.files_mmp_registration import MMP_RecordParser
from files.mmp.files_mmp_registration import register_MMP_RecordParser

# ==

class Comment(SimpleCopyMixin, Node):
    """
    A Comment stores a comment in the MMP file, accessible from the Model Tree as a node.
    """
    # text representation: self.lines is a list of lines (str or unicode python strings).
    # This is the fundamental representation for use by mmp read/write, copy, and Undo.
    # For convenience, get_text() and set_text() are also available.

    sym = "Comment"

    lines = ()

    copyable_attrs = Node.copyable_attrs + ('lines',)
        #bruce 060523 this fixes bug 1939 (undo) and apparently 1938 (file modified),
        # and together with SimpleCopyMixin it also fixes bug 1940 (copy)

    def __init__(self, assy, name, text=''):
        self.const_pixmap = imagename_to_pixmap("modeltree/comment.png")
        if not name:
            name = gensym("%s" % self.sym, assy)
        Node.__init__(self, assy, name)
        self.lines = [] # this makes set_text changed() test legal (result of test doesn't matter)
        self.set_text(text)
        return

    def assert_valid_line(self, line): #bruce 070502
        assert type(line) in (type(""), type(u"")), "invalid type for line = %r, with str = %s" % (line, line)
        return

    def set_text(self, text):
        """
        Set our text (represented in self.lines, a list of 1 or more str or unicode strings, no newlines)
        to the lines in the given str or unicode python string, or QString.
        """
        oldlines = self.lines
        if type(text) in (type(""), type(u"")):
            # this (text.split) works for str or unicode text;
            # WARNING: in Qt4 it would also work for QString, but produces QStrings,
            # so we have to do the explicit type test rather than try/except like in Qt3.
            # (I didn't check whether we got away with try/except in Qt3 due to QString.split not working
            #  or due to not being passed a QString in that case.) [bruce 070502 Qt4 bugfix]
            lines = text.split('\n')
        else:
            # it must be a QString
            text = unicode(text)
            ## self.text = text # see if edit still works after this -- it does
            lines = text.split('\n')
            # ok that they are unicode but needn't be? yes.
        map( self.assert_valid_line, lines)
        self.lines = lines
        if oldlines != lines:
            self.changed()
        return

    def get_text(self):
        """
        return our text (perhaps as a unicode string, whether or not unicode is needed)
        """
        return u'\n'.join(self.lines) #bruce 070502 bugfix: revert Qt4 porting error which broke this for unicode

    def _add_line(self, line, encoding = 'ascii'):
        """
        [private method to support mmp reading (main record and info records)]

        Add the given line (which might be str or unicode, but is assumed to contain no \ns and not be a QString) to our text.
        """
        if encoding == 'utf-8':
            line = line.decode(encoding)
        else:
            if encoding != 'ascii':
                print "Comment._add_line treating unknown encoding as if ascii:", encoding
            # no need to decode
        self.assert_valid_line(line)
        self.lines.append(line)
        self.changed()
        return

    def _init_line1(self, card):
        """
        [private method]

        readmmp helper -- card is entire line of mmp record (perhaps including \n at end)
        """
        # as of 060522 it does end with \n, but we won't assume it does; but we will assume it was written by our writemmp method
        if card[-1] == '\n':
            card = card[:-1]
        # comment (name) encoding1, line1
        junk, rest = card.split(') ', 1)
        try:
            encoding1, line1 = rest.split(' ', 1) # assume ending blank has been preserved, if line was empty
        except:
            # assume ending blank got lost
            encoding1 = rest
            line1 = ""
        self.lines = [] # kluge
        self._add_line( line1, encoding1)
        return

    def readmmp_info_leaf_setitem( self, key, val, interp ): #bruce 060522
        "[extends superclass method]"
        if key[0] == 'commentline' and len(key) == 2:
            # key[1] is the encoding, and val is one line in the comment
            self._add_line(val, key[1])
        else:
            Node.readmmp_info_leaf_setitem( self, key, val, interp)
        return

    def edit(self):
        """
        Opens Comment dialog with current text.
        """
        self.assy.w.commentcntl.setup(self)

    def writemmp(self, mapping):
        lines = self.lines
        def encodeline(line):
            self.assert_valid_line(line) #k should be redundant, since done whenever we modify self.lines
            try:
                return 'ascii', line.encode('ascii')
            except:
                return 'utf-8', line.encode('utf-8') # needed if it contains unicode characters
            # in future we might have more possibilities, e.g. html or images or links...
        encodedlines = map( encodeline, lines)
        encoding1, line1 = encodedlines[0] # this works even if the comment is empty (1 line, length 0)
        mapping.write("comment (" + mapping.encode_name(self.name) + ") %s %s\n" % (encoding1, line1))
        for encoding1, line1 in encodedlines[1:]:
            mapping.write("info leaf commentline %s = %s\n" % (encoding1, line1))
        self.writemmp_info_leaf(mapping)
        return

    def __str__(self):
        return "<comment " + self.name + ">"

    pass # end of class Comment

# ==

class _MMP_RecordParser_for_Comment( MMP_RecordParser): #bruce 071019
    """
    Read the first line of the MMP record for a Comment.
    """
    def read_record(self, card): #bruce 060522
        name = self.get_name(card, "Comment")
        name = self.decode_name(name) #bruce 050618
        comment = Comment(self.assy, name)
        comment._init_line1(card) # card ends with a newline
        self.addmember(comment)
        # Note: subsequent lines of the Comment text (if any)
        # come from info leaf records following this record
        # in the mmp file.
        return
    pass

def register_MMP_RecordParser_for_Comment():
    """
    [call this during init, before reading any mmp files]
    """
    register_MMP_RecordParser( 'comment', _MMP_RecordParser_for_Comment )
    return

# end

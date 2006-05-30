# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
Comment.py - The Comment class.

$Id$

History:

mark 060530 - Comment class moved here from Utility.py.

'''

from Utility import SimpleCopyMixin, Node, imagename_to_pixmap, genViewNum

class Comment(SimpleCopyMixin, Node):
    """A Comment stores a comment in the MMP file, accessible from the Model Tree as a node.
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
        self.const_icon = imagename_to_pixmap("comment.png")
        if not name:
            name = genViewNum("%s-" % self.sym)
        Node.__init__(self, assy, name)
        self.lines = [] # this makes set_text changed() test legal (result of test doesn't matter)
        self.set_text(text)
        return

    def set_text(self, text):
        """Set our text (represented in self.lines, a list of 1 or more str or unicode strings, no newlines)
        to the lines in the given str or unicode python string, or QString.
        """
        oldlines = self.lines
        try:
            # this works for str or unicode
            lines = text.split('\n')
        except:
            # this happens for QStrings
            text = unicode(text)
            ## self.text = text # see if edit still works after this -- it does
            lines = text.split('\n')
            # ok that they are unicode but needn't be? yes.
        self.lines = lines
        if oldlines != lines:
            self.changed()
        return

    def get_text(self):
        "return our text (perhaps as a unicode string, whether or not unicode is needed)"
        return u'\n'.join(self.lines)

    def _add_line(self, line, encoding = 'ascii'):
        """[private method to support mmp reading (main record and info records)]
        Add the given line (which might be str or unicode, but is assumed to contain no \ns and not be a QString) to our text.
        """
        if encoding == 'utf-8':
            line = line.decode(encoding)
        else:
            if encoding != 'ascii':
                print "Comment._add_line treating unknown encoding as if ascii:", encoding
            # no need to decode
        self.lines.append(line)
        self.changed()
        return

    def _init_line1(self, card):
        "[private method] readmmp helper -- card is entire line of mmp record (perhaps including \n at end)"
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
        "Opens Comment dialog with current text."
        self.assy.w.commentcntl.setup(self)
        
    def writemmp(self, mapping):
        lines = self.lines
        def encodeline(line):
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
# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
files_mmp_registration.py - registration scheme for helper functions
for parsing mmp record lines which start with specific recordnames.

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 080304 split this out of files_mmp.py, to avoid import cycles,
since anything should be able to import this module, but the main
reading code (which remains in files_mmp) needs to import a variety
of model classes for constructing them (since not everything uses
the registration scheme or should have to).
"""

# ==

class MMP_RecordParser(object): #bruce 071018
    """
    Public superclass for parsers for reading specific kinds of mmp records.

    Concrete subclasses should be registered with the global default
    mmp grammar using

      register_MMP_RecordParser('recordname', recordParser)

    for one or more recordnames which that parser subclass can support.

    Typically, each subclass knows how to parse just one kind of record,
    and is registered with only one recordname.

    Instance creation is only done by the mmp parser module,
    at least once per assembly (the instance will know which assembly
    it's for in self.assy, a per-instance constant), and perhaps
    as often as once per mmp file read (or conceivably even once
    per mmp record read -- REVIEW whether to rule that out in order
    to permit instances to remember things between records while
    one file is being read, e.g. whether they've emitted certain
    warnings, and similarly whether to promise they're instantiated
    once per file, as opposed to less often, for the same reason).

    Concrete subclasses need to define method read_record,
    which will be called with one line of text
    (including the final newline) whose first word
    is one of the record names for which that subclass was
    registered.

    ### REVIEW: will they also be called for subsequent lines
    in some cases? motors, atoms/bonds, info records...

    The public methods in this superclass can be called by
    the subclass to help it work; their docstrings contain
    essential info about how to write concrete subclasses.
    """
    def __init__(self, readmmp_state, recordname):
        """
        @param readmmp_state: object which tracks state of one mmp reading operation.
        @type readmmp_state: class _readmmp_state (implem is private to files_mmp.py).

        @param recordname: mmp record name for which this instance is registered.
        @type recordname: string (containing no whitespace)
        """
        self.readmmp_state = readmmp_state
        self.recordname = recordname
        self.assy = readmmp_state.assy
        return

    def get_name(self, card, default):
        """
        [see docstring of same method in class _readmmp_state]
        """
        return self.readmmp_state.get_name(card, default)

    def get_decoded_name_and_rest(self, card, default = None):
        """
        [see docstring of same method in class _readmmp_state]
        """
        return self.readmmp_state.get_decoded_name_and_rest(card, default)

    def decode_name(self, name):
        """
        [see docstring of same method in class _readmmp_state]
        """
        return self.readmmp_state.decode_name(name)

    def addmember(self, model_component):
        """
        [see docstring of same method in class _readmmp_state]
        """
        self.readmmp_state.addmember(model_component)

    def set_info_object(self, kind, model_component):
        """
        [see docstring of same method in class _readmmp_state]
        """
        self.readmmp_state.set_info_object(kind, model_component)

    def read_new_jig(self, card, constructor):
        """
        [see docstring of same method in class _readmmp_state]
        """
        self.readmmp_state.read_new_jig(card, constructor)

    def read_record(self, card):
        msg = "subclass %r for recordname %r must implement method read_record" % \
               (self.__class__, self.recordname)
        self.readmmp_state.bug_error(msg)

    pass # end of class MMP_RecordParser

class _fake_MMP_RecordParser(MMP_RecordParser):
    """
    Use this as an initial registered RecordParser
    for a known mmp recordname, to detect the error
    of the real one not being registered soon enough
    when that kind of mmp record is first read.
    """
    def read_record(self, card):
        msg = "init code has not registered " \
              "an mmp record parser for recordname %r " \
              "to parse this mmp line:\n%r" % (self.recordname, card,)
        self.readmmp_state.bug_error(msg)
    pass

# ==

class _MMP_Grammar(object):
    """
    An mmp file grammar (for reading only), not including the hardcoded part.
    Presently just a set of registered mmp-recordname-specific parser classes,
    typically subclasses of MMP_RecordParser.

    Note: as of 071019 there is only one of these, a global singleton
    _The_MMP_Grammar, private to this module (though it could be made
    public if desired). But nothing in principle prevents this class
    from being instantiated multiple times with different record parsers
    in each one.
    """
    def __init__(self):
        self._registered_record_parsers = {}
    def register_MMP_RecordParser(self, recordname, recordParser):
        assert issubclass(recordParser, MMP_RecordParser)
            ### not a valid requirement eventually, but good for catching errors
            # in initial uses of this system.
        self._registered_record_parsers[ recordname] = recordParser
    def get_registered_MMP_RecordParser(self, recordname):
        return self._registered_record_parsers.get( recordname, None)
    pass

_The_MMP_Grammar = _MMP_Grammar() # private grammar for registering record parsers
    # Note: nothing prevents this _MMP_Grammar from being public,
    # except that for now we're just making public a static function
    # for registering into it, register_MMP_RecordParser,
    # and one for accessing it for reading, find_registered_parser_class,
    # so to avoid initial confusion I'm only making those
    # static functions public. [bruce 071019/080304]

# ==

def register_MMP_RecordParser(recordname, recordParser):
    """
    Public function for registering RecordParsers with specific recordnames
    in the default grammar for reading MMP files. RecordParsers are typically
    subclasses of class MMP_RecordParser, whose docstring describes the
    interface they must satisfy to be registered here.
    """
    if recordname not in _RECORDNAMES_THAT_MUST_BE_REGISTERED:
        # probably too early for a history warning, for now
        print "\n*** Warning: a developer forgot to add %r "\
              "to _RECORDNAMES_THAT_MUST_BE_REGISTERED" % (recordname,)
        assert type(recordname) is type("")
    _The_MMP_Grammar.register_MMP_RecordParser( recordname, recordParser)
    return

# Now register some fake recordparsers for all documented mmp recordnames
# whose parsers are not hardcoded into class _readmmp_state,
# so if other code forgets to register the real ones before we first read
# an mmp file containing them, we'll detect the error instead of just
# ignoring those records as we intentionally ignore unrecognized records.
# We do this directly on import, to be sure it's not done after the real ones
# are registered, and since doing so should not cause any trouble.

_RECORDNAMES_THAT_MUST_BE_REGISTERED = [
    'comment',
    'gamess',
    'povrayscene',
    'DnaSegmentMarker',
    'DnaStrandMarker',
 ]
    ### TODO: extend this list as more parsers are moved out of files_mmp.py

for recordname in _RECORDNAMES_THAT_MUST_BE_REGISTERED:
    register_MMP_RecordParser( recordname, _fake_MMP_RecordParser)

# ==

def find_registered_parser_class(recordname): #bruce 071019
    """
    Return the class registered for parsing mmp lines which start with
    recordname (a string), or None if no class was registered (yet)
    for that recordname. (Such a class is typically a subclass of
    MMP_RecordParser.)

    [note: intended to be used only by the main mmp reading code.]
    """
    ### REVIEW: if we return None, should we warn about a subsequent
    # registration for the same name, since it's too late for it to help?
    # That would be wrong if the user added a plugin and then read another
    # mmp file that required it, but right if we have startup order errors
    # in registering standard readers vs. reading built-in mmp files.
    # Ideally, we'd behave differently during or after startup.
    # For now, we ignore this issue, except for the _fake_MMP_RecordParsers
    # registered for _RECORDNAMES_THAT_MUST_BE_REGISTERED above.

    return _The_MMP_Grammar.get_registered_MMP_RecordParser( recordname)

# end

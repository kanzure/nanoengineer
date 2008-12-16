# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
mmpformat_versions.py -- list of all mmpformat versions ever used, and
related parsing and testing code, and definitions of currently written
versions.

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 080328 split this out of files_mmp_writing.py, which was earlier
split out of files_mmp.py, which may have been called fileIO.py when
this list was first started.

bruce 080328 added reader code (not in this file) to warn if the mmpformat
being read appears to be too new.

bruce 080410 added a long string comment about the mmpformat situation
for the upcoming release of NE1 1.0.0.

TODO:

- fix the logic bug in "info leaf", described below.
"""

# ==

# imports are lower down

_RAW_LIST_OF_KNOWN_MMPFORMAT_VERSIONS = \
"""
Notes by bruce 050217 about mmp file format version strings,
and a list of all that have been used so far.

Developers -- please maintain this list!

For general notes about when and how to change the mmp format version,
see a separate file, files_mmp_format_version.txt,
which may be in the same directory as this source file.

WARNING: THIS LONG STRING LITERAL IS PARSED TO OBTAIN THE LIST
OF KNOWN VERSIONS. Any line in it which starts with "'" (a single quote)
must look like the lines below which present an mmpformat version string
that has been used. The testing code in this module extracts this list
and makes sure each version string can be parsed by the mmp reader's
code for doing that, and makes sure they are presented here in
chronological order, and fit other rules described with that code.

===

There was no mmpformat record before 050130 (shortly before Alpha-1 was
released), though the format had several versions before then, not all of
which were upward-compatible.

At some points, new elements were added, but this was not listed here
as a new required format (though it should have been),
since it was not noticed that this broke the reading of new files by
old code due to exceptions for unrecognized elements.

===

'050130' -- the mmpformat record, using this format-version "050130",
was introduced just before Alpha-1 release, at or shortly after
the format was changed so that two (rather than one) NamedView (Csys) records
were stored, one for Home View and one for Last View

'050130 required; 050217 optional' -- introduced by bruce on 050217,
when the info record was added, for info chunk hotspot.
(The optional part needs incrementing whenever more kinds of info records
are interpretable, at least once per "release".)

'050130 required; 050421 optional' -- bruce, adding new info records,
namely "info leaf hidden" and "info opengroup open";
and adding "per-part views" in the initial data group,
whose names are HomeView%d and LastView%d. All these changes are
backward-compatible -- old code will ignore the new records.

'050130 required; 050422 optional' -- bruce, adding forward_ref,
info leaf forwarded, and info leaf disabled.

'050502 required' -- bruce, now writing bond2, bond3, bonda, bondg
for higher-valence bonds appearing in the model (if any). (The code
that actually writes these is not in this file.)

Actually, "required" is conservative -- these are only "required" if
higher-valence bonds are present in the model being written.

Unfortunately, we don't yet have any way to say that to old code reading the file.
(This would require declaring these new bond records in the file, using a "declare"
record known by older reading-code, and telling it (as part of the declaration,
something formal that meant) "if you see these new record types and don't understand
them, then you miss some essential bond info of the kind carried by bond1 which you
do understand". In other words, "error if you see bond2 (etc), don't understand it,
but do understand (and care about) bond1".)

'050502 required; 050505 optional' -- bruce, adding "info chunk color".

'050502 required; 050511 optional' -- bruce, adding "info atom atomtype".

Strictly speaking, these are required in the sense that the atoms in the file
will seem to have the wrong number of bonds if these are not understood. But since
the file would still be usable to old code, and no altered file would be better
for old code, we call these new records optional.

'050502 required; 050618 preferred' -- bruce, adding url-encoding of '(', ')',
and '%' in node names (so ')' is legal in them, fixing part of bug 474).
I'm calling it optional, since old code could read new files with only the
harmless cosmetic issue of the users seeing the encoded node-names.

I also decided that "preferred" is more understandable than "optional".
Nothing yet uses that word (except the user who sees this format in the
Part Properties dialog), so no harm is caused by changing it.

'050502 required; 050701 preferred' -- bruce, adding gamess jig and info gamess records.

'050502 required; 050706 preferred' -- bruce, increased precision of Linear Motor force & stiffness

'050920 required' -- bruce, save carbomeric bonds as their own bond type bondc, not bonda as before

'050920 required; 051102 preferred' -- bruce, adding "info leaf enable_in_minimize"

'050920 required; 051103 preferred' -- this value existed for some time; unknown whether the prior one actually existed or not

'050920 required; 060421 preferred' -- bruce, adding "info leaf dampers_enabled"

'050920 required; 060522 preferred' -- bruce, adding "comment" and "info leaf commentline <encoding>" [will be in Alpha8]

'050920 required; 070415 preferred' -- bruce, adding "bond_direction" record

'050920 required; 080115 preferred' -- bruce, adding group classifications DnaGroup, DnaSegment, DnaStrand, Block

'050920 required; 080321 preferred' -- bruce, adding info chunk display_as_pam, save_as_pam

'080327 required' -- bruce, ADDED AFTER THE FACT to cover new display style names but not new "write_bonds_compactly" records

'080327 required; 080412 preferred' -- bruce, to cover mark's "info opengroup nanotube-parameters" record, added today
    (it should be ok that 080412 > 080328, since the pair of dates are compared independently, *but* the preferred
     date defaults to the required date, therefore we also have to upgrade '080328 required' to '080328 required; 080412 preferred')

'080327 required; 080523 preferred' -- bruce, adding "info atom +5data" for saving PAM3+5 data on Ss3 pseudoatoms

'080327 required; 080529 preferred' -- bruce, adding "info atom ghost" for marking placeholder bases aka ghost bases

'080328 required' -- bruce, adding new records bond_chain, directional_bond_chain, and dna_rung_bonds
                     (all enabled for writing by the option write_bonds_compactly in the present code),
                     and also using new display style names

'080328 required; 080412 preferred' -- bruce, see comment for '080327 required; 080412 preferred'

'080328 required; 080523 preferred' -- bruce, see comment for '080327 required; 080523 preferred'

'080328 required; 080529 preferred' -- bruce, see comment for '080327 required; 080529 preferred'
"""

# ==
 
# comment about status for NE1 1.0.0, to be released soon: [bruce 080410]

"""
This describes the mmp format situation as it's being revised today [080410]
to prepare for releasing NE1 1.0.0 in the near future. It covers
two incompatible changes (write_bonds_compactly and new display style names),
one being written by default, one not. (It's edited email, but ought
to be rewritten from scratch to be more useful as a comment in this file.)

==

We will not enable the write_bonds_compactly optimized mmp format by
default, for NE1 1.0.0. The risk is small, the work is small, the
testing is small, but they are all nonzero, and the gain is at most a
20-30% savings in disk space (and some in runtime for file open or
save, perhaps, but less than that) (never yet measured, FYI), and at
this late stage (shortly before the release, 080410) that gain doesn't
really justify any nonzero risk or extra work.

(One of the work and/or risk items is that there are loose ends in the
writing code for certain cases where strands leave one corner of a dna
ladder and reenter another corner of the same ladder -- rare, but
theoretically possible; easy to fix, but not yet fixed; only a writing
code bug, not needing any change in format or reading code. I'd
forgotten I still needed to fix those writing bugs when I was
discussing this on today's call.)

We should still (and I just did) enable the new display style names,
which *are* worth enabling now for all mmp writing. Those have
essentially zero risk, and are a confusion-reduction rather than just
an optimization.

These changes were both part of a single new "mmpformat version". The
code before now was conservative -- if either change was enabled, it
wrote the new mmpformat version, to warn reading code about both
changes being potentially present. To avoid needless worry by reading
code that understands new display names but not new bond records (as
we are writing now), I'll add an intermediate mmpformat version "after
the fact" for that, dated one day before the one that includes both
changes: '080327 required'. This won't matter for NE1 reading code
(since if it's new enough to care about the mmpformat version record,
it can also read both revisions to the mmp format itself), but will
allow other code to rely on that record to know that compact bonds are
not present even though new display style names are present.

==

The debug_pref we have now controls write_bonds_compactly for NE1
save, only. It will remain available but off by default. In current
code, there is no way to turn it on for mmp writing meant for ND1 or
NV1.

If time permits, we'll add 2 other debug_prefs to enable
write_bonds_compactly for writing files for ND1 and for NV1, so we can
easily test it for them later.

(ND1 has code to read it but this is untested. NV1 doesn't read it and
no work on making it read it is urgent -- unlike for its reading new
display style codes, now required but trivial.)

==

It is worth noting here that there are two known compatibility bugs
not covered by the mmpformat version record value:

- New element numbers cause crashes when read by old code,
  or turn into the wrong element (I think) in fairly recent code.
  (Ideally, we'd read them as special atoms which permitted any
   number of bonds and could be written out again with the same
   "unrecognized element number".)

- There is a logic bug in the "info leaf" record, or in any info kind
  which can apply to more mmp recordnames in newer writing code
  ("leaf" is the only one). Old readers will ignore the new mmp recordnames
  it applies to, but will recognize "info leaf" and will associate it
  with the wrong record (whichever prior one it can apply to which they
  *did* recognize and read). This bug won't matter for this release,
  even though it adds a DnaMarker record to the set which can use
  info leaf, since that record can't occur without new element numbers
  (for PAM DNA elements), and those cause all older released reading
  code to crash. But it will matter for the next subsequent release
  in which we add any jigs applicable to not-just-added element numbers.
  (It even affects this release, for a debugging-only jig which can mark any
   kind of atom, but that can be ignored since it's undocumented and only
   useful for debugging.)

  The solution is to close off the set of mmprecords info leaf can apply to,
  after this upcoming release of NE1 1.0.0, and revise that scheme somehow
  for any new mmp recordname that needs it, by adding a new info kind just for
  that mmp recordname (which can be isomorphic to info leaf).

==

Update, 080521: I fixed a bug in Atom.writemmp's rounding of negative
atom position coordinates. I didn't modify the mmpformat version for this,
since it would cause old code to warn when reading new files, even though
these are *more* compatible with that reader code than older-written
files are (since their atom coordinates were written by buggy code).
This forgoes a chance to record in the file whether the writing bug
was fixed, but there will very soon be a new preferred mmpformat version
for other reasons, so it's not important.
"""

# ==

# When you revise these, also revise (if necessary) the body of
# def _mmp_format_version_we_can_read() in files_mmp.py.

MMP_FORMAT_VERSION_TO_WRITE = '050920 required; 080321 preferred'
    # this semi-formally indicates required & ideal reader versions...
    # for notes about when/how to revise this, see general notes referred to
    # at end of module docstring.

MMP_FORMAT_VERSION_TO_WRITE__WITH_NEW_DISPLAY_NAMES = '080327 required; 080529 preferred'
    # For NE1 1.0.0 we will write new display names but not (by default)
    # the new bond records enabled in current code by 'write_bonds_compactly'.

MMP_FORMAT_VERSION_TO_WRITE__WITH_COMPACT_BONDS_AND_NEW_DISPLAY_NAMES = '080328 required; 080529 preferred'
    # Soon after NE1 1.0.0, this can become the usually-written version, I hope,
    # and these separately named constants can go away. (Or, the oldest one
    # might be retained, so we can offer the ability to write mmp files for
    # old reading code, if there is any reason for that.)

_version_being_written_by_default = MMP_FORMAT_VERSION_TO_WRITE__WITH_NEW_DISPLAY_NAMES
    # used locally, only for startup prints, but still it ought to be
    # kept in sync with reality as determined by files_mmp_writing.py
    # and by the default values of certain debug_prefs

# ==

from utilities.debug import print_compact_traceback

# ==

def _extract(raw_list):
    lines = raw_list.split('\n')
    res = []
    for line in lines:
        if line.startswith("'"):
            res.append( line.split("'")[1] )
        continue
    return res

KNOWN_MMPFORMAT_VERSIONS = _extract(_RAW_LIST_OF_KNOWN_MMPFORMAT_VERSIONS)

assert MMP_FORMAT_VERSION_TO_WRITE in KNOWN_MMPFORMAT_VERSIONS

assert MMP_FORMAT_VERSION_TO_WRITE__WITH_NEW_DISPLAY_NAMES in KNOWN_MMPFORMAT_VERSIONS

assert MMP_FORMAT_VERSION_TO_WRITE__WITH_COMPACT_BONDS_AND_NEW_DISPLAY_NAMES in KNOWN_MMPFORMAT_VERSIONS

if _version_being_written_by_default != KNOWN_MMPFORMAT_VERSIONS[-1]:
    # warn, since this situation should be temporary; warning will be wrong
    # if these constants are not kept up to date with the actual writing code
    print "note: KNOWN_MMPFORMAT_VERSIONS contains more recent versions " \
          "than the one we're writing by default, %r" % _version_being_written_by_default
    pass

# ==

def parse_mmpformat(mmpformat): #bruce 080328
    """
    Parse an mmpformat value string of the syntax which can presently be used
    in an mmpformat mmp record, or any syntax which has been used previously.
    
    @return: a tuple of (ok, required_date, preferred_date)
             (containing types boolean, string (if ok), string (if ok),
              where the dates are raw date strings from the mmpformat record,
              understandable only to functions in this module, namely
              mmp_date_newer)
    
    @note: never raises exceptions for syntax errors, just returns ok == false
    """
    mmpformat = mmpformat.strip()
    try:
        sections = mmpformat.split(';')
        assert len(sections) in (1, 2)
        def parse_section(section, allowed_descriptive_words):
            """
            parse a section of the mmpformat record,
            such as "050502 required" or "050701 preferred",
            verifying the word is ok,
            and returning the date string.
            """
            words = section.strip().split()
            if len(words) == 1:
                assert words[0] == '050130' # kluge, special case
            else:
                assert len(words) == 2 and words[1] in allowed_descriptive_words
            return words[0]
        required_date = parse_section(sections[0], ["required"])
        if len(sections) == 1:
            preferred_date = required_date
        else:
            preferred_date = parse_section(sections[1], ["optional", "preferred"])
        return True, required_date, preferred_date
    except:
        msg = "syntax error in mmpformat (or bug) [%s]" % (mmpformat,)
        print_compact_traceback(msg + ": ")
        return False, None, None
    pass

def mmp_date_newer(date1, date2): #bruce 080328
    """
    """
    date1 = _normalize_mmp_date(date1)
    date2 = _normalize_mmp_date(date2)
    return (date1 > date2)

def _normalize_mmp_date(date): #bruce 080328
    """
    [private helper for mmp_date_newer]
    
    @note: raises exceptions for some mmp file syntax errors
    """
    assert type(date) == type('080328') and date.isdigit()
    if len(date) == 6:
        date = '20' + date
    assert len(date) == 8
    assert int(date) >= 20050130, "too early: %r" % (date,)
    assert date >= '20050130', "too early : %r" % (date,)
        # date of earliest mmpformat record, compared two equivalent ways
    return int(date)

def _mmp_format_newer( (required1, preferred1), (required2, preferred2) ):
    return mmp_date_newer( required1, required2) or \
           ( required1 == required2 and
             mmp_date_newer( preferred1, preferred2) )

# ==

def _test():
    """
    Make sure the parsing code can handle all the format versions,
    and (same thing) that newly defined format versions can be parsed.

    Also verify the versions occur in the right order.
    """
    last_version = None
    last_version_data = None
    
    for version in KNOWN_MMPFORMAT_VERSIONS:
        ok, required, preferred = parse_mmpformat(version)
        assert ok, "parse failure or error in %r" % (version,)
        assert not mmp_date_newer( required, preferred), "invalid dates in %r" % (version,)
        if last_version:
            assert _mmp_format_newer( (required, preferred), last_version_data ), \
                   "wrong order: %r comes after %r" % \
                   (version, last_version)
        last_version = version
        last_version_data = (required, preferred)
        continue
    # print "fyi: all %d mmpformat versions passed the test" % len(KNOWN_MMPFORMAT_VERSIONS)
    return

# always test, once at startup (since it takes less than 0.01 second)

_test()

# end

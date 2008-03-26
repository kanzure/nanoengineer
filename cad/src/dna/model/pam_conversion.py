# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
pam_conversion.py -- help dna model objects convert between PAM models

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities.GlobalPreferences import dna_updater_is_enabled

from utilities.constants import PAM_MODELS

import foundation.env as env
from utilities.Log import orangemsg, redmsg

# ==

# refile with class writemmp_mapping

class writemmp_mapping_memo(object):
    mapping = None
    def __init__(self, mapping):
        self.mapping = mapping
    def destroy(self): # todo: call, to avoid ref cycles 
        self.mapping = None
    pass

# ==

# helpers for DnaLadderRailChunk and subclasses

class DnaLadderRailChunk_writemmp_mapping_memo(writemmp_mapping_memo):

    convert_pam_enabled = False

    _ladder_memo = None
    
    def __init__(self, mapping, chunk):
        # immediately memoize some settings which need to be constant
        # during use, as a bug precaution. Also do whatever precomputes
        # are convenient.
        writemmp_mapping_memo.__init__(self, mapping)
        self.chunk = chunk
        self.ladder = chunk.ladder
        if not dna_updater_is_enabled():
            msg = "Warning: can't convert PAM model when dna updater is disabled; affects [N] chunk(s)"
            env.history.deferred_summary_message( orangemsg( msg))
        elif not self.ladder:
            # (might happen if dna updater is turned off at runtime -- not sure;
            #  note, doing that might have worse effects, like self.ladder existing
            #  but being out of date, causing traceback errors. #### FIX those sometime (elsewhere).)
            print "error: ladder not set during writemmp, can't convert pam model, in %r" % chunk
            msg = "Error: [N] chunk(s) don't have ladders set"
            env.history.deferred_summary_message( redmsg( msg))
        else:
            self.convert_pam_enabled = True
        if self.convert_pam_enabled:
            self._ladder_memo = mapping.get_memo_object_for(self.ladder)
        return
    
    def _f_save_as_what_PAM_model(self):
        if not self.convert_pam_enabled:
            return None
        return self._ladder_memo._f_save_as_what_PAM_model()

    pass

# ==

# helpers for DnaLadder

class DnaLadder_writemmp_mapping_memo(writemmp_mapping_memo):

    def __init__(self, mapping, ladder):
        # assume never created except by chunks, so we know dna updater is enabled
        writemmp_mapping_memo.__init__(self, mapping)
        assert dna_updater_is_enabled()
        self.ladder = ladder
        self.save_as_pam = self._compute_save_as_pam()
        return
    
    def _f_save_as_what_PAM_model(self):
        return self.save_as_pam

    def _compute_save_as_pam(self):
        common_answer = None
        mapping = self.mapping
        for chunk in self.ladder.all_chunks():
            r = chunk._f_requested_pam_model_for_save(mapping)
            if r is None:
                return None
            assert r
            assert r in PAM_MODELS
                # todo: enforce in mmp read (silently)
            if not common_answer:
                common_answer = r
            if r != common_answer:
                return None
            continue
        assert common_answer
        return common_answer

    pass

# TODO: (remember single strand domains tho -- what kind of chunks are they?)


# end


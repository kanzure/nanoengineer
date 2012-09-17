    def describe_leftDown_action(self, selatom): # bruce 050124
        # [bruce 050124 new feature, to mitigate current lack of model tree highlighting of pastable;
        #  this copies a lot of logic from leftDown, which is bad, should be merged somehow --
        #  maybe as one routine to come up with a command object, with a str method for messages,
        #  called from here to say potential cmd or from leftDown to give actual cmd to do ##e]
        # WARNING: this runs with every bareMotion (even when selatom doesn't change),
        # so it had better be fast.
        onto_open_bond = selatom and selatom.is_singlet()
        try:
            what = self.describe_paste_action(onto_open_bond) # always a string
            if what and len(what) > 60: # guess at limit
                what = what[:60] + "..."
        except:
            if debug_flags.atom_debug:
                print_compact_traceback("atom_debug: describe_paste_action failed: ")
            what = "click to paste"
        if onto_open_bond:
            cmd = "%s onto bondpoint at %s" % (what, self.posn_str(selatom))
            #bruce 050416 also indicate hotspot if we're on clipboard
            # (and if this hotspot will be drawn in special color, since explaining that
            #  special color is the main point of this statusbar-text addendum)
            if selatom is selatom.molecule.hotspot and not self.viewing_main_part():
                # also only if chunk at toplevel in clipboard (ie pastable)
                # (this is badly in need of cleanup, since both here and chunk.draw
                #  should not hardcode the cond for that, they should all ask the same method here)
                if selatom.molecule in self.o.assy.shelf.members:
                    cmd += " (hotspot)"
        elif selatom is not None:
            cmd = "click to drag %r" % selatom
            cmd += " (%s)" % selatom.atomtype.fullname_for_msg() # nested parens ###e improve
        else:
            cmd = "%s at \"water surface\"" % what
            #e cmd += " at position ..."
        return cmd

from selectMode:

        # someday -- we'll need to do this in a callback when selobj is set:
        ## self.update_selatom(event, msg_about_click = True)
        # but for now, I removed the msg_about_click option, since it's no longer used,
        # and can't yet be implemented correctly (due to callback issue when selobj
        # is not yet known), and it tried to call a method defined only in depositMode,
        # describe_leftDown_action, which I'll also remove or comment out. [bruce 071025]
        return not new_selobj_unknown # from update_selobj

the def of update_selatom that had code for msg_about_click was in selectAtomsMode.
that code was:

-        if msg_about_click:
-            # [always do the above, since many things can change what it should
-            # say] Come up with a status bar message about what we would paste
-            # now.
-            # [bruce 050124 new feature, to mitigate current lack of model
-            # tree highlighting of pastable]
-            msg = self.describe_leftDown_action( glpane.selatom)
-            env.history.statusbar_msg( msg)

removing this has also made more depositMode methods have no calls:

    def describe_paste_action(self, onto_open_bond): # bruce 050124; added onto_open_bond flag, 050127
        """
        return a description of what leftDown would paste or deposit (and how user could do that), if done now
        """
        #e should be split into "determine what to paste" and "describe it"
        # so the code for "determine it" can be shared with leftDown
        # rather than copied from it as now
        if self.w.depositState == 'Clipboard':
            p = self.pastable
            if p:
                if onto_open_bond:
                    ok = is_pastable_onto_singlet( p) #e if this is too slow, we'll memoize it
                else:
                    ok = is_pastable_into_free_space( p) # probably always true, but might as well check
                if ok:
                    return "click to paste %s" % self.pastable.name
                else:
                    return "can't paste %s" % self.pastable.name
            else:
                return "nothing to paste" # (trying would be an error)
        else:
            atype = self.pastable_atomtype()
            return "click to deposit %s" % atype.fullname_for_msg()

TODO: also check for calls of
posn_str,[still used! but NOT DEFINED IN selMode which uses it! ### FIX]
viewing_main_part,[still used!]
pastable_atomtype, [still used!]
and maybe uses of
self.w.depositState, [still used]
self.pastable, [still used]

is_pastable_onto_singlet, [still used but no longer need imports in depmode]
is_pastable_into_free_space [ditto]



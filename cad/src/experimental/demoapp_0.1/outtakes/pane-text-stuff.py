


outtakes:
    def set_tip(self, tip, obj):
        #print "set_tip:", tip, obj # works, except should be a better message when cmd is NOOP, and appearance/location
        self.tip.text = tip or ""
        self.tip_player = obj

    def unset_tip(self):
        self.set_tip("", None)

##    def on_mouse_motion_FROM_SOUNDSPACE(self, x, y, dx, dy): #### port me [already done?]
##        handle, offset = self.hit_test(x, y)
##        if handle:
##            self.tip.text = handle.tip # string constant describing what the handle adjusts
##            pos = self.player_transform(handle.player) # bks cmt: is this line needed?
##            self.tip_player = handle.player # the obj the handle is controlling
##        else:
##            self.tip.text = ''

        # tooltip [modified from soundspace.py; comments by bks, some are about the old context of the code]
        if self.tip_player: # the player that the tip should be near
            player_pos = self.player_transform(self.tip_player) # get transform for this player, for placing the tip
            # note: some other code has set tip.text... and has maintained tip_player ###k
            self.tip.x = player_pos[0]
            self.tip.y = player_pos[1] - 15
            self.tip.draw()

    def player_transform(self, obj): ### RENAME, get pos of obj for purpose of placing the tip
        try:
            return obj.pos
        except:
            print "tip needs pos from %r, nim" % (obj,)
            return None
        pass

        self.tip_player = None
            # the player object that the tip should be near; set in window on_mouse_motion [bks cmt]


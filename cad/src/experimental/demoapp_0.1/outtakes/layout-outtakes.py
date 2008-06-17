    # or maybe store this on the children, as child.size, child.pos, or child.rect, etc?
    # since the children sometimes need to know it too (incl when drawing).
    def find_child(self, x, y):
        for child, (cx,cy,w,h) in self._layout.iteritems(): # maps children -> rects
            if (cx <= x < cx + w and
                cy <= y < cy + h):
                return child
        return None

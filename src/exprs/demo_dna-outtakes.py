$Id$

      Ribbon2(1, 0.2, 1/10.5, 50, blue, color2 = green), # this color2 arg stuff is a kluge
      Highlightable( Ribbon2(1, 0.2, 1/10.5, 50, yellow, color2 = red), sbar_text = "bottom ribbon2" ),


debug_color_override = 0

class Corkscrew(WidgetExpr):
    "Corkscrew(radius, axis, turn, n, color) - axis is length in DX, turn might be 1/10.5"
    def init(self):
        radius, axis, turn, n, color = self.args #k checks length
    def draw(self, **mods):
        radius, axis, turn, n, color = self.args
            # axis is for x, theta starts 0, at top (y), so y = cos(theta), z = sin(theta)
        color = mods.get('color',color)##kluge; see comments in Ribbon.draw
        glDisable(GL_LIGHTING) ### not doing this makes it take the color from the prior object 
        glColor3fv(color)
        glBegin(GL_LINE_STRIP)
        points = self.points()
        for p in points:
            ##glNormal3fv(-DX) #####WRONG? with lighting: doesn't help, anyway. probably we have to draw ribbon edges as tiny rects.
            # without lighting, probably has no effect.
            glVertex3fv(p)
        glEnd()
        glEnable(GL_LIGHTING)
    def points(self, theta_offset = 0.0):
        radius, axis, turn, n, color = self.args
        res = []
        for i in range(n+1):
            theta = 2*pi*turn*i + theta_offset
            y = cos(theta) * radius; z = sin(theta) * radius
            x = i * axis
            res.append(V(x,y,z)) #e or could do this in list extension notation
        return res
    def _get_bright(self):
        radius, axis, turn, n, color = self.args
        return n * axis
    def _get_btop(self):
        radius, axis, turn, n, color = self.args
        return radius
    _get_bbottom = _get_btop
    pass


class Ribbon(Corkscrew):
    def draw(self, **mods):
        radius, axis, turn, n, color = self.args
        color0 = mods.get('color',color)##kluge
            ##e todo: should be more general; maybe should get "state ref" (to show & edit) as arg, too?
        if color != color0:
            if debug_color_override:
                print "color override in %r from %r to %r" % (self, color, color0) # seems to happen to much and then get stuck... ###@@@
        else:
            if debug_color_override:
                print "no color override in %r for %r" % (self, color) 
        color = color0
        offset = axis * 2
        halfoffset = offset / 2.0
        interior_color = ave_colors(0.8,color, white) ###
        self.args = list(self.args) # slow!
        # the next line (.args[-1]) is zapped since it causes the color2-used-for-ribbon1 bug;
        # but it was needed for the edge colors to be correct.
        # Try to fix that: add color = interior_color to Corkscrew.draw. [060729 233p g4]
        #self.args[-1] = interior_color #### kluge! and/or misnamed, since used for both sides i think #####@@@@@ LIKELY CAUSE OF BUG
        if 1:
            # draw the ribbon-edges; looks slightly better this way in some ways, worse in other ways --
            # basically, looks good on egdes that face you, bad on edges that face away (if the ribbons had actual thickness)
            # (guess: some kluge with lighting and normals could fix this)
            Corkscrew.draw(self, color = interior_color)
            if 0:
                glTranslate(offset, 0,0)            
                Corkscrew.draw(self, color = interior_color) ### maybe we should make the two edges look different, since they are (major vs minor groove)
                glTranslate(-offset, 0,0)
        
        ## glColor3fv(interior_color)

        # actually I want a different color on the back, can I get that? ###k
        glDisable(GL_CULL_FACE)
        drawer.apply_material(interior_color)
        ## glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color) # gl args partly guessed #e should add specularity, shininess...
        glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

        points = self.points()
        otherpoints = self.points(theta_offset = 150/360.0 * 2*pi)
        glBegin(GL_QUAD_STRIP) # this uses CULL_FACE so it only colors the back ones... but why gray not pink?
            # the answer - see draw_vane() -- I have to do a lot of stuff to get this right:
            # - set some gl state, use apply_material, get CCW ordering right, and calculate normals.
##        glColor3fv(interior_color)
        colorkluge = 0####@@@@ (works, except white edge is opposite as i'd expect, and doesn't happen for 1 of my 4 ribbons)
        if colorkluge:
            col1 = interior_color
            col2 = white
        for p in points:
            perpvec = norm(V(0, p[1], p[2])) # norm here means divide by radius, that might be faster
            ## perpvec = V(0,0,1) # this makes front & back different solid lightness, BUT the values depend on the glRotate we did
            glNormal3fv( perpvec)
            if colorkluge:
                drawer.apply_material(col1)
                col1, col2 = col2, col1
            glVertex3fv(p + offset * DX)
            if colorkluge and 1:
                drawer.apply_material(col1)
                col1, col2 = col2, col1
            glVertex3fv(p)
        glEnd()
        glEnable(GL_CULL_FACE)
        glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
        if 0:
            # ladder rungs - warning, they are buggy -- when they poke out, there are two in each place, but there should not be
            glDisable(GL_LIGHTING)
            glColor3fv(gray)
            glTranslate(halfoffset,0,0) # center the end within the ribbon width
            glBegin(GL_LINES)
            for p,op in zip(points,otherpoints):
                # bugs: they poke through; they look distracting (white worse than gray);
                # end1 (blue?) is not centered (fixed);
                # end2 is not clearly correct;
                # would look better in closeup if ends were inside rects (not on kinks like now), but never mind,
                # whole thing will be replaced with something better
                mid = (p + op)/2.0
                pv = p - mid
                opv = op - mid
                radfactor = 1.1 # make them poke out on purpose
                pv *= radfactor
                opv *= radfactor
                p = mid + pv
                op = mid + opv
                glVertex3fv(p)
                glVertex3fv(op)
            glEnd()
            glTranslate(-halfoffset,0,0)
            glEnable(GL_LIGHTING)
        return
    pass

class Ribbon2(Ribbon): ##, Atom): ####@@@@ class Atom - hack kluge experiment - had no noticable effect - i guess it wouldn't...
                                    # the selobj is not this, but the Highlighted made from it
    def draw(self):
        radius, axis, turn, n, color1 = self.args
        color2 = self.kws.get('color2')
        angle = 150.0
        ## angle = angle/360.0 * 2*pi
        Ribbon.draw(self, color = color1)
        glRotatef(angle, 1,0,0) # accepts degrees, I guess
        Ribbon.draw(self, color = color2)
        glRotatef(-angle, 1,0,0)
    pass

# Ribbon2 has: radius, axis (some sort of length - of one bp?), turn (angle??), n, color1, color2, and full position/orientation
# and it will have display modes, incl cyl with helix/base/groove texture, and flexible coloring;
# and ability to show the units in it, namely strands, or basepairs, or bases (selected/opd by type)
# and for us to add cmd bindings like "make neighbor strand" (if room) or "make crossover here" (maybe only on a base?)

# but as a first step, we can select it as a unit, copy/paste, deposit, move, etc.
# In this, it is sort of like an atom or set of co-selected atoms... some relation to chunk or jig too.
# I'd get best results by letting it be its own thing... but fastest, by borrowing one of those...

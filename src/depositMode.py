from Numeric import *
from modes import *
from VQT import *

class depositMode(basicMode):
    """ This class is used to manually add atoms to create any structure
    """
    def __init__(self, glpane):
        basicMode.__init__(self, glpane, 'DEPOSIT')
	self.backgroundColor = 174/256.0, 255/256.0, 247/256.0
	self.gridColor = 52/256.0, 129/256.0, 26/256.0
	self.newMolecule = None
	
	self.makeMenus()
	self.picking = False
	
    ### Operational functions(interface/public functions)
    def leftDown(self, event):
        """ Press left mouse button down to add an atom
	""" 
	atomPos = self.getCoords(event)
            
        if not self.newMolecule:
            self.newMolecule = molecule(self.o.assy)
            self.o.assy.addmol(self.newMolecule)
        newAtom = atom(self.o.assy.DesiredElement,
                       atomPos, self.newMolecule)
        self.newMolecule.shakedown()
        self.o.assy.updateDisplays()

 
    def Done(self):
        self.o.setMode(self.prevmode.modename)
                  

    def leftDouble(self, event):
        """ End deposit mode
	"""
	self.Done()

    def Draw(self):
        """ Draw a sketch plane to indicate where the new atoms will sit
	on by default Make the sketch plane translucent
	"""
        self.rectgrid()
        if self.sellist: self.pickdraw()
        self.o.assy.draw(self.o)



    def getCoords(self, event):
        """ Retrieve the object coordinates of the point on the screen
	with window coordinates(int x, int y) 
	"""
	# Transfer x, y into OpenGL format of Window coordinates

        x = event.pos().x()
        y = self.o.height - event.pos().y()

        p1 = A(gluUnProject(x, y, 0.0))
        p2 = A(gluUnProject(x, y, 1.0))
        at = self.o.assy.findpick(p1,norm(p2-p1),2.0)
        if at: pnt = at.posn()
        else: pnt = - self.o.pov
        k = (dot(self.o.lineOfSight,  pnt - p1) /
             dot(self.o.lineOfSight, p2 - p1))

        return p1+k*(p2-p1)
        

                             
    def rectgrid(self):
        """Assigned as griddraw for a rectangular grid that is always parallel
	to the screen.
	"""

	glColor3fv(self.gridColor)
	n=int(ceil(1.5*self.o.scale))
	# the grid is in eyespace
	glPushMatrix()
	q = self.o.quat
	glTranslatef(-self.o.pov[0], -self.o.pov[1], -self.o.pov[2])
	glRotatef(- q.angle*180.0/pi, q.x, q.y, q.z)
	glDisable(GL_LIGHTING)
	glBegin(GL_LINES)
	for x in range(-n, n+1):
	    glVertex(x,n,0)
	    glVertex(x,-n,0)
	    glVertex(n,x,0)
	    glVertex(-n,x,0)
	glEnd()
	glEnable(GL_LIGHTING)
	glPopMatrix()

        
    def makeMenus(self):
        
        self.Menu1 = self.makemenu([('Cancel', self.Flush),
                                    ('Restart', self.Restart),
                                    ('Backup', self.Backup),
                                    None,
                                    ('Carbon', self.w.setCarbon),
                                    ('Hydrogen', self.w.setHydrogen),
                                    ('Oxygen', self.w.setOxygen),
                                    ('Nitrogen', self.w.setNitrogen)])
        
        self.Menu2 = self.makemenu([('Move', self.move)
                                    ])
        
        self.Menu3 = self.makemenu([('Passivate', self.o.assy.modifyPassivate),
                                    ('Hydrogenate', self.o.assy.modifyHydrogenate),
                                    ('Separate', self.o.assy.modifySeparate)])

    def move(self):
        # go into move mode
        self.o.setMode('MODIFY')
                                    
    def skip(self):
        pass


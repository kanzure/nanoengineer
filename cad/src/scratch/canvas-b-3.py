#!/usr/bin/env python
# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.

"""
this is just some drag & drop example code -- it's not part of our product.

note -- it runs in Qt3 but has not been ported to Qt4.

it comes with a test file 'butterfly.png' which needs to be next to it for it to work.

it's made from a PyQt example which was made from a Qt example
and might be partly copyright by one or both of them.
it was made from examples3/canvas/canvas.py in a PyQt distro, which had no copyright notice,
but a nearby example, examples3/dirview.py, has a copyright from Trolltech which says
"This example program may be used, distributed and modified without limitation."

$Id$

if it's here in cad/src, that's just so it can import some code modules from our product
and/or be shared with other developers for testing. It need not be distributed with our product,
but if it is this doesn't seem to be a problem.

You can try running it as "./ExecSubDir.py scratch/canvas-b-3.py", but it uses
features of Qt3 that no longer exist in Qt4, so it needs to be ported before it
will work.

The current dir probably needs to be the same dir as this code module
so it can find the 'butterfly.png' file.
"""

import sys
from PyQt4.Qt import * # this statement has been ported to Qt4, but nothing else has!
import random

import time #bruce
try:
    from utilities.debug import print_compact_stack
except:
    print "could not import print_compact_stack"
    def print_compact_stack(msg):
        print "nim: print_compact_stack(%r)" % msg
    pass

no_dragevent_item = True # 050127

True = 1
False = 0
butterfly_fn = QString.null
butterflyimg = []
logo_fn = QString.null
logoimg = []
bouncy_logo = None
views = []


class ImageItem(QCanvasRectangle):
    def __init__(self,img,canvas):
        QCanvasRectangle.__init__(self,canvas)
        self.imageRTTI=984376
        self.image=img
        self.pixmap=QPixmap()
        self.setSize(self.image.width(), self.image.height())
        self.pixmap.convertFromImage(self.image, Qt.OrderedAlphaDither)

    def rtti(self):
        return self.imageRTTI

    def hit(self,p):
        ix = p.x()-self.x()
        iy = p.y()-self.y()
        if not self.image.valid( ix , iy ):
            return False
        self.pixel = self.image.pixel( ix, iy )
        return  (qAlpha( self.pixel ) != 0)

    def drawShape(self,p):
        p.drawPixmap( self.x(), self.y(), self.pixmap )

    def bruce_start_drag(self, dragsource): # drag and (don't bother to) drop this image!
        print "bruce_start_drag"

        if 0:
            # use QImageDrag
            print 'making: dragobj = QImageDrag( self.image, dragsource)'
            dragobj = QImageDrag( self.image, dragsource)
            ## the source has to be a QWidget -- not the canvas! TypeError: argument 2 of QImageDrag() has an invalid type
            print "made dragobj"
        else:
            # use QTextDrag
            print 'making: dragobj = QTextDrag( "copying 5 items", dragsource)'
            dragobj = QTextDrag( "copying 5 items", dragsource)
            print "made it"

        if 0:
            print "not setting a custom pixmap this time"
            pass # don't set a custom pixmap
        elif 1:
            # set a custom pixmap
            print "now will set its pixmap to display during the drag",dragobj
            # warning, there is self.pixmap but that's the butterfly... hmm, would it work? let's try it:
            pixmap = self.pixmap
            dragobj.setPixmap(pixmap)
            print "set the pixmap to (presumably) the butterfly:",pixmap

        if 1:
            # try to modify the one Qt made for us to use? no, that fails (null pixmap), so:
            # try to modify the one we set, above.
            print "will try to modify the pixmap we just told Qt to use..."
            pixmap = dragobj.pixmap()
            print "this is the pixmap object:",pixmap # it's different id than the one we set, probably setPixmap copies it
            print "this is another get of that, is it same id?",dragobj.pixmap() # no! i guess it copies on get, at least.
            # let's hope we own it! try this twice to find out... i mean click on two butterflys in a row...
            # hmm, can we draw on it?
            p = painter = QPainter(pixmap)
                # if we never did dragobj.setPixmap ourselves, then [for QImageDrag or QTextDrag] we get
                #   QPainter::begin: Cannot paint null pixmap
            color = Qt.blue
            p.setPen(QPen(color, 3)) # 3 is pen thickness
            w,h = 100,9
            x,y = pos = (0,0)
            x += int(time.time()) % 10 # randomize coords
            y += int(time.time()*10.0) % 10
            p.drawEllipse(x,y,h,h) # this worked, various sizes of butterfly got this blue circle (same size) in topleft corner
            print "after drawing, pixmap is ",pixmap
            ## this is needed:
            del p, painter
            print "after del p,painter, pixmap is ",pixmap
            ## since without it we got (various ones of these, I guess randomly): [btw that checksum on free, verify on malloc is a clever idea! ###@@@]
            #
            ##Qt: QPaintDevice: Cannot destroy paint device that is being painted.  Be sure to QPainter::end() painters!
            ##Segmentation fault
            ##Exit 139
            #
            ##Qt: QPaintDevice: Cannot destroy paint device that is being painted.  Be sure to QPainter::end() painters!
            ##*** malloc[1008]: error for object 0x9abb0d0: Incorrect checksum for freed object - object was probably modified after being freed; break at szone_error
            ##Segmentation fault
            ##Exit 139

            dragobj.setPixmap(pixmap) # needed?? yes!
            print "setting pixmap back into dragobj, might not be needed"
            """
making: dragobj = QTextDrag( "copying 5 items", dragsource)
made it
will try to modify the pixmap Qt made for us to use...
this is the pixmap object: <__main__.qt.QPixmap object at 0x88bd0>
QPainter::begin: Cannot paint null pixmap
QPainter::setPen: Will be reset by begin()
            """
            pass

        wantdel = dragobj.dragCopy()
            # during this call, we do recursive event processing, including the expected dragEnter event, and moves and drop,
            # plus another *initial* unexpected dragEnter event, different event object. To debug those, print the stack!
            # then our dropevent has an exception (for known reasons).
        # Then, this prints: wantdel = None, target = source = the figureeditor obj (expected).
        print "dragged image: wantdel = %r, target = %r, dragsource = %r" % (wantdel, dragobj.target(), dragsource)
        ###e delete it?

class NodeItem(QCanvasEllipse):
    def __init__(self,canvas):
        QCanvasEllipse.__init__(self,6,6,canvas)
        self.__inList=[]
        self.__outList=[]
        self.setPen(QPen(Qt.black))
        self.setBrush(QBrush(Qt.red))
        self.setZ(128)

    def addInEdge(self,edge):
        self.__inList.append(edge)

    def addOutEdge(self,edge):
        self.__outList.append(edge)

    def moveBy(self,dx,dy):
        QCanvasEllipse.moveBy(self,dx,dy)
        for each_edge in self.__inList:
            each_edge.setToPoint( int(self.x()), int(self.y()) )
        for each_edge in self.__outList:
            each_edge.setFromPoint( int(self.x()), int(self.y()) )

class EdgeItem(QCanvasLine):
    __c=0
    def __init__(self,fromNode, toNode,canvas):
        QCanvasLine.__init__(self,canvas)
        self.__c=self.__c+1
        self.setPen(QPen(Qt.black))
        self.setBrush(QBrush(Qt.red))
        fromNode.addOutEdge(self)
        toNode.addInEdge(self)
        self.setPoints(int(fromNode.x()),int(fromNode.y()), int(toNode.x()), int(toNode.y()))
        self.setZ(127)

    def setFromPoint(self,x,y):
        self.setPoints(x,y,self.endPoint().x(),self.endPoint().y())

    def setToPoint(self,x,y):
        self.setPoints(self.startPoint().x(), self.startPoint().y(),x,y)

    def count(self):
        return self.__c

    def moveBy(self,dx,dy):
        pass


class FigureEditor(QCanvasView):
    def __init__(self,canvas1,parent,name,wflags):
        QCanvasView.__init__(self,canvas1,parent,name,wflags) # bruce cmt: last arg: WFlags f = 0
        self.__moving=0
        self.__moving_start= 0
        # bruce added the rest
        # note: self.canvas() returns canvas1, no need to store it
        self.viewport().setAcceptDrops(True) # does doing this first make autoscroll work??? ###@@@ [using viewport, does it now???]
        ## self.viewport().setDragAutoScroll(True) ###@@@ bruce hack experiment 050103. doesn't work. [using viewport, does it now???]
        self.setDragAutoScroll(True)
        # Qt doc says "Of course this works only if the viewport accepts drops." and refers to "drag move events"...
        # so maybe it's only for "drag and drop".
        print "self.dragAutoScroll()",self.dragAutoScroll()

    def contentsMousePressEvent(self,e): # QMouseEvent e
        point = self.inverseWorldMatrix().map(e.pos())
        ilist = self.canvas().collisions(point) #QCanvasItemList ilist
        for each_item in ilist:
            if each_item.rtti()==984376: # bruce comment: this is for the custom image item class
                if not each_item.hit(point):
                    continue
            self.__moving=each_item
            self.__moving_start=point
            try: ###@@@ bruce exper
                meth = self.__moving.bruce_start_drag
            except AttributeError:
                pass
            else:
                dragsource = self
                meth(dragsource) # lack of separate call was hiding bugs!
                # recursive event processing occurs during that call.
            return
        self.__moving=0

    def clear(self):
        ilist = self.canvas().allItems()
        for each_item in ilist:
            if each_item:
                each_item.setCanvas(None)
                del each_item
        self.canvas().update()

    def contentsMouseMoveEvent(self,e):
        ## print "contentsMouseMoveEvent"
        if  self.__moving :
            point = self.inverseWorldMatrix().map(e.pos());
            self.__moving.moveBy(point.x() - self.__moving_start.x(),point.y() - self.__moving_start.y())
            self.__moving_start = point
        self.canvas().update()

    ###@@@ bruce added the rest; changed them to contents methods late in testing, 37pm

##    def contentsDragEnterEvent(self, event):
##        print "does this exist?" # apparently not. but try again with no other one... still not.
##        # BUT IT DOES if we do self.viewport().setAcceptDrops(True) instead of self.setAcceptDrops(True)!
##        # And then that does make autoscroll work, though it work pretty badly, just like in the Mac finder.

    def contentsDragEnterEvent(self, event): # the dup ones can't be told apart by any method i know of except lack of move/drop/leave.
        print_compact_stack("dragEnterEvent stack (fyi): ")
            # nothing on stack except this code-line and app.exec_() [not even a call of this method]
        try:
            event.bruce_saw_me
        except:
            event.bruce_saw_me = 1
        else:
            event.bruce_saw_me = event.bruce_saw_me + 1
        self.oldevent = event ###@@@
        ok = QTextDrag.canDecode(event) or QImageDrag.canDecode(event) or QUriDrag.canDecode(event)
        print "drag enter %r, pos.x = %r, ok = %r (determines our acceptance)" % (event, event.pos().x(), ok)
        print "event.bruce_saw_me",event.bruce_saw_me
        ## try doing this later: event.accept(ok)
        canvas = self.canvas()
        i = QCanvasText(canvas)
        i.setText("drag action type %r, %r" % (event.action(), time.asctime()))
        self.dragevent_item = i
        i.show() # would removing this fix the dup enter? no, but it makes the text invisible!
        self.dragevent_item_move_to_event(event)
        event.accept(ok) # try doing this here, does it remove that duplicate enter?
         # no; moving codeline to here has no effect i can notice.

    def contentsDragMoveEvent(self, event):
        ##print "contentsDragMoveEvent"
        self.dragevent_item_move_to_event(event)

    def dragevent_item_move_to_event(self, event):
        if no_dragevent_item:
            return
        ## print "drag move, raw x,y = (%r, %r)" % (event.pos().x(), event.pos().y()) # this seems to happen once after the drop!
        # do we need a different retval from the dropEvent processor??
        point = self.inverseWorldMatrix().map(event.pos()) # using event.pos() directly failed when scrollbar was moved
        # why does this work whether the event was given to a contents method or a scrollview method? ###@@@ is it same or only close?
        x = point.x()
        y = point.y()
        self.dragevent_item.move(x,y)

    def contentsDragLeaveEvent(self, event):
        print "drag leave, event == %r" % event ## pos = %r" % event.pos() # AttributeError: pos ###@@@
        ## self.dragevent_item_move_to_event(event)
        self.dragevent_item.setColor(Qt.red) # guesses

    def contentsDropEvent(self, event):
        print "drop event %r" % event ###@@@
        for i in range(20):
            fmt = event.format(i)
            print "dropevent.format[%d] = %r" % (i, fmt) # should be list of available formats!
            if i > 0 and fmt == None:
                break
        okimage = QImageDrag.canDecode(event)
        okuri = QUriDrag.canDecode(event)
        oktext = QTextDrag.canDecode(event)
        print "oktext = %r, okimage = %r, okuri = %r" % (oktext, okimage, okuri)
        print "event.source(), event.action()",event.source(), event.action()
        print "accepting it iff we can decode it, but not creating anything"
        print "fyi: QDropEvent.Copy, QDropEvent.Move, QDropEvent.Link are:",QDropEvent.Copy, QDropEvent.Move, QDropEvent.Link
        if okimage:
            print "accepting image"
            img = QImage()
            res = QImageDrag.decode(event, img) #guess
            print "got this res & image (discarding it but accepting the event): %r, %r" % (res,img)
            event.accept(True)
        elif oktext:
            print "accepting text"
            str1 = QString() # see dropsite.py in examples3
            res = QTextDrag.decode(event, str1)
            text = str(str1)
            print "got this res and text: %r, %r" % (res,text) # guess: from finder it will be filename
            event.accept(True)  # was still acceptAction for a long time, by accident
            ## event.acceptAction(True) # DANGER, acceptAction MIGHT DELETE IT -- but it did not, maybe since text only?
            # or acceptAction? no, that's if we actually understand and do the specific requested action.
            # from finder with a file, it's Move!
        else:
            event.accept(False)
        ## return True ####@@@ guess; wrong: TypeError: invalid result type from FigureEditor.dropEvent()

class BouncyLogo(QCanvasSprite):
    def __init__(self,canvas):
        # Make sure the logo exists.
        global bouncy_logo
        if bouncy_logo is None:
            bouncy_logo=QCanvasPixmapArray("qt-trans.xpm")

        QCanvasSprite.__init__(self,None,canvas)
        self.setSequence(bouncy_logo)
        self.setAnimated(True)
        self.initPos()
        self.logo_rtti=1234

    def rtti(self):
        return self.logo_rtti

    def initPos(self):
        self.initSpeed()
        trial=1000
        self.move(random.random()%self.canvas().width(), random.random()%self.canvas().height())
        self.advance(0)
        trial=trial-1
        while (trial & (self.xVelocity()==0 )& (self.yVelocity()==0)):
            elf.move(random.random()%self.canvas().width(), random.random()%self.canvas().height())
            self.advance(0)
            trial=trial-1

    def initSpeed(self):
        speed=4.0
        d=random.random()%1024/1024.0
        self.setVelocity(d*speed*2-speed, (1-d)*speed*2-speed)

    def advance(self,stage):
        if stage == 0:
            vx=self.xVelocity()
            vy=self.yVelocity()
            if (vx == 0.0) & (vy == 0.0):
                self.initSpeed()
                vx=self.xVelocity()
                vy=self.yVelocity()

            nx=self.x()+vx
            ny=self.y()+vy

            if (nx<0) | (nx >= self.canvas().width()):
                vx=-vx
            if (ny<0) | (ny >= self.canvas().height()):
                vy=-vy

            for bounce in [0,1,2,3]:
                l=self.collisions(False)
                for hit in l:
                    if (hit.rtti()==1234) & (hit.collidesWith(self)):
                        if bounce == 0:
                            vx=-vx
                        elif bounce == 1:
                            vy=-vy
                            vx=-vx
                        elif bounce == 2:
                            vx=-vx
                        elif bounce == 3:
                            vx=0
                            vy=0
                        self.setVelocity(vx,vy)
                        break

            if (self.x()+vx < 0) | (self.x()+vx >= self.canvas().width()):
                vx=0
            if (self.y()+vy < 0) | (self.y()+vy >= self.canvas().height()):
                vy=0

            self.setVelocity(vx,vy)
        elif stage == 1:
            QCanvasItem.advance(self,stage)


class Main (QMainWindow):
    def __init__(self,canvas1,parent,name,wflags=0):
        QMainWindow.__init__(self,parent,name,wflags)
        self.editor=FigureEditor(canvas1,self,name,wflags)
        self.printer=QPrinter()
        self.dbf_id=0
        self.canvas=canvas1
        self.mainCount=0
        file=QPopupMenu(self.menuBar())
        file.insertItem("&Fill canvas", self.init, Qt.CTRL+Qt.Key_F)
        file.insertItem("&Erase canvas", self.clear, Qt.CTRL+Qt.Key_E)
        file.insertItem("&New view", self.newView, Qt.CTRL+Qt.Key_N)
        file.insertItem("(text editor)", self.textEditor)
        file.insertSeparator();
        file.insertItem("&Print", self._print, Qt.CTRL+Qt.Key_P)
        file.insertSeparator()
        file.insertItem("E&xit", qApp, SLOT("quit()"), Qt.CTRL+Qt.Key_Q)
        self.menuBar().insertItem("&File", file)

        edit = QPopupMenu(self.menuBar() )
        edit.insertItem("Add &Circle",  self.addCircle, Qt.ALT+Qt.Key_C)
        edit.insertItem("Add &Hexagon",  self.addHexagon, Qt.ALT+Qt.Key_H)
        edit.insertItem("Add &Polygon",  self.addPolygon, Qt.ALT+Qt.Key_P)
        edit.insertItem("Add Spl&ine", self.addSpline, Qt.ALT+Qt.Key_I)
        edit.insertItem("Add &Text", self.addText, Qt.ALT+Qt.Key_T)
        edit.insertItem("Add &Line", self.addLine, Qt.ALT+Qt.Key_L)
        edit.insertItem("Add &Rectangle", self.addRectangle, Qt.ALT+Qt.Key_R)
        edit.insertItem("Add &Sprite", self.addSprite, Qt.ALT+Qt.Key_S)
        edit.insertItem("Create &Mesh", self.addMesh, Qt.ALT+Qt.Key_M )
        edit.insertItem("Add &Alpha-blended image", self.addButterfly, Qt.ALT+Qt.Key_A)
        self.menuBar().insertItem("&Edit", edit)

        view = QPopupMenu(self.menuBar() );
        view.insertItem("&Enlarge", self.enlarge, Qt.SHIFT+Qt.CTRL+Qt.Key_Plus);
        view.insertItem("Shr&ink", self.shrink, Qt.SHIFT+Qt.CTRL+Qt.Key_Minus);
        view.insertSeparator();
        view.insertItem("&Rotate clockwise", self.rotateClockwise, Qt.CTRL+Qt.Key_PageDown);
        view.insertItem("Rotate &counterclockwise", self.rotateCounterClockwise, Qt.CTRL+Qt.Key_PageUp);
        view.insertItem("&Zoom in", self.zoomIn, Qt.CTRL+Qt.Key_Plus);
        view.insertItem("Zoom &out", self.zoomOut, Qt.CTRL+Qt.Key_Minus);
        view.insertItem("Translate left", self.moveL, Qt.CTRL+Qt.Key_Left);
        view.insertItem("Translate right", self.moveR, Qt.CTRL+Qt.Key_Right);
        view.insertItem("Translate up", self.moveU, Qt.CTRL+Qt.Key_Up);
        view.insertItem("Translate down", self.moveD, Qt.CTRL+Qt.Key_Down);
        view.insertItem("&Mirror", self.mirror, Qt.CTRL+Qt.Key_Home);
        self.menuBar().insertItem("&View", view)

        self.options = QPopupMenu( self.menuBar() );
        self.dbf_id = self.options.insertItem("Double buffer", self.toggleDoubleBuffer)
        self.options.setItemChecked(self.dbf_id, True)
        self.menuBar().insertItem("&Options",self.options)

        self.menuBar().insertSeparator();

        help = QPopupMenu( self.menuBar() )
        help.insertItem("&About", self.help, Qt.Key_F1)
        help.insertItem("&About Qt", self.aboutQt, Qt.Key_F2)
        help.setItemChecked(self.dbf_id, True)
        self.menuBar().insertItem("&Help",help)

        self.statusBar()

        self.setCentralWidget(self.editor)

        self.printer = 0
        self.tb=0
        self.tp=0

        self.init()

    def init(self):
        self.clear()
        r=24
        r=r+1
        random.seed(r)
        for i in range(self.canvas.width()/56):
            self.addButterfly()
        for j in range(self.canvas.width()/85):
            self.addHexagon()
        for k in range(self.canvas.width()/128):
            self.addLogo()

    def newView(self):
        m=Main(self.canvas,None,"new window",Qt.WDestructiveClose)
        qApp.setMainWidget(m)
        m.show()
        qApp.setMainWidget(None)
        views.append(m)

    def textEditor(self):
        try:
            from qt_debug_hacks import make_DebugTextEdit
            self.te2 = make_DebugTextEdit()
        except:
            raise # for now
            self.texted = QTextEdit(self)
            self.texted.setFixedSize(100,100) # w,h
            self.texted.show() # puts it in upper left corner, over the canvas

    def clear(self):
        self.editor.clear()

    def help(self):
        QMessageBox.information(None, "PyQt Canvas Example",
            "<h3>The PyQt QCanvas classes example</h3><hr>"
            "<p>This is the PyQt implementation of "
            "Qt canvas example.</p> by Sadi Kose "
            "<i>(kose@nuvox.net)</i><hr>"
            "<ul>"
            "<li> Press ALT-S for some sprites."
            "<li> Press ALT-C for some circles."
            "<li> Press ALT-L for some lines."
            "<li> Drag the objects around."
            "<li> Read the code!"
            "</ul>","Dismiss")

    def aboutQt(self):
        QMessageBox.aboutQt(self,"PyQt Canvas Example")

    def toggleDoubleBuffer(self):
        s = not self.options.isItemChecked(self.dbf_id)
        self.options.setItemChecked(self.dbf_id,s)
        self.canvas.setDoubleBuffering(s)

    def enlarge(self):
        self.canvas.resize(self.canvas.width()*4/3, self.canvas.height()*4/3)

    def shrink(self):
        self.canvas.resize(self.canvas.width()*3/4, self.canvas.height()*3/4)

    def rotateClockwise(self):
        m = self.editor.worldMatrix()
        m.rotate( 22.5 )
        self.editor.setWorldMatrix( m )

    def rotateCounterClockwise(self):
        m = self.editor.worldMatrix()
        m.rotate( -22.5 )
        self.editor.setWorldMatrix( m )

    def zoomIn(self):
        m = self.editor.worldMatrix()
        m.scale( 2.0, 2.0 )
        self.editor.setWorldMatrix( m )

    def zoomOut(self):
        m = self.editor.worldMatrix()
        m.scale( 0.5, 0.5 )
        self.editor.setWorldMatrix( m )

    def mirror(self):
        m = self.editor.worldMatrix()
        m.scale( -1, 1 )
        self.editor.setWorldMatrix( m )

    def moveL(self):
        m = self.editor.worldMatrix()
        m.translate( -16, 0 )
        self.editor.setWorldMatrix( m )

    def moveR(self):
        m = self.editor.worldMatrix()
        m.translate( +16, 0 )
        self.editor.setWorldMatrix( m )

    def moveU(self):
        m = self.editor.worldMatrix()
        m.translate( 0, -16 )
        self.editor.setWorldMatrix( m )

    def moveD(self):
        m = self.editor.worldMatrix();
        m.translate( 0, +16 );
        self.editor.setWorldMatrix( m )

    def _print(self):
        if not self.printer:
            self.printer = QPrinter()
        if  self.printer.setup(self) :
            pp=QPainter(self.printer)
        self.canvas.drawArea(QRect(0,0,self.canvas.width(),self.canvas.height()),pp,False)

    def addSprite(self):
        i = BouncyLogo(self.canvas)
        i.setZ(256*random.random()%256);
        i.show();

    def addButterfly(self):
        if butterfly_fn.isEmpty():
            return
        if not butterflyimg:
            butterflyimg.append(QImage())
            butterflyimg[0].load(butterfly_fn)
            butterflyimg.append(QImage())
            butterflyimg[1] = butterflyimg[0].smoothScale( int(butterflyimg[0].width()*0.75),
                int(butterflyimg[0].height()*0.75) )
            butterflyimg.append(QImage())
            butterflyimg[2] = butterflyimg[0].smoothScale( int(butterflyimg[0].width()*0.5),
                int(butterflyimg[0].height()*0.5) )
            butterflyimg.append(QImage())
            butterflyimg[3] = butterflyimg[0].smoothScale( int(butterflyimg[0].width()*0.25),
                int(butterflyimg[0].height()*0.25) )

        i = ImageItem(butterflyimg[int(4*random.random()%4)],self.canvas)
        i.move((self.canvas.width()-butterflyimg[0].width())*random.random()%(self.canvas.width()-butterflyimg[0].width()),
            (self.canvas.height()-butterflyimg[0].height())*random.random()%(self.canvas.height()-butterflyimg[0].height()))
        i.setZ(256*random.random()%256+250);
        i.show()

    def addLogo(self):
        if logo_fn.isEmpty():
            return;
        if not logoimg:
            logoimg.append(QImage())
            logoimg[0].load( logo_fn )
            logoimg.append(QImage())
            logoimg[1] = logoimg[0].smoothScale( int(logoimg[0].width()*0.75),
                int(logoimg[0].height()*0.75) )
            logoimg.append(QImage())
            logoimg[2] = logoimg[0].smoothScale( int(logoimg[0].width()*0.5),
                int(logoimg[0].height()*0.5) )
            logoimg.append(QImage())
            logoimg[3] = logoimg[0].smoothScale( int(logoimg[0].width()*0.25),
                int(logoimg[0].height()*0.25) );

        i = ImageItem(logoimg[int(4*random.random()%4)],self.canvas)
        i.move((self.canvas.width()-logoimg[0].width())*random.random()%(self.canvas.width()-logoimg[0].width()),
            (self.canvas.height()-logoimg[0].width())*random.random()%(self.canvas.height()-logoimg[0].width()))
        i.setZ(256*random.random()%256+256)
        i.show()

    def addCircle(self):
        i = QCanvasEllipse(50,50,self.canvas)
        i.setBrush( QBrush(QColor(256*random.random()%32*8,256*random.random()%32*8,256*random.random()%32*8) ))
        i.move(self.canvas.width()*random.random()%self.canvas.width(),self.canvas.width()*random.random()%self.canvas.height())
        i.setZ(256*random.random()%256)
        i.show()

    def addHexagon_old(self):
        i = QCanvasPolygon(self.canvas)
        size = canvas.width() / 25
        pa=QPointArray(6)
        pa.setPoint(0,QPoint(2*size,0))
        pa.setPoint(1,QPoint(size,-size*173/100))
        pa.setPoint(2,QPoint(-size,-size*173/100))
        pa.setPoint(3,QPoint(-2*size,0))
        pa.setPoint(4,QPoint(-size,size*173/100))
        pa.setPoint(5,QPoint(size,size*173/100))
        i.setPoints(pa)
        i.setBrush( QBrush(QColor(256*random.random()%32*8,256*random.random()%32*8,256*random.random()%32*8) ))
        i.move(self.canvas.width()*random.random()%self.canvas.width(),self.canvas.width()*random.random()%self.canvas.height())
        i.setZ(256*random.random()%256)
        i.show()

    def addHexagon(self):###brucehack 050106... these triangles look bad, need antialiasing, i suppose should be images
        i = QCanvasPolygon(self.canvas)
        w = h = 9
        pa=QPointArray(3)
        pa.setPoint(0,QPoint(0,0))
        # pa.setPoint(1,QPoint(size,-size*173/100))
        pa.setPoint(1,QPoint(w,h/2))
        # pa.setPoint(3,QPoint(-2*size,0))
        pa.setPoint(2,QPoint(0,h))
        # pa.setPoint(5,QPoint(size,size*173/100))
        i.setPoints(pa)
        i.setBrush( QBrush(QColor(128,128,128) ))
        i.move(self.canvas.width()*random.random()%self.canvas.width(),self.canvas.width()*random.random()%self.canvas.height())
        i.show()

    def addPolygon(self):
        i = QCanvasPolygon(self.canvas)
        size = self.canvas.width()/2
        pa=QPointArray(6)
        pa.setPoint(0, QPoint(0,0))
        pa.setPoint(1, QPoint(size,size/5))
        pa.setPoint(2, QPoint(size*4/5,size))
        pa.setPoint(3, QPoint(size/6,size*5/4))
        pa.setPoint(4, QPoint(size*3/4,size*3/4))
        pa.setPoint(5, QPoint(size*3/4,size/4))

        i.setPoints(pa)
        i.setBrush(QBrush( QColor(256*random.random()%32*8,256*random.random()%32*8,256*random.random()%32*8)) )
        i.move(self.canvas.width()*random.random()%self.canvas.width(),self.canvas.width()*random.random()%self.canvas.height())
        i.setZ(256*random.random()%256)
        i.show()

    def addSpline(self):
        i = QCanvasSpline(self.canvas)
        size = canvas.width()/6
        pa=QPointArray(12)
        pa.setPoint(0,QPoint(0,0))
        pa.setPoint(1,QPoint(size/2,0))
        pa.setPoint(2,QPoint(size,size/2))
        pa.setPoint(3,QPoint(size,size))
        pa.setPoint(4,QPoint(size,size*3/2))
        pa.setPoint(5,QPoint(size/2,size*2))
        pa.setPoint(6,QPoint(0,size*2))
        pa.setPoint(7,QPoint(-size/2,size*2))
        pa.setPoint(8,QPoint(size/4,size*3/2))
        pa.setPoint(9,QPoint(0,size))
        pa.setPoint(10,QPoint(-size/4,size/2))
        pa.setPoint(11,QPoint(-size/2,0))
        i.setControlPoints(pa)
        i.setBrush( QBrush(QColor(256*random.random()%32*8,256*random.random()%32*8,256*random.random()%32*8) ))
        i.move(self.canvas.width()*random.random()%self.canvas.width(),self.canvas.width()*random.random()%self.canvas.height())
        i.setZ(256*random.random()%256)
        i.show()

    def addText(self):
        i = QCanvasText(self.canvas)
        i.setText("QCanvasText")
        i.move(self.canvas.width()*random.random()%self.canvas.width(),self.canvas.width()*random.random()%self.canvas.height())
        i.setZ(256*random.random()%256)
        i.show()

    def addLine(self):
        i = QCanvasLine(self.canvas);
        i.setPoints( self.canvas.width()*random.random()%self.canvas.width(), self.canvas.width()*random.random()%self.canvas.height(),
                self.canvas.width()*random.random()%self.canvas.width(), self.canvas.width()*random.random()%self.canvas.height() )
        i.setPen( QPen(QColor(256*random.random()%32*8,256*random.random()%32*8,256*random.random()%32*8), 6) )
        i.setZ(256*random.random()%256)
        i.show()

    def ternary(self,exp,x,y):
        if exp:
            return x
        else:
            return y

    def addMesh(self):
        x0 = 0;
        y0 = 0;

        if not self.tb:
            self.tb = QBrush( Qt.red )
        if not self.tp:
            self.tp = QPen( Qt.black )

        nodecount = 0;

        w = self.canvas.width()
        h = self.canvas.height()

        dist = 30
        rows = h / dist
        cols = w / dist

        #ifndef QT_NO_PROGRESSDIALOG
        #progress=QProgressDialog( "Creating mesh...", "Abort", rows,
        #         self, "progress", True );
        #endif

        lastRow=[]
        for c1 in range(cols):
            lastRow.append(NodeItem(self.canvas))
        for j in range(rows):
            n = self.ternary(j%2 , cols-1 , cols)
            prev = 0;
            for i in range(n):
                el = NodeItem( self.canvas )
                nodecount=nodecount+1
                r = 20*20*random.random()
                xrand = r %20
                yrand = (r/20) %20
                el.move( xrand + x0 + i*dist + self.ternary(j%2 , dist/2 , 0 ),
                    yrand + y0 + j*dist );

                if  j > 0 :
                    if  i < cols-1 :
                        EdgeItem( lastRow[i], el, self.canvas ).show()
                    if  j%2 :
                        EdgeItem( lastRow[i+1], el, self.canvas ).show()
                    elif i > 0 :
                        EdgeItem( lastRow[i-1], el, self.canvas ).show()
                if  prev:
                    EdgeItem( prev, el, self.canvas ).show()

                if  i > 0 :
                    lastRow[i-1] = prev
                prev = el
                el.show()

            lastRow[n-1]=prev
            #ifndef QT_NO_PROGRESSDIALOG
            #progress.setProgress( j )
            #if  progress.wasCancelled() :
            #   break
            #endif

        #ifndef QT_NO_PROGRESSDIALOG
        #progress.setProgress( rows )
        #endif
        #// qDebug( "%d nodes, %d edges", nodecount, EdgeItem::count() );

    def addRectangle(self):
        i = QCanvasRectangle( self.canvas.width()*random.random()%self.canvas.width(),
            self.canvas.width()*random.random()%self.canvas.height(),
            self.canvas.width()/5,self.canvas.width()/5,self.canvas)
        z = 256*random.random()%256
        i.setBrush( QBrush(QColor(z,z,z) ))
        i.setPen( QPen(QColor(self.canvas.width()*random.random()%32*8,
            self.canvas.width()*random.random()%32*8,
            self.canvas.width()*random.random()%32*8), 6) )
        i.setZ(z)
        i.show()


if __name__ == '__main__':

    app=QApplication(sys.argv)

    if len(sys.argv) > 1:
        butterfly_fn=QString(sys.argv[1])
    else:
        butterfly_fn=QString("butterfly.png")

    if len(sys.argv) > 2:
        logo_fn = QString(sys.argv[2])
    else:
        logo_fn=QString("qtlogo.png")

    canvas=QCanvas(800,600)
    canvas.setAdvancePeriod(30)
    m=Main(canvas,None,"pyqt canvas example")
    m.resize(m.sizeHint())

    qApp.setMainWidget(m)
    m.setCaption("Qt Canvas Example ported to PyQt")
    if QApplication.desktop().width() > m.width() + 10 and QApplication.desktop().height() > m.height() + 30:
        m.show()
    else:
        m.showMaximized()

    m.show();
    #//    m.help();
    qApp.setMainWidget(None);

    QObject.connect( qApp, SIGNAL("lastWindowClosed()"), qApp, SLOT("quit()") )

    app.exec_() ###@@@ this is first on dragEnterEvent stack

    # We need to explicitly delete the canvas now (and, therefore, the main
    # window beforehand) to make sure that the sprite logo doesn't get garbage
    # collected first.
    views = []
    del m
    del canvas

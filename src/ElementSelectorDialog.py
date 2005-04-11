# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Huaicai\atom\cad\src\ElementSelectorDialog.ui'
#
# Created: Mon Apr 11 11:24:31 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x01" \
    "\x1c\x49\x44\x41\x54\x78\x9c\xed\x93\xb1\x6a\xc2" \
    "\x40\x18\xc7\x7f\x57\x1c\xa5\x8b\x53\x9e\xa1\x4d" \
    "\xe7\x82\xef\x50\x28\xb7\x95\x0e\x82\xd0\x9b\xe2" \
    "\x52\xc8\xa6\x64\x72\x28\x74\xca\x74\x0e\xe2\x20" \
    "\x2e\x0e\x85\xbe\x43\x8e\x2c\x72\xd2\xb4\xe2\xe6" \
    "\xe2\x13\xf4\x05\xec\x10\x12\x92\x96\x48\x89\x38" \
    "\x54\xfa\x9b\xbe\xbb\x3f\xf7\xdd\xf1\xe3\x3e\x61" \
    "\x8c\xe1\x18\x34\xea\x1e\x54\x4a\xed\xaa\x32\xad" \
    "\xb5\x38\xab\xdb\x18\x20\x89\x66\x24\xd1\x0c\x80" \
    "\xe9\x28\x66\x3a\x8a\xf3\xec\xa0\xc6\xfb\x38\x5a" \
    "\xe3\xdc\xf1\x3e\x67\x55\xb8\xed\xbb\xbc\xbe\x7f" \
    "\xb8\x2e\x65\xa5\x17\xb7\xba\x96\x56\xd7\x02\xb0" \
    "\x1e\x6c\x59\x0f\xb6\x00\x98\x61\x8c\x19\xa6\xfe" \
    "\xc6\x9b\x15\xe3\xcd\x0a\x80\xe6\xd2\xa7\xb9\xf4" \
    "\x81\x53\x70\x2c\xb2\x01\xa9\xe3\xb8\x8a\x1f\xff" \
    "\xb8\xdf\x8b\xe9\xf7\x52\x4f\x52\x4a\xa4\x94\x00" \
    "\x04\x8e\x25\x70\x52\xf7\x76\xee\x60\xe7\x4e\xba" \
    "\xbf\x70\x09\x16\x2e\xf0\xef\xb8\x02\xad\xb5\x68" \
    "\x14\x17\x59\xad\x94\xda\xbd\xbe\xbc\x03\x70\x73" \
    "\x7b\xc9\x24\x89\x00\xe8\xb8\x6d\xde\xfc\x4f\x00" \
    "\xae\x9e\xce\xf9\x78\xee\x00\x70\xf1\x38\xc9\xfd" \
    "\x66\x83\xf2\x87\x1d\x17\x39\xd4\x77\xc9\xf1\xf7" \
    "\xa0\x78\x49\x18\x86\x00\x78\x9e\xc7\x6f\x6a\x38" \
    "\x19\xc7\x45\xea\xf8\xd6\x5a\x8b\x2f\x29\x94\x78" \
    "\x0c\x77\x48\xb1\xfb\x00\x00\x00\x00\x49\x45\x4e" \
    "\x44\xae\x42\x60\x82"
image1_data = [
"22 22 10 1",
"a c #2d2d2d",
"c c #7f7f75",
"d c #808076",
"g c #b6b5b0",
"h c #b6b6aa",
"f c #b6b6ae",
"# c #b7b7ab",
"b c #b8b8ae",
"e c #c2c3c2",
". c #ffffff",
"......................",
"......................",
"......................",
"......#aaaaaaaaaaaaa..",
".....#aaaaaaaaaaaaaa..",
"....bacaa.......daaa..",
"...#adeaa......fadaa..",
"..#ade.aa.....gadeaa..",
"..aaaaaaaaaaaaade.aa..",
"..aaaaaaaaaaaaae..aa..",
"..aa...aa....aa...aa..",
"..aa...aa....aa...aa..",
"..aa...aa....aa...aa..",
"..aa...aaaaaaaaaaaaa..",
"..aa..#aaaaaaaaaaaaa..",
"..aa.#ade....aa.eda#..",
"..aadade.....aaeda#...",
"..aaade......aadah....",
"..aaaaaaaaaaaaaa#.....",
"..aaaaaaaaaaaaa#......",
"......................",
"......................"
]
image2_data = [
"22 22 6 1",
"a c #2d2d2d",
"c c #82d2b5",
"b c #9bf5d6",
"d c #a1a1a1",
"# c #c2c3c2",
". c #ffffff",
"......................",
"......................",
"......#aa#.......#aa#.",
"......abbaaaaaaaaabba.",
".....#abca.......abca.",
"....#adaa#......#aaa#.",
"...#a#.a.......#a#.a..",
".#aad..a.....aaa#..a..",
".abbaaaaaaaaabba...a..",
".abca..a....abca...a..",
".#aa#..a.....aa....a..",
"..a....a......a....a..",
"..a...#aa#....a..#aa#.",
"..a...abba....a..abba.",
"..a...abcaaaaaaaaabca.",
"..a..#aaa#....a..daa#.",
"..a.#a#.......a.#a#...",
".#aaa#......#aada#....",
".abba.......abba#.....",
".abcaaaaaaaaabca......",
".#aa#.......#aa#......",
"......................"
]
image3_data = [
"22 22 309 2",
"aV c #0f8380",
"aI c #188f89",
"aY c #1d5755",
"a0 c #1d5a58",
"bm c #215b59",
"#w c #21605f",
"a6 c #21615f",
"bc c #226260",
"ba c #229994",
"bd c #229a98",
"a9 c #23605f",
"bE c #23a8a3",
"bF c #246461",
"a5 c #255956",
"b. c #255d5b",
".3 c #265450",
"ap c #275350",
"#e c #276766",
"aW c #285c59",
"aJ c #28615d",
"bu c #28b0ae",
"cs c #2b625f",
"aP c #2b6765",
".2 c #2c5a56",
"#c c #2c6e6b",
"cc c #2e615c",
".4 c #2e6462",
".Y c #2e6865",
"#k c #2ec3c1",
"#j c #2f7473",
"aS c #2f9e98",
"#U c #2faaa5",
"#X c #305754",
".W c #305956",
".X c #30615f",
"bo c #30706e",
"cF c #315753",
"aa c #315855",
"a7 c #329391",
"aD c #329791",
"bn c #32aba5",
"a8 c #339391",
"bb c #349391",
"aX c #34a6a0",
".c c #355956",
".d c #365955",
"ci c #368d8b",
"ai c #369593",
"bX c #369693",
"#4 c #369694",
"bM c #369e97",
"a1 c #36b2b0",
".j c #375854",
"aw c #378d89",
"a. c #379690",
"b# c #37a9a4",
".b c #385955",
"#N c #389593",
"aC c #3a7775",
"#T c #3b7f7e",
"bt c #3d7e7e",
"#9 c #3d7f7d",
".B c #3e625f",
"cK c #3e6a65",
"ao c #3e7f7c",
"#v c #3ea8a5",
"am c #3efffe",
"aA c #40fefe",
"b3 c #41fdfc",
"ae c #41fdfe",
"al c #41ffff",
".V c #42635f",
"cl c #42feff",
".i c #435d59",
"cH c #43726e",
"ag c #43fdfc",
"af c #43ffff",
"#1 c #44fcfc",
"at c #44fefd",
"bP c #456b68",
".A c #45a3a0",
"ad c #45fbfc",
"an c #45fcfa",
"c. c #45fdfb",
".n c #46635f",
"cr c #46bbb5",
"#M c #46c1bd",
"#Y c #46fcfd",
"#8 c #46fdfb",
"bi c #47bfbd",
"bU c #47faf7",
"bS c #47fbf8",
"az c #47fbfa",
"ca c #47fbfc",
".L c #486c66",
"aO c #48d0ce",
"#I c #48fafa",
"#6 c #48fcfd",
"aR c #496c67",
"av c #49c4bd",
"bW c #49cac6",
".8 c #49cecb",
"au c #49f9f7",
"#b c #4ab5b2",
"co c #4af8f7",
"aN c #4afaf7",
"#L c #4bf9f8",
"#P c #4bfbf9",
"as c #4bfbfb",
".E c #4c6763",
"cE c #4cb1ab",
"#3 c #4ccecb",
"aZ c #4cd4d2",
"aG c #4cf8f8",
"b6 c #4cf9f5",
"#2 c #4cf9f7",
"ce c #4d716c",
"b7 c #4dd1cc",
"#C c #4dd7d5",
"#R c #4df9f9",
".v c #4e635f",
"#F c #4f6e6a",
".M c #4fa7a3",
"#f c #4fb8b5",
"#x c #4fbbb9",
"ch c #4fcfc9",
"aM c #4ff8f5",
"ah c #4ff9f8",
".a c #50736d",
".w c #50a9a6",
"cg c #50f9f6",
".k c #516f6c",
"cz c #518683",
"#o c #51908d",
"#i c #51d1d0",
"bL c #51d9d7",
"ck c #51f6f2",
".7 c #51f7f5",
"b9 c #51faf7",
"#d c #52d9d3",
"cb c #52f5f4",
"#5 c #52f6f5",
"bV c #52f7f3",
"by c #53a19d",
"bl c #53d0cd",
".0 c #53d1ce",
"bp c #53d7d4",
"#l c #53f6f3",
"cp c #53f6f5",
"ak c #53f7f6",
"bB c #53f8f4",
"cu c #53f9f7",
"#E c #547471",
"aU c #54d7d2",
"bG c #54ddda",
".5 c #54dedc",
"ay c #54f4f2",
"b0 c #54f4f4",
"bK c #54f7f6",
"bJ c #54f9f5",
"aL c #55cdc8",
"ct c #55d4d0",
"#s c #55f5f3",
"#A c #55f5f5",
"bI c #55f6f1",
".1 c #567a75",
"cG c #56a298",
"aT c #56dedc",
"#r c #56f4f3",
"ac c #56f4f5",
"#S c #56f5f1",
"bA c #56f6f4",
"b8 c #57d7d2",
"#t c #57f3f0",
"#B c #57f5f4",
"cC c #58d3cf",
"cv c #58d5d1",
"#z c #58f4f1",
"#H c #58f4f3",
".t c #597a77",
"cB c #59c7c2",
"bf c #59f3f3",
".R c #59f4f0",
"bR c #59f5f2",
"cm c #5a7b75",
"aK c #5abab5",
"ax c #5ac8c4",
"cj c #5ac9c4",
"aj c #5ad8d5",
"ar c #5af3f1",
"bC c #5af6f3",
"cA c #5bc4bf",
"#h c #5bdbda",
"#a c #5be6e3",
"aB c #5bf0ee",
".K c #5cb0a9",
"cD c #5cd5d1",
"cI c #5cd6d2",
"cq c #5cedea",
".6 c #5cf2f0",
".Q c #5cf3ee",
"#q c #5cf5f3",
"cJ c #5dd1ce",
"bv c #5df1f1",
"#y c #5df2f0",
"bH c #5df3f1",
"br c #5df4ef",
"bD c #5ef0ed",
"bN c #5f8481",
"#g c #5fdad5",
"#O c #5fe3df",
"a2 c #5ff1ee",
"cL c #60988d",
"cn c #60c9c5",
"#D c #60f1ee",
"bq c #60f2ef",
"#V c #61807b",
"be c #61e3e1",
"bs c #61f0ee",
"#u c #61f3f0",
"ab c #62c9c5",
"b2 c #62d0cb",
"#G c #62dfdb",
"bj c #62f1ef",
".H c #62f2f2",
"cf c #63cfcb",
"bY c #63e8e4",
".P c #63efec",
".I c #63efee",
".Z c #64efea",
"bk c #64efec",
"aH c #64f0ed",
"## c #65c0bc",
".G c #65f0ed",
"cw c #66867e",
"aQ c #66dfda",
"bz c #67efed",
".S c #688580",
".h c #688981",
".o c #68c9c2",
".N c #68cdc7",
".s c #69bcb8",
"bh c #6a8a84",
"#. c #6b847d",
"#p c #6beee9",
".F c #6cbfb7",
".J c #6debe8",
".x c #6ed3cd",
".q c #6ee9e7",
".z c #6eebe5",
".O c #70ede9",
"bQ c #71e0db",
"aF c #729b98",
".y c #72e9e3",
".r c #73eae8",
".p c #75e9e6",
"cP c #76b2a8",
"cQ c #78aea1",
".U c #79968e",
".e c #7c9490",
"cM c #7cb0a4",
"bx c #81a9a3",
"a4 c #83c6bf",
"cN c #8cb7ad",
"#J c #8dfdfc",
"#Z c #8dfefe",
"#K c #8efdfc",
"cy c #90b7ab",
".m c #92b3ad",
"b4 c #92ffff",
"cT c #93bbb0",
"c# c #93feff",
"b5 c #93ffff",
"cU c #94baad",
"#7 c #94feff",
".u c #95bfb6",
"#n c #96a9a4",
"bZ c #96fdfc",
"#Q c #96fdfd",
"bT c #96fefd",
"a# c #97a59a",
"cS c #97bbaf",
"b1 c #98a59a",
"cd c #9ba69b",
"cO c #9cbcb1",
"#0 c #9dfdfd",
".f c #9fbeb7",
".C c #a1cbc6",
"cR c #a2c0b4",
"cV c #a8c3b9",
"bw c #a9c4b8",
".# c #aac2be",
"aq c #adc6bc",
".l c #b0cec9",
"#m c #b2bfb3",
"bg c #b2c9be",
"cW c #b2c9c0",
"bO c #b3c2b8",
"aE c #bac3b6",
".9 c #bac5bb",
".g c #becfc8",
"#W c #c1cac2",
"a3 c #c3d3cb",
"cX c #c6dbd2",
".D c #cdd4d2",
".T c #d0d6d1",
"cY c #d9ddd9",
"cx c #dfe2df",
"Qt c #ffffff",
"QtQtQtQtQt.#.a.b.c.d.e.fQt.g.h.i.j.k.e.lQtQt",
"QtQtQtQt.m.n.o.p.q.r.s.t.u.v.w.x.y.z.A.B.CQt",
"QtQtQt.D.E.F.y.G.H.I.J.K.L.M.N.O.P.Q.R.A.S.T",
"Qt.D.U.V.W.X.Y.B.Z.Z.0.1.2.3.4.1.5.6.7.8.B.9",
".D#.###a#a#a#a#b#c#d#e#f#g#g#h#i#j#k#l.8.B#m",
"#n#o#p#q#r#s#t#u#v#w#x#y#z#s#A#B#C.1#D.8#E#m",
"#F#G#H#I#J#K#L#B#M#N#O#s#P#Q#Q#R#S#T#U.8#V#W",
"#X#G#A#Y#Z#0#1#2#3#4#O#5#6#7#7#8.7#9a..Ba#Qt",
"aaabacadaeafagah#3aiajak#Yalaman#laoapa#aqQt",
".a##arasagatau#SavawaxayazaAae#LaBaCaD.BQtQt",
"aEaF###AaG#2#HaHaIaJaKaLaMaNaGacaOaPaQ.8.aQt",
"QtaRaS####aTaUaVaWaXaYaKaKaK#GaZa0a1a2.8.Ba3",
"Qta4a5a6a7a8a9b.b#aYba#wbba8bbbcbdbebf.8.Bbg",
"Qtbhbibj.6.Qbkblbmbnbobpbqbr#ybsbtbubv.8.Bbw",
"bxbybzbA#5bBbCbDbEbFbGbHbIbJbK#HbL.B.8bMbNbO",
"bPbQbRbS#QbTbUbVbWbXbYbB#PbZ#Q#Lb0.BbM.Bb1#W",
"aab2bBb3b4b5agb6b7bXb8b9c.b5c#cacb.Bcccd.9Qt",
"cecf#s#1aAaA#1cgchcicjck#8aAclasarcea#.9QtQt",
"cm##cn.7coaGcpcqcrcsaKctcu#LaG#Scvcw#mcxQtQt",
"cyczaKcAcBcCcDcEcFcGcHaKaKaKcIcJcKcL#mQtQtQt",
"QtcM.1.B.B.B.BcwcNcOcP.1.B.B.BcwcQcRcxQtQtQt",
"QtQtQtcScTcUcVcWQtQtcXcOcOcOcVcWcYQtQtQtQtQt"
]

class ElementSelectorDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        self.image1 = QPixmap(image1_data)
        self.image2 = QPixmap(image2_data)
        self.image3 = QPixmap(image3_data)

        if not name:
            self.setName("ElementSelectorDialog")

        pal = QPalette()
        cg = QColorGroup()
        cg.setColor(QColorGroup.Foreground,Qt.black)
        cg.setColor(QColorGroup.Button,QColor(230,231,230))
        cg.setColor(QColorGroup.Light,Qt.white)
        cg.setColor(QColorGroup.Midlight,QColor(242,243,242))
        cg.setColor(QColorGroup.Dark,QColor(115,115,115))
        cg.setColor(QColorGroup.Mid,QColor(153,154,153))
        cg.setColor(QColorGroup.Text,Qt.black)
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,Qt.black)
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(230,231,230))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,Qt.black)
        cg.setColor(QColorGroup.LinkVisited,Qt.black)
        pal.setActive(cg)
        cg.setColor(QColorGroup.Foreground,Qt.black)
        cg.setColor(QColorGroup.Button,QColor(230,231,230))
        cg.setColor(QColorGroup.Light,Qt.white)
        cg.setColor(QColorGroup.Midlight,Qt.white)
        cg.setColor(QColorGroup.Dark,QColor(115,115,115))
        cg.setColor(QColorGroup.Mid,QColor(153,154,153))
        cg.setColor(QColorGroup.Text,Qt.black)
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,Qt.black)
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(230,231,230))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,QColor(0,0,255))
        cg.setColor(QColorGroup.LinkVisited,QColor(255,0,255))
        pal.setInactive(cg)
        cg.setColor(QColorGroup.Foreground,QColor(128,128,128))
        cg.setColor(QColorGroup.Button,QColor(230,231,230))
        cg.setColor(QColorGroup.Light,Qt.white)
        cg.setColor(QColorGroup.Midlight,Qt.white)
        cg.setColor(QColorGroup.Dark,QColor(115,115,115))
        cg.setColor(QColorGroup.Mid,QColor(153,154,153))
        cg.setColor(QColorGroup.Text,QColor(128,128,128))
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,QColor(128,128,128))
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(230,231,230))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,QColor(0,0,255))
        cg.setColor(QColorGroup.LinkVisited,QColor(255,0,255))
        pal.setDisabled(cg)
        self.setPalette(pal)
        self.setIcon(self.image0)

        ElementSelectorDialogLayout = QVBoxLayout(self,11,6,"ElementSelectorDialogLayout")

        layout15 = QHBoxLayout(None,0,6,"layout15")

        self.elemInfoLabel = QLabel(self,"elemInfoLabel")
        self.elemInfoLabel.setSizePolicy(QSizePolicy(5,5,0,1,self.elemInfoLabel.sizePolicy().hasHeightForWidth()))
        self.elemInfoLabel.setMinimumSize(QSize(0,0))
        self.elemInfoLabel.setPaletteBackgroundColor(QColor(227,211,231))
        self.elemInfoLabel.setTextFormat(QLabel.RichText)
        self.elemInfoLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout15.addWidget(self.elemInfoLabel)

        layout3 = QVBoxLayout(None,0,1,"layout3")

        self.elementFrame = QFrame(self,"elementFrame")
        self.elementFrame.setSizePolicy(QSizePolicy(5,5,0,0,self.elementFrame.sizePolicy().hasHeightForWidth()))
        self.elementFrame.setMinimumSize(QSize(0,0))
        self.elementFrame.setFrameShape(QFrame.Box)
        self.elementFrame.setFrameShadow(QFrame.Raised)
        layout3.addWidget(self.elementFrame)

        self.elemColorLabel = QLabel(self,"elemColorLabel")
        self.elemColorLabel.setSizePolicy(QSizePolicy(5,5,0,0,self.elemColorLabel.sizePolicy().hasHeightForWidth()))
        self.elemColorLabel.setMinimumSize(QSize(0,40))
        self.elemColorLabel.setTextFormat(QLabel.RichText)
        self.elemColorLabel.setAlignment(QLabel.AlignCenter)
        layout3.addWidget(self.elemColorLabel)
        layout15.addLayout(layout3)

        self.buttonGroup1 = QButtonGroup(self,"buttonGroup1")
        self.buttonGroup1.setFrameShape(QButtonGroup.PopupPanel)
        self.buttonGroup1.setFrameShadow(QButtonGroup.Sunken)
        self.buttonGroup1.setColumnLayout(0,Qt.Vertical)
        self.buttonGroup1.layout().setSpacing(6)
        self.buttonGroup1.layout().setMargin(11)
        buttonGroup1Layout = QVBoxLayout(self.buttonGroup1.layout())
        buttonGroup1Layout.setAlignment(Qt.AlignTop)

        self.radioButton1 = QRadioButton(self.buttonGroup1,"radioButton1")
        self.radioButton1.setPixmap(self.image1)
        self.radioButton1.setChecked(1)
        self.buttonGroup1.insert( self.radioButton1,0)
        buttonGroup1Layout.addWidget(self.radioButton1)

        self.radioButton1_2 = QRadioButton(self.buttonGroup1,"radioButton1_2")
        self.radioButton1_2.setPixmap(self.image2)
        self.buttonGroup1.insert( self.radioButton1_2,1)
        buttonGroup1Layout.addWidget(self.radioButton1_2)

        self.radioButton1_3 = QRadioButton(self.buttonGroup1,"radioButton1_3")
        self.radioButton1_3.setPixmap(self.image3)
        self.buttonGroup1.insert( self.radioButton1_3,2)
        buttonGroup1Layout.addWidget(self.radioButton1_3)
        layout15.addWidget(self.buttonGroup1)
        ElementSelectorDialogLayout.addLayout(layout15)

        self.elementButtonGroup = QButtonGroup(self,"elementButtonGroup")
        self.elementButtonGroup.setPaletteBackgroundColor(QColor(223,231,212))
        self.elementButtonGroup.setExclusive(1)
        self.elementButtonGroup.setColumnLayout(0,Qt.Vertical)
        self.elementButtonGroup.layout().setSpacing(1)
        self.elementButtonGroup.layout().setMargin(2)
        elementButtonGroupLayout = QGridLayout(self.elementButtonGroup.layout())
        elementButtonGroupLayout.setAlignment(Qt.AlignTop)

        self.pushButton1 = QPushButton(self.elementButtonGroup,"pushButton1")
        self.pushButton1.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton1.sizePolicy().hasHeightForWidth()))
        self.pushButton1.setPaletteBackgroundColor(QColor(60,215,205))
        self.pushButton1.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton1.setToggleButton(1)
        self.pushButton1.setOn(0)
        self.pushButton1.setDefault(0)
        self.elementButtonGroup.insert( self.pushButton1,1)

        elementButtonGroupLayout.addWidget(self.pushButton1,0,4)

        self.pushButton2 = QPushButton(self.elementButtonGroup,"pushButton2")
        self.pushButton2.setEnabled(1)
        self.pushButton2.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton2.sizePolicy().hasHeightForWidth()))
        self.pushButton2.setPaletteBackgroundColor(QColor(210,210,255))
        self.pushButton2.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton2.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton2,2)

        elementButtonGroupLayout.addWidget(self.pushButton2,0,5)

        self.pushButton6 = QPushButton(self.elementButtonGroup,"pushButton6")
        self.pushButton6.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton6.sizePolicy().hasHeightForWidth()))
        self.pushButton6.setPaletteBackgroundColor(QColor(35,165,75))
        self.pushButton6.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton6.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton6,6)

        elementButtonGroupLayout.addWidget(self.pushButton6,1,1)

        self.pushButton7 = QPushButton(self.elementButtonGroup,"pushButton7")
        self.pushButton7.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton7.sizePolicy().hasHeightForWidth()))
        self.pushButton7.setPaletteBackgroundColor(QColor(255,170,255))
        self.pushButton7.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton7.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton7,7)

        elementButtonGroupLayout.addWidget(self.pushButton7,1,2)

        self.pushButton8 = QPushButton(self.elementButtonGroup,"pushButton8")
        self.pushButton8.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton8.sizePolicy().hasHeightForWidth()))
        self.pushButton8.setPaletteBackgroundColor(QColor(191,0,0))
        self.pushButton8.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton8.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton8,8)

        elementButtonGroupLayout.addWidget(self.pushButton8,1,3)

        self.pushButton9 = QPushButton(self.elementButtonGroup,"pushButton9")
        self.pushButton9.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton9.sizePolicy().hasHeightForWidth()))
        self.pushButton9.setPaletteBackgroundColor(QColor(85,255,127))
        self.pushButton9.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton9.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton9,9)

        elementButtonGroupLayout.addWidget(self.pushButton9,1,4)

        self.pushButton10 = QPushButton(self.elementButtonGroup,"pushButton10")
        self.pushButton10.setEnabled(1)
        self.pushButton10.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton10.sizePolicy().hasHeightForWidth()))
        self.pushButton10.setPaletteBackgroundColor(QColor(210,210,255))
        self.pushButton10.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton10.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton10,10)

        elementButtonGroupLayout.addWidget(self.pushButton10,1,5)

        self.pushButton16 = QPushButton(self.elementButtonGroup,"pushButton16")
        self.pushButton16.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton16.sizePolicy().hasHeightForWidth()))
        self.pushButton16.setPaletteBackgroundColor(QColor(255,213,73))
        self.pushButton16.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton16.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton16,16)

        elementButtonGroupLayout.addWidget(self.pushButton16,2,3)

        self.pushButton17 = QPushButton(self.elementButtonGroup,"pushButton17")
        self.pushButton17.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton17.sizePolicy().hasHeightForWidth()))
        self.pushButton17.setPaletteBackgroundColor(QColor(149,223,0))
        self.pushButton17.setBackgroundOrigin(QPushButton.ParentOrigin)
        self.pushButton17.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton17.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton17,17)

        elementButtonGroupLayout.addWidget(self.pushButton17,2,4)

        self.pushButton18 = QPushButton(self.elementButtonGroup,"pushButton18")
        self.pushButton18.setEnabled(1)
        self.pushButton18.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton18.sizePolicy().hasHeightForWidth()))
        self.pushButton18.setPaletteBackgroundColor(QColor(210,210,255))
        self.pushButton18.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton18.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton18,18)

        elementButtonGroupLayout.addWidget(self.pushButton18,2,5)

        self.pushButton32 = QPushButton(self.elementButtonGroup,"pushButton32")
        self.pushButton32.setEnabled(1)
        self.pushButton32.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton32.sizePolicy().hasHeightForWidth()))
        self.pushButton32.setPaletteBackgroundColor(QColor(206,206,0))
        self.pushButton32.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton32.setToggleButton(1)
        self.pushButton32.setOn(0)
        self.elementButtonGroup.insert( self.pushButton32,32)

        elementButtonGroupLayout.addWidget(self.pushButton32,3,1)

        self.pushButton33 = QPushButton(self.elementButtonGroup,"pushButton33")
        self.pushButton33.setEnabled(1)
        self.pushButton33.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton33.sizePolicy().hasHeightForWidth()))
        self.pushButton33.setPaletteBackgroundColor(QColor(229,62,255))
        self.pushButton33.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton33.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton33,33)

        elementButtonGroupLayout.addWidget(self.pushButton33,3,2)

        self.pushButton34 = QPushButton(self.elementButtonGroup,"pushButton34")
        self.pushButton34.setEnabled(1)
        self.pushButton34.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton34.sizePolicy().hasHeightForWidth()))
        self.pushButton34.setPaletteBackgroundColor(QColor(230,144,23))
        self.pushButton34.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton34.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton34,34)

        elementButtonGroupLayout.addWidget(self.pushButton34,3,3)

        self.pushButton35 = QPushButton(self.elementButtonGroup,"pushButton35")
        self.pushButton35.setEnabled(1)
        self.pushButton35.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton35.sizePolicy().hasHeightForWidth()))
        self.pushButton35.setPaletteBackgroundColor(QColor(77,202,156))
        self.pushButton35.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton35.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton35,35)

        elementButtonGroupLayout.addWidget(self.pushButton35,3,4)

        self.pushButton36 = QPushButton(self.elementButtonGroup,"pushButton36")
        self.pushButton36.setEnabled(1)
        self.pushButton36.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton36.sizePolicy().hasHeightForWidth()))
        self.pushButton36.setPaletteBackgroundColor(QColor(210,210,255))
        self.pushButton36.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton36.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton36,36)

        elementButtonGroupLayout.addWidget(self.pushButton36,3,5)

        self.pushButton51 = QPushButton(self.elementButtonGroup,"pushButton51")
        self.pushButton51.setEnabled(0)
        self.pushButton51.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton51.sizePolicy().hasHeightForWidth()))
        self.pushButton51.setPaletteBackgroundColor(QColor(170,0,255))
        self.pushButton51.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton51.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton51,51)

        elementButtonGroupLayout.addWidget(self.pushButton51,4,2)

        self.pushButton52 = QPushButton(self.elementButtonGroup,"pushButton52")
        self.pushButton52.setEnabled(0)
        self.pushButton52.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton52.sizePolicy().hasHeightForWidth()))
        self.pushButton52.setPaletteBackgroundColor(QColor(238,183,53))
        self.pushButton52.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton52.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton52,52)

        elementButtonGroupLayout.addWidget(self.pushButton52,4,3)

        self.pushButton53 = QPushButton(self.elementButtonGroup,"pushButton53")
        self.pushButton53.setEnabled(0)
        self.pushButton53.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton53.sizePolicy().hasHeightForWidth()))
        self.pushButton53.setPaletteBackgroundColor(QColor(0,180,135))
        self.pushButton53.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton53.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton53,53)

        elementButtonGroupLayout.addWidget(self.pushButton53,4,4)

        self.pushButton54 = QPushButton(self.elementButtonGroup,"pushButton54")
        self.pushButton54.setEnabled(0)
        self.pushButton54.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton54.sizePolicy().hasHeightForWidth()))
        self.pushButton54.setPaletteBackgroundColor(QColor(210,210,255))
        self.pushButton54.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton54.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton54,54)

        elementButtonGroupLayout.addWidget(self.pushButton54,4,5)

        self.pushButton15 = QPushButton(self.elementButtonGroup,"pushButton15")
        self.pushButton15.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton15.sizePolicy().hasHeightForWidth()))
        self.pushButton15.setPaletteBackgroundColor(QColor(170,85,200))
        self.pushButton15.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton15.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton15,15)

        elementButtonGroupLayout.addWidget(self.pushButton15,2,2)

        self.pushButton14 = QPushButton(self.elementButtonGroup,"pushButton14")
        self.pushButton14.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton14.sizePolicy().hasHeightForWidth()))
        self.pushButton14.setPaletteBackgroundColor(QColor(156,156,156))
        self.pushButton14.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton14.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton14,14)

        elementButtonGroupLayout.addWidget(self.pushButton14,2,1)

        self.pushButton13 = QPushButton(self.elementButtonGroup,"pushButton13")
        self.pushButton13.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton13.sizePolicy().hasHeightForWidth()))
        self.pushButton13.setPaletteBackgroundColor(QColor(170,170,255))
        self.pushButton13.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton13.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton13,13)

        elementButtonGroupLayout.addWidget(self.pushButton13,2,0)

        self.pushButton5 = QPushButton(self.elementButtonGroup,"pushButton5")
        self.pushButton5.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton5.sizePolicy().hasHeightForWidth()))
        self.pushButton5.setPaletteBackgroundColor(QColor(80,135,255))
        self.pushButton5.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton5.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton5,5)

        elementButtonGroupLayout.addWidget(self.pushButton5,1,0)
        ElementSelectorDialogLayout.addWidget(self.elementButtonGroup)

        layout13 = QGridLayout(None,1,1,9,9,"layout13")

        self.closePTableButton = QPushButton(self,"closePTableButton")
        self.closePTableButton.setSizePolicy(QSizePolicy(5,0,0,0,self.closePTableButton.sizePolicy().hasHeightForWidth()))
        self.closePTableButton.setDefault(1)

        layout13.addWidget(self.closePTableButton,1,1)

        self.transmuteCheckBox = QCheckBox(self,"transmuteCheckBox")
        self.transmuteCheckBox.setSizePolicy(QSizePolicy(5,0,0,0,self.transmuteCheckBox.sizePolicy().hasHeightForWidth()))

        layout13.addWidget(self.transmuteCheckBox,0,1)

        self.TransmuteButton = QPushButton(self,"TransmuteButton")
        self.TransmuteButton.setSizePolicy(QSizePolicy(5,0,0,0,self.TransmuteButton.sizePolicy().hasHeightForWidth()))

        layout13.addWidget(self.TransmuteButton,0,0)
        ElementSelectorDialogLayout.addLayout(layout13)

        self.languageChange()

        self.resize(QSize(417,442).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.closePTableButton,SIGNAL("clicked()"),self,SLOT("close()"))
        self.connect(self.TransmuteButton,SIGNAL("clicked()"),self.transmutePressed)
        self.connect(self.elementButtonGroup,SIGNAL("clicked(int)"),self.setElementInfo)
        self.connect(self.buttonGroup1,SIGNAL("clicked(int)"),self.changeDisplayMode)

        self.setTabOrder(self.TransmuteButton,self.transmuteCheckBox)
        self.setTabOrder(self.transmuteCheckBox,self.closePTableButton)


    def languageChange(self):
        self.setCaption(self.__tr("Element Selector"))
        self.elemInfoLabel.setText(QString.null)
        self.elemColorLabel.setText(QString.null)
        self.buttonGroup1.setTitle(self.__tr("Display Mode"))
        self.radioButton1.setText(QString.null)
        QToolTip.add(self.radioButton1,self.__tr("Tubes"))
        self.radioButton1_2.setText(QString.null)
        QToolTip.add(self.radioButton1_2,self.__tr("CPK"))
        self.radioButton1_3.setText(QString.null)
        QToolTip.add(self.radioButton1_3,self.__tr("VdW"))
        self.elementButtonGroup.setTitle(QString.null)
        self.pushButton1.setText(self.__tr("H"))
        self.pushButton2.setText(self.__tr("He"))
        self.pushButton6.setText(self.__tr("C"))
        self.pushButton7.setText(self.__tr("N"))
        self.pushButton8.setText(self.__tr("O"))
        self.pushButton9.setText(self.__tr("F"))
        self.pushButton10.setText(self.__tr("Ne"))
        self.pushButton16.setText(self.__tr("S"))
        self.pushButton17.setText(self.__tr("Cl"))
        self.pushButton18.setText(self.__tr("Ar"))
        self.pushButton32.setText(self.__tr("Ge"))
        self.pushButton33.setText(self.__tr("As"))
        self.pushButton34.setText(self.__tr("Se"))
        self.pushButton35.setText(self.__tr("Br"))
        self.pushButton36.setText(self.__tr("Kr"))
        self.pushButton51.setText(self.__tr("Sb"))
        self.pushButton52.setText(self.__tr("Te"))
        self.pushButton53.setText(self.__tr("I"))
        self.pushButton54.setText(self.__tr("Xe"))
        self.pushButton15.setText(self.__tr("P"))
        self.pushButton14.setText(self.__tr("Si"))
        self.pushButton13.setText(self.__tr("Al"))
        self.pushButton5.setText(self.__tr("B"))
        self.closePTableButton.setText(self.__tr("Close"))
        self.transmuteCheckBox.setText(self.__tr("Force to Keep Bonds"))
        QToolTip.add(self.transmuteCheckBox,self.__tr("Check if transmuted atoms should keep all existing bonds,  even if chemistry is wrong."))
        self.TransmuteButton.setText(self.__tr("Transmute"))


    def setElementInfo(self,a0):
        print "ElementSelectorDialog.setElementInfo(int): Not implemented yet"

    def transmutePressed(self):
        print "ElementSelectorDialog.transmutePressed(): Not implemented yet"

    def changeDisplayMode(self,a0):
        print "ElementSelectorDialog.changeDisplayMode(int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ElementSelectorDialog",s,c)

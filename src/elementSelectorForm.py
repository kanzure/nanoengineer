# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'elementSelectorForm.ui'
#
# Created: Thu Sep 9 10:27:18 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 8 1",
". c None",
"# c #2d2d2d",
"e c #b4b5b4",
"c c #bfc0bf",
"b c #c2c3c2",
"f c #c8c9c8",
"a c #d2d2d2",
"d c #dbdcdb",
"......................",
"......................",
"......................",
".###.............###a.",
".#b#.............#b#cd",
".#b#.........#####b#ef",
".#b#.........#b#b#b#ef",
".#b###########b#b#b#ef",
".#b#b#b#b#b#b#b#b#b#ef",
".#b#b#b#b#b#b#b#b#b#ef",
".#b#b#b#b#b#b#b#b#b#ef",
".#b#b#b#b#b#b#b#b#b#ef",
".#b#b#b#b#b#b#b#b#b#ef",
".###################ef",
".aceeeeeeeeeeeeeeeeeef",
"..d###############dddf",
"...#bbbbbbbbbbbbb#a...",
"...###############ca..",
"...#bbbbbbbbbbbbb#ef..",
"...###############ef..",
"...aceeeeeeeeeeeeeef..",
"...dddffffffffffffff.."
]

class elementSelectorForm(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("elementSelectorForm")

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


        self.elementButtonGroup = QButtonGroup(self,"elementButtonGroup")
        self.elementButtonGroup.setGeometry(QRect(10,0,250,330))
        self.elementButtonGroup.setExclusive(1)

        self.elementFrame = QFrame(self.elementButtonGroup,"elementFrame")
        self.elementFrame.setGeometry(QRect(6,7,235,110))
        self.elementFrame.setPaletteBackgroundColor(QColor(60,215,205))
        self.elementFrame.setFrameShape(QFrame.StyledPanel)
        self.elementFrame.setFrameShadow(QFrame.Raised)

        self.elementNumberLabel = QLabel(self.elementFrame,"elementNumberLabel")
        self.elementNumberLabel.setGeometry(QRect(10,2,100,30))
        elementNumberLabel_font = QFont(self.elementNumberLabel.font())
        self.elementNumberLabel.setFont(elementNumberLabel_font)
        self.elementNumberLabel.setAlignment(QLabel.AlignCenter)

        self.amuLabel = QLabel(self.elementFrame,"amuLabel")
        self.amuLabel.setGeometry(QRect(10,77,100,30))
        amuLabel_font = QFont(self.amuLabel.font())
        self.amuLabel.setFont(amuLabel_font)
        self.amuLabel.setAlignment(QLabel.AlignCenter)

        self.elementSymbolLabel = QLabel(self.elementFrame,"elementSymbolLabel")
        self.elementSymbolLabel.setGeometry(QRect(10,29,100,52))
        elementSymbolLabel_font = QFont(self.elementSymbolLabel.font())
        elementSymbolLabel_font.setPointSize(26)
        elementSymbolLabel_font.setBold(1)
        self.elementSymbolLabel.setFont(elementSymbolLabel_font)
        self.elementSymbolLabel.setAlignment(QLabel.AlignCenter)

        self.pixmapLabel1 = QLabel(self.elementFrame,"pixmapLabel1")
        self.pixmapLabel1.setGeometry(QRect(125,5,100,100))
        self.pixmapLabel1.setScaledContents(1)

        self.pushButton2 = QPushButton(self.elementButtonGroup,"pushButton2")
        self.pushButton2.setEnabled(1)
        self.pushButton2.setGeometry(QRect(201,123,40,40))
        self.pushButton2.setPaletteBackgroundColor(QColor(210,210,255))
        pushButton2_font = QFont(self.pushButton2.font())
        pushButton2_font.setPointSize(9)
        pushButton2_font.setBold(1)
        self.pushButton2.setFont(pushButton2_font)
        self.pushButton2.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton2,2)

        self.pushButton5 = QPushButton(self.elementButtonGroup,"pushButton5")
        self.pushButton5.setGeometry(QRect(6,162,40,40))
        self.pushButton5.setPaletteBackgroundColor(QColor(80,135,255))
        pushButton5_font = QFont(self.pushButton5.font())
        pushButton5_font.setPointSize(9)
        pushButton5_font.setBold(1)
        self.pushButton5.setFont(pushButton5_font)
        self.pushButton5.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton5,5)

        self.pushButton6 = QPushButton(self.elementButtonGroup,"pushButton6")
        self.pushButton6.setGeometry(QRect(45,162,40,40))
        self.pushButton6.setPaletteBackgroundColor(QColor(35,165,75))
        pushButton6_font = QFont(self.pushButton6.font())
        pushButton6_font.setPointSize(9)
        pushButton6_font.setBold(1)
        self.pushButton6.setFont(pushButton6_font)
        self.pushButton6.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton6,6)

        self.pushButton7 = QPushButton(self.elementButtonGroup,"pushButton7")
        self.pushButton7.setGeometry(QRect(84,162,40,40))
        self.pushButton7.setPaletteBackgroundColor(QColor(255,170,255))
        pushButton7_font = QFont(self.pushButton7.font())
        pushButton7_font.setPointSize(9)
        pushButton7_font.setBold(1)
        self.pushButton7.setFont(pushButton7_font)
        self.pushButton7.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton7,7)

        self.pushButton8 = QPushButton(self.elementButtonGroup,"pushButton8")
        self.pushButton8.setGeometry(QRect(123,162,40,40))
        self.pushButton8.setPaletteBackgroundColor(QColor(191,0,0))
        pushButton8_font = QFont(self.pushButton8.font())
        pushButton8_font.setPointSize(9)
        pushButton8_font.setBold(1)
        self.pushButton8.setFont(pushButton8_font)
        self.pushButton8.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton8,8)

        self.pushButton9 = QPushButton(self.elementButtonGroup,"pushButton9")
        self.pushButton9.setGeometry(QRect(162,162,40,40))
        self.pushButton9.setPaletteBackgroundColor(QColor(85,255,127))
        pushButton9_font = QFont(self.pushButton9.font())
        pushButton9_font.setPointSize(9)
        pushButton9_font.setBold(1)
        self.pushButton9.setFont(pushButton9_font)
        self.pushButton9.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton9,9)

        self.pushButton13 = QPushButton(self.elementButtonGroup,"pushButton13")
        self.pushButton13.setGeometry(QRect(6,201,40,40))
        self.pushButton13.setPaletteBackgroundColor(QColor(170,170,255))
        pushButton13_font = QFont(self.pushButton13.font())
        pushButton13_font.setPointSize(9)
        pushButton13_font.setBold(1)
        self.pushButton13.setFont(pushButton13_font)
        self.pushButton13.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton13,13)

        self.pushButton14 = QPushButton(self.elementButtonGroup,"pushButton14")
        self.pushButton14.setGeometry(QRect(45,201,40,40))
        self.pushButton14.setPaletteBackgroundColor(QColor(156,156,156))
        pushButton14_font = QFont(self.pushButton14.font())
        pushButton14_font.setPointSize(9)
        pushButton14_font.setBold(1)
        self.pushButton14.setFont(pushButton14_font)
        self.pushButton14.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton14,14)

        self.pushButton15 = QPushButton(self.elementButtonGroup,"pushButton15")
        self.pushButton15.setGeometry(QRect(84,201,40,40))
        self.pushButton15.setPaletteBackgroundColor(QColor(170,85,200))
        pushButton15_font = QFont(self.pushButton15.font())
        pushButton15_font.setPointSize(9)
        pushButton15_font.setBold(1)
        self.pushButton15.setFont(pushButton15_font)
        self.pushButton15.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton15,15)

        self.pushButton16 = QPushButton(self.elementButtonGroup,"pushButton16")
        self.pushButton16.setGeometry(QRect(123,201,40,40))
        self.pushButton16.setPaletteBackgroundColor(QColor(255,213,73))
        pushButton16_font = QFont(self.pushButton16.font())
        pushButton16_font.setPointSize(9)
        pushButton16_font.setBold(1)
        self.pushButton16.setFont(pushButton16_font)
        self.pushButton16.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton16,16)

        self.pushButton17 = QPushButton(self.elementButtonGroup,"pushButton17")
        self.pushButton17.setGeometry(QRect(162,201,40,40))
        self.pushButton17.setPaletteBackgroundColor(QColor(149,223,0))
        self.pushButton17.setBackgroundOrigin(QPushButton.WindowOrigin)
        pushButton17_font = QFont(self.pushButton17.font())
        pushButton17_font.setPointSize(9)
        pushButton17_font.setBold(1)
        self.pushButton17.setFont(pushButton17_font)
        self.pushButton17.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton17,17)

        self.pushButton18 = QPushButton(self.elementButtonGroup,"pushButton18")
        self.pushButton18.setEnabled(1)
        self.pushButton18.setGeometry(QRect(201,201,40,40))
        self.pushButton18.setPaletteBackgroundColor(QColor(210,210,255))
        pushButton18_font = QFont(self.pushButton18.font())
        pushButton18_font.setPointSize(9)
        pushButton18_font.setBold(1)
        self.pushButton18.setFont(pushButton18_font)
        self.pushButton18.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton18,18)

        self.pushButton1 = QPushButton(self.elementButtonGroup,"pushButton1")
        self.pushButton1.setGeometry(QRect(162,123,40,40))
        self.pushButton1.setPaletteBackgroundColor(QColor(60,215,205))
        pushButton1_font = QFont(self.pushButton1.font())
        pushButton1_font.setPointSize(9)
        pushButton1_font.setBold(1)
        self.pushButton1.setFont(pushButton1_font)
        self.pushButton1.setToggleButton(1)
        self.pushButton1.setOn(0)
        self.pushButton1.setDefault(0)
        self.elementButtonGroup.insert( self.pushButton1,1)

        self.pushButton32 = QPushButton(self.elementButtonGroup,"pushButton32")
        self.pushButton32.setEnabled(1)
        self.pushButton32.setGeometry(QRect(45,240,40,40))
        self.pushButton32.setPaletteBackgroundColor(QColor(206,206,0))
        pushButton32_font = QFont(self.pushButton32.font())
        pushButton32_font.setPointSize(9)
        pushButton32_font.setBold(1)
        self.pushButton32.setFont(pushButton32_font)
        self.pushButton32.setToggleButton(1)
        self.pushButton32.setOn(0)
        self.elementButtonGroup.insert( self.pushButton32,32)

        self.pushButton33 = QPushButton(self.elementButtonGroup,"pushButton33")
        self.pushButton33.setEnabled(1)
        self.pushButton33.setGeometry(QRect(84,240,40,40))
        self.pushButton33.setPaletteBackgroundColor(QColor(229,62,255))
        pushButton33_font = QFont(self.pushButton33.font())
        pushButton33_font.setPointSize(9)
        pushButton33_font.setBold(1)
        self.pushButton33.setFont(pushButton33_font)
        self.pushButton33.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton33,33)

        self.pushButton34 = QPushButton(self.elementButtonGroup,"pushButton34")
        self.pushButton34.setEnabled(1)
        self.pushButton34.setGeometry(QRect(123,240,40,40))
        self.pushButton34.setPaletteBackgroundColor(QColor(230,144,23))
        pushButton34_font = QFont(self.pushButton34.font())
        pushButton34_font.setPointSize(9)
        pushButton34_font.setBold(1)
        self.pushButton34.setFont(pushButton34_font)
        self.pushButton34.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton34,34)

        self.pushButton35 = QPushButton(self.elementButtonGroup,"pushButton35")
        self.pushButton35.setEnabled(1)
        self.pushButton35.setGeometry(QRect(162,240,40,40))
        self.pushButton35.setPaletteBackgroundColor(QColor(77,202,156))
        pushButton35_font = QFont(self.pushButton35.font())
        pushButton35_font.setPointSize(9)
        pushButton35_font.setBold(1)
        self.pushButton35.setFont(pushButton35_font)
        self.pushButton35.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton35,35)

        self.pushButton36 = QPushButton(self.elementButtonGroup,"pushButton36")
        self.pushButton36.setEnabled(1)
        self.pushButton36.setGeometry(QRect(201,240,40,40))
        self.pushButton36.setPaletteBackgroundColor(QColor(210,210,255))
        pushButton36_font = QFont(self.pushButton36.font())
        pushButton36_font.setPointSize(9)
        pushButton36_font.setBold(1)
        self.pushButton36.setFont(pushButton36_font)
        self.pushButton36.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton36,36)

        self.pushButton51 = QPushButton(self.elementButtonGroup,"pushButton51")
        self.pushButton51.setEnabled(1)
        self.pushButton51.setGeometry(QRect(84,279,40,40))
        self.pushButton51.setPaletteBackgroundColor(QColor(170,0,255))
        pushButton51_font = QFont(self.pushButton51.font())
        pushButton51_font.setPointSize(9)
        pushButton51_font.setBold(1)
        self.pushButton51.setFont(pushButton51_font)
        self.pushButton51.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton51,51)

        self.pushButton52 = QPushButton(self.elementButtonGroup,"pushButton52")
        self.pushButton52.setEnabled(1)
        self.pushButton52.setGeometry(QRect(123,279,40,40))
        self.pushButton52.setPaletteBackgroundColor(QColor(238,183,53))
        pushButton52_font = QFont(self.pushButton52.font())
        pushButton52_font.setPointSize(9)
        pushButton52_font.setBold(1)
        self.pushButton52.setFont(pushButton52_font)
        self.pushButton52.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton52,52)

        self.pushButton53 = QPushButton(self.elementButtonGroup,"pushButton53")
        self.pushButton53.setEnabled(1)
        self.pushButton53.setGeometry(QRect(162,279,40,40))
        self.pushButton53.setPaletteBackgroundColor(QColor(0,180,135))
        pushButton53_font = QFont(self.pushButton53.font())
        pushButton53_font.setPointSize(9)
        pushButton53_font.setBold(1)
        self.pushButton53.setFont(pushButton53_font)
        self.pushButton53.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton53,53)

        self.pushButton54 = QPushButton(self.elementButtonGroup,"pushButton54")
        self.pushButton54.setEnabled(1)
        self.pushButton54.setGeometry(QRect(201,279,40,40))
        self.pushButton54.setPaletteBackgroundColor(QColor(210,210,255))
        pushButton54_font = QFont(self.pushButton54.font())
        pushButton54_font.setPointSize(9)
        pushButton54_font.setBold(1)
        self.pushButton54.setFont(pushButton54_font)
        self.pushButton54.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton54,54)

        self.pushButton10 = QPushButton(self.elementButtonGroup,"pushButton10")
        self.pushButton10.setEnabled(1)
        self.pushButton10.setGeometry(QRect(201,162,40,40))
        self.pushButton10.setPaletteBackgroundColor(QColor(210,210,255))
        pushButton10_font = QFont(self.pushButton10.font())
        pushButton10_font.setPointSize(9)
        pushButton10_font.setBold(1)
        self.pushButton10.setFont(pushButton10_font)
        self.pushButton10.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton10,10)

        self.closePTableButton = QPushButton(self,"closePTableButton")
        self.closePTableButton.setGeometry(QRect(160,340,100,29))

        self.TransmuteButton = QPushButton(self,"TransmuteButton")
        self.TransmuteButton.setGeometry(QRect(10,340,131,31))

        self.languageChange()

        self.resize(QSize(266,385).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.closePTableButton,SIGNAL("clicked()"),self,SLOT("close()"))
        self.connect(self.elementButtonGroup,SIGNAL("clicked(int)"),self.setElementInfo)
        self.connect(self.TransmuteButton,SIGNAL("clicked()"),self.transmutePressed)


    def languageChange(self):
        self.setCaption(self.__tr("Element Selector"))
        self.elementButtonGroup.setTitle(QString.null)
        self.elementNumberLabel.setText(self.__tr("1"))
        self.amuLabel.setText(self.__tr("1.008"))
        self.elementSymbolLabel.setText(self.__tr("H"))
        self.pushButton2.setText(self.__tr("2\n"
"He"))
        self.pushButton5.setText(self.__tr("5\n"
"B"))
        self.pushButton6.setText(self.__tr("6\n"
"C"))
        self.pushButton7.setText(self.__tr("7\n"
"N"))
        self.pushButton8.setText(self.__tr("8\n"
"O"))
        self.pushButton9.setText(self.__tr("9\n"
"F"))
        self.pushButton13.setText(self.__tr("13\n"
"Al"))
        self.pushButton14.setText(self.__tr("14\n"
"Si"))
        self.pushButton15.setText(self.__tr("15\n"
"P"))
        self.pushButton16.setText(self.__tr("16\n"
"S"))
        self.pushButton17.setText(self.__tr("17\n"
"Cl"))
        self.pushButton18.setText(self.__tr("18\n"
"Ar"))
        self.pushButton1.setText(self.__tr("1\n"
"H"))
        self.pushButton32.setText(self.__tr("32\n"
"Ge"))
        self.pushButton33.setText(self.__tr("33\n"
"As"))
        self.pushButton34.setText(self.__tr("34\n"
"Se"))
        self.pushButton35.setText(self.__tr("35\n"
"Br"))
        self.pushButton36.setText(self.__tr("36\n"
"Kr"))
        self.pushButton51.setText(self.__tr("51\n"
"Sb"))
        self.pushButton52.setText(self.__tr("52\n"
"Te"))
        self.pushButton53.setText(self.__tr("53\n"
"I"))
        self.pushButton54.setText(self.__tr("54\n"
"Xe"))
        self.pushButton10.setText(self.__tr("10\n"
"Ne"))
        self.closePTableButton.setText(self.__tr("Close"))
        self.TransmuteButton.setText(self.__tr("Transmute"))


    def setElementInfo(self):
        print "elementSelectorForm.setElementInfo(): Not implemented yet"

    def transmutePressed(self):
        print "elementSelectorForm.transmutePressed(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("elementSelectorForm",s,c)

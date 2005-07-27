# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\MMKitDialog.ui'
#
# Created: Wed Jul 27 01:53:16 2005
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
image1_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x01" \
    "\x02\x49\x44\x41\x54\x78\x9c\xb5\x95\xbd\x71\xc3" \
    "\x30\x0c\x85\x1f\x42\x37\x1a\x24\x8d\x96\x30\xa8" \
    "\x51\x3c\x80\xdd\x66\x8d\xb8\xc8\x26\x69\x09\x7a" \
    "\x88\x14\xda\xc0\x85\x3d\x81\x8e\x79\x69\x64\x9d" \
    "\x12\xfd\xf9\x14\x0a\x77\xbc\x63\x01\x7e\x7c\x24" \
    "\x88\x47\x21\x89\x2d\xe2\x65\x13\x2a\x80\xdd\x63" \
    "\xe2\xbd\x8f\x00\xf6\x22\xa2\x21\x84\xcb\x7f\xc1" \
    "\x9d\x62\x33\x53\x00\x17\x92\xb1\xaa\xaa\x7d\x36" \
    "\x70\x6e\xf8\xe0\x8e\x73\xc1\x47\x8b\x97\x03\x3e" \
    "\xf9\x2a\xfa\xf0\x35\x60\x90\x9c\x1d\xaa\x1a\x97" \
    "\x72\xc6\x86\x3c\xd3\x20\x65\x59\xbe\x8a\xc8\x81" \
    "\x64\x93\x52\x3a\xd7\x75\x7d\x5b\x5a\xb3\x5b\x4a" \
    "\x00\x80\x16\xfa\x06\x80\xce\xb9\x2b\x80\x0f\x55" \
    "\x7d\x9f\xca\x8f\x31\x9e\x26\xc1\x8f\x86\x31\x33" \
    "\x21\xd9\x00\x20\x80\x06\xc0\xbd\xdd\xec\x38\xa3" \
    "\x65\x08\xee\x75\xe0\x29\x84\xa0\x00\x90\x52\x3a" \
    "\x3b\xe7\xbe\x44\xe4\xbb\x28\x8a\x4f\x00\x30\x33" \
    "\x99\x3d\x66\xaf\x48\x54\x55\x7a\xef\x8f\x7f\x8a" \
    "\xc7\x35\xc5\xeb\x14\x8f\x29\x68\xd5\xaf\x8a\xc9" \
    "\x77\xdc\x37\xa5\x6c\xe0\x1c\x4e\x37\x00\xe7\xb2" \
    "\xcf\x5f\xe0\x9c\x9e\xdc\x81\x73\x1b\xfd\x53\x2d" \
    "\xbd\x26\x36\xfb\xf3\x7e\x00\x29\x71\xfa\xa4\x1a" \
    "\xab\x1a\x9a\x00\x00\x00\x00\x49\x45\x4e\x44\xae" \
    "\x42\x60\x82"
image2_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x00" \
    "\xff\x49\x44\x41\x54\x78\x9c\xd5\xd5\xb1\x55\xc3" \
    "\x30\x10\x06\xe0\xff\x50\x1a\x0f\x42\xe3\x25\xa2" \
    "\xf3\x28\x0c\x40\x5a\xd6\xc0\x45\x76\x60\x00\x5a" \
    "\x9f\x32\x04\x85\x36\xa0\x80\x09\xfc\xc4\x4f\x91" \
    "\x38\xcf\x3c\x23\x61\x82\x52\x70\x95\x9f\xe5\xfb" \
    "\xde\x3d\xe9\x74\x16\x92\xb8\x46\xdc\x5c\x45\x05" \
    "\xb0\x99\x1e\x54\x35\x00\xd8\x8a\x88\x1f\x86\xe1" \
    "\xf0\x57\xf8\x5c\xb1\x99\x79\x00\x07\x92\xa1\xeb" \
    "\xba\x6d\x35\xb8\x36\xbe\xd8\xe3\x5a\xf8\xb7\x87" \
    "\x57\x03\xcf\x76\xc5\x1c\xbf\x04\xde\x94\x16\xcd" \
    "\xcc\x9f\xba\x65\x11\xaa\x9a\xbd\x00\x66\x26\x45" \
    "\x78\xc2\xdb\xb6\xbd\x15\x91\x3b\x92\x63\x4a\xa9" \
    "\x8f\x31\xbe\x91\xec\x2f\xae\x78\x8a\x13\xfa\x00" \
    "\x80\xce\xb9\x57\x00\xfb\x10\xc2\xae\x94\xb3\xea" \
    "\xe6\x91\x1c\x01\x10\xc0\x08\xe0\x7d\x4d\xce\xaa" \
    "\x8a\x53\x4a\xbd\x73\xee\x45\x44\x3e\x9a\xa6\x79" \
    "\x06\x00\xef\xfd\x63\xee\xfb\x10\xc2\xee\x47\x58" \
    "\x55\x19\x63\x14\x00\x4f\xf3\xf7\x22\x72\x5f\x48" \
    "\x2b\xc3\xb9\x8e\x00\x8e\x27\x5f\xca\xcd\xee\xf1" \
    "\x7c\x28\x95\x80\x5f\xc1\x35\x26\xdd\x02\xae\x35" \
    "\x3e\xbf\xc0\x35\x67\xf2\x19\xae\x3d\xe8\xe5\xdf" \
    "\xfd\xf3\x3e\x01\xbf\x60\x85\xfd\xce\x79\x06\xd6" \
    "\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"
image3_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x00" \
    "\xa0\x49\x44\x41\x54\x78\x9c\xed\x93\x31\x0a\x02" \
    "\x31\x14\x44\x67\xfc\xdb\xa4\xf7\x0a\x12\xc8\x29" \
    "\x02\xde\xc4\x03\xb8\xad\xd7\xd0\xc2\x9b\xd8\xe7" \
    "\x00\xb9\x40\x6e\x60\xa1\xad\x4d\x88\xdf\xc6\x52" \
    "\x4d\x58\x08\xb8\xb0\xd3\x0e\xf3\x60\x3e\x7f\xa8" \
    "\xaa\xe8\xa1\x55\x17\xea\x02\x9e\x37\x78\x98\x1a" \
    "\xf4\xde\x1f\xbf\x79\x21\x84\x71\x32\x98\xe4\xfe" \
    "\x87\x3d\xb2\x65\x20\xce\xb9\x0d\xc9\x9d\xaa\xe6" \
    "\x52\xca\x29\xa5\x74\xab\x65\x06\xa0\x5e\xeb\x0d" \
    "\x3d\x00\x50\x11\xb9\x02\x38\x37\x9d\xa2\x56\x4b" \
    "\x55\x33\x00\x05\x90\x01\xdc\x5b\x32\x4d\xa7\xb0" \
    "\xd6\xae\x45\x64\x4b\xf2\x69\x8c\xb9\xc4\x18\x1f" \
    "\xb5\x4c\x13\xf8\x93\xfe\xfb\x2b\xa6\x68\x7e\x93" \
    "\x5e\xc0\xfd\xc1\x2f\x92\x26\x41\xe2\x3a\xc7\x34" \
    "\xaa\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60" \
    "\x82"
image4_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x01" \
    "\x16\x49\x44\x41\x54\x78\x9c\xb5\x95\x3d\x4e\xc4" \
    "\x30\x10\x85\xdf\xc3\xdb\xe4\x20\x34\x69\x73\x80" \
    "\x8c\x73\x94\x3d\x00\xb4\x5c\x83\x2d\xb8\x09\x6d" \
    "\x92\xed\xa1\xa4\xc8\x0d\x28\xe0\x04\x91\x79\x34" \
    "\x71\x14\x56\xde\xac\xc8\x7a\x47\xb2\xe4\x1f\xf9" \
    "\x9b\xd1\x78\xe6\x99\x92\x70\x0b\xbb\xbb\x09\x15" \
    "\xc0\x2e\x4e\xbc\xf7\x3d\x80\x9a\xa4\xb5\x6d\x7b" \
    "\xbc\x16\x3c\x47\xdc\x75\x9d\x01\x38\x4a\xea\x9b" \
    "\xa6\xa9\xb3\x81\x73\xc3\x67\xb0\xf7\x5e\x59\xe1" \
    "\x92\x30\x55\x46\x65\x66\x8a\x6b\x33\xeb\xcd\x4c" \
    "\xde\xfb\x3a\xee\xfd\x67\xac\x1e\x46\x78\x36\xf0" \
    "\x69\xe4\x5b\xc0\x4c\x35\x08\xc9\xca\xcc\xde\xba" \
    "\xae\x23\x00\x94\x65\x79\x4f\x72\x2f\x69\x0c\x21" \
    "\x1c\x86\x61\xf8\xba\x94\xe2\x5d\x6a\x53\xd2\x3b" \
    "\x00\x2e\x1c\xed\x25\x3d\x01\x90\x73\xee\x13\xc0" \
    "\x8b\x99\x3d\x9f\x83\xf6\x7d\xff\x98\x04\x27\x1c" \
    "\x8d\x00\x04\x60\x04\xf0\x3d\x39\x7b\x58\xb9\x92" \
    "\x06\x9f\xa6\x22\x84\x70\x70\xce\x7d\x90\xfc\x29" \
    "\x8a\xe2\x15\x00\xe2\xd9\x5a\x34\x97\x1e\x6f\x53" \
    "\x55\x24\x45\x28\x46\x33\xe9\xc7\x26\x9b\xc1\x24" \
    "\xab\xd8\x7d\x0b\x68\x4d\xd2\x36\x91\xcf\xd5\xee" \
    "\x35\x5d\x97\xac\xe3\x5c\xf2\xf9\x27\xc7\x39\x35" \
    "\x79\xa9\x6e\xd9\xa0\x00\xd2\x2d\x9d\xc3\x6e\xf6" \
    "\xe7\xfd\x02\xaf\xe3\xa6\x1c\x89\x9c\xce\x65\x00" \
    "\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

class MMKitDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        self.image1 = QPixmap()
        self.image1.loadFromData(image1_data,"PNG")
        self.image2 = QPixmap()
        self.image2.loadFromData(image2_data,"PNG")
        self.image3 = QPixmap()
        self.image3.loadFromData(image3_data,"PNG")
        self.image4 = QPixmap()
        self.image4.loadFromData(image4_data,"PNG")
        if not name:
            self.setName("MMKitDialog")

        self.setSizePolicy(QSizePolicy(5,1,0,0,self.sizePolicy().hasHeightForWidth()))
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

        MMKitDialogLayout = QVBoxLayout(self,11,6,"MMKitDialogLayout")

        self.elementFrame = QFrame(self,"elementFrame")
        self.elementFrame.setMinimumSize(QSize(200,150))
        self.elementFrame.setFrameShape(QFrame.Box)
        self.elementFrame.setFrameShadow(QFrame.Raised)
        MMKitDialogLayout.addWidget(self.elementFrame)

        self.tabWidget2 = QTabWidget(self,"tabWidget2")

        self.tab = QWidget(self.tabWidget2,"tab")
        tabLayout = QVBoxLayout(self.tab,2,6,"tabLayout")

        self.elementButtonGroup = QButtonGroup(self.tab,"elementButtonGroup")
        self.elementButtonGroup.setMinimumSize(QSize(0,110))
        self.elementButtonGroup.setFrameShape(QButtonGroup.NoFrame)
        self.elementButtonGroup.setFrameShadow(QButtonGroup.Plain)
        self.elementButtonGroup.setLineWidth(0)
        self.elementButtonGroup.setExclusive(1)
        self.elementButtonGroup.setColumnLayout(0,Qt.Vertical)
        self.elementButtonGroup.layout().setSpacing(0)
        self.elementButtonGroup.layout().setMargin(1)
        elementButtonGroupLayout = QGridLayout(self.elementButtonGroup.layout())
        elementButtonGroupLayout.setAlignment(Qt.AlignTop)

        self.pushButton1 = QPushButton(self.elementButtonGroup,"pushButton1")
        self.pushButton1.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton1.sizePolicy().hasHeightForWidth()))
        self.pushButton1.setMinimumSize(QSize(22,22))
        self.pushButton1.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton1.setToggleButton(1)
        self.pushButton1.setOn(0)
        self.pushButton1.setDefault(0)
        self.pushButton1.setFlat(0)
        self.elementButtonGroup.insert( self.pushButton1,1)

        elementButtonGroupLayout.addWidget(self.pushButton1,0,4)

        self.pushButton2 = QPushButton(self.elementButtonGroup,"pushButton2")
        self.pushButton2.setEnabled(1)
        self.pushButton2.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton2.sizePolicy().hasHeightForWidth()))
        self.pushButton2.setMinimumSize(QSize(22,22))
        self.pushButton2.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton2.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton2,2)

        elementButtonGroupLayout.addWidget(self.pushButton2,0,5)

        self.pushButton6 = QPushButton(self.elementButtonGroup,"pushButton6")
        self.pushButton6.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton6.sizePolicy().hasHeightForWidth()))
        self.pushButton6.setMinimumSize(QSize(22,22))
        self.pushButton6.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton6.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton6,6)

        elementButtonGroupLayout.addWidget(self.pushButton6,1,1)

        self.pushButton7 = QPushButton(self.elementButtonGroup,"pushButton7")
        self.pushButton7.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton7.sizePolicy().hasHeightForWidth()))
        self.pushButton7.setMinimumSize(QSize(22,22))
        self.pushButton7.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton7.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton7,7)

        elementButtonGroupLayout.addWidget(self.pushButton7,1,2)

        self.pushButton8 = QPushButton(self.elementButtonGroup,"pushButton8")
        self.pushButton8.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton8.sizePolicy().hasHeightForWidth()))
        self.pushButton8.setMinimumSize(QSize(22,22))
        self.pushButton8.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton8.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton8,8)

        elementButtonGroupLayout.addWidget(self.pushButton8,1,3)

        self.pushButton9 = QPushButton(self.elementButtonGroup,"pushButton9")
        self.pushButton9.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton9.sizePolicy().hasHeightForWidth()))
        self.pushButton9.setMinimumSize(QSize(22,22))
        self.pushButton9.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton9.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton9,9)

        elementButtonGroupLayout.addWidget(self.pushButton9,1,4)

        self.pushButton10 = QPushButton(self.elementButtonGroup,"pushButton10")
        self.pushButton10.setEnabled(1)
        self.pushButton10.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton10.sizePolicy().hasHeightForWidth()))
        self.pushButton10.setMinimumSize(QSize(22,22))
        self.pushButton10.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton10.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton10,10)

        elementButtonGroupLayout.addWidget(self.pushButton10,1,5)

        self.pushButton16 = QPushButton(self.elementButtonGroup,"pushButton16")
        self.pushButton16.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton16.sizePolicy().hasHeightForWidth()))
        self.pushButton16.setMinimumSize(QSize(22,22))
        self.pushButton16.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton16.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton16,16)

        elementButtonGroupLayout.addWidget(self.pushButton16,2,3)

        self.pushButton17 = QPushButton(self.elementButtonGroup,"pushButton17")
        self.pushButton17.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton17.sizePolicy().hasHeightForWidth()))
        self.pushButton17.setMinimumSize(QSize(22,22))
        self.pushButton17.setBackgroundOrigin(QPushButton.AncestorOrigin)
        self.pushButton17.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton17.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton17,17)

        elementButtonGroupLayout.addWidget(self.pushButton17,2,4)

        self.pushButton18 = QPushButton(self.elementButtonGroup,"pushButton18")
        self.pushButton18.setEnabled(1)
        self.pushButton18.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton18.sizePolicy().hasHeightForWidth()))
        self.pushButton18.setMinimumSize(QSize(22,22))
        self.pushButton18.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton18.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton18,18)

        elementButtonGroupLayout.addWidget(self.pushButton18,2,5)

        self.pushButton32 = QPushButton(self.elementButtonGroup,"pushButton32")
        self.pushButton32.setEnabled(1)
        self.pushButton32.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton32.sizePolicy().hasHeightForWidth()))
        self.pushButton32.setMinimumSize(QSize(22,22))
        self.pushButton32.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton32.setToggleButton(1)
        self.pushButton32.setOn(0)
        self.elementButtonGroup.insert( self.pushButton32,32)

        elementButtonGroupLayout.addWidget(self.pushButton32,3,1)

        self.pushButton33 = QPushButton(self.elementButtonGroup,"pushButton33")
        self.pushButton33.setEnabled(1)
        self.pushButton33.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton33.sizePolicy().hasHeightForWidth()))
        self.pushButton33.setMinimumSize(QSize(22,22))
        self.pushButton33.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton33.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton33,33)

        elementButtonGroupLayout.addWidget(self.pushButton33,3,2)

        self.pushButton34 = QPushButton(self.elementButtonGroup,"pushButton34")
        self.pushButton34.setEnabled(1)
        self.pushButton34.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton34.sizePolicy().hasHeightForWidth()))
        self.pushButton34.setMinimumSize(QSize(22,22))
        self.pushButton34.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton34.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton34,34)

        elementButtonGroupLayout.addWidget(self.pushButton34,3,3)

        self.pushButton35 = QPushButton(self.elementButtonGroup,"pushButton35")
        self.pushButton35.setEnabled(1)
        self.pushButton35.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton35.sizePolicy().hasHeightForWidth()))
        self.pushButton35.setMinimumSize(QSize(22,22))
        self.pushButton35.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton35.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton35,35)

        elementButtonGroupLayout.addWidget(self.pushButton35,3,4)

        self.pushButton36 = QPushButton(self.elementButtonGroup,"pushButton36")
        self.pushButton36.setEnabled(1)
        self.pushButton36.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton36.sizePolicy().hasHeightForWidth()))
        self.pushButton36.setMinimumSize(QSize(22,22))
        self.pushButton36.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton36.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton36,36)

        elementButtonGroupLayout.addWidget(self.pushButton36,3,5)

        self.pushButton15 = QPushButton(self.elementButtonGroup,"pushButton15")
        self.pushButton15.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton15.sizePolicy().hasHeightForWidth()))
        self.pushButton15.setMinimumSize(QSize(22,22))
        self.pushButton15.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton15.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton15,15)

        elementButtonGroupLayout.addWidget(self.pushButton15,2,2)

        self.pushButton14 = QPushButton(self.elementButtonGroup,"pushButton14")
        self.pushButton14.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton14.sizePolicy().hasHeightForWidth()))
        self.pushButton14.setMinimumSize(QSize(22,22))
        self.pushButton14.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton14.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton14,14)

        elementButtonGroupLayout.addWidget(self.pushButton14,2,1)

        self.pushButton13 = QPushButton(self.elementButtonGroup,"pushButton13")
        self.pushButton13.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton13.sizePolicy().hasHeightForWidth()))
        self.pushButton13.setMinimumSize(QSize(22,22))
        self.pushButton13.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton13.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton13,13)

        elementButtonGroupLayout.addWidget(self.pushButton13,2,0)

        self.pushButton5 = QPushButton(self.elementButtonGroup,"pushButton5")
        self.pushButton5.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton5.sizePolicy().hasHeightForWidth()))
        self.pushButton5.setMinimumSize(QSize(22,22))
        self.pushButton5.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton5.setToggleButton(1)
        self.elementButtonGroup.insert( self.pushButton5,5)

        elementButtonGroupLayout.addWidget(self.pushButton5,1,0)
        tabLayout.addWidget(self.elementButtonGroup)

        self.hybrid_btngrp = QButtonGroup(self.tab,"hybrid_btngrp")
        self.hybrid_btngrp.setFrameShape(QButtonGroup.NoFrame)
        self.hybrid_btngrp.setFrameShadow(QButtonGroup.Plain)
        self.hybrid_btngrp.setLineWidth(0)
        self.hybrid_btngrp.setExclusive(1)
        self.hybrid_btngrp.setColumnLayout(0,Qt.Vertical)
        self.hybrid_btngrp.layout().setSpacing(0)
        self.hybrid_btngrp.layout().setMargin(1)
        hybrid_btngrpLayout = QHBoxLayout(self.hybrid_btngrp.layout())
        hybrid_btngrpLayout.setAlignment(Qt.AlignTop)

        self.sp3_btn = QPushButton(self.hybrid_btngrp,"sp3_btn")
        self.sp3_btn.setMinimumSize(QSize(30,30))
        self.sp3_btn.setPixmap(self.image1)
        self.sp3_btn.setToggleButton(1)
        self.sp3_btn.setOn(1)
        self.sp3_btn.setDefault(0)
        self.hybrid_btngrp.insert( self.sp3_btn,0)
        hybrid_btngrpLayout.addWidget(self.sp3_btn)

        self.sp2_btn = QPushButton(self.hybrid_btngrp,"sp2_btn")
        self.sp2_btn.setMinimumSize(QSize(30,30))
        self.sp2_btn.setPixmap(self.image2)
        self.sp2_btn.setToggleButton(1)
        self.hybrid_btngrp.insert( self.sp2_btn,1)
        hybrid_btngrpLayout.addWidget(self.sp2_btn)

        self.sp_btn = QPushButton(self.hybrid_btngrp,"sp_btn")
        self.sp_btn.setMinimumSize(QSize(30,30))
        self.sp_btn.setPixmap(self.image3)
        self.sp_btn.setToggleButton(1)
        self.hybrid_btngrp.insert( self.sp_btn,2)
        hybrid_btngrpLayout.addWidget(self.sp_btn)

        self.aromatic_btn = QPushButton(self.hybrid_btngrp,"aromatic_btn")
        self.aromatic_btn.setMinimumSize(QSize(30,30))
        self.aromatic_btn.setPixmap(self.image4)
        self.aromatic_btn.setToggleButton(1)
        self.hybrid_btngrp.insert( self.aromatic_btn,3)
        hybrid_btngrpLayout.addWidget(self.aromatic_btn)
        spacer4 = QSpacerItem(5,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        hybrid_btngrpLayout.addItem(spacer4)
        tabLayout.addWidget(self.hybrid_btngrp)
        self.tabWidget2.insertTab(self.tab,QString(""))

        self.tab_2 = QWidget(self.tabWidget2,"tab_2")

        self.clipboard_combox = QComboBox(0,self.tab_2,"clipboard_combox")
        self.clipboard_combox.setGeometry(QRect(10,20,180,21))
        self.tabWidget2.insertTab(self.tab_2,QString(""))
        MMKitDialogLayout.addWidget(self.tabWidget2)
        spacer4_2 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        MMKitDialogLayout.addItem(spacer4_2)

        layout10 = QHBoxLayout(None,0,6,"layout10")
        spacer8 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout10.addItem(spacer8)

        self.closePTableButton = QPushButton(self,"closePTableButton")
        self.closePTableButton.setSizePolicy(QSizePolicy(1,0,0,0,self.closePTableButton.sizePolicy().hasHeightForWidth()))
        self.closePTableButton.setDefault(1)
        layout10.addWidget(self.closePTableButton)
        MMKitDialogLayout.addLayout(layout10)

        self.languageChange()

        self.resize(QSize(222,415).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.closePTableButton,SIGNAL("clicked()"),self,SLOT("close()"))
        self.connect(self.elementButtonGroup,SIGNAL("clicked(int)"),self.setElementInfo)
        self.connect(self.hybrid_btngrp,SIGNAL("clicked(int)"),self.set_hybrid_type)



    def languageChange(self):
        self.setCaption(self.__tr("Modeling Kit"))
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
        self.pushButton15.setText(self.__tr("P"))
        self.pushButton14.setText(self.__tr("Si"))
        self.pushButton13.setText(self.__tr("Al"))
        self.pushButton5.setText(self.__tr("B"))
        self.hybrid_btngrp.setTitle(QString.null)
        self.sp3_btn.setText(QString.null)
        self.sp2_btn.setText(QString.null)
        self.sp_btn.setText(QString.null)
        self.aromatic_btn.setText(QString.null)
        self.tabWidget2.changeTab(self.tab,self.__tr("Atoms"))
        self.tabWidget2.changeTab(self.tab_2,self.__tr("Clipboard"))
        self.closePTableButton.setText(self.__tr("Close"))


    def setElementInfo(self,a0):
        print "MMKitDialog.setElementInfo(int): Not implemented yet"

    def set_hybrid_type(self,a0):
        print "MMKitDialog.set_hybrid_type(int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("MMKitDialog",s,c)

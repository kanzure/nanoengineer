# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HelpDialog.ui'
#
# Created: Tue Sep 13 16:00:26 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"20 20 46 1",
"s c #0065a3",
"y c #0065a4",
"G c #0166a4",
"r c #0266a5",
"B c #0367a5",
"t c #0568a5",
"C c #0568a6",
"K c #0568a7",
"x c #0669a7",
"q c #0769a7",
"u c #0c6ca8",
"F c #0e6da9",
"m c #0f6ea9",
"I c #126faa",
"k c #1370aa",
"l c #1470ab",
"J c #1772ab",
"H c #2077ae",
"N c #2278af",
"M c #257aaf",
"A c #297cb0",
"a c #359103",
"j c #3784b5",
"Q c #3a86b5",
"n c #3c87b6",
"b c #469903",
"c c #4f9e03",
"d c #5aa403",
"e c #61a702",
"p c #68a0c2",
"f c #68ab01",
"D c #6ea3c4",
"# c #70af00",
"P c #71a5c5",
"R c #75a7c6",
"L c #87b1cb",
"w c #93b8cf",
"v c #96bacf",
"i c #a3c1d3",
"o c #b0c8d7",
"h c #bdd0da",
"O c #bdd0db",
"E c #bed1db",
"g c #c2d3dc",
"z c #cdd9df",
". c #ffffff",
"....................",
".###################",
"..a...#########.....",
"..b...#########.....",
"..c...#########.....",
"..d...#########.....",
"..e...#########.....",
"..f......ghg........",
"..f....ijklmno......",
"..f...pqrssstuv.....",
"..f..wxysssssykz....",
".....ABsssssssCD....",
"....EFssssssssGH....",
"....hIssssssssyJ....",
"....gFysssssssyA....",
".....ntsssssssKL....",
".....ouysssssGM.....",
"......vkCGyGxNO.....",
".......zPQnQR.......",
"...................."
]

class HelpDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("HelpDialog")

        self.setIcon(self.image0)

        HelpDialogLayout = QVBoxLayout(self,11,6,"HelpDialogLayout")

        self.help_tab = QTabWidget(self,"help_tab")

        self.tab = QWidget(self.help_tab,"tab")
        tabLayout = QGridLayout(self.tab,1,1,11,6,"tabLayout")

        self.mouse_controls_textbrowser = QTextBrowser(self.tab,"mouse_controls_textbrowser")

        tabLayout.addWidget(self.mouse_controls_textbrowser,0,0)
        self.help_tab.insertTab(self.tab,QString.fromLatin1(""))

        self.tab_2 = QWidget(self.help_tab,"tab_2")
        tabLayout_2 = QGridLayout(self.tab_2,1,1,11,6,"tabLayout_2")

        self.keyboard_shortcuts_textbrowser = QTextBrowser(self.tab_2,"keyboard_shortcuts_textbrowser")

        tabLayout_2.addWidget(self.keyboard_shortcuts_textbrowser,0,0)
        self.help_tab.insertTab(self.tab_2,QString.fromLatin1(""))
        HelpDialogLayout.addWidget(self.help_tab)

        layout1 = QHBoxLayout(None,0,6,"layout1")
        spacer3 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout1.addItem(spacer3)

        self.close_btn = QPushButton(self,"close_btn")
        layout1.addWidget(self.close_btn)
        HelpDialogLayout.addLayout(layout1)

        self.languageChange()

        self.resize(QSize(600,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.help_tab,SIGNAL("selected(const QString&)"),self.setup_current_page)
        self.connect(self.close_btn,SIGNAL("clicked()"),self.close)


    def languageChange(self):
        self.setCaption(self.__tr("nanoENGINEER-1 Help"))
        self.help_tab.changeTab(self.tab,self.__tr("Mouse Controls"))
        self.help_tab.changeTab(self.tab_2,self.__tr("Keyboard Shortcuts"))
        self.close_btn.setText(self.__tr("Close"))


    def setup_current_page(self):
        print "HelpDialog.setup_current_page(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("HelpDialog",s,c)

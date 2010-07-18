__author__ = "Geoffroy Couprie"
__copyright__ = "Copyright 2010, Geoffroy Couprie"
__license__ = "GPL v2"
__version__ = "0.0.1"
__maintainer__ = "Geoffroy Couprie"
__email__ = "geo.couprie@gmail.com"
__status__ = "Prototype"

import sys
from PyQt4 import QtGui
from PyQt4.QtCore import *
from gui import Ui_MainWindow
from newclass import Ui_NewClass
from newmethod import Ui_NewMethod
from newpackage import Ui_NewPackage
import sqlite3
from PyQt4.Qsci import QsciLexerPython

class Pyssenlit(QObject):

    def __init__(self):
        QObject.__init__(self)

        self.conn = sqlite3.connect('example.db')
        self.c = self.conn.cursor()

        self.app = QtGui.QApplication(sys.argv)
        self.window = QtGui.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        self.ui.code.setLexer(QsciLexerPython())


        self.connect(self.ui.packages, SIGNAL("itemSelectionChanged()"),
                        self.UpdateClasses)
        self.ui.classes.itemClicked.connect(self.ShowImports)
        self.connect(self.ui.classes, SIGNAL("itemSelectionChanged()"),
                        self.UpdateMethods)
        self.connect(self.ui.methods, SIGNAL("itemSelectionChanged()"),
                        self.UpdateCode)
        savekey = QtGui.QShortcut(Qt.CTRL + Qt.Key_S, self.ui.code, self.save)
        self.ui.newpackage.clicked.connect(self.newPackage)
        self.connect(self.ui.newclass, SIGNAL("clicked()"), self.newClass)
        self.connect(self.ui.newmethod, SIGNAL("clicked()"), self.newMethod)

        #fill packages list
        self.c.execute('select * from package')
        itemslist = []
        for row in self.c:
            #print row
            item  = QtGui.QTreeWidgetItem()
            item.setText(0,row[2])
            item.setText(1,str(row[0]))
            itemslist.append(item)
            if row[1]==0:
                self.ui.packages.addTopLevelItem(item)
            else:
                itemslist[row[1]-1].addChild(item)

        self.window.show()

        self.app.exec_()


    def __del__(self):
        print 'application closing'
        QObject.__del__(self)
        self.c.close()
        self.conn.close()   
    
    def UpdateClasses(self):
        #print ui.packages.selectedItems()[0].text(0)
        self.ui.classes.clear()
        self.ui.methods.clear()
        self.ui.code.clear()
        self.currentpackage = self.ui.packages.selectedItems()[0]
        self.c.execute('select * from class where pk_id=?',
                  (int(self.ui.packages.selectedItems()[0].text(1)),))
        for row in self.c:
            #print row
            item = QtGui.QListWidgetItem()
            item.setText(row[2])
            self.ui.classes.addItem(item)

    def ShowImports(self,item):
        print 'showiports'+str(item.text())
        #if len(ui.methods.selectedItems())==0 or \
        #(hasattr(self, 'currentclass') and self.currentclass==item):
            #print "show imports"
            #print self.currentclass
        self.c.execute('select name, inherits, imports from class where name=?',
                  (str(item.text()),))
        name, inherits,imports = self.c.fetchone()
        print name+' '+inherits+' '+imports
        signature = 'class '+name
        if inherits!='':
            signature = signature+'('+inherits+')'
        self.ui.methods.clearSelection()
        self.ui.code.clear()
        self.ui.code.setText(signature)

        self.currentclass = item
            
    def UpdateMethods(self):
        self.ui.code.clear()
        self.ui.methods.clear()
        
        if len(self.ui.classes.selectedItems()) > 0:
            self.c.execute("select id from class where name=?",
                      (str(self.ui.classes.selectedItems()[0].text()),))
            clid=self.c.fetchone()[0]
            self.c.execute('select * from method where cl_id=?',
                      (clid,))
            for row in self.c:
                item = QtGui.QListWidgetItem()
                item.setText(row[1])
                self.ui.methods.addItem(item)

    def UpdateCode(self):
        #print ui.methods.selectedItems()[0].text()
        self.ui.code.clear()
        if len(self.ui.methods.selectedItems()) > 0 :
            self.c.execute("select code from method where name=?",
                  (str(self.ui.methods.selectedItems()[0].text()),))
            code=self.c.fetchone()[0]
            self.ui.code.setText(code)

    def save(self):
        #print "saving code"
        #print ui.code.document().toPlainText()
        self.c.execute("update method set code=? where name=?",
                  (str(self.ui.code.text()),
                   str(self.ui.methods.selectedItems()[0].text())))
        self.conn.commit()

    def newPackage(self):
        dialog = QtGui.QDialog()
        packageDialog = Ui_NewPackage()
        packageDialog.setupUi(dialog)
        dialog.show()
        if dialog.exec_():
            print packageDialog.packagename.text()
            self.c.execute("select max(id) from package")
            pkid = self.c.fetchone()[0]
            self.c.execute("insert into package values(?,0,?)",
                           (pkid+1,str(packageDialog.packagename.text())))
            self.conn.commit()

    def newClass(self):
        dialog = QtGui.QDialog()
        classDialog = Ui_NewClass()
        classDialog.setupUi(dialog)
        dialog.show()
        if dialog.exec_():
            print classDialog.classname.text()
            self.c.execute("select max(id) from class")
            clid = self.c.fetchone()[0]
            self.c.execute("insert into class \
                values(?,?,?,?,?)",
                (clid+1, int(self.ui.packages.selectedItems()[0].text(1)),
                 str(classDialog.classname.text()),
                 str(classDialog.classinherits.text()),
                 ''))
            self.conn.commit()
            self.UpdateClasses()

    def newMethod(self):
        dialog = QtGui.QDialog()
        methodDialog = Ui_NewMethod()
        methodDialog.setupUi(dialog)
        dialog.show()
        if dialog.exec_():
            self.c.execute("select id from class where name=?",
                           (str(self.ui.classes.selectedItems()[0].text()),))
            clid = self.c.fetchone()[0]
            self.c.execute("insert into method \
                values(?,?,?,?,?,?)",
                (clid,str(methodDialog.methodname.text()),
                 str(methodDialog.methodcategory.text()),
                 str(methodDialog.methodarguments.text()),
                 str(methodDialog.methodcomments.document().toPlainText()),
                 ''))
            self.conn.commit()
            self.UpdateMethods()


if __name__ == '__main__':
    p = Pyssenlit()

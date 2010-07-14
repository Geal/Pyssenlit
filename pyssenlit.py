# editor.py
import sys
from PyQt4 import QtGui
from PyQt4.QtCore import *
import syntax
from gui import Ui_MainWindow
from newclass import Ui_NewClass
import sqlite3

class Pyssenlit(QObject):

    def __init__(self):
        QObject.__init__(self)

        self.conn = sqlite3.connect('example.db')
        self.c = self.conn.cursor()

        self.app = QtGui.QApplication(sys.argv)
        self.window = QtGui.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        self.connect(self.ui.packages, SIGNAL("itemSelectionChanged()"),
                        self.UpdateClasses)
        self.ui.classes.itemClicked.connect(self.ShowImports)
        self.connect(self.ui.classes, SIGNAL("itemSelectionChanged()"),
                        self.UpdateMethods)
        self.connect(self.ui.methods, SIGNAL("itemSelectionChanged()"),
                        self.UpdateCode)
        savekey = QtGui.QShortcut(Qt.CTRL + Qt.Key_S, self.ui.code, self.save)
        self.connect(self.ui.newclass, SIGNAL("clicked()"), self.newClass)
        
        highlight = syntax.Python(self.ui.code.document())

        # Load syntax.py into the editor for demo purposes
        infile = open('syntax.py', 'r')
        self.ui.code.setPlainText(infile.read())

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
        self.ui.code.setPlainText(signature)

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
            self.ui.code.setPlainText(code)

    def save(self):
        #print "saving code"
        #print ui.code.document().toPlainText()
        self.c.execute("update method set code=? where name=?",
                  (str(self.ui.code.document().toPlainText()),
                   str(self.ui.methods.selectedItems()[0].text())))
        self.conn.commit()

    def newClass(self):
        print "new class"
        item = QtGui.QListWidgetItem()
        item.setText('new class')
        self.dialog = QtGui.QDialog()
        self.ui2 = Ui_NewClass()
        self.ui2.setupUi(self.dialog)
        self.dialog.show()         
        if self.dialog.exec_():
            print self.ui2.classname.text()
            self.c.execute("select max(id) from class")
            clid = self.c.fetchone()[0]
            self.c.execute("insert into class \
                values(?,?,?,?,?)",
                (clid+1, int(self.ui.packages.selectedItems()[0].text(1)),
                 str(self.ui2.classname.text()), str(self.ui2.classinherits.text()),
                 ''))
            self.conn.commit()
            self.UpdateClasses()


if __name__ == '__main__':
    p = Pyssenlit()

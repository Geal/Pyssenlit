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

        self.m = Model('example.db')

        self.app = QtGui.QApplication(sys.argv)
        self.window = QtGui.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        self.ui.code.setLexer(QsciLexerPython())


        self.ui.packages.itemSelectionChanged.connect(self.UpdateClasses)
        self.ui.classes.itemClicked.connect(self.ShowImports)
        self.ui.classes.itemSelectionChanged.connect(self.UpdateMethods)
        self.ui.methods.itemSelectionChanged.connect(self.UpdateCode)
        savekey = QtGui.QShortcut(Qt.CTRL + Qt.Key_S, self.ui.code, self.save)
        self.ui.newpackage.clicked.connect(self.newPackage)
        self.ui.newclass.clicked.connect(self.newClass)
        self.ui.newmethod.clicked.connect(self.newMethod)

        #fill packages list
        self.UpdatePackage()

        self.window.show()

        self.app.exec_()


    def __del__(self):
        print 'application closing'
        QObject.__del__(self)
        del self.m

    def UpdatePackage(self):
        self.ui.packages.clear()
        self.ui.classes.clear()
        self.ui.methods.clear()
        self.ui.code.clear()
        res = self.m.getAllPackages()
        itemslist = []
        for row in res:
            item  = QtGui.QTreeWidgetItem()
            item.setText(0,row[2])
            item.setText(1,str(row[0]))
            itemslist.append(item)
            if row[1]==0:
                self.ui.packages.addTopLevelItem(item)
            else:
                itemslist[row[1]-1].addChild(item)
    
    def UpdateClasses(self):
        self.ui.classes.clear()
        self.ui.methods.clear()
        self.ui.code.clear()
        self.currentpackage = self.ui.packages.selectedItems()[0]
        res = self.m.getClassesFromPackage(self.currentpackage.text(0))
        for row in res:
            item = QtGui.QListWidgetItem()
            item.setText(row[2])
            self.ui.classes.addItem(item)

    def ShowImports(self,item):
        name, inherits,imports = self.m.getInfosFromClass(item.text())
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
            res = self.m.getMethodsFromClass(self.ui.classes.selectedItems()[0].text())
            for row in res:
                item = QtGui.QListWidgetItem()
                item.setText(row[1])
                self.ui.methods.addItem(item)

    def UpdateCode(self):
        self.ui.code.clear()
        if len(self.ui.methods.selectedItems()) > 0 :
            code=self.m.getCodeFromMethod(self.ui.methods.selectedItems()[0].text())
            self.ui.code.setText(code)

    def save(self):
        self.m.setCodeOfMethod(self.ui.methods.selectedItems()[0].text(),
                               self.ui.code.text())

    def newPackage(self):
        dialog = QtGui.QDialog()
        packageDialog = Ui_NewPackage()
        packageDialog.setupUi(dialog)
        dialog.show()
        if dialog.exec_():
            self.m.newPackage(packageDialog.packagename.text())
            self.UpdatePackage()

    def newClass(self):
        dialog = QtGui.QDialog()
        classDialog = Ui_NewClass()
        classDialog.setupUi(dialog)
        dialog.show()
        if dialog.exec_():
            self.m.newClass(self.ui.packages.selectedItems()[0].text(0),
                            classDialog.classname.text(),
                            classDialog.classinherits.text(), '')
            self.UpdateClasses()

    def newMethod(self):
        dialog = QtGui.QDialog()
        methodDialog = Ui_NewMethod()
        methodDialog.setupUi(dialog)
        dialog.show()
        if dialog.exec_():
            self.m.newMethod(self.ui.classes.selectedItems()[0].text(),
                             methodDialog.methodname.text(),
                             methodDialog.methodcategory.text(),
                             methodDialog.methodarguments.text(),
                             methodDialog.methodcomments.document().toPlainText()
                             )
            self.UpdateMethods()

class Model:
    def __init__(self, database):
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()

    def getAllPackages(self):
        self.c.execute('select * from package')
        itemslist = []
        for row in self.c:
            itemslist.append(row)
        return itemslist

    def getClassesFromPackage(self, pkname):
        self.c.execute("select * from class where pk_id=(select id from \
                       package where name=?)",(str(pkname),))
        itemslist = []
        for row in self.c:
            itemslist.append(row)
        return itemslist

    def getMethodsFromClass(self, classname):
        self.c.execute("select * from method where cl_id=( \
                        select id from class where name=?)",
                       (str(classname),))
        itemslist = []
        for row in self.c:
            itemslist.append(row)
        return itemslist

    def getInfosFromClass(self, classname):
        self.c.execute('select name, inherits, imports from class where name=?',
                  (str(classname),))
        name, inherits,imports = self.c.fetchone()
        return name, inherits, imports

    def getCodeFromMethod(self, method):
        self.c.execute("select code from method where name=?",
            (str(method),))
        return self.c.fetchone()[0]

    def setCodeOfMethod(self, method, code):
        self.c.execute("update method set code=? where name=?",
            (str(code),
           str(method)))
        self.conn.commit()

    def newPackage(self, name, parent=0):
        #TODO: throw error if existent package
        self.c.execute("select max(id) from package")
        pkid = self.c.fetchone()[0]
        self.c.execute("insert into package values(?,?,?)",
                       (pkid+1, int(parent), str(name)))
        self.conn.commit()

    def newClass(self, package, name, inherits, imports=''):
        #TODO: throw error of existent class
        self.c.execute("select max(id) from class")
        clid = self.c.fetchone()[0]
        self.c.execute("insert into class \
            values(?,(select id from package where name=?),?,?,?)",
            (clid+1, str(package), str(name), str(inherits), ''))
        self.conn.commit()

    def newMethod(self, classname, method, category, args, comments, code=''):
        self.c.execute("select id from class where name=?",
                       (str(classname),))
        clid = self.c.fetchone()[0]
        self.c.execute("insert into method values(?,?,?,?,?,?)",
            (clid,str(method), str(category), str(args),
             str(comments), str(code)))
        self.conn.commit()

    def __del__(self):
        print "model closing"
        self.c.close()
        self.conn.close()

if __name__ == '__main__':
    p = Pyssenlit()

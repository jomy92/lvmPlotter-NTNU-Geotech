from PyQt4.uic import loadUiType
from PyQt4 import QtGui, QtCore
import numpy as np
import crs, triaxial
import os

from crs import *

Ui_MainWindow, QMainWindow = loadUiType("selector.ui")

class Selector(QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        super(Selector, self).__init__()
        self.setupUi(self)
        
        # Set column size
        self.treeWidget.setColumnWidth(0,300)
        self.treeWidget.setColumnWidth(1,75)
        self.treeWidget.setColumnWidth(2,50)        
        self.treeWidget.setColumnWidth(3,100)        
        
        self.home()
        
        
    def home(self):
        
        # Select files/folder and remove file
        self.btnFile.clicked.connect(self.file_Open)      
        self.btnFolder.clicked.connect(self.folder_Open)
        self.btnDelete.clicked.connect(self.file_Remove)
        
        # OK/Cancel listener
        self.btnYesNo.accepted.connect(self.new_Event)
        self.btnYesNo.rejected.connect(self.exit)
    
    
    def file_Open(self):
        # #name = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'c:\\',"Image files (*.jpg *.gif)")
        name = QtGui.QFileDialog.getOpenFileNames(self, 'Select Files')
        
        for i in name: # Note: i = name[1,2,3,...]
            fileNameString = str(i)                  # File path
            self.collect_Data(i, fileNameString)
        
    def folder_Open(self):          
        folder = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory")
        
        if folder:
            for i in os.listdir(folder): # Note: i = name[1,2,3,...]
                fileNameString = str(folder+'\\'+i)      # File path
                self.collect_Data(fileNameString)
     
            
    def collect_Data(self, fileNameString):
            fileInfo = QtCore.QFileInfo(fileNameString)
            fileSize = fileInfo.size()
            fileSize = str(fileSize/1000)+' Kb'      # kilo bytes
            fileExt  = fileInfo.suffix()             # Extension
            dateModified = fileInfo.lastModified()   # Last modified        
            dateModified = dateModified.toPyDateTime()
            dateModified = dateModified.strftime("%d-%m-%Y %H:%M")
    
            data = [fileNameString, fileSize, fileExt, dateModified]
            if fileExt:
                self.addFile_toList(data)
      
            
    def addFile_toList(self, data):    
        path, name = os.path.split(data[0])

        numRoots = self.treeWidget.topLevelItemCount()
        
        if numRoots == 0: # Check if empty list
            NewRoot = QtGui.QTreeWidgetItem(self.treeWidget, [path])
            QtGui.QTreeWidgetItem(NewRoot, [name, data[1], data[2], data[3]])
            self.treeWidget.expandItem(NewRoot)

        else:
            for i in range(numRoots):
                root = self.treeWidget.topLevelItem(i)
                if root.text(0) == path:
                    pathExist = 1
                else:
                    pathExist = 0
                
                for j in range(root.childCount()):
                    if root.child(j).text(0) == name:
                        itemExist = 1
                        break
                    else:
                        itemExist = 0
            
            if pathExist == 0:
                NewRoot = QtGui.QTreeWidgetItem(self.treeWidget, [path])
                self.treeWidget.expandItem(NewRoot)
                
            if itemExist == 0 and pathExist == 0:
                QtGui.QTreeWidgetItem(NewRoot, [name, data[1], data[2], data[3]])
            elif itemExist == 0 and pathExist == 1:
                QtGui.QTreeWidgetItem(root, [name, data[1], data[2], data[3]])
        
        
    def file_Remove(self):
        highLightedIndex = self.treeWidget.currentIndex()
        parent = highLightedIndex.parent()
        
        rowInParent = highLightedIndex.row()
        rowInModel  = parent.row()
        
        if highLightedIndex:
            if rowInModel == -1: # Referes to imaginary root
                self.treeWidget.takeTopLevelItem(rowInParent)
            else:
                self.treeWidget.topLevelItem(rowInModel).takeChild(rowInParent)
                if self.treeWidget.topLevelItem(rowInModel).childCount()==0:
                    self.treeWidget.takeTopLevelItem(rowInModel)
    
            
    def new_Event(self):
        #radioBtnCRS - radioBtnCRS
        if not( self.radioBtnCRS.isChecked() or self.radioBtnIL.isChecked() or self.radioBtnTri.isChecked()):
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle("Error")
            msgBox.setIcon(QtGui.QMessageBox.Information)
            msgBox.setText("Please select either CRS, IL or Triaxial")
            msgBox.exec()
            
        else:
            if self.radioBtnCRS.isChecked() and self.treeWidget.topLevelItemCount():
                ## Possible implementations: Check if CRS files
                filePaths = self.retrieve_Filepaths()
                self.myOtherWindow = crs.CRS(filePaths)
                self.myOtherWindow.show()
                self.close()
            elif self.radioBtnIL.isChecked() and self.treeWidget.topLevelItemCount():
                print('Start IL')
            elif self.radioBtnTri.isChecked() and self.treeWidget.topLevelItemCount():
                filePaths = self.retrieve_Filepaths()
                self.myOtherWindow = triaxial.TRIAXIAL(filePaths)
                self.myOtherWindow.show()
                self.close()
            else:
                msgBox = QtGui.QMessageBox()
                msgBox.setWindowTitle("Error")
                msgBox.setIcon(QtGui.QMessageBox.Information)
                msgBox.setText("Please choose some data")
                msgBox.exec()       
    
    def retrieve_Filepaths(self):
        numRoots = self.treeWidget.topLevelItemCount()
        filePath = []      
        for i in range(numRoots):
            root = self.treeWidget.topLevelItem(i)   
            for j in range(root.childCount()):
                filePath.append(root.text(0)+'\\'+root.child(j).text(0))
        return(filePath)        
                
        
        
    def exit(self):
        self.close()
        

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    main = Selector()
    main.show()
    sys.exit(app.exec_())
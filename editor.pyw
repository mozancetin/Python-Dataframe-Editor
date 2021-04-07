from PyQt5 import QtWidgets
from PyQt5 import QtGui
import pandas as pd
import sys
import os


class Editor(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.canSave = False
        self.editor_ui()


    def editor_ui(self):
        self.fileText = QtWidgets.QLabel("File")
        self.searchBar = QtWidgets.QLineEdit()
        self.searchBar.setReadOnly(True)
        self.getDataFrameButton = QtWidgets.QPushButton("Select Dataframe")
        self.columnsText = QtWidgets.QLabel("Columns")
        self.columns = QtWidgets.QListWidget()
        self.deleteColumnButton = QtWidgets.QPushButton("Delete Column")
        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveAsButton = QtWidgets.QPushButton("Save As...")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.searchBar)
        hbox.addWidget(self.getDataFrameButton)

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.deleteColumnButton)
        hbox2.addWidget(self.saveButton)
        hbox2.addWidget(self.saveAsButton)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addSpacing(20)
        vbox.addWidget(self.columnsText)
        vbox.addWidget(self.columns)
        vbox.addLayout(hbox2)

        self.getDataFrameButton.clicked.connect(self.getDataFrame)
        self.deleteColumnButton.clicked.connect(self.deleteColumn)
        self.saveButton.clicked.connect(lambda: self.save(saveAs=False))
        self.saveAsButton.clicked.connect(lambda: self.save(saveAs=True))

        self.setLayout(vbox)
        self.setWindowTitle("Dataframe Editor")
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        self.setMinimumHeight(400)
        self.setMaximumHeight(400)
        self.setMinimumWidth(500)
        self.setMaximumWidth(500)

    def getDataFrame(self):
        self.dfPath = QtWidgets.QFileDialog.getOpenFileName(self, "Select a File", os.getenv("HOMEPATH") + "\Desktop",
        "CSV File (*.csv);; JSON File (*.json);; Excel File (*.xlsx)")
        
        self.fileType = self.dfPath[1]
        self.dfPath = self.dfPath[0]
        self.searchBar.setText(self.dfPath)

        if self.fileType == "CSV File (*.csv)":
            self.df = pd.read_csv(self.dfPath)
            self.canSave = True

        elif self.fileType == "JSON File (*.json)":
            self.df = pd.read_json(self.dfPath)
            self.canSave = True
        
        elif self.fileType == "Excel File (*.xlsx)":
            self.df = pd.read_excel(self.dfPath)
            self.canSave = True

        else:
            return False

        self.columns.clear()
        for i in range(len(self.df.columns)):
            self.columns.insertItem(i, self.df.columns[i])
        self.columns.repaint()
            

    def deleteColumn(self):
        if self.columns.currentItem() != None:
            column = self.columns.currentItem().text()
            self.df.drop(column, axis = 1, inplace = True)

            self.columns.clear()
            for i in range(len(self.df.columns)):
                self.columns.insertItem(i, self.df.columns[i])
            self.columns.repaint()

        else:
            return False

    def save(self, saveAs = False):
        if not self.canSave:
            return False

        self.new_file_name = self.dfPath.split("/")[-1]
        if saveAs:
            self.savePath = QtWidgets.QFileDialog.getSaveFileName(self, "Select Save Path", os.getenv("HOMEPATH") + "\Desktop" + f"/NEW_{self.new_file_name}"
            , "CSV File (*.csv);; JSON File (*.json);; Excel File (*.xlsx)")
            
            self.savefileType = self.savePath[1]
            self.savePath = self.savePath[0]

            if self.savefileType == "CSV File (*.csv)":
                self.df.to_csv(self.savePath, index = False)

            elif self.savefileType == "JSON File (*.json)":
                self.df.to_json(self.savePath)
            
            elif self.savefileType == "Excel File (*.xlsx)":
                # openpyxl Module is neccessary
                self.df.to_excel(self.savePath, index = False)

            else:
                return False

            self.searchBar.setText("Saved successfully")

        else:
            if self.fileType == "CSV File (*.csv)":
                self.df.to_csv(self.dfPath, index = False)

            elif self.fileType == "JSON File (*.json)":
                self.df.to_json(self.dfPath)
            
            elif self.fileType == "Excel File (*.xlsx)":
                # openpyxl Module is neccessary
                self.df.to_excel(self.dfPath, index = False)

            else:
                return False
            
            self.searchBar.setText("Saved successfully")

app = QtWidgets.QApplication(sys.argv)
window = Editor()
window.show()
sys.exit(app.exec_())

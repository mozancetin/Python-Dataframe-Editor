from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, Qt, QThread, QObject
import pandas as pd
import random
import sys
import os

class Worker(QObject):

    def __init__(self, n, df):
        super().__init__()
        self.n = n
        self.df = df

    finished = pyqtSignal()
    newDf = pyqtSignal(pd.DataFrame)
    oldDf = pyqtSignal(pd.DataFrame)

    def main(self):
        dropList = list()
        self.dfTest = pd.DataFrame(columns=self.df.columns)
        for i in range(self.n):
            index = random.randint(0, self.df.shape[0] - 1)
            self.dfTest.loc[i] = self.df.loc[index]
            dropList.append(index)
        else:
            self.df.drop(dropList, inplace=True)
            self.oldDf.emit(self.df)
            self.newDf.emit(self.dfTest)
            self.finished.emit()

class TestWindow(QtWidgets.QWidget):

    numberOfTests = pyqtSignal(int)

    def __init__(self, maxValue):
        super().__init__()
        self.maxValue = maxValue
        self.test_ui()

    def test_ui(self):
        self.valueCount = QtWidgets.QLabel("10")
        self.text = QtWidgets.QLabel("Number of Test Rows:")
        self.inputArea = QtWidgets.QSlider(Qt.Horizontal)
        self.inputArea.setMinimum(10)
        self.inputArea.setMaximum(self.maxValue)
        self.inputArea.valueChanged.connect(lambda: self.valueCount.setText(str(self.inputArea.value())))
        self.button = QtWidgets.QPushButton("Okay")

        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(self.text)
        v_box.addWidget(self.inputArea)
        v_box.addWidget(self.valueCount)
        v_box.addWidget(self.button)

        self.button.clicked.connect(self.click)

        self.setLayout(v_box)
        self.setWindowTitle("Number of Test Rows")
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        self.setMinimumHeight(120)
        self.setMaximumHeight(120)
        self.setMinimumWidth(350)
        self.setMaximumWidth(350)

    def click(self):
        self.valueCount.setText("Please Wait...")
        self.numberOfTests.emit(self.inputArea.value())
        self.close()

class Editor(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.canSave = False
        self.editor_ui()

    def editor_ui(self):
        self.searchBar = QtWidgets.QLineEdit()
        self.searchBar.setReadOnly(True)
        self.getDataFrameButton = QtWidgets.QPushButton("Select Dataframe")
        self.columnsText = QtWidgets.QLabel("Columns")
        self.columns = QtWidgets.QListWidget()
        self.generateTestButton = QtWidgets.QPushButton("Generate Test File")
        self.deleteColumnButton = QtWidgets.QPushButton("Delete Column")
        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveAsButton = QtWidgets.QPushButton("Save As...")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.searchBar)
        hbox.addWidget(self.getDataFrameButton)

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.generateTestButton)
        hbox2.addWidget(self.deleteColumnButton)
        hbox2.addWidget(self.saveButton)
        hbox2.addWidget(self.saveAsButton)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addSpacing(20)
        vbox.addWidget(self.columnsText)
        vbox.addWidget(self.columns)
        vbox.addLayout(hbox2)

        self.generateTestButton.clicked.connect(self.selectTestNumber)
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

    def selectTestNumber(self):
        if not self.canSave:
            return False
        
        self.secondWindow = TestWindow(maxValue=int(self.df.shape[0] * 1 / 5))
        self.secondWindow.show()
    
        self.secondWindow.numberOfTests.connect(lambda x: self.generateTestFile(x))

    def generateTestFile(self, n):
        def saveInside(df=None, dfTest=None, test=False):
            if test:
                self.savePath = QtWidgets.QFileDialog.getSaveFileName(self, "Select Save Path", os.getenv("HOMEPATH") + "\Desktop"
                , "CSV File (*.csv);; JSON File (*.json);; Excel File (*.xlsx)")
                
                self.savefileType = self.savePath[1]
                self.savePath = self.savePath[0]

                if self.savefileType == "CSV File (*.csv)":
                    dfTest.to_csv(self.savePath, index = False)

                elif self.savefileType == "JSON File (*.json)":
                    dfTest.to_json(self.savePath)
                
                elif self.savefileType == "Excel File (*.xlsx)":
                    # openpyxl Module is neccessary
                    dfTest.to_excel(self.savePath, index = False)

                else:
                    return False

            if not test:
                if self.fileType == "CSV File (*.csv)":
                    df.to_csv(self.dfPath, index = False)

                elif self.fileType == "JSON File (*.json)":
                    df.to_json(self.dfPath)
                
                elif self.fileType == "Excel File (*.xlsx)":
                    # openpyxl Module is neccessary
                    df.to_excel(self.dfPath, index = False)

                else:
                    return False

        self.thread = QThread()
        self.worker = Worker(n, self.df)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.main)
        self.thread.started.connect(lambda: self.searchBar.setText("Please Wait"))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.start()
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.newDf.connect(lambda x: saveInside(dfTest=x, test=True))
        self.worker.oldDf.connect(lambda x: saveInside(df=x, test=False))
        self.thread.finished.connect(lambda: self.searchBar.setText("Saved successfully"))

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

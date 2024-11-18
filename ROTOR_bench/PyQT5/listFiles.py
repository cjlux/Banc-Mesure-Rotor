from PyQt5.QtWidgets import (QWidget, QScrollArea, QApplication, QVBoxLayout, QRadioButton)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic

import sys, json, os
sys.path.insert(0, sys.path[0].replace('PyQT5',''))
#print(sys.path)

class ListFile(QScrollArea):
    
    def __init__(self, items=None, parent=None):
        super(ListFile, self).__init__(parent)
        
        self.parent = parent
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setMinimumHeight(600)
        self.listItem = items
        if self.listItem == None:
            self.listItem = ['0']*20
        self.listState = [False]*len(self.listItem)
        
        self.initUI()
        
    def initUI(self):
        container=QWidget()
        self.setWidget(container)
        layout = QVBoxLayout(container)
        
        for i, item in enumerate(self.listItem):
            b = QRadioButton(text=item)
            b.toggled.connect(lambda state, file=item: self.changeChk(state, file))
            layout.addWidget(b)
    
    def refresh(self, items):
        self.listItem = items
        self.listState = [False]*len(self.listItem)
        
        container = self.widget()
        layout = container.layout()
        
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
              layout.removeWidget(child.widget())    
              del child
            
        for i, item in enumerate(self.listItem):
            b = QRadioButton(text=item)
            b.toggled.connect(lambda state, file=item: self.changeChk(state, file))
            layout.addWidget(b)
        
    def changeChk(self, state, file):
        print(f"{state} : {file}")
        if self.parent: 
            self.parent.select_file(file)
               

def main():
    app = QApplication(sys.argv)
    main = ListFile(list("abcdefghijklmnopqrstuvwxyz"))
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
#
# widget QTabWidget: création d'onglets dans la fenêtre principale
#
import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget,
                             QTabWidget, QVBoxLayout, QHBoxLayout, QDesktopWidget,
                             QDoubleSpinBox, QSpinBox, QLabel)

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
 
class MyApp(QMainWindow):
 
    def __init__(self):
        QMainWindow.__init__(self) 
        self.initUI()          
        self.show()            

        self.zPos = [0, 0, 0, 0, 0]
        self.rotStep = 0
    
    def initUI(self):               
        self.resize(600, 300) 
        self.center()       
        self.setWindowTitle('PyQt5 tabs')
 
        # Création d'un objet QTabWidget et de 3 onglets vides:
        self.tabs = QTabWidget(parent=self)
        tab1 = QWidget(parent=self)
        tab2 = QWidget(parent=self)
        tab3 = QWidget(parent=self)
        self.setCentralWidget(self.tabs) 

        # Ajouter les 3 onglets Add tabs
        self.tabs.addTab(tab1,"Launch")
        self.tabs.addTab(tab2,"Display")
  
        # Remplissage du 1er onglet :
        vlayout1 = QVBoxLayout()
        w = QLabel("Rotation step angle ", parent=self)
        b = QPushButton('RUN', parent=self)
        b.clicked.connect(self.run)
        q = QDoubleSpinBox(parent=self)
        q.setValue(1.2)
        q.setRange(1.2, 360)
        q.setSingleStep(1.2)
        q.setGeometry(250,50,60,25)
        q.valueChanged.connect(self.rotStepChange)
        h = QHBoxLayout()
        h.addWidget(w)
        h.addWidget(q)
        h.addStretch()
        h.addWidget(b)
        
        vlayout1.addLayout(h)
        vlayout1.addStretch()

        self.posWidgets = []
        for i in range(5):
            w = QLabel(f"Position #{i+1} [mm]", parent=self)
            q = QSpinBox(parent=self)
            self.posWidgets.append(q)
            q.setValue(0)
            q.setRange(0, 130)
            q.setSingleStep(1)
            q.setGeometry(250,50,60,25)
            h = QHBoxLayout()
            h.addWidget(w)
            h.addWidget(q)
            h.addStretch()
            vlayout1.addLayout(h)
        vlayout1.addStretch()
        tab1.setLayout(vlayout1)
        self.posWidgets[0].valueChanged.connect(lambda x: self.zposChange(x, 0))
        self.posWidgets[1].valueChanged.connect(lambda x: self.zposChange(x, 1))
        self.posWidgets[2].valueChanged.connect(lambda x: self.zposChange(x, 2))
        self.posWidgets[3].valueChanged.connect(lambda x: self.zposChange(x, 3))
        self.posWidgets[4].valueChanged.connect(lambda x: self.zposChange(x, 4)) 
 
        # Remplissage du 2me onglet :
        vlayout2 = QVBoxLayout()
        btn21 = QPushButton("button21")
        btn22 = QPushButton("button22")
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(btn21)
        hlayout2.addStretch()
        hlayout2.addWidget(btn22)
        vlayout2.addLayout(hlayout2)
        vlayout2.addStretch()
        tab2.setLayout(vlayout2)

    def run(self):
        print('run')
        
    def zposChange(self, z, n):
        self.zPos[n] = z
        print(self.zPos)

    def rotStepChange(self, r):
        self.rotStep = r
        print(r)
        
    def center(self):
        desktop = QApplication.desktop()
        n = desktop.screenNumber(self.cursor().pos())
        screen_center = desktop.screenGeometry(n).center()
        geo_window = self.frameGeometry()
        geo_window.moveCenter(screen_center)
        self.move(geo_window.topLeft())
        
if __name__ == '__main__':
    app = QApplication(sys.argv) # instanciation classe QApplication
    my_app = MyApp()             # instanciation classe MyApp
    app.exec_()                  # lancement boucle événementielle Qt

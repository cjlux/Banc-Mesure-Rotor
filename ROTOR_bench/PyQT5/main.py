#
# widget QTabWidget: création d'onglets dans la fenêtre principale
#
import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget,
                             QTabWidget, QVBoxLayout, QHBoxLayout, QDesktopWidget,
                             QDoubleSpinBox, QSpinBox, QLabel)

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
import subprocess

class MyApp(QMainWindow):

    NB_MAX_ZPOS = 10
    
    def __init__(self):
        QMainWindow.__init__(self)

        self.tab1 = None
        self.tab2 = None
        self.tab3 = None

        self.workDist = 1
        self.zPos     = []    # The list of the Z positions
        self.rotStep  = 1.2   # the step of the ROTOR rotation 
        self.repet    = 1     # number of repetition of the same measurement run

        self.platform = subprocess.getoutput('uname -a').split()[1]
        print("Platform: ", self.platform)

        self.tmp_launch_file_path = "/tmp/ROTOR_LAUNCH.txt"

        if self.platform != 'raspberrypi':
            print("ERROR:you must use a Rasberry Pi platform !!!")
            sys.exit()
        self.terminal_cmd = ["lxterminal", "--command", 
        "/usr/bin/bash -c 'source /home/rotor/rotor/bin/activate && cd /home/rotor/Banc-Mesure-Rotor/ && python ROTOR_bench/strike.py; read'"]
        print(self.terminal_cmd)

        self.InitUI()          
        self.show()            
    
    def InitUI(self):
        
        self.zPos = [0 for _ in range(self.NB_MAX_ZPOS)]
        
        self.resize(900, 700) 
        self.Center()       
        self.setWindowTitle('ROTOR mesurement bench')
 
        # Création d'un objet QTabWidget et de 3 onglets vides:
        self.tabs = QTabWidget(parent=self)
        self.tab1 = QWidget(parent=self)
        self.tab2 = QWidget(parent=self)
        self.tab3 = QWidget(parent=self)
        self.setCentralWidget(self.tabs) 

        # Add 3 tabs:
        self.tabs.addTab(self.tab1,"Run bench")
        self.tabs.addTab(self.tab2,"Run Free")
        self.tabs.addTab(self.tab3,"Display")

        # Fill in the tabs:
        self.__InitTab1()
        self.__InitTab2()
        self.__InitTab3()
        
    def __InitTab1(self):
        ''' To fill in the RunBench tab'''

        VL = QVBoxLayout()
        self.tab1.setLayout(VL)
        
        w = QLabel("Working distance ", parent=self)
        sb = QSpinBox(parent=self)
        sb.setValue(1)
        sb.setMinimum(0)
        sb.setSingleStep(1)
        sb.setSuffix(" mm")
        sb.setGeometry(250,50,60,25)
        sb.valueChanged.connect(self.WorkingDistChanged) 
        b = QPushButton('RUN bench', parent=self)
        b.clicked.connect(self.RunBench)
        h = QHBoxLayout()
        h.addWidget(w)
        h.addWidget(sb)
        h.addStretch()
        h.addWidget(b)

        VL.addLayout(h)
        VL.addStretch()
        
        w = QLabel("Rotation step angle ", parent=self)
        sb = QDoubleSpinBox(parent=self)
        sb.setValue(1.2)
        sb.setRange(1.2, 360)
        sb.setSingleStep(1.2)
        sb.setSuffix(" °")
        sb.setGeometry(250,50,60,25)
        sb.valueChanged.connect(self.RotStepChanged)
        h = QHBoxLayout()
        h.addWidget(w)
        h.addWidget(sb)
        h.addStretch()
        
        VL.addLayout(h)
        VL.addStretch()

        self.posWidgets = []
        for i in range(self.NB_MAX_ZPOS):
            w = QLabel(f"Position #{i+1:2d}:", parent=self)
            sb = QSpinBox(parent=self)
            self.posWidgets.append(sb)
            sb.setValue(0)
            sb.setRange(0, 130)
            sb.setSingleStep(1)
            sb.setSuffix(" mm")
            sb.setGeometry(250,50,60,25)
            h = QHBoxLayout()
            h.addWidget(w)
            h.addWidget(sb)
            h.addStretch()
            VL.addLayout(h)  
        VL.addStretch()

        w = QLabel("Number of repetition: ", parent=self)
        sb = QSpinBox(parent=self)
        sb.setValue(1)
        sb.setRange(1, 100)
        sb.setSingleStep(1)
        sb.setGeometry(250,50,60,25)
        sb.valueChanged.connect(self.RepetChanged)
        h = QHBoxLayout()
        h.addWidget(w)
        h.addWidget(sb)
        h.addStretch()
        VL.addLayout(h)

        self.posWidgets[0].valueChanged.connect(lambda x: self.ZposChanged(x, 0))
        self.posWidgets[1].valueChanged.connect(lambda x: self.ZposChanged(x, 1))
        self.posWidgets[2].valueChanged.connect(lambda x: self.ZposChanged(x, 2))
        self.posWidgets[3].valueChanged.connect(lambda x: self.ZposChanged(x, 3))
        self.posWidgets[4].valueChanged.connect(lambda x: self.ZposChanged(x, 4)) 
        self.posWidgets[5].valueChanged.connect(lambda x: self.ZposChanged(x, 5))
        self.posWidgets[6].valueChanged.connect(lambda x: self.ZposChanged(x, 6))
        self.posWidgets[7].valueChanged.connect(lambda x: self.ZposChanged(x, 7))
        self.posWidgets[8].valueChanged.connect(lambda x: self.ZposChanged(x, 8)) 
        self.posWidgets[9].valueChanged.connect(lambda x: self.ZposChanged(x, 9)) 

    def __InitTab3(self):
        ''' To fill the "Run Free" tab'''
        
        VL = QVBoxLayout()
        self.tab3.setLayout(VL)

        btn21 = QPushButton("button21")
        btn22 = QPushButton("button22")
        h = QHBoxLayout()
        h.addWidget(btn21)
        h.addStretch()
        h.addWidget(btn22)
        VL.addLayout(h)
        VL.addStretch()

    def __InitTab2(self):
        ''' To fill the "Run Free" tab'''
        
        VL = QVBoxLayout()
        self.tab2.setLayout(VL)
        
        w = QLabel("Xorking distance [mm]", parent=self)
        sb = QSpinBox(parent=self)
        sb.setValue(0)
        sb.setMinimum(0)
        sb.setSingleStep(1)
        sb.setSuffix(" mm")
        sb.setGeometry(250,50,60,25)
        b = QPushButton('RUN bench', parent=self)
        b.clicked.connect(self.RunBench)
        h = QHBoxLayout()
        h.addWidget(w)
        h.addWidget(sb)
        h.addStretch()
        h.addWidget(b)
        VL.addLayout(h)
        VL.addStretch()

    def RunBench(self):
        zPos = [ z for z in self.zPos if z > 0]
        self.params = {'WORK_DIST': self.workDist,
                       'ROT_STEP_DEG': self.rotStep,
                       'Z_POS_MM': zPos,
                       'NB_REPET': self.repet}
        print(self.params)
        
        params_str = "{"
        for k in self.params.keys():
                params_str += f"'{k}': {self.params[k]}, "
        params_str += '}'
        
        with open(self.tmp_launch_file_path, "w", encoding="utf8") as F:
                F.write(params_str)

        subprocess.run(self.terminal_cmd)

    def RunFree(self):
        pass

    def WorkingDistChanged(self, x):
        self.workDist = x
    
    def ZposChanged(self, z, n):
        print(n, z, self.zPos)
        if z == 0:
            print('a')
            for i in range(n, len(self.posWidgets)):
                self.posWidgets[i].setValue(0)
                self.posWidgets[i].setMinimum(0)
        else:
            print('b')
            if n >= 1:
                prev_z_pos = self.zPos[n-1]
                if z <= prev_z_pos:
                    z = prev_z_pos+1
                    self.posWidgets[n].setValue(z)
                    self.posWidgets[n].setMinimum(0)
                
        self.zPos[n] = z

    def RepetChanged(self, r):
        self.repet = r
        
    def RotStepChanged(self, r):
        self.rotStep = r
        
    def Center(self):
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

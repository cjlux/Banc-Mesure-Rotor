#
# widget QTabWidget: création d'onglets dans la fenêtre principale
#
import sys, json
sys.path.insert(0, sys.path[0].replace('PyQT5',''))
#print(sys.path)

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget,
                             QTabWidget, QVBoxLayout, QHBoxLayout, QDesktopWidget,
                             QDoubleSpinBox, QSpinBox, QLabel, QGridLayout, QPlainTextEdit,
                             QSizePolicy)

from PyQt5.QtGui import QIcon, QTextCursor, QFont
from PyQt5.QtCore import QCoreApplication, QProcess
import subprocess
from ROTOR_config import StepperMotor, Zaxis, Param

class MyApp(QMainWindow):

    NB_MAX_ZPOS = 10
    
    def __init__(self):
        QMainWindow.__init__(self)

        self.tab1 = None
        self.tab2 = None
        self.tab3 = None
        self.tab4 = None
        self.tab5 = None
        
        self.display = None     # the testedit zone to display the ouput of the running command        
        self.process = None     #  QProcess object for external app
        
        self.workDist = 1
        self.zPos     = []      # The list of the Z positions
        self.rotStep  = 1.2     # the step of the ROTOR rotation 
        self.repet    = 1       # number of repetition of the same measurement run
        
        self.duration = 10      # duration [s] of the free run
        self.sampling = 0.1     # sampling time when running free
        self.SENSOR_NB_SAMPLE  = Param['SENSOR_NB_SAMPLE']
        self.SENSOR_GAIN       = Param['SENSOR_GAIN']
        self.SENSOR_READ_DELAY = Param['SENSOR_READ_DELAY']

        self.platform = subprocess.getoutput('uname -a').split()[1]
        print("Platform: ", self.platform)

        self.tmp_launch_file_path = "/tmp/ROTOR_LAUNCH.txt"

        if self.platform != 'raspberrypi':
            print("ERROR:you must use a Rasberry Pi platform !!!")
#            sys.exit()
        self.terminal_cmd = ["lxterminal", "--geometry=200x30", "--command", 
        "/usr/bin/bash -c 'source /home/rotor/rotor/bin/activate && cd /home/rotor/Banc-Mesure-Rotor/ && python ROTOR_bench/strike.py; read'"]

        self.plotROTOR_cmd = ["lxterminal", "--command",     
        "/usr/bin/bash -c 'source /home/rotor/rotor/bin/activate && cd /home/rotor/Banc-Mesure-Rotor/ && python ROTOR_bench/Processing/plot_ROTOR.py'"]
        
        self.plotFREE_cmd = ["lxterminal", "--command",     
        "/usr/bin/bash -c 'source /home/rotor/rotor/bin/activate && cd /home/rotor/Banc-Mesure-Rotor/ && python ROTOR_bench/Processing/plot_FREE.py'"]
        
        self.terminal_cmd2 = "source $HOME/rotor/bin/activate && cd $HOME/Banc-Mesure-Rotor/ && python ROTOR_bench/strike.py"

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
        self.tab4 = QWidget(parent=self)
        self.setCentralWidget(self.tabs) 

        # Add 3 tabs:
        self.tabs.addTab(self.tab1,"ROTOR bench")
        self.tabs.addTab(self.tab2,"Free recording")
        self.tabs.addTab(self.tab3,"Running display")
        self.tabs.addTab(self.tab4,"Process data files")

        # Fill in the tabs:
        self.__InitTab1()
        self.__InitTab2()
        self.__InitTab3()
        self.__InitTab4()

    def __InitTab1(self):
        ''' To fill in the RunBench tab'''

        VL = QVBoxLayout()
        self.tab1.setLayout(VL)
        
        g = QGridLayout()
        h = QHBoxLayout()
        h.addLayout(g)
        h.addStretch()
        VL.addLayout(h)
        VL.addStretch()

        g.setColumnMinimumWidth(1, 250)
        g.setColumnMinimumWidth(2, 150)
        g.setColumnMinimumWidth(3, 400)
        g.setColumnMinimumWidth(4, 100)
        
        w = QLabel("Working distance ", parent=self)
        sb = QSpinBox(parent=self)
        sb.setValue(1)
        sb.setMinimum(0)
        sb.setSingleStep(1)
        sb.setSuffix(" mm")
        sb.valueChanged.connect(self.WorkingDistChanged) 
        b = QPushButton('RUN bench', parent=self)
        b.clicked.connect(self.RunBench)
        g.addWidget(w, 1, 1)
        g.addWidget(sb, 1, 2)
        g.addWidget(b, 1, 4)
        
        w = QLabel("Rotation step angle ", parent=self)
        sb = QDoubleSpinBox(parent=self)
        sb.setValue(1.2)
        sb.setRange(1.2, 360)
        sb.setSingleStep(1.2)
        sb.setSuffix(" °")
        sb.valueChanged.connect(self.RotStepChanged)
        g.addWidget(w,  2, 1)
        g.addWidget(sb, 2, 2)

        self.posWidgets = []
        for i in range(self.NB_MAX_ZPOS):
            w = QLabel(f"Position #{i+1:2d}:", parent=self)
            sb = QSpinBox(parent=self)
            self.posWidgets.append(sb)
            sb.setValue(0)
            sb.setRange(0, 130)
            sb.setSingleStep(1)
            sb.setSuffix(" mm")
            sb.valueChanged.connect(lambda x, n=i: self.ZposChanged(n, x))
            g.addWidget(w,  i+5, 1)
            g.addWidget(sb, i+5, 2)

        w = QLabel("Number of repetition: ", parent=self)
        sb = QSpinBox(parent=self)
        sb.setValue(1)
        sb.setRange(1, 100)
        sb.setSingleStep(1)
        sb.valueChanged.connect(self.RepetChanged)
        g.addWidget(w, self.NB_MAX_ZPOS+7, 1)
        g.addWidget(sb, self.NB_MAX_ZPOS+7, 2)

    def __InitTab2(self):
        ''' To fill the "Run Free" tab'''
        
        VL = QVBoxLayout()
        self.tab2.setLayout(VL)
        
        g = QGridLayout()
        h = QHBoxLayout()
        h.addLayout(g)
        h.addStretch()
        VL.addLayout(h)
        VL.addStretch()

        g.setColumnMinimumWidth(1, 250)
        g.setColumnMinimumWidth(2, 150)
        g.setColumnMinimumWidth(3, 400)
        g.setColumnMinimumWidth(4, 100)

        w = QLabel("Free run duration ", parent=self)
        sb = QSpinBox(parent=self)
        sb.setValue(self.duration)
        sb.setMinimum(0)
        sb.setSingleStep(1)
        sb.setSuffix(" s")
        sb.valueChanged.connect(self.DurationChanged) 
        b = QPushButton('RUN free', parent=self)
        b.clicked.connect(self.RunFree)
        g.addWidget(w, 1, 1)
        g.addWidget(sb, 1, 2)
        g.addWidget(b, 1, 4)
        
        w = QLabel("Sampling time ", parent=self)
        self.sampling_spinbox = QDoubleSpinBox(parent=self)
        sb = self.sampling_spinbox
        sb.setValue(self.SENSOR_READ_DELAY)
        sb.setMinimum(0.1)
        sb.setSingleStep(0.1)
        sb.setSuffix(" s")
        sb.valueChanged.connect(self.SamplingChanged) 
        g.addWidget(w, 2, 1)
        g.addWidget(sb, 2, 2)
        
        w = QLabel("SENSOR_NB_SAMPLE ", parent=self)
        sb = QSpinBox(parent=self)
        sb.setValue(self.SENSOR_NB_SAMPLE)
        sb.setMinimum(1)
        sb.setSingleStep(1)
        sb.valueChanged.connect(self.SAMPLE_Changed) 
        g.addWidget(w, 3, 1)
        g.addWidget(sb, 3, 2)
        
        w = QLabel("SENSOR_GAIN   ", parent=self)
        sb = QSpinBox(parent=self)
        sb.setValue(self.SENSOR_GAIN)
        sb.setMinimum(1)
        sb.setSingleStep(1)
        sb.valueChanged.connect(self.GAIN_Changed) 
        g.addWidget(w, 4,1)
        g.addWidget(sb, 4, 2)
        
        w = QLabel("SENSOR_READ_DELAY ", parent=self)
        sb = QDoubleSpinBox(parent=self)
        sb.setValue(self.SENSOR_READ_DELAY)
        sb.setMinimum(0.1)
        sb.setSingleStep(0.1)
        sb.valueChanged.connect(self.DELAY_Changed) 
        g.addWidget(w, 5,1)
        g.addWidget(sb, 5, 2)
        
        w = QLabel("Number of repetition: ", parent=self)
        sb = QSpinBox(parent=self)
        sb.setValue(1)
        sb.setRange(1, 100)
        sb.setSingleStep(1)
        sb.valueChanged.connect(self.RepetChanged)
        g.addWidget(w, 6, 1)
        g.addWidget(sb, 6, 2)
        
    def __InitTab3(self):
        ''' To display the output of "Run Bench" or "Run Free" process'''
        
        VL = QVBoxLayout()
        self.tab3.setLayout(VL)
        self.display = QPlainTextEdit()
        self.display.setReadOnly(True)
        self.display.setMinimumSize(650,400)
        self.display.setFont(QFont('Courier New', 8))
        self.display.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.display.setFixedWidth(900)
        self.display.insertPlainText("Hello ")
        VL.addWidget(self.display)
        
    def __InitTab4(self):
        
        VL = QVBoxLayout()
        self.tab4.setLayout(VL)
        b = QPushButton('Plot ROTOR data', parent=self)
        b.clicked.connect(self.PlotROTOR)
        VL.addWidget(b)
        b = QPushButton('Plot FREE data', parent=self)
        b.clicked.connect(self.PlotFREE)
        VL.addWidget(b)
        VL.addStretch()
        
    def PlotROTOR(self):
        subprocess.run(self.plotROTOR_cmd)
        
    def PlotFREE(self):
        subprocess.run(self.plotFREE_cmd)
        
    def AppendSerialText(self, appendText, color):
        self.display.moveCursor(QTextCursor.MoveOperaton.End)
        self.display.setFont(QFont('Courier New', 8))
        self.display.setTextColor(color)
        self.display.insertPlainText(appendText)
        self.display.moveCursor(QTextCursor.MoveOperation.End)        

    def dataReady(self):
        cursor = self.disply.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(str(self.process.readAll()))
        self.display.ensureCursorVisible()        

    def RunBench(self):
        zPos = [ z for z in self.zPos if z > 0]
        self.params = {'MODE': 'RunBench',
                       'WORK_DIST': self.workDist,
                       'ROT_STEP_DEG': self.rotStep,
                       'Z_POS_MM': zPos,
                       'NB_REPET': self.repet}
        
        with open(self.tmp_launch_file_path, "w", encoding="utf8") as F:
            F.write(json.dumps(self.params))

        '''# QProcess object for external app
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.stateChanged.connect(self.handle_state)
        # QProcess emits `readyRead` when there is data to be read
        #self.process.finished.connect(self.process_finished)
        self.process.readyRead.connect(self.dataReady)
        self.process.start(self.terminal_cmd2, [])'''
        subprocess.run(self.terminal_cmd)
    
    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")
        
    def message(self, s):
        self.display.appendPlainText(s)        
    
    def RunFree(self):
        self.params = {'MODE': 'RunFree',
                       'DURATION': self.duration,
                       'SAMPLING': self.sampling,
                       'SENSOR_NB_SAMPLE': self.SENSOR_NB_SAMPLE,
                       'SENSOR_GAIN': self.SENSOR_GAIN,
                       'SENSOR_READ_DELAY':self.SENSOR_READ_DELAY,
                       'NB_REPET': self.repet
                       }
        
        with open(self.tmp_launch_file_path, "w", encoding="utf8") as F:
            F.write(json.dumps(self.params))

        subprocess.run(self.terminal_cmd)

    def WorkingDistChanged(self, x):
        self.workDist = x
        
        self.message(str(x))
            
    def ZposChanged(self, n, z):
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

    def RepetChanged(self, x):
        self.repet = x
        
    def RotStepChanged(self, x):
        self.rotStep = x
        
    def DurationChanged(self, x):
        self.duration = x
        
    def SamplingChanged(self, x):
        if x < self.SENSOR_READ_DELAY: 
                x = self.SENSOR_READ_DELAY
        self.sampling = x     
        self.sampling_spinbox.setValue(x)   

    def SAMPLE_Changed(self, x):
        self.SENSOR_NB_SAMPLE = x        

    def GAIN_Changed(self, x):
        self.SENSOR_GAIN = x        

    def DELAY_Changed(self, x):
        self.SENSOR_READ_DELAY = x   

    def Center(self):
        desktop = QApplication.desktop()
        n = desktop.screenNumber(self.cursor().pos())
        screen_center = desktop.screenGeometry(n).center()
        geo_window = self.frameGeometry()
        geo_window.moveCenter(screen_center)
        self.move(geo_window.topLeft())
        
if __name__ == '__main__':
    
    ps_au = subprocess.getoutput("ps au")
    print(ps_au)
    if ps_au.count('ROTOR_bench/PyQT5/main.py') >= 2:
        print("process <python3 .../ROTOR_bench/PyQT5/main.py> already running, tchao !")
    else:
        app = QApplication(sys.argv) # instanciation classe QApplication
        my_app = MyApp()             # instanciation classe MyApp
        app.exec_()                  # lancement boucle événementielle Qt

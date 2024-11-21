#
# widget QTabWidget: création d'onglets dans la fenêtre principale
#
import sys, json, os
sys.path.insert(0, sys.path[0].replace('PyQT5',''))
#print(sys.path)

import numpy as np

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget,
                             QTabWidget, QVBoxLayout, QHBoxLayout, QDesktopWidget,
                             QDoubleSpinBox, QSpinBox, QLabel, QGridLayout, QPlainTextEdit,
                             QSizePolicy, QCheckBox, QMessageBox, QComboBox)

from PyQt5.QtGui import QIcon, QTextCursor, QFont
from PyQt5.QtCore import QCoreApplication, QProcess, QDate, QTime, QSize
import subprocess
from ROTOR_config import StepperMotor, Zaxis, Param

from listFiles import ListFile

class MyApp(QMainWindow):

    NB_MAX_ZPOS = 10
    TXT_dir = '../TXT'
    
    def __init__(self):
        QMainWindow.__init__(self)

        self.tabs = None         # The main QTabWiget
        self.tab1 = QWidget()    # The tab to start the rotor bench
        self.tab2 = QWidget()    # The tab to run free recording
        self.tab3 = QWidget()    # the tab to run data plotting
        self.tab4 = QWidget()    # the tab to ...
        self.tab5 = QWidget()    # The Tools tab
        
        # usefull widgets:
        self.display    = None   # the textedit zone to display the ouput of the running command        
        self.process    = None   # QProcess object for external app
        self.list_files = None   # ListFile object : the list of *.txt files in ./TXT dir
        self.ZPos_label = None   # QLabel object to display the ZPos list
        
        self.first_ZPos = None   # QSpinBox for the first Z position
        self.ZPos_step  = None   # QSpinbox for the Z poistion step 
        self.ZPos_nb    = None   # number of Z positions
        
        self.dict_plot_btn = {}
        
        self.workDist = 1
        self.ZPos     = []       # The list of the Z positions
        self.rotStep  = 1.2      # the step of the ROTOR rotation 
        self.repet    = 1        # number of repetition of the same measurement run
        self.XYZ      = {'X': 1, 'Y': 1, 'Z':1} # Wether to plot or no the X,Y,Z component of the magn. field
        
        self.list_TXT_file = []
        self.selected_file = ""
        
        self.duration = 10       # duration [s] of the free run
        self.sampling = 0.7      # sampling time when running free
        self.SENSOR_NB_SAMPLE  = Param['SENSOR_NB_SAMPLE']
        self.SENSOR_GAIN       = Param['SENSOR_GAIN']
        self.SENSOR_READ_DELAY = Param['SENSOR_READ_DELAY']

        self.platform = subprocess.getoutput('uname -a').split()[1]
        print("Platform: ", self.platform)

        self.tmp_launch_file_path = "/tmp/ROTOR_LAUNCH.txt"

        if self.platform != 'raspberrypi':
            print("ERROR:you must use a Rasberry Pi platform !!!")
#            sys.exit()
        self.terminal_cmd = ["lxterminal", "--geometry=250x30", "--command", 
        "/usr/bin/bash -c 'source /home/rotor/rotor/bin/activate && cd /home/rotor/Banc-Mesure-Rotor/ && python ROTOR_bench/strike.py; read '"]

        self.plotROTOR_cmd = ["lxterminal", "--geometry=60x10", "--command",     
        "/usr/bin/bash -c 'source /home/rotor/rotor/bin/activate && cd /home/rotor/Banc-Mesure-Rotor/ && python ROTOR_bench/Processing/plot_ROTOR.py "]

        self.plotROTOR_CMAP_cmd = ["lxterminal", "--geometry=60x10", "--command",     
        "/usr/bin/bash -c 'source /home/rotor/rotor/bin/activate && cd /home/rotor/Banc-Mesure-Rotor/ && python ROTOR_bench/Processing/plot_ROTOR_CMAP.py "]
        
        self.plotFREE_cmd = ["lxterminal", "--geometry=60x10", "--command",     
        "/usr/bin/bash -c 'source /home/rotor/rotor/bin/activate && cd /home/rotor/Banc-Mesure-Rotor/ && python ROTOR_bench/Processing/plot_FREE.py "]

        self.terminal_cmd2 = "source $HOME/rotor/bin/activate && cd $HOME/Banc-Mesure-Rotor/ && python ROTOR_bench/strike.py"

        self.InitUI()
        self.show()            
    
    def InitUI(self):
                
        self.resize(900, 700) 
        self.Center()       
        self.setWindowTitle('ROTOR mesurement bench')
 
        # Create the QTabWidget object and empty tabs:
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Add all the tabs:
        self.tabs.addTab(self.tab1,"ROTOR bench")
        self.tabs.addTab(self.tab2,"Free recording")
        self.tabs.addTab(self.tab3,"Plot data files")
        self.tabs.addTab(self.tab4,"Display...")
        self.tabs.addTab(self.tab5,"Tools...")
        
        # Fill in the tabs:
        self.__InitTab1()
        self.__InitTab2()
        self.__InitTab3()
        self.__InitTab4()
        self.__InitTab5()

        # Select tab [rotor bENCH]:
        self.tabs.setCurrentIndex(0)        
        

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

        g.setColumnMinimumWidth(1, 150)
        g.setColumnMinimumWidth(2, 150)
        g.setColumnMinimumWidth(3, 100)
        g.setColumnMinimumWidth(4, 200)
        g.setColumnMinimumWidth(5, 200)
        
        w = QLabel("Working distance ")
        sb = QSpinBox()
        sb.setValue(1)
        sb.setMinimum(0)
        sb.setSingleStep(1)
        sb.setSuffix(" mm")
        sb.valueChanged.connect(self.WorkingDistChanged)
        sb.setMinimumHeight(40)
        
        b1 = QPushButton(icon=QIcon("./PyQT5/icons/Icon_RunByAngle.png"),
                        text='RUN by Angle')
        b1.setMinimumHeight(110)
        b1.setIconSize(QSize(100,100))
        b1.clicked.connect(lambda s, mode='ByAngle': self.RunBench(s, mode))

        b2 = QPushButton(icon=QIcon("./PyQT5/icons/Icon_RunByZPos.png"),
                        text='RUN by Zpos')
        b2.setMinimumHeight(110)
        b2.setIconSize(QSize(100,100))
        b2.clicked.connect(lambda s, mode='ByZPos': self.RunBench(s, mode))
        
        g.addWidget(w,  1, 1)
        g.addWidget(sb, 1, 2)
        g.addWidget(b1, 1, 4)
        g.addWidget(b2, 1, 5)
        
        w = QLabel("Rotation step angle ")
        cb = QComboBox()
        L2 = [f'{n*0.6:.2f}' for n in range(1,301) if divmod(360, 0.6*n)[1] <= 0.001]
        cb.addItems(L2)
        cb.activated[str].connect(self.RotStepChanged)
        cb.setMinimumHeight(40)
        g.addWidget(w,  3, 1)
        g.addWidget(cb, 3, 2)
        self.RotStepChanged(L2[0])

        g.addWidget(QLabel(""), 4, 1)
        g.addWidget(QLabel(""), 5, 1)

        w = QLabel(f"First ZPos [mm]")
        w.setToolTip('Choose a step angle...')
        self.first_ZPos = QSpinBox()
        sb = self.first_ZPos
        sb.setToolTip('Choose a step angle...')
        sb.setValue(10)
        sb.setRange(0, 130)
        sb.setSingleStep(1)
        sb.valueChanged.connect(self.ZposEditingFinished)
        sb.setMinimumHeight(40)
        g.addWidget(w,  6, 1)
        g.addWidget(sb, 6, 2)
        
        w = QLabel(f"ZPos step [mm]")
        w.setToolTip('The step between each Z position...')
        self.ZPos_step = QSpinBox()
        sb = self.ZPos_step
        sb.setToolTip('The step between each Z position...')
        sb.setValue(10)
        sb.setRange(1, 130)
        sb.setSingleStep(1)
        sb.valueChanged.connect(self.ZposEditingFinished)
        sb.setMinimumHeight(40)
        g.addWidget(w,  7, 1)
        g.addWidget(sb, 7, 2)
        
        w = QLabel(f"Nb ZPos [mm]")
        w.setToolTip('The total number of Z positions...')
        self.ZPos_nb = QSpinBox()
        sb = self.ZPos_nb
        sb.setToolTip('The total number of Z positions...')
        sb.setValue(1)
        sb.setRange(1, 20)
        sb.setSingleStep(1)
        sb.valueChanged.connect(self.ZposEditingFinished)
        sb.setMinimumHeight(40)
        g.addWidget(w,  8, 1)
        g.addWidget(sb, 8, 2)

        g.addWidget(QLabel(""), 9, 1)
        g.addWidget(QLabel(""), 10, 1)
        
        w = QLabel("Number of repetition: ")
        sb = QSpinBox()
        sb.setValue(1)
        sb.setRange(1, 100)
        sb.setSingleStep(1)
        sb.valueChanged.connect(self.RepetChanged)
        sb.setMinimumHeight(40)
        g.addWidget(w, 11, 1)
        g.addWidget(sb, 11, 2)
                
        self.ZPos_label = QLabel("ZPos: ")
        w = self.ZPos_label
        g.addWidget(w, 7, 4) 
        
        self.ZposEditingFinished()

    def RefreshZPosList(self):
        pass
    
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
        g.setColumnMinimumWidth(4, 150)

        w = QLabel("Free run duration ")
        sb = QSpinBox()
        sb.setValue(self.duration)
        sb.setMinimum(1)
        sb.setMaximum(600)
        sb.setSingleStep(1)
        sb.setSuffix(" s")
        sb.valueChanged.connect(self.DurationChanged)
        sb.setMinimumHeight(40)
        b = QPushButton('RUN free')
        b.setMinimumHeight(110)
        b.clicked.connect(self.RunFree)
        g.addWidget(w, 1, 1)
        g.addWidget(sb, 1, 2)
        g.addWidget(b, 1, 4)
        
        w = QLabel("Sampling time ")
        self.sampling_spinbox = QDoubleSpinBox()
        sb = self.sampling_spinbox
        sb.setValue(self.SENSOR_READ_DELAY)
        sb.setMinimum(0.1)
        sb.setSingleStep(0.1)
        sb.setSuffix(" s")
        sb.valueChanged.connect(self.SamplingChanged)
        sb.setMinimumHeight(40)
        g.addWidget(w, 2, 1)
        g.addWidget(sb, 2, 2)
        
        w = QLabel("SENSOR_NB_SAMPLE ")
        sb = QSpinBox()
        sb.setValue(self.SENSOR_NB_SAMPLE)
        sb.setMinimum(1)
        sb.setSingleStep(1)
        sb.valueChanged.connect(self.SAMPLE_Changed)
        sb.setMinimumHeight(40)
        g.addWidget(w, 3, 1)
        g.addWidget(sb, 3, 2)
        
        w = QLabel("SENSOR_GAIN   ")
        sb = QSpinBox()
        sb.setValue(self.SENSOR_GAIN)
        sb.setMinimum(1)
        sb.setSingleStep(1)
        sb.valueChanged.connect(self.GAIN_Changed)
        sb.setMinimumHeight(40)
        g.addWidget(w, 4,1)
        g.addWidget(sb, 4, 2)
        
        w = QLabel("SENSOR_READ_DELAY ")
        sb = QDoubleSpinBox()
        sb.setValue(self.SENSOR_READ_DELAY)
        sb.setMinimum(0.1)
        sb.setSingleStep(0.1)
        sb.valueChanged.connect(self.DELAY_Changed)
        sb.setMinimumHeight(40)
        g.addWidget(w, 5,1)
        g.addWidget(sb, 5, 2)
        
        w = QLabel("Number of repetition: ")
        sb = QSpinBox()
        sb.setValue(1)
        sb.setRange(1, 100)
        sb.setSingleStep(1)
        sb.valueChanged.connect(self.RepetChanged)
        sb.setMinimumHeight(40)
        g.addWidget(w, 6, 1)
        g.addWidget(sb, 6, 2)
                

    def __InitTab3(self):
        '''
            To fill in the "Plot data file" tab
        '''
        
        V = QVBoxLayout()
        self.tab3.setLayout(V)
        
        H = QHBoxLayout()

        b = QPushButton(icon=QIcon("./PyQT5/icons/refresh.png"),
                        text='Refresh\nList')
        b.setMinimumHeight(50)
        b.setMinimumWidth(50)
        b.clicked.connect(self.refresh_TXT_list)
        H.addWidget(b)
        H.addStretch()

        self.dict_plot_btn['ROTOR'] = []
        self.dict_plot_btn['FREE']  = []

        for label, callback in zip(('Plot ROTOR data', 'Plot ROTOR PSD', 'ColorMap ROTOR data', 'Plot FREE data'),
                                 (self.PlotROTOR, None, self.CmapROTOR, (self.PlotFREE))):
            b = QPushButton(label)
            b.setMinimumHeight(50)
            b.setMinimumWidth(150)
            if label == 'Plot ROTOR PSD':
                b.clicked.connect(lambda: self.PlotROTOR(fft=True))
            else:
                b.clicked.connect(callback)
            H.addWidget(b)
            if 'ROTOR' in label : 
                self.dict_plot_btn['ROTOR'].append(b)
            else:
                self.dict_plot_btn['FREE'].append(b)
            b.setEnabled(False)    
            
        H.addStretch()
        
        h = QHBoxLayout()
        for lab in ("X", "Y", "Z"):
            c = QCheckBox(lab)
            c.toggle()
            c.stateChanged.connect(lambda state, label=lab: self.set_XYZ(state, label))
            h.addWidget(c)
        
        H.addLayout(h)
        
        V.addLayout(H)
        
        self.refresh_TXT_list()
        self.list_files = ListFile(self.list_TXT_file, parent=self)
        V.addWidget(self.list_files)
        
        V.addStretch()
        
    def refresh_TXT_list(self):
        '''
            To updat the list of the *.txt files in the TXT dirextory
        '''
        self.list_TXT_file = [f for f in os.listdir(self.TXT_dir)  \
            if f.lower().endswith('.txt') and (f.startswith('ROTOR') or f.startswith('FREE'))]    
        self.list_TXT_file.sort(reverse=True)
        
        if self.list_files: self.list_files.refresh(self.list_TXT_file)
        
        for key in self.dict_plot_btn.keys():
            for btn in self.dict_plot_btn[key]:
                    btn.setEnabled(False)
    
    def select_file(self, file):
        self.selected_file = file
        
        if 'ROTOR' in file:
            tag = 'ROTOR'
        elif 'FREE' in file:
            tag = 'FREE'
            
        for key in self.dict_plot_btn.keys():
            if key == tag:
                for btn in self.dict_plot_btn[key]:
                    btn.setEnabled(True)
            else:
                for btn in self.dict_plot_btn[key]:
                    btn.setEnabled(False)
                
    def set_XYZ(self, state, lab):
        self.XYZ[lab] = state//2
        print(f'{self.XYZ=}')

    def __InitTab4(self):
        ''' To display the output of "Run Bench" or "Run Free" process'''
        
        VL = QVBoxLayout()
        self.tab4.setLayout(VL)
        self.display = QPlainTextEdit()
        self.display.setReadOnly(True)
        self.display.setMinimumSize(650,400)
        self.display.setFont(QFont('Courier New', 8))
        self.display.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.display.setFixedWidth(900)
        self.display.insertPlainText("Hello ")
        VL.addWidget(self.display)
        
    def __InitTab5(self):
        ''' Tools'''
        VL = QVBoxLayout()
        self.tab5.setLayout(VL)
        b = QPushButton('Release all motors')
        b.setMinimumHeight(40)
        b.clicked.connect(self.RunReleaseMotors)
        VL.addWidget(b)
        VL.addStretch()
        
    def PlotROTOR(self, fft=False):
                
        xyz = f"{self.XYZ['X']}{self.XYZ['Y']}{self.XYZ['Z']}"
        cmd = self.plotROTOR_cmd.copy()
        if fft: cmd[-1] += " --fft"
        cmd[-1] += f" --file ./TXT/{self.selected_file}"
        cmd[-1] += f" --xyz {xyz}; read'"
        print(f'{self.plotROTOR_cmd=}\n{cmd=}')
        ret = subprocess.run(cmd)
        if ret.returncode in (1,2) : self.ErrorPopup(ret.returncode)        

        
    def CmapROTOR(self):
        
        xyz = f"{self.XYZ['X']}{self.XYZ['Y']}{self.XYZ['Z']}"
        cmd = self.plotROTOR_CMAP_cmd.copy()
        cmd[-1] += f" --file ./TXT/{self.selected_file}"
        cmd[-1] += f" --xyz {xyz}; read'"
        print(f'{self.plotROTOR_CMAP_cmd=}\n{cmd=}')
        ret = subprocess.run(cmd, capture_output=True)
        if ret.returncode in (1,2) : self.ErrorPopup(ret.returncode)

        
    def ErrorPopup(self, ret_code):
        message = [None, 
                   'An unknown error occured....',
                   'Cannot draw a Color Map with just one Z_pos = 0, sorry....']
        QMessageBox.warning(self, 'Warning', f'{message[ret_code]}\n when using file: {self.selected_file}')


    def PlotFREE(self):

        xyz = f"{self.XYZ['X']}{self.XYZ['Y']}{self.XYZ['Z']}"
        cmd = self.plotFREE_cmd.copy()
        cmd[-1] += f" --file ./TXT/{self.selected_file}"
        cmd[-1] += f" --xyz {xyz}; read'"
        print(f'{self.plotFREE_cmd=}\n{cmd=}')
        ret = subprocess.run(cmd)
        if ret.returncode in (1,2) : self.ErrorPopup(ret.returncode)    

        
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

    def RunBench(self, state, mode):
        print(f'{self.ZPos=}')
        zPos = [ z for z in self.ZPos if z >= 0]
        zPos = list(set(zPos)) # don't dupplicate Z position
        if zPos[0] == 0 and self.ZPos[0] != 0: zPos.remove(0)
        # JLC: bug the set modifies the order!!!!
        zPos.sort()   # !!!!

        self.params = {'MODE': mode,
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

        print(f'mode: <{mode}>')
        subprocess.run(self.terminal_cmd)

    def RunReleaseMotors(self):
        '''To release the holding torque of all motors'''
        self.params = {'MODE': 'ReleaseMotors',
                       'WORK_DIST': 0,
                       'ROT_STEP_DEG': 0,
                       'Z_POS_MM': [],
                       'NB_REPET': 0}
        
        with open(self.tmp_launch_file_path, "w", encoding="utf8") as F:
            F.write(json.dumps(self.params))
            
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
        self.params = {'MODE': 'Free',
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


    def ZposEditingFinished(self):
                
        first_ZPos = self.first_ZPos.value()
        ZPos_step  = self.ZPos_step.value()
        Zpos_nb    = self.ZPos_nb.value()
        
        self.ZPos = [first_ZPos + n*ZPos_step for n in range(Zpos_nb)]
        
        self.ZPos_label.setText('ZPos: ' + ', '.join([str(z) for z in self.ZPos]))
        
    def RepetChanged(self, x):
        self.repet = x

    def RotStepChanged(self, x):
        self.rotStep = float(x)
        print(f'{self.rotStep=} °')

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
        if x > self.sampling:
            self.sampling_spinbox.setValue(x)

    def CheckZpos(self):
        zPos = self.ZPos
        
        # zPos must be strictly incresing:
        for i in range(1, len(zPos)):
            if zPos[i] > 0 and zPos[i] <= zPos[i-1]:
                return -1
        

    def Center(self):
        desktop = QApplication.desktop()
        n = desktop.screenNumber(self.cursor().pos())
        screen_center = desktop.screenGeometry(n).center()
        geo_window = self.frameGeometry()
        geo_window.moveCenter(screen_center)
        self.move(geo_window.topLeft())
        
if __name__ == '__main__':

    ps_axu = subprocess.getoutput("ps axu")
    # Debug: print(ps_au)
    ps_axu = "debug"
    if ps_axu.count('ROTOR_bench/PyQT5/main.py') >= 2:
        print("process <python3 .../ROTOR_bench/PyQT5/main.pyy> already running, tchao !")
    else:
        target_dir = os.path.dirname(os.path.dirname(__file__))
        os.chdir(target_dir)
        app = QApplication(sys.argv) # instanciation classe QApplication
        my_app = MyApp()             # instanciation classe MyApp
        app.exec_()                  # lancement boucle événementielle Qt

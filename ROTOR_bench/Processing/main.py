import os, sys
from pathlib import Path
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QFileDialog,
    QTabWidget, QMainWindow, QLabel, QCheckBox, QScrollArea, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from tools import read_file_ROTOR, read_file_FREE
from magnetic_canvas import MagneticPlotCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.XYZ                  = {'X': 1, 'Y': 1, 'Z':1} # Wether to plot the X,Y,Z components
        self.dict_plot_btn        = {}
        self.ROTOR_B_data_dir     = None    # the directory containing the ROTOR data files
        self.ROTOR_L_data_dir     = None    # the directory containing the LILLE ROTOR data files
        self.ROTOR_B_txt_file     = None    # the selected ROTOR_B file to plot
        self.ROTOR_L_txt_file     = None    # the selected ROTOR_L file to plot
        self.curr_plt_func        = None    # The current active plot function
        self.ROTOR_B_magn_field   = None    # The ROTOR_B magnetic field
        self.angle_values         = None    # The angles of the ROTOR data file  
        self.time_values          = None    # The time values of the FREE data file
        self.list_pos             = None    # The list of the Z positions found in the ROTOR data file
        self.plot_fft             = False   # whether the plos is a DSP or not
        
        self.file_tab             = None    # The tab to choose a directory and list .txt files
        self.plot_tab             = None    # the tab to draw the plots"
        self.plot_txt_csv         = None    # The tab to superpose a .txt and a .csv plots
        
        self.btn_free_stat        = None    # The button to display the statistics in the FREE data plot  
        
        self.setWindowTitle("ROTOR bench data plot")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.__init_tab_ChoseFolder()
        self.__init_tab_Visualisation()
        self.__init_tab_CSV_TXT_plot()
        
        # Select tab [rotor bENCH]:
        self.tabs.setCurrentIndex(0)        
        
        
    def __init_tab_ChoseFolder(self):
        '''
            Tab_1 : Choose Directory
        '''
        self.file_tab = QWidget()
        self.tabs.addTab(self.file_tab, "Choose Directory")
        
        HBox = QHBoxLayout()
        self.file_tab.setLayout(HBox)
        
        V = QVBoxLayout()
        btn = QPushButton("ROTOR data directory")
        btn.clicked.connect(self.select_ROTOR_B_dir)            
        V.addWidget(btn)
        scroll_area = QScrollArea()
        self.ROTOR_B_file_list_widget = QGroupBox("ROTOR *.TXT files")
        self.ROTOR_B_file_list_layout = QVBoxLayout()
        self.ROTOR_B_file_list_widget.setLayout(self.ROTOR_B_file_list_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.ROTOR_B_file_list_widget)
        V.addWidget(scroll_area)
        
        HBox.addLayout(V)
        
        self.LILLE_choose_dir = QVBoxLayout()
        V = self.LILLE_choose_dir
        self.button_LILLE_data_dir = QPushButton("LILLE rotor bench folder")
        btn = self.button_LILLE_data_dir
        btn.clicked.connect(self.select_ROTOR_L_dir)            
        V.addWidget(btn)
        scroll_area = QScrollArea()
        self.ROTOR_L_file_list_widget = QGroupBox("LILLE rotor *.CSV files")
        self.ROTOR_L_file_list_layout = QVBoxLayout()
        self.ROTOR_L_file_list_widget.setLayout(self.ROTOR_L_file_list_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.ROTOR_L_file_list_widget)
        V.addWidget(scroll_area)

        HBox.addLayout(V)
        
        self.button_LILLE_data_dir.setEnabled(False)
        self.ROTOR_L_file_list_widget.setEnabled(False)
        
    def __init_tab_Visualisation(self):
        '''
        Tab_2: data plots
        '''
        self.plot_tab = QWidget()
        self.tabs.addTab(self.plot_tab, "Data plots")
        
        VBox = QVBoxLayout()
        self.plot_tab.setLayout(VBox)                
        
        H = QHBoxLayout()
        H.addStretch()
        
        self.dict_plot_btn['ROTOR'] = []
        self.dict_plot_btn['FREE'] = []

        labels    = ('Plot ROTOR data', 'Plot ROTOR PSD', 'ColorMap ROTOR data', 'Plot FREE data')
        callbacks = (self.plot_ROTOR, None, None, self.plot_FREE)
        for label, callback in zip(labels, callbacks):
            btn = QPushButton(label)
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(120)
            btn.setCheckable(False)
            if label == 'Plot ROTOR PSD':
                btn.clicked.connect(lambda: self.plot_ROTOR(fft=True))
            elif label == 'ColorMap ROTOR data':
                btn.clicked.connect(lambda: self.plot_ROTOR(colormap=True))
            else:
                btn.clicked.connect(callback)
            H.addWidget(btn)
            if 'ROTOR' in label : 
                self.dict_plot_btn['ROTOR'].append(btn)
            else:
                self.dict_plot_btn['FREE'].append(btn)
            btn.setEnabled(False)    
            
        H.addStretch()
        btn = QCheckBox('display stat')
        btn.setChecked(True)
        btn.setEnabled(False)
        btn.stateChanged.connect(self.plot_FREE)
        self.dict_plot_btn['FREE'].append(btn)
        self.btn_free_stat = btn
        H.addWidget(btn)
        
        for etiq, lab in zip(('X radial', 'Y axial', 'Z tang'), ('X', 'Y', 'Z')):
            btn = QCheckBox(etiq)
            btn.toggle()
            btn.stateChanged.connect(lambda state, label=lab: self.set_XYZ(state, label))
            H.addWidget(btn)
        VBox.addLayout(H)
        self.canvas  = MagneticPlotCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        VBox.addWidget(self.canvas)
        VBox.addWidget(self.toolbar)


    def __init_tab_CSV_TXT_plot(self):
        '''
        Tab_3: superposed plots of a .csv and a .txt files
        '''
        self.plot_tab = QWidget()
        self.tabs.addTab(self.plot_tab, "CSV & TXT plots")        
        
        
    def set_XYZ(self, state, lab):
        self.XYZ[lab] = state//2
        #print(f'{self.XYZ=}')
        if self.curr_plt_func: self.curr_plt_func()
        
    def convert_XYZ_to_tuple(self):
        xyz = (self.XYZ['X'], self.XYZ['Y'], self.XYZ['Z'])
        return xyz

    def activate_plotButtons(self):
        file = self.ROTOR_B_txt_file.name
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
        

    def plot_ROTOR(self, colormap=False, fft=False):
        '''
        To plot the ROTOR data.
        '''
        
        DATA, list_pos = read_file_ROTOR(self.ROTOR_B_txt_file)

        if colormap and len(list_pos) <  2:
            self.ErrorPopup('''The ROTOR data file does not contain enough Z positions to plot a colormap''')
            return
        
        self.plot_fft = fft
        self.list_pos = list_pos
        
        if DATA.shape[1] == 5:
            mode="ByAngle"
            # re-arrange DATA to be an array with lines formated like:
            # "# angle[°]; X1_magn [mT]; Y1_magn [mT]; Z1_magn [mT]; X2_magn [mT]; Y2_magn [mT]; Z2_magn [mT];..."
            # instead of:
            # "# ZPos#; a[°]; X1_magn[mT]; Y1_magn[mT]; Z1_magn[mT]"
            nb_col = 1 + 3 * len(list_pos) #  angle col + (X , Y, Z) * nb_Zpo
            nb_row = int(len(DATA)/len(list_pos))
            newDATA = np.ndarray((nb_row, nb_col), dtype=float)

            # copy angle columngit config pull.rebase false
            newDATA[ :, 0] = DATA[ : nb_row, 1]
            # copy X,Y,Z for all Zpos:
            nb_val = 3 # the 3 components X, Y and Z
            for n in range(len(list_pos)):
                newDATA[ : , 1 + n*nb_val : 1 + (n+1)*nb_val] = DATA[n*nb_row : (n+1)*nb_row, 2:]
            DATA = newDATA
        else:
            mode="ByZPos"
        
        # plot the data
        if colormap:
            self.angle_values, self.ROTOR_B_magn_field = DATA[:, 0], DATA[:, 1:] 
            self.canvas.colormap_magField()
            self.curr_plt_func = self.canvas.colormap_magField
        else:
            # transpose DATA to extract the different variables:
            self.angle_values, self.ROTOR_B_magn_field = DATA.T[0], DATA.T[1:]        
            self.canvas.plot_magField_at_positions()
            self.curr_plt_func = self.canvas.plot_magField_at_positions
            
        return

    
    def plot_FREE(self):
    
        DATA = read_file_FREE(self.ROTOR_B_txt_file)

        # transpose DATA to extract the different variables:
        self.time_values, self.ROTOR_B_magn_field = DATA.T[0], DATA.T[1:]            

        # plot the data
        self.canvas.plot_magField()
        self.curr_plt_func = self.canvas.plot_magField
        return 
        
    def select_ROTOR_B_dir(self):
        data_dir = QFileDialog.getExistingDirectory(self, "Directory for the *.txt ROTOR bench files")
        if data_dir:
            self.ROTOR_B_data_dir = Path(data_dir)
            self.ROTOR_B_file_list_widget.setTitle(f'*.TXT files in <{data_dir}>')
            self.update_ROTOR_B_file_list()

    def select_ROTOR_L_dir(self):
        data_dir = QFileDialog.getExistingDirectory(self, "Directory for the *.CSV LILLE ROTOR bench files")
        if data_dir:
            self.ROTOR_L_data_dir = Path(data_dir)
            self.ROTOR_L_file_list_widget.setTitle(f'*.CSV files in <{data_dir}>')
            self.update_ROTOR_L_file_list()

    def update_ROTOR_B_file_list(self):
        # Vider la liste existante
        for i in reversed(range(self.ROTOR_B_file_list_layout.count())):
            widget = self.ROTOR_B_file_list_layout.itemAt(i).widget()
            if widget and not isinstance(widget, QPushButton):
                widget.setParent(None)

        # Ajouter une checkbox par fichier .txt
        for file_path in sorted(self.ROTOR_B_data_dir.iterdir()):
            if file_path.name.lower().endswith(".txt"):
                checkbox = QRadioButton(file_path.name)
                checkbox.toggled.connect(lambda state, path=file_path: self.process_ROTOR_B_file(path))
                self.ROTOR_B_file_list_layout.addWidget(checkbox)


    def update_ROTOR_L_file_list(self):
        # Vider la liste existante
        for i in reversed(range(self.ROTOR_L_file_list_layout.count())):
            widget = self.ROTOR_L_file_list_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Ajouter une checkbox par fichier .txt
        for file_path in sorted(self.ROTOR_L_data_dir.iterdir()):
            if file_path.name.lower().endswith(".csv"):
                checkbox = QRadioButton(file_path.name)
                checkbox.toggled.connect(lambda state, path=file_path: self.process_ROTOR_L_file(path))
                self.ROTOR_L_file_list_layout.addWidget(checkbox)
    

    def process_ROTOR_L_file(self, filepath):
        pass

    def process_ROTOR_B_file(self, filepath):
        
        self.ROTOR_B_txt_file = Path(filepath)
        #print(f'{self.ROTOR_B_txt_file=}, {filepath=}')
        
        file_name = self.ROTOR_B_txt_file.name
        if file_name.startswith("FREE") or file_name.startswith("ROTOR"):
            self.activate_plotButtons()
            self.button_LILLE_data_dir.setEnabled(True)
            self.ROTOR_L_file_list_widget.setEnabled(True)

            self.tabs.setCurrentIndex(1)
        
            if file_name.startswith("FREE"):
                self.plot_FREE()
            elif file_name.startswith("ROTOR"):
                self.plot_ROTOR()
        else:
            self.ErrorPopup('''File name {<>} does not start with 
                            'ROTOR_...' or 'FREE... or is corrupted''')
        
        return

    def ErrorPopup(self, message):
        QMessageBox.warning(self, 'Error', f'{message}')

        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1300, 900)
    window.show()
    sys.exit(app.exec_())

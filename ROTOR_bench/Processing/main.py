import os, sys
from pathlib import Path
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QFileDialog,
    QTabWidget, QMainWindow, QLabel, QCheckBox, QScrollArea, QGroupBox
)
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from tools import read_file_ROTOR, read_file_FREE
from magnetic_canvas import MagneticPlotCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.XYZ                = {'X': 1, 'Y': 1, 'Z':1} # Wether to plot the X,Y,Z components
        self.dict_plot_btn      = {}
        self.data_dir           = None
        self.selected_file      = None   # the selected file to plot
        self.curr_plt_func      = None   # The current active plot function
        self.ROTOR_magn_field   = None   # The ROTOR magnetic field
        self.angle_values       = None   # The angles of the ROTOR data file  
        self.time_values        = None   # The time values of the FREE data file
        self.list_pos           = None   # The list of the Z positions found in the ROTOR data file
        self.plot_fft           = False  # whether the plos is a DSP or not
        
        self.file_tab           = None   # The tab to choose a directory and list .txt files
        self.plot_tab           = None   # the tab to draw the plots"
        self.plot_txt_csv       = None   # The tab to superpose a .txt and a .csv plots
        
        self.btn_free_stat      = None   # The button to display the statistics in the FREE data plot  
        
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
        VBox = QVBoxLayout()
        self.file_tab.setLayout(VBox)
        HBox = QHBoxLayout()
        self.folder_label = QLabel("No folder selected.")
        self.select_button = QPushButton("Choose a folder")
        self.select_button.clicked.connect(self.select_folder)            
        HBox.addWidget(self.select_button)
        HBox.addStretch()
        HBox.addWidget(self.folder_label)
        VBox.addLayout(HBox)

        self.scroll_area = QScrollArea()
        self.file_list_widget = QGroupBox("*.txt files")
        self.file_list_layout = QVBoxLayout()
        self.file_list_widget.setLayout(self.file_list_layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.file_list_widget)
        VBox.addWidget(self.scroll_area)


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
        file = self.selected_file.name
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
        
        DATA, list_pos = read_file_ROTOR(self.selected_file)

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
            self.angle_values, self.ROTOR_magn_field = DATA[:, 0], DATA[:, 1:] 
            self.canvas.colormap_magField()
            self.curr_plt_func = self.canvas.colormap_magField
        else:
            # transpose DATA to extract the different variables:
            self.angle_values, self.ROTOR_magn_field = DATA.T[0], DATA.T[1:]        
            self.canvas.plot_magField_at_positions()
            self.curr_plt_func = self.canvas.plot_magField_at_positions
            
        return

    
    def plot_FREE(self):
    
        DATA = read_file_FREE(self.selected_file)

        # transpose DATA to extract the different variables:
        self.time_values, self.ROTOR_magn_field = DATA.T[0], DATA.T[1:]            

        # plot the data
        self.canvas.plot_magField()
        self.curr_plt_func = self.canvas.plot_magField
        return 

        
    def colormap_ROTOR(self):

        DATA, list_pos = read_file_ROTOR(self.selected_file)
        self.list_pos = list_pos

        
    def select_folder(self):
        data_dir = QFileDialog.getExistingDirectory(self, "Choose a directory for the *.txt ROTOR bench files")
        if data_dir:
            self.data_dir = Path(data_dir)
            self.folder_label.setText("Working directory : {}".format(data_dir))
            self.update_file_list()


    def update_file_list(self):
        # Vider la liste existante
        for i in reversed(range(self.file_list_layout.count())):
            widget = self.file_list_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Ajouter une checkbox par fichier .txt
        for file_path in sorted(self.data_dir.iterdir()):
            if file_path.name.lower().endswith(".txt"):
                checkbox = QRadioButton(file_path.name)
                checkbox.toggled.connect(lambda state, path=file_path: self.process_file(path))
                self.file_list_layout.addWidget(checkbox)


    def process_file(self, filepath):
        
        self.selected_file = Path(filepath)
        #print(f'{self.selected_file=}, {filepath=}')

        self.activate_plotButtons()
        self.tabs.setCurrentIndex(1)
        file_name = self.selected_file.name
        if file_name.startswith("FREE"):
            self.plot_FREE()
        elif file_name.startswith("ROTOR"):
            self.plot_ROTOR()
        else:
            self.folder_label.setText("Fichier non reconnu : {}".format(file_name))
            return
        

    def plot_file(self, filepath):
        try:
            angles, x_vals, y_vals, z_vals = parse_data_file(filepath)
            self.canvas.plot_data(angles, x_vals, y_vals, z_vals, title)
            self.tabs.setCurrentWidget(self.plot_tab)
        except Exception as e:
            self.folder_label.setText("Erreur lors de la lecture : {}".format(str(e)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1300, 900)
    window.show()
    sys.exit(app.exec_())

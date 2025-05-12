import os, sys
from pathlib import Path
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QFileDialog,
    QTabWidget, QMainWindow, QLabel, QCheckBox, QScrollArea, QGroupBox, QMessageBox, QButtonGroup
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from tools import read_file_ROTOR, read_file_FREE, read_file_ROTOR_L
from magnetic_canvas import MagneticPlotCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.XYZ_B                = {'X': 1, 'Y': 1, 'Z':1} # Wether to plot the X,Y,Z components for ROTOR_B plots
        self.XYZ_B_L              = {'X': 1, 'Y': 1, 'Z':1} # Wether to plot the X,Y,Z components for ROTOR_B_L plots
        self.dict_plot_btn        = {}
        self.ROTOR_B_data_dir     = None    # the directory containing the ROTOR data files
        self.ROTOR_B_txt_file     = None    # the selected ROTOR_B file to plot
        self.ROTOR_B_magn_field   = None    # The ROTOR_B magnetic field
        self.ROTOR_B_selected_Zpos= None    # the selected Z position in the ROTOR_B file
        self.ROTOR_L_data_dir     = None    # the directory containing the LILLE ROTOR data files
        self.ROTOR_L_txt_file     = None    # the selected ROTOR_L file to plot
        self.ROTOR_L_magn_field   = None    # The ROTOR_B magnetic field
        self.angles_B             = None    # The angles of the ROTOR data file
        self.angles_L             = None    # The angles of the LILLE data file
        self.curr_plt_func_B      = None    # The current active plot function for the ROTOR_B Plots tab
        self.curr_plt_func_B_L    = None    # The current active plot function for the ROTOR_B_L Plots tab
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
        self.__init_tab_ROTOR_B_Plots()
        self.__init_tab_ROTOR_B_L_Plots()
        
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
        
    def __init_tab_ROTOR_B_Plots(self):
        '''
        Tab_2: data plots
        '''
        self.plot_tab = QWidget()
        self.tabs.addTab(self.plot_tab, "ROTOR_B Plots")
        
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
        
        etiqs, colors = ('X (radial)', 'Y (axial)', 'Z (tang)'), ('red', 'green', 'blue')
        for etiq, lab, color in zip(etiqs, ('X', 'Y', 'Z'), colors):
            btn = QCheckBox(etiq)
            btn.toggle()
            btn.setStyleSheet(f'color: {color}')
            btn.stateChanged.connect(lambda state, label=lab: self.set_XYZ_B(state, label))
            self.dict_plot_btn['ROTOR'].append(btn)
            self.dict_plot_btn['FREE'].append(btn)
            btn.setEnabled(False) 
            H.addWidget(btn)
        VBox.addLayout(H)
        self.canvas_B  = MagneticPlotCanvas(self)
        self.toolbar_B = NavigationToolbar(self.canvas_B, self)
        VBox.addWidget(self.canvas_B)
        VBox.addWidget(self.toolbar_B)


    def __init_tab_ROTOR_B_L_Plots(self):
        '''
        Tab_3: superposed plots of a .csv and a .txt files
        '''
        self.plot_tab = QWidget()
        self.tabs.addTab(self.plot_tab, "ROTOR_B & L Plots")        
        
        VBox = QVBoxLayout()
        self.plot_tab.setLayout(VBox)                

        H = QHBoxLayout()
        H.addStretch()
        
        btn = QPushButton('Plot ROTOR B & L')
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(120)
        btn.setCheckable(False)
        btn.clicked.connect(self.plot_ROTOR_B_L)
        H.addWidget(btn)
        btn.setEnabled(False)    
        self.dict_plot_btn['ROTOR_B_L'] = [btn]

        # Add Zpos selection
        btn = QLabel('Choose ROTOR Zpos (mm): ')
        H.addWidget(btn)
        self.zpos_group_box = QGroupBox('')
        self.zpos_layout = QHBoxLayout()
        self.zpos_group_box.setLayout(self.zpos_layout)
        H.addWidget(self.zpos_group_box)

        self.zpos_button_group = QButtonGroup(self.zpos_group_box)
        self.zpos_button_group.setExclusive(True)
        self.zpos_button_group.buttonClicked.connect(self.on_zpos_selected)
        
        H.addStretch()        
        etiqs, colors = ('X (radial)', 'Y (axial)', 'Z (tang)'), ('red', 'green', 'blue')
        for etiq, lab, color in zip(etiqs, ('X', 'Y', 'Z'), colors):            
            btn = QCheckBox(etiq)
            btn.toggle()
            btn.setStyleSheet(f'color: {color}')            
            btn.stateChanged.connect(lambda state, label=lab: self.set_XYZ_B_L(state, label))
            H.addWidget(btn)
        VBox.addLayout(H)
        
        self.canvas_B_L  = MagneticPlotCanvas(self)
        self.toolbar_B_L = NavigationToolbar(self.canvas_B_L, self)
        VBox.addWidget(self.canvas_B_L)
        VBox.addWidget(self.toolbar_B_L)


    def set_XYZ_B(self, state, lab):
        self.XYZ_B[lab] = state//2
        #print(f'{self.XYZ=}')
        if self.curr_plt_func_B: self.curr_plt_func_B()
        
        
    def set_XYZ_B_L(self, state, lab):
        self.XYZ_B_L[lab] = state//2
        #print(f'{self.XYZ=}')
        if self.curr_plt_func_B_L: self.curr_plt_func_B_L()


    def convert_XYZ_B_to_tuple(self):
        xyz = (self.XYZ_B['X'], self.XYZ_B['Y'], self.XYZ_B['Z'])
        return xyz


    def convert_XYZ_B_L_to_tuple(self):
        xyz = (self.XYZ_B_L['X'], self.XYZ_B_L['Y'], self.XYZ_B_L['Z'])
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
        

    def reshape_magnetic_field(self, DATA, list_pos):
        '''
        Reshape DATA to be a 2D array with shape (nb_angles, 1 + 3*nb_Zpos).
        DATA is eshaoed to be an array with lines formated like:
            "# angle[°]; X1_magn [mT]; Y1_magn [mT]; Z1_magn [mT]; X2_magn [mT]; Y2_magn [mT]; Z2_magn [mT];..."
        instead of:
            "# ZPos#; a[°]; X1_magn[mT]; Y1_magn[mT]; Z1_magn[mT]"
        '''
        if DATA.shape[1] == 5:
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
        
        return DATA

    def extract_magnetic_field(self, DATA, list_pos, Zpos):
        '''
        Reshape DATA to be a 2D array with shape (nb_angles, 1 + 3*nb_Zpos),
        and extract the magnetic field data for a given Z position.
        
        DATA is reshaped to be an array with lines formated like:
            "# angle[°]; X1_magn [mT]; Y1_magn [mT]; Z1_magn [mT]; X2_magn [mT]; Y2_magn [mT]; Z2_magn [mT];..."
        instead of:
            "# ZPos#; a[°]; X1_magn[mT]; Y1_magn[mT]; Z1_magn[mT]"
        '''
        if DATA.shape[1] == 5:
            nb_col = 1 + 3 #  angle col + (X , Y, Z)
            nb_row = int(len(DATA)/len(list_pos))
            newDATA = np.ndarray((nb_row, nb_col), dtype=float)

            # copy angle column
            newDATA[ :, 0] = DATA[ : nb_row, 1]
            # copy X,Y,Z for all Zpos:
            nb_val = 3 # the 3 components X, Y and Z

        # Extract data for position Zpos:
        try:
            index_Zpos = list_pos.index(f'{Zpos:03d}')
            for n in range(len(list_pos)):
                if n != index_Zpos: continue
                newDATA[ : , 1 : 1 + nb_val] = DATA[n*nb_row : (n+1)*nb_row, 2:]
            DATA = newDATA
        except:
            message = f'Zpos: {Zpos} not found in the list of Zpos:\n{list_pos}. Try another value'
            QMessageBox.warning(self, 'Warning', message)
            return None
           
        return DATA
        
    
    def plot_ROTOR(self, colormap=False, fft=False):
        '''
        To plot the ROTOR data.
        '''
        DATA, list_pos = read_file_ROTOR(self.ROTOR_B_txt_file)
        DATA = self.reshape_magnetic_field(DATA, list_pos)
        
        if colormap and len(list_pos) <  2:
            message = f'Data file must have at least 2 Zpos to plot a colormap\nPlease select another file'''
            QMessageBox.warning(self, 'Warning', message)
            return
        
        self.plot_fft = fft
        self.list_pos = list_pos

        # Check there is at least one component to plot
        xyz = self.convert_XYZ_B_to_tuple()
        if sum(xyz) == 0:
            message = f'You must select at least one component X,Y, or Z'
            QMessageBox.warning(self, 'Warning', message)
            return        
 
        # plot the data
        if colormap:
            self.angles_B, self.ROTOR_B_magn_field = DATA[:, 0], DATA[:, 1:] 
            self.canvas_B.colormap_magField()
            self.curr_plt_func_B = lambda: self.plot_ROTOR(colormap=True)
        else:
            # transpose DATA to extract the different variables:
            self.angles_B, self.ROTOR_B_magn_field = DATA.T[0], DATA.T[1:]        
            self.canvas_B.plot_magField_at_positions()
            self.curr_plt_func_B = self.plot_ROTOR    
        return

    
    def plot_FREE(self):
    
        DATA = read_file_FREE(self.ROTOR_B_txt_file)
        # transpose DATA to extract the different variables:
        self.time_values, self.ROTOR_B_magn_field = DATA.T[0], DATA.T[1:]            

        # plot the data
        self.canvas_B.plot_magField()
        self.curr_plt_func_B = self.canvas_B.plot_magField

        return 
    
    
    def plot_ROTOR_B_L(self):        
        '''
        To plot the data from the Lille bench (.csv file) and the ROTOR data (.txt file)
        '''    
        ROTOR_B_data, list_pos = read_file_ROTOR(self.ROTOR_B_txt_file)
        ROTOR_L_data = read_file_ROTOR_L(self.ROTOR_L_txt_file)
        
        Zpos = self.ROTOR_B_selected_Zpos
        ROTOR_B_data = self.extract_magnetic_field(ROTOR_B_data, list_pos, Zpos)

        Zpos = self.ROTOR_B_selected_Zpos
        i_range = np.where(ROTOR_L_data.T[2] == int(Zpos))
        ROTOR_L_data  = ROTOR_L_data[i_range]

        # transpose DATA to extract the different variables:
        self.angles_B, self.ROTOR_B_magn_field = ROTOR_B_data.T[0], ROTOR_B_data.T[1:]       
        self.angles_L, self.ROTOR_L_magn_field = ROTOR_L_data.T[1], ROTOR_L_data.T[3:]
        
        # Check there is at least one component to plot
        xyz = self.convert_XYZ_B_L_to_tuple()
        if sum(xyz) == 0:
            message = f'You must select at least one component X,Y, or Z'
            QMessageBox.warning(self, 'Warning', message)
            return
        
        # plot the data
        self.canvas_B_L.plot_ROTOR_B_L_for_Zpos()
        self.curr_plt_func_B_L = self.plot_ROTOR_B_L

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
        print(f'process_ROTOR_L_file')
        self.ROTOR_L_txt_file = Path(filepath)
        
        self.tabs.setCurrentIndex(2)

        tag = 'ROTOR_B_L'
        for key in self.dict_plot_btn.keys():
            if key == tag:
                for btn in self.dict_plot_btn[key]: btn.setEnabled(True)
        self.plot_ROTOR_B_L()
        

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
                for btn in self.dict_plot_btn['ROTOR_B_L']: btn.setEnabled(False)
                for btn in self.dict_plot_btn['FREE']: btn.setEnabled(True)
            elif file_name.startswith("ROTOR"):
                self.plot_ROTOR()
                self.update_zpos_buttons()
                for btn in self.dict_plot_btn['ROTOR_B_L']: btn.setEnabled(False)
                for btn in self.dict_plot_btn['ROTOR']: btn.setEnabled(True)
        else:
            message = f'File name <{file_name}> does not start with\nROTOR_... or FREE_... or is corrupted'
            QMessageBox.warning(self, 'Warning', message)
        
        return

    def update_zpos_buttons(self):
        '''
        Update the Zpos radio buttons based on self.list_pos.
        '''
        # Clear existing buttons
        for i in reversed(range(self.zpos_layout.count())):
            widget = self.zpos_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Add new buttons
        if self.list_pos:
            done = False
            for zpos in self.list_pos:
                radio_button = QRadioButton(f"{int(zpos)}")
                self.zpos_button_group.addButton(radio_button)
                self.zpos_layout.addWidget(radio_button)
                if not done:
                    radio_button.setChecked(True)
                    self.ROTOR_B_selected_Zpos = int(zpos)
                    done = True

    def on_zpos_selected(self, button):
        '''
        Handle Zpos selection.
        '''
        selected_zpos = button.text()
        self.ROTOR_B_selected_Zpos = int(selected_zpos)
        print(f"Selected Zpos: {self.ROTOR_B_selected_Zpos}")
        
        self.plot_ROTOR_B_L()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1400, 900)
    window.show()
    sys.exit(app.exec_())

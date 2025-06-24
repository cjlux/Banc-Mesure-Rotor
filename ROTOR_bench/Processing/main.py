#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#

import os, sys
from shutil import rmtree
from pathlib import Path
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QFileDialog,
    QTabWidget, QMainWindow, QLabel, QCheckBox, QScrollArea, QGroupBox, QMessageBox, QButtonGroup, 
    QAction, QSpinBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from tools import read_file_ROTOR, read_file_FREE, read_file_ROTOR_L, build_XYZ_name_with_tuple
from magnetic_canvas import MagneticPlotCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.XYZ_B                = {'X': 1, 'Y': 1, 'Z':1} # Wether to plot the X,Y,Z components for ROTOR_B plots
        self.XYZ_B_L              = {'X': 1, 'Y': 1, 'Z':1} # Wether to plot the X,Y,Z components for ROTOR_B_L plots
        self.dict_plot_widgets    = {}
        self.ROTOR_B_data_dir     = Path('')  # the directory containing the ROTOR data files
        self.ROTOR_B_txt_file     = None      # the selected ROTOR_B file to plot
        self.ROTOR_B_magn_field   = None      # The ROTOR_B magnetic field
        self.ROTOR_B_sel_Zpos     = None      # the selected Z position in the ROTOR_B file
        self.ROTOR_L_data_dir     = Path('')  # the directory containing the LILLE ROTOR data files
        self.ROTOR_L_txt_file     = None      # the selected ROTOR_L file to plot
        self.ROTOR_L_magn_field   = None      # The ROTOR_B magnetic field
        self.ROTOR_L_sel_Zpos     = None      # the selected Z position in the ROTOR_L file
        self.ROTOR_L_sel_Angle    = 0         # the selected angle in the ROTOR_L file
        self.angles_B             = None      # The angles of the ROTOR data file
        self.angles_L             = None      # The angles of the LILLE data file
        self.curr_plt_info_B      = {}        # Dictionnary of infos on the current plot for the ROTOR_B tab
        self.curr_plt_info_B_L    = {}        # Dictionnary of infos on the current plot for the ROTOR_B_L tab
        self.time_values          = None      # The time values of the FREE data file
        self.list_pos             = None      # The list of the Z positions found in the ROTOR data file
        self.plot_fft             = False     # whether the plos is a DSP or not
        
        self.file_tab             = None      # The tab to choose a directory and list .txt files
        self.plot_tab             = None      # the tab to draw the plots"
        self.plot_txt_csv         = None      # The tab to superpose a .txt and a .csv plots
        
        self.btn_free_stat        = None      # The button to display the statistics in the FREE data plot
        self.ROTOR_L_Zpos         = None      # The SpinBox to choose the Zpos in the ROTOR_L data  
        self.ROTOR_L_ShiftAngle   = None      # The SpinBox to choose the angle shift in the ROTOR_L data
        
        self.last_ROTOR_L_txt_file = Path('') # The last read ROTOR_L file to avoid re-reading it
        self.last_ROTOR_L_data     = None     # The last read ROTOR_L data to avoid re-reading it
        self.last_ROTOR_B_txt_file = Path('') # The last read ROTOR_B file to avoid re-reading it
        self.last_ROTOR_B_data     = None     # The last read ROTOR_B data to avoid re-reading it   
        self.last_list_pos         = None     # The last read list of Z positions to avoid re-reading it
        
        self.setWindowTitle("ROTOR bench data plot")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.curr_plt_info_B = {'func': None, 'param': None}
        self.curr_plt_info_B_L = {'func': None, 'param': None}        

        # Create the menu bar
        self.create_menu_bar()

        # Initialize tabs
        self.__init_tab_ChoseFolder()
        self.__init_tab_ROTOR_B_Plots()
        self.__init_tab_ROTOR_B_L_Plots()
        
        # Select the first tab by default
        self.tabs.setCurrentIndex(0)        
        
    def create_menu_bar(self):
        """
        Create the menu bar with File, Parameters, and Tools menus.
        """
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)  # Close the application
        file_menu.addAction(quit_action)

        # Parameters menu
        parameters_menu = menu_bar.addMenu("Parameters")
        # Add actions to the Parameters menu as needed

        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")
        clean_png_action = QAction("Clean PNG directories", self)
        clean_png_action.triggered.connect(self.clean_png_directories)  # Connect to a method
        tools_menu.addAction(clean_png_action)

    def clean_png_directories(self):
        """
        Placeholder method for cleaning PNG directories.
        Implement the logic for cleaning PNG directories here.
        """
        print("Cleaning PNG directories...")
        # Add your logic here
        PNG_dirs = []
        for root, dirs, files in Path.cwd().walk():
            if 'PNG' in dirs:
                PNG_dirs.append(Path(root, 'PNG'))
        
        if PNG_dirs:
            for dir in PNG_dirs:
                rel_dir = dir.relative_to(Path.cwd().parent)
                OK = QMessageBox.question(self, 'Warning', f'Do you want to delete the directory:\n<{rel_dir}> ?')
                if OK == QMessageBox.Yes:
                    if dir.exists(): rmtree(dir)
                    print(f'Deleted directory: {dir}')
        else:
            QMessageBox.information(self, 'Info', 'No PNG directories found')
            print('No PNG directories found')
        
        return
            
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
        btn.setMinimumHeight(40)
        btn.clicked.connect(self.select_ROTOR_B_dir)            
        V.addWidget(btn)
        
        self.ROTOR_B_file_list_widget = QGroupBox("ROTOR *.TXT files")
        self.ROTOR_B_file_list_layout = QVBoxLayout(self.ROTOR_B_file_list_widget)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.ROTOR_B_file_list_widget)
        V.addWidget(scroll_area)
        
        HBox.addLayout(V)
        
        self.LILLE_choose_dir = QVBoxLayout()
        V = self.LILLE_choose_dir
        self.button_LILLE_data_dir = QPushButton("LILLE rotor bench folder")
        btn = self.button_LILLE_data_dir
        btn.setMinimumHeight(40)
        btn.clicked.connect(self.select_ROTOR_L_dir)
        V.addWidget(btn)
        
        self.ROTOR_L_file_list_widget = QGroupBox("LILLE rotor *.CSV files")
        self.ROTOR_L_file_list_layout = QVBoxLayout(self.ROTOR_L_file_list_widget)
        scroll_area = QScrollArea()
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
        
        self.dict_plot_widgets['ROTOR'] = []
        self.dict_plot_widgets['FREE'] = []

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
                self.dict_plot_widgets['ROTOR'].append(btn)
            else:
                self.dict_plot_widgets['FREE'].append(btn)
            btn.setEnabled(False)    

        btn = QPushButton('Save Current Plot')
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(120)
        btn.setCheckable(False)
        btn.clicked.connect(self.save_ROTOR_B)
        H.addWidget(btn)
        btn.setEnabled(False)    
        self.dict_plot_widgets['ROTOR'].append(btn)
        self.dict_plot_widgets['FREE'].append(btn)
            
        H.addStretch()
        btn = QCheckBox('display stat')
        btn.setChecked(True)
        btn.setEnabled(False)
        btn.stateChanged.connect(self.plot_FREE)
        self.dict_plot_widgets['FREE'].append(btn)
        self.btn_free_stat = btn
        H.addWidget(btn)
        
        etiqs, colors = ('X (radial)', 'Y (axial)', 'Z (tang)'), ('red', 'green', 'blue')
        for etiq, lab, color in zip(etiqs, ('X', 'Y', 'Z'), colors):
            btn = QCheckBox(etiq)
            btn.toggle()
            btn.setStyleSheet(f'color: {color}')
            btn.stateChanged.connect(lambda state, label=lab: self.set_XYZ_B(state, label))
            self.dict_plot_widgets['ROTOR'].append(btn)
            self.dict_plot_widgets['FREE'].append(btn)
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
        
        self.dict_plot_widgets['ROTOR_B_L'] = []
        
        VBox = QVBoxLayout()
        self.plot_tab.setLayout(VBox)                

        H = QHBoxLayout()
        H.addStretch()

        # The Button to plot the ROTOR_B data        
        btn = QPushButton('ROTOR B & L')
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(120)
        btn.setCheckable(False)
        btn.clicked.connect(self.plot_ROTOR_B_L)
        H.addWidget(btn)
        btn.setEnabled(False)    
        self.dict_plot_widgets['ROTOR_B_L'].append(btn)

        # The button to save the current plot as a PNG file
        btn = QPushButton('Save Current Plot')
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(120)
        btn.setCheckable(False)
        btn.clicked.connect(self.save_ROTOR_B_L)
        H.addWidget(btn)
        btn.setEnabled(False)    
        self.dict_plot_widgets['ROTOR_B_L'].append(btn)

        self.ROTOR_R_group_box = QGroupBox('')
        self.ROTOR_R_layout = QHBoxLayout()
        self.ROTOR_R_group_box.setLayout(self.ROTOR_R_layout)
        H.addWidget(self.ROTOR_R_group_box)
        self.ROTOR_R_group_box.setFixedHeight(45)

        # Add Zpos selection
        lab = QLabel('ROTOR_B Zpos (mm)')
        self.dict_plot_widgets['ROTOR_B_L'].append(lab)
        self.ROTOR_R_layout.addWidget(lab)
        
        self.ROTOR_B_Zpos_combo =  QComboBox()
        cb = self.ROTOR_B_Zpos_combo
        cb.setEnabled(False)
        cb.setEditable(False)
        cb.setMaxVisibleItems(50)
        cb.setMaxCount(50)
        cb.currentIndexChanged.connect(self.zpos_R_selected)
        #cb.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        cb.setToolTip('Select the Zpos to plot')
        #cb.setStyleSheet('QComboBox { background-color: white; }')
        self.dict_plot_widgets['ROTOR_B_L'].append(cb)
        self.ROTOR_R_layout.addWidget(cb)
        
        self.ROTOR_L_group_box = QGroupBox('')
        self.HBox = QHBoxLayout()
        self.ROTOR_L_group_box.setLayout(self.HBox)
        H.addWidget(self.ROTOR_L_group_box)
        self.ROTOR_L_group_box.setFixedHeight(45)


        lab = QLabel('ROTOR_L')
        self.dict_plot_widgets['ROTOR_B_L'].append(lab)
        self.HBox.addWidget(lab)
        
        # The SpinBox to choose the Zpos in the ROTOR_B_L data
        lab = QLabel('Zpos (mm)')
        self.HBox.addWidget(lab)
        self.ROTOR_L_Zpos = QSpinBox()
        sb = self.ROTOR_L_Zpos
        sb.setRange(-7, 144)
        sb.setSingleStep(1)
        sb.setValue(0)
        sb.setEnabled(False)
        sb.setFixedHeight(23)
        sb.setToolTip('Select the Zpos to plot')
        sb.valueChanged.connect(lambda value: self.zpos_L_changed(value))
        self.HBox.addWidget(sb)
        self.dict_plot_widgets['ROTOR_B_L'].append(lab)
        self.dict_plot_widgets['ROTOR_B_L'].append(sb)
        
        # The SpinBox to choose the angle shift in the ROTOR_B_L data
        lab = QLabel('angle shift (°)')
        self.HBox.addWidget(lab)
        sb = QSpinBox()
        sb.setRange(0, 360)
        sb.setSingleStep(1)
        sb.setValue(0)
        sb.setEnabled(False)
        sb.setFixedHeight(23)
        sb.setToolTip('Select the angle shift to apply to the plot of ROTOR_L')
        sb.valueChanged.connect(lambda value: self.angle_shift_L_changed(value))
        self.HBox.addWidget(sb)
        self.dict_plot_widgets['ROTOR_B_L'].append(sb)
        
        H.addStretch()        
        etiqs, colors = ('X (radial)', 'Y (axial)', 'Z (tang)'), ('red', 'green', 'blue')
        for etiq, lab, color in zip(etiqs, ('X', 'Y', 'Z'), colors):            
            btn = QCheckBox(etiq)
            btn.toggle()
            btn.setStyleSheet(f'color: {color}')            
            btn.stateChanged.connect(lambda state, label=lab: self.set_XYZ_B_L(state, label))
            H.addWidget(btn)
            self.dict_plot_widgets['ROTOR_B_L'].append(btn)
        VBox.addLayout(H)
        
        self.canvas_B_L  = MagneticPlotCanvas(self)
        self.toolbar_B_L = NavigationToolbar(self.canvas_B_L, self)
        VBox.addWidget(self.canvas_B_L)
        VBox.addWidget(self.toolbar_B_L)
        
        self.set_state('ROTOR_B_L', False)


    def set_state(self, key, state):
        '''
        Enable or disable the widgets in the dictionary dico.
        '''
        for widget in self.dict_plot_widgets[key]:
            widget.setEnabled(state)
                
                
    def set_XYZ_B(self, state, lab):
        self.XYZ_B[lab] = state//2
        #print(f'{self.XYZ=}')
        if self.curr_plt_info_B['func']: self.curr_plt_info_B['func']()
        
        
    def set_XYZ_B_L(self, state, lab):
        self.XYZ_B_L[lab] = state//2
        #print(f'{self.XYZ=}')
        if self.curr_plt_info_B_L['func']: self.curr_plt_info_B_L['func']()


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
            
        for key in self.dict_plot_widgets.keys():
            if key == tag:
                for btn in self.dict_plot_widgets[key]:
                    btn.setEnabled(True)
            else:
                for btn in self.dict_plot_widgets[key]:
                    btn.setEnabled(False)
        

    def ROTOR_B_reshape_magnetic_field(self, DATA, list_pos):
        '''
        Reshape the DATA of a ROTOR_B file to be a 2D array with shape (nb_angles, 1 + 3*nb_Zpos).
        DATA is reshaped to be an array with lines formated like:
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
                newDATA[:, 1+n*nb_val:1+(n+1)*nb_val] = DATA[n*nb_row:(n+1)*nb_row, 2:]
            DATA = newDATA
        
        return DATA


    def ROTOR_B_extract_magnetic_field(self, DATA, list_pos, Zpos):
        '''
        Reshape DATA to be a 2D array with shape (nb_angles, 1 + 3*nb_Zpos),
        and extract the magnetic field data for a given Z position.
        
        DATA is already an array with lines formated like:
            "# angle[°]; X1_magn [mT]; Y1_magn [mT]; Z1_magn [mT]; X2_magn [mT]; Y2_magn [mT]; Z2_magn [mT];..."
        '''
        
        i_Zpos = list_pos.index(f'{Zpos:03d}')
        print(f'i_Zpos: {i_Zpos}', flush=True)

        # copy X,Y,Z for all Zpos:
        nb_val = 3                  # the 3 components X, Y and Z
        new_nb_col = 1 + nb_val     # the angle col + the 3 components X, Y and Z
        nb_row = DATA.shape[0]
        newDATA = np.ndarray((nb_row, new_nb_col), dtype=float)
        # Extract angle column:
        newDATA[:, 0] = DATA[:nb_row, 0]
        # Extract X, Y, Z data for position Zpos:
        try:
            newDATA[:, 1:1+nb_val] = DATA[:, 1+i_Zpos*nb_val:1+(i_Zpos+1)*nb_val]
            DATA = newDATA
        except:
            message = f'index of {Zpos:03d} not found in the list of Zpos:\n{list_pos}. Try another value'
            QMessageBox.warning(self, 'Warning', message)
                       
        return DATA
        
    
    def plot_ROTOR(self, colormap=False, fft=False):
        '''
        To plot the ROTOR data.
        '''
        DATA, list_pos = read_file_ROTOR(self.ROTOR_B_txt_file)
        DATA = self.ROTOR_B_reshape_magnetic_field(DATA, list_pos)
        
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
            self.curr_plt_info_B['func']  = lambda: self.plot_ROTOR(colormap=True)
            self.curr_plt_info_B['param'] = 'color'
            self.canvas_B.colormap_magField()
        else:
            # transpose DATA to extract the different variables:
            self.angles_B, self.ROTOR_B_magn_field = DATA.T[0], DATA.T[1:]        
            self.curr_plt_info_B['func'] = self.plot_ROTOR
            if fft:
                self.curr_plt_info_B['param'] = 'fft'
            else:
                self.curr_plt_info_B['param'] = 'plot' 
            self.canvas_B.plot_magField_at_positions()
            
        return


    def save_ROTOR_B(self):
        '''
        Save the current plot of the ROTOR_B data in a PNG file.  
        '''
        fig       = self.canvas_B.figure
        png_dir   = Path(self.ROTOR_B_data_dir, 'PNG')
        file_name = self.ROTOR_B_txt_file.name
        
        if not png_dir.exists(): png_dir.mkdir(exist_ok=True)
        
        XYZ = build_XYZ_name_with_tuple(self.convert_XYZ_B_to_tuple())
        
        param = self.curr_plt_info_B['param']
        assert param in ['fft', 'color', 'plot', 'free'], f"Unknown self.curr_plt_info_B['param']: <{param}>"

        if param == 'fft':
            fig_path = Path(png_dir, file_name.replace('.txt', f'_PSD_{XYZ}.png'))
        elif param == 'color':
            fig_path = Path(png_dir, file_name.replace('.txt', f'_COLORMAP_{XYZ}.png'))
        elif param == 'plot':
            fig_path = Path(png_dir, file_name.replace('.txt', f'_PLOT_{XYZ}.png'))            
        elif param == 'free':
            fig_path = Path(png_dir, file_name.replace('.txt', f'_FREE_{XYZ}.png'))

        if fig:
            file_name, _ = QFileDialog.getSaveFileName(self, 
                                                       "Save plot", 
                                                       str(fig_path), 
                                                       "PNG files (*.png)")
            if file_name:
                fig.savefig(file_name)
        else:
            QMessageBox.warning(self, 'Warning', 'No plot to save')
        return
    
    def save_ROTOR_B_L(self):
        '''
        Save the current plot of the ROTOR_B_L data in a PNG file.  
        '''
        fig         = self.canvas_B_L.figure
        data_dir_B  = self.ROTOR_B_data_dir.name
        data_dir_L  = self.ROTOR_L_data_dir.name
        file_name_B = self.ROTOR_B_txt_file.name
        file_name_L = self.ROTOR_L_txt_file.name
        
        assert(data_dir_B == data_dir_L), f"ROTOR_B and ROTOR_L data directories must be the same: <{dir_name_B}> != <{dir_name_L}>"
        png_dir   = Path(data_dir_B, 'PNG')
        if not png_dir.exists(): png_dir.mkdir(exist_ok=True)
        
        XYZ = build_XYZ_name_with_tuple(self.convert_XYZ_B_to_tuple())
        
        Zpos_B = self.ROTOR_B_sel_Zpos
        Zpos_L = self.ROTOR_L_sel_Zpos
        shift  = self.ROTOR_L_sel_Angle

        file_name  = f'{file_name_B}@{Zpos_B}mm__'
        file_name += f'{file_name_L}@{Zpos_L}mm_shift:{shift}__{XYZ}.png>'

        fig_path = Path(png_dir, file_name.replace('.txt', f''))

        if fig:
            file_name, _ = QFileDialog.getSaveFileName(self, 
                                                       "Save plot", 
                                                       str(fig_path), 
                                                       "PNG files (*.png)")
            if file_name:
                fig.savefig(file_name)
        else:
            QMessageBox.warning(self, 'Warning', 'No plot to save')
        return
    
    
    def plot_FREE(self):
    
        DATA = read_file_FREE(self.ROTOR_B_txt_file)
        # transpose DATA to extract the different variables:
        self.time_values, self.ROTOR_B_magn_field = DATA.T[0], DATA.T[1:]            

        # plot the data
        self.canvas_B.plot_magField()
        self.curr_plt_info_B['func'] = self.canvas_B.plot_magField
        self.curr_plt_info_B['param'] = 'free'

        return 
    
    
    def plot_ROTOR_B_L(self):        
        '''
        To plot the data from the Lille bench (.csv file) and the ROTOR data (.txt file)
        '''
        # Get the ROTOR_B data from the file or from the cache:    
        if self.last_ROTOR_B_txt_file.name != self.ROTOR_B_txt_file.name: 
            ROTOR_B_data, list_pos = read_file_ROTOR(self.ROTOR_B_txt_file)
            ROTOR_B_data = self.ROTOR_B_reshape_magnetic_field(ROTOR_B_data, list_pos)
            self.last_ROTOR_B_txt_file = self.ROTOR_B_txt_file
            self.last_ROTOR_B_data = ROTOR_B_data
            self.last_list_pos = list_pos
        else:
            ROTOR_B_data = self.last_ROTOR_B_data
            list_pos = self.last_list_pos
        # Extract the data of the ROTOR_B corresponding to the selected Zpos:
        Zpos = self.ROTOR_B_sel_Zpos
        ROTOR_B_data = self.ROTOR_B_extract_magnetic_field(ROTOR_B_data, list_pos, Zpos)
        
        # Get the ROTOR_L data from the file or from the cache:
        if self.ROTOR_L_txt_file is not None:
            if self.last_ROTOR_L_txt_file.name != self.ROTOR_L_txt_file.name:            
                ROTOR_L_data = read_file_ROTOR_L(self.ROTOR_L_txt_file)
                self.last_ROTOR_L_txt_file = self.ROTOR_L_txt_file
                self.last_ROTOR_L_data = ROTOR_L_data
            else:
                ROTOR_L_data = self.last_ROTOR_L_data
        
        # Extract the data of the ROTOR_L corresponding to the selected Zpos:
        Zpos = self.ROTOR_L_Zpos.value()
        try:
            i_range = np.where(ROTOR_L_data.T[2] == int(Zpos))
            ROTOR_L_data  = ROTOR_L_data[i_range]
        except:
            message = f'Zpos: {Zpos} not found in the LILLE ROTOR data file\nPlease select another value'
            QMessageBox.warning(self, 'Warning', message)
            return
        
        # Apply shift angle on ROTOR_L data if required:
        #if self.ROTOR_L_sel_Angle != 0:
        i = self.ROTOR_L_sel_Angle
        nb_angle = len(ROTOR_L_data)
        new_ROTOR_L_data = ROTOR_L_data.copy()
        new_ROTOR_L_data[:nb_angle-i, 3:] = ROTOR_L_data[i:, 3:]
        new_ROTOR_L_data[nb_angle-i:, 3:] = ROTOR_L_data[:i, 3:]
        ROTOR_L_data = new_ROTOR_L_data

        # transpose DATA to extract the different variables:
        self.angles_B, self.ROTOR_B_magn_field = ROTOR_B_data.T[0], ROTOR_B_data.T[1:]       
        self.angles_L, self.ROTOR_L_magn_field = ROTOR_L_data.T[1], ROTOR_L_data.T[3:]
        
        # Check there is currently at least one component to plot
        xyz = self.convert_XYZ_B_L_to_tuple()
        if sum(xyz) == 0:
            message = f'You must select at least one component X,Y, or Z'
            QMessageBox.warning(self, 'Warning', message)
            return
        
        # plot the data
        self.canvas_B_L.plot_ROTOR_B_L_for_Zpos()
        self.curr_plt_info_B_L['func']  = self.plot_ROTOR_B_L
        self.curr_plt_info_B_L['param'] = 'plot_B_L'

        return 
    
            
    def select_ROTOR_B_dir(self):
        data_dir = QFileDialog.getExistingDirectory(self, "Directory for the *.txt ROTOR bench files")
        if data_dir:
            self.ROTOR_B_data_dir = Path(data_dir)
            self.ROTOR_B_file_list_widget.setTitle(f'*.TXT files in <{data_dir}>')
            self.update_ROTOR_B_file_list()
            
            # Replicate the data directory for the LILLE ROTOR files:
            self.ROTOR_L_data_dir = Path(data_dir)
            self.ROTOR_L_file_list_widget.setTitle(f'*.CSV files in <{data_dir}>')
            self.update_ROTOR_L_file_list()


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
                del widget

        # Ajouter une checkbox par fichier .txt
        for file_path in sorted(self.ROTOR_B_data_dir.iterdir()):
            if file_path.name.lower().endswith(".txt"):
                checkbox = QRadioButton(file_path.name)
                checkbox.toggled.connect(lambda state, path=file_path: self.process_ROTOR_B_file(path))
                self.ROTOR_B_file_list_layout.addWidget(checkbox)
        self.ROTOR_B_file_list_layout.addStretch()

    def update_ROTOR_L_file_list(self):
        # Vider la liste existante
        for i in reversed(range(self.ROTOR_L_file_list_layout.count())):
            widget = self.ROTOR_L_file_list_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                del widget

        # Ajouter une checkbox par fichier .csv
        for file_path in sorted(self.ROTOR_L_data_dir.iterdir()):
            if file_path.name.lower().endswith(".csv"):
                rb = QRadioButton(file_path.name)
                rb.pressed.connect(lambda path=file_path, btn=rb: self.process_ROTOR_L_file(path, btn))
                self.ROTOR_L_file_list_layout.addWidget(rb)
        self.ROTOR_L_file_list_layout.addStretch()
    

    def process_ROTOR_L_file(self, filepath, button):
        '''
        Process the selected ROTOR CSV file.
        '''
        
        if self.ROTOR_B_txt_file.name.startswith('ROTOR'):
            button.setChecked(True)
            self.ROTOR_L_txt_file = Path(filepath)    
            self.tabs.setCurrentIndex(2)
            self.set_state('ROTOR_B_L', True)
            self.plot_ROTOR_B_L()
        else:
            message = f'Please select a ROTOR data file first'
            QMessageBox.warning(self, 'Warning', message)
            return
        

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
                self.set_state('ROTOR_B_L', False)
                self.set_state('FREE', True)
            elif file_name.startswith("ROTOR"):
                self.plot_ROTOR()
                self.update_zpos_combo()
                self.set_state('ROTOR_B_L', False)
                self.set_state('ROTOR', True)
        else:
            message = f'File name <{file_name}> does not start with\nROTOR_... or FREE_... or is corrupted'
            QMessageBox.warning(self, 'Warning', message)
        
        return

    def update_zpos_combo(self):
        '''
        Update the Zpos ComboBox based on self.list_pos.
        '''
        # Clear existing buttons
        self.ROTOR_B_Zpos_combo.clear()
        
        # Add new buttons
        if self.list_pos:
            done = False
            for zpos in self.list_pos:
                self.ROTOR_B_Zpos_combo.addItem(zpos)
                if not done:
                    # Select the first Zpos by default
                    value = int(zpos)
                    self.ROTOR_B_Zpos_combo.setCurrentIndex(0)
                    self.ROTOR_B_sel_Zpos = value
                    # set the Zpos SpinBox for ROTOR_L to the selected value:
                    self.ROTOR_L_Zpos.setValue(value)
                    self.ROTOR_L_sel_Zpos = value
                    done = True
        
        

    def zpos_R_selected(self, index):
        '''
        Handle Zpos selection.
        '''
        selected_zpos = self.ROTOR_B_Zpos_combo.itemText(index)
        if selected_zpos == '': return
        
        self.ROTOR_B_sel_Zpos = int(selected_zpos)
        print(f"Selected ROTOR_B Zpos: {self.ROTOR_B_sel_Zpos}")
        # set the Zpos SpinBox for ROTOR_L to the selected value:
        self.ROTOR_L_Zpos.setValue(self.ROTOR_B_sel_Zpos)
        self.ROTOR_L_sel_Zpos = self.ROTOR_B_sel_Zpos
        
        self.plot_ROTOR()
        
    def zpos_L_changed(self, value):
        '''
        Handle Zpos selection in the ROTOR_L data (LILLE rotor bench).
        '''
        self.ROTOR_L_sel_Zpos = value
        print(f"Selected ROTOR_L Zpos: {self.ROTOR_L_sel_Zpos}")
        
        self.plot_ROTOR_B_L()   
    
    
    def angle_shift_L_changed(self, value):
        '''
        Handle angle shift selection in the ROTOR_L data (LILLE rotor bench).
        '''
        self.ROTOR_L_sel_Angle = value
        print(f"Selected ROTOR_L angle shift: {self.ROTOR_L_sel_Angle}")
        
        # Update the plot with the new angle shift
        self.plot_ROTOR_B_L()   
        
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1400, 900)
    window.show()
    sys.exit(app.exec_())

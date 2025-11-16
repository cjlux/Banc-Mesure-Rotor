#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, 
                             QScrollArea, QGroupBox, QFileDialog, QMessageBox)

from pathlib import Path
from tools import read_file_ROTOR_L, read_file_SIMUL_ROTOR, read_file_ROTOR

class FilesTab(QWidget):
    '''
    Tab for selecting and managing data files for ROTOR_B, LILLE ROTOR, and SIMULATION rotor benches.
    '''
    # Declare attributes for memory optimization
    __slots__ = ('main', 
                 'ROTOR_B_file_list_widget', 'ROTOR_B_file_list_layout',
                 'ROTOR_L_file_list_widget', 'ROTOR_L_file_list_layout',
                 'ROTOR_S_file_list_widget', 'ROTOR_S_file_list_layout',
                 'button_L_data_dir', 'button_S_data_dir',)
    
    def __init__(self, main_window):
        '''
        Initialize the FilesTab with buttons for selecting data directories,    
        and lists of available data files for each bench.
        '''
        super().__init__()
        self.main = main_window  # Reference to MainWindow for shared state and callbacks

        HBox = QHBoxLayout()
        self.setLayout(HBox)

        # ROTOR data directory
        V = QVBoxLayout()
        
        btn = QPushButton("Select ROTOR data directory")
        btn.setMinimumHeight(40)
        btn.setStyleSheet("background-color: #eee8aa;")  # Darker ivory
        btn.clicked.connect(self.select_ROTOR_B_dir)
        V.addWidget(btn)
        
        self.ROTOR_B_file_list_widget = QGroupBox("Bdx ROTOR <ROTOR_*.txt> or <FREE_*.txt> files")
        self.ROTOR_B_file_list_layout = QVBoxLayout(self.ROTOR_B_file_list_widget)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.ROTOR_B_file_list_widget)
        V.addWidget(scroll_area)
        
        HBox.addLayout(V)

        # LILLE ROTOR data directory
        V = QVBoxLayout()
        
        self.button_L_data_dir = QPushButton("Select LILLE rotor bench directory")
        self.button_L_data_dir.setMinimumHeight(40)
        self.button_L_data_dir.setStyleSheet("background-color: #eee8aa;")  # Darker ivory
        self.button_L_data_dir.clicked.connect(self.select_ROTOR_L_dir)
        V.addWidget(self.button_L_data_dir)
        
        self.ROTOR_L_file_list_widget = QGroupBox("LILLE rotor <*.csv> files")
        self.ROTOR_L_file_list_layout = QVBoxLayout(self.ROTOR_L_file_list_widget)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.ROTOR_L_file_list_widget)
        V.addWidget(scroll_area)
        
        HBox.addLayout(V)

        # SIMUL data directory
        V = QVBoxLayout()
        
        self.button_S_data_dir = QPushButton("Select SIMULATION rotor directory")
        self.button_S_data_dir.setMinimumHeight(40)
        self.button_S_data_dir.setStyleSheet("background-color: #eee8aa;")  # Darker ivory
        self.button_S_data_dir.clicked.connect(self.select_SIMUL_dir)
        V.addWidget(self.button_S_data_dir)
        
        self.ROTOR_S_file_list_widget = QGroupBox("SIMULATION rotor <Bsimul_*.txt> files")
        self.ROTOR_S_file_list_layout = QVBoxLayout(self.ROTOR_S_file_list_widget)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.ROTOR_S_file_list_widget)
        V.addWidget(scroll_area)
        
        HBox.addLayout(V)
        
        self.button_S_data_dir.setEnabled(True)
        self.ROTOR_S_file_list_widget.setEnabled(True)


    def select_ROTOR_B_dir(self):
        '''
        Select the ROTOR data directory.
        '''
        data_dir = QFileDialog.getExistingDirectory(self, "Directory for the *.txt ROTOR bench files")
        
        if data_dir:
            self.main.ROTOR_B_data_dir = Path(data_dir)
            self.ROTOR_B_file_list_widget.setTitle(f'*.TXT in <{data_dir}>')
            self.update_ROTOR_B_file_list()
            
            # Clear previous plots and reset states    
            self.main.rotor_bdx_tab.canvas.clear()            
            self.main.set_state('ROTOR', False)
            self.main.set_state('FREE', False)
            self.main.ROTOR_B_txt_file = None


    def select_ROTOR_L_dir(self):
        '''
        Select the LILLE ROTOR data directory.
        '''
        data_dir = QFileDialog.getExistingDirectory(self, "Directory for the *.CSV LILLE ROTOR bench files")
        
        if data_dir:
            self.main.ROTOR_L_data_dir = Path(data_dir)
            self.ROTOR_L_file_list_widget.setTitle(f'*.CSV in <{data_dir}>')
            self.update_ROTOR_L_file_list()
            
            # Clear previous plots and reset states
            self.main.rotor_lille_tab.canvas.clear()
            self.main.set_state('ROTOR_L', False)
            self.main.ROTOR_L_txt_file = None


    def select_SIMUL_dir(self):
        '''
        Select the SIMULATION ROTOR data directory.
        ''' 
        data_dir = QFileDialog.getExistingDirectory(self, "Directory for the *.TXT SIMULATION ROTOR bench files")
        
        if data_dir:
            self.main.SIMUL_data_dir = Path(data_dir)
            self.ROTOR_S_file_list_widget.setTitle(f'*.TXT in <{data_dir}>')
            self.update_SIMUL_file_list()

            # Clear previous plots and reset states
            self.main.simul_tab.canvas.clear()
            self.main.set_state('SIMUL', False)
            self.main.SIMUL_txt_file = None


    def update_ROTOR_B_file_list(self):
        '''
        Update the list of ROTOR TXT files in the GUI.
        '''
        layout   = self.ROTOR_B_file_list_layout
        data_dir = self.main.ROTOR_B_data_dir

        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                layout.removeWidget(widget)
                widget.setParent(None)
                del widget

        try:
            for file_path in sorted(data_dir.iterdir()):
                if file_path.name.lower().endswith(".txt"):
                    rb = QRadioButton(file_path.name)
                    rb.clicked.connect(lambda state, path=file_path, btn=rb: self.process_ROTOR_B_file(path, btn))
                    layout.addWidget(rb)
        except Exception as e:
            print(e)
            pass

    def update_ROTOR_L_file_list(self):
        '''
        Update the list of LILLE ROTOR CSV files in the GUI.
        '''
        layout   = self.ROTOR_L_file_list_layout
        data_dir = self.main.ROTOR_L_data_dir

        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                layout.removeWidget(widget)
                widget.setParent(None)
                del widget

        try:
            for file_path in sorted(data_dir.iterdir()):
                if file_path.name.lower().endswith(".csv"):
                    rb = QRadioButton(file_path.name)
                    rb.clicked.connect(lambda state, path=file_path, btn=rb: self.process_ROTOR_L_file(path, btn))
                    layout.addWidget(rb)
        except Exception as e:
            print(e)
            pass


    def update_SIMUL_file_list(self):
        '''
        Update the list of SIMULATION TXT files in the GUI.
        '''
        layout  = self.ROTOR_S_file_list_layout
        data_dir = self.main.SIMUL_data_dir

        if data_dir.is_dir() is False:
            return
        
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                layout.removeWidget(widget)
                widget.setParent(None)
                del widget

        try:
            for file_path in sorted(data_dir.iterdir()):
                if file_path.name.lower().startswith("bsimul_r") and file_path.name.lower().endswith(".txt"):
                    rb = QRadioButton(file_path.name)
                    rb.clicked.connect(lambda state, path=file_path, btn=rb: self.process_SIMUL_file(path, btn))
                    layout.addWidget(rb)
        except Exception as e:
            print(e)
            pass

    def process_ROTOR_B_file(self, filepath, button):
        '''
        Process the selected ROTOR TXT file.
        ''' 
        # Fix the problem when there is only one file in the list
        if self.ROTOR_B_file_list_layout.count() == 1:
            button.setChecked(True)
            
        # If the file is already selected, do nothing
        if self.main.ROTOR_B_txt_file == filepath:
            return
        
        if filepath.name.startswith("FREE") or filepath.name.startswith("ROTOR"):

            self.main.ROTOR_B_txt_file = filepath
            DATA, list_pos, step_angle = read_file_ROTOR(filepath)
            DATA = self.main.ROTOR_B_reshape_magnetic_field(DATA, list_pos)   
            
            # set the step angle
            self.main.rotor_bdx_tab.step_angle = step_angle
            self.main.all_fields_tab.ROTOR_B_shift.setSuffix(f' x{step_angle}°')
            self.main.all_fields_tab.ROTOR_B_shift.setFastStep(10*step_angle)
            
            # Update the list of Z positions in the ROTOR_B tab
            self.main.rotor_bdx_tab.list_pos = list_pos
            
            # Let the data be accessible from main window fot the othet tabs
            self.main.ROTOR_B_DATA = DATA        

            self.main.rotor_bdx_tab.activate_plotButtons()
            self.main.tabs.setCurrentIndex(1)
                        
            if filepath.name.startswith("FREE"):
                self.main.rotor_bdx_tab.plot_FREE()
                self.main.set_state('ROTOR', False)
                self.main.set_state('FREE', True)
                #self.main.set_state('ROTOR_B_L_S', False)
                self.main.all_fields_tab.ROTOR_B_checkBtn.setChecked(False)
                self.main.all_fields_tab.ROTOR_B_checkBtn.setEnabled(False)

                
            elif filepath.name.startswith("ROTOR"):
                self.main.rotor_bdx_tab.plot_ROTOR(plot_superposed=True)
                self.main.set_state('FREE', False)
                self.main.set_state('ROTOR', True)
                self.main.set_state('ROTOR_B_L_S', True)
                self.main.set_state('ROTOR_B', True)
                self.main.all_fields_tab.ROTOR_B_checkBtn.setChecked(True)
                self.main.all_fields_tab.ROTOR_B_checkBtn.setEnabled(True)
        else:
            message = f'File name <{filepath}> does not start with\nROTOR_... or FREE_'
            QMessageBox.warning(self, 'Warning', message)
    

    def process_ROTOR_L_file(self, filepath, button):
        '''
        Process the selected LILLE ROTOR CSV file.
        '''
        # Fix the problem when there is only one file in the list
        if self.ROTOR_L_file_list_layout.count() == 1:
            button.setChecked(True)
            
        # If the file is already selected, do nothing
        if self.main.ROTOR_L_txt_file == filepath:
            return

        # Plot the ROTOR_L data in the ROTOR_L tab        
        if filepath.name.lower().endswith('.csv'):
            button.setChecked(True)
            self.main.ROTOR_L_txt_file = filepath
            self.main.set_state('LILLE', True)
            self.main.set_state('ROTOR_B_L_S', True)
            self.main.set_state('ROTOR_L', True)
            
            # Read the data when a file is selected
            DATA = read_file_ROTOR_L(self.main.ROTOR_L_txt_file)
            # Let the data be accessible from main window fot the other tabs
            self.main.ROTOR_L_DATA = DATA
            
            # Run the plot method:
            self.main.rotor_lille_tab.plot_ROTOR(plot_superposed=True)
            self.main.all_fields_tab.ROTOR_L_checkBtn.setChecked(True)
            self.main.tabs.setCurrentIndex(2)
        else:
            message = 'Please select a Bsimu...txt file'
            QMessageBox.warning(self, 'Warning', message)


    def process_SIMUL_file(self, filepath, button):
        '''
        Process the selected SIMULATION data file.
        '''
        # Fix the problem when there is only one file in the list
        if self.ROTOR_S_file_list_layout.count() == 1:
            button.setChecked(True)
            
        # If the file is already selected, do nothing
        if self.main.SIMUL_txt_file == filepath:
            return
                
        if filepath.name.lower().startswith('bsimul_'):
            self.main.SIMUL_txt_file = filepath

            # Read the data when a file is selected
            DATA, list_dist = read_file_SIMUL_ROTOR(self.main.SIMUL_txt_file)
            print(f'Found {list_dist=} in SIMUL file')
            if DATA is None:
                message = f'File <{filepath.name}> is corrupted or has an invalid format'
                QMessageBox.warning(self, 'Warning', message)
                return

            button.setChecked(True)
            self.main.set_state('SIMUL', True)
            self.main.set_state('ROTOR_B_L_S', True)
            self.main.set_state('ROTOR_S', True)            
            
            # Update the list of distances in the SIMUL tab
            self.main.simul_tab.list_dist = list_dist
            # Let the data be accessible from main window fot the other tabs
            self.main.SIMUL_DATA = DATA

            ret = self.main.simul_tab.plot_SIMUL(plot_superposed=True)
            self.main.all_fields_tab.ROTOR_S_checkBtn.setChecked(True)
            if ret == -1: 
                self.main.simul_tab.canvas.clear()
                self.main.SIMUL_txt_file = None
                self.main.set_state('SIMUL', False)
                self.main.set_state('ROTOR_S', False)
                self.main.all_fields_tab.ROTOR_S_checkBtn.setChecked(False)
            
            else:
                self.main.tabs.setCurrentIndex(3)
        else:
            message = 'Please select a Bsimu...txt file'
            QMessageBox.warning(self, 'Warning', message)

#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QFileDialog, QMessageBox
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from magnetic_canvas import MagneticPlotCanvas

from tools import read_file_FREE, build_XYZ_name_with_tuple

class RotorBdxTab(QWidget):
    '''
    Tab for displaying and analyzing magnetic field data from the ROTOR bench at ENSAM Bordeaux.
    '''
    
    # Declare attributes for memory optimization
    __slots__ = ('main', 'XYZ', 'btn_free_stat', 'list_pos', 'canvas', 'toolbar_B')
    
    def __init__(self, main_window):
        '''
        Initialize the RotorBdxTab with buttons for plotting ROTOR and FREE data,
        checkboxes for selecting components, and a matplotlib canvas for visualization.
        '''
        super().__init__()
        
        self.main = main_window              # Reference to MainWindow for shared state and callbacks
        self.XYZ  = main_window.default_XYZ.copy()  # Wether to plot the X,Y,Z components for ROTOR_B plots
        self.btn_free_stat  = None           # the Checkbox button to display or not statistics for FREE data
        self.list_pos       = None           # List of Z positions for ROTOR Bdx found when reading data file
        self.canvas         = None           # The MagneticPlotCanvas for plotting
        self.toolbar_B      = None           # The NavigationToolbar for the canvas
        self.step_angle     = None           # the step angle 
       
        # Main layout
        VBox = QVBoxLayout()
        self.setLayout(VBox)

        # Controls layout
        H = QHBoxLayout()
        H.addStretch()

        self.main.dict_plot_widgets['ROTOR'] = []
        self.main.dict_plot_widgets['FREE']  = []

        labels    = ('Plot ROTOR data', 'Plot ROTOR PSD', 'Plot ROTOR ColorMap', 'Plot FREE data')
        callbacks = (self.plot_ROTOR, None, None, self.plot_FREE)
        for label, callback in zip(labels, callbacks):
            btn = QPushButton(label)
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(120)
            btn.setCheckable(False)
            if 'ROTOR PSD' in label:
                btn.clicked.connect(lambda: self.plot_ROTOR(fft=True))
            elif 'ROTOR ColorMap' in label:
                btn.clicked.connect(lambda: self.plot_ROTOR(colormap=True))
            else:
                btn.clicked.connect(callback)
            H.addWidget(btn)
            if 'ROTOR' in label : 
                self.main.dict_plot_widgets['ROTOR'].append(btn)
            elif 'FREE' in label:
                self.main.dict_plot_widgets['FREE'].append(btn)
            btn.setEnabled(False)    

        H.addStretch()
        btn = QPushButton('Save Plot')
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(80)
        btn.setCheckable(False)
        btn.clicked.connect(self.save_current_plot)
        H.addWidget(btn)
        btn.setEnabled(False)    
        self.main.dict_plot_widgets['ROTOR'].append(btn)
        self.main.dict_plot_widgets['FREE'].append(btn)
            
        H.addStretch()
        btn = QCheckBox('display stat')
        btn.setChecked(True)
        btn.setEnabled(False)
        btn.stateChanged.connect(self.plot_FREE)
        self.main.dict_plot_widgets['FREE'].append(btn)
        self.btn_free_stat = btn
        H.addWidget(btn)

        # XYZ component checkboxes
        etiqs, colors = ('Radial (X)', 'Axial (Y)', 'tang. (Z)'), ('red', 'green', 'blue')
        for etiq, lab, color in zip(etiqs, ('X', 'Y', 'Z'), colors):
            btn = QCheckBox(etiq)
            btn.setChecked(self.XYZ[lab])
            btn.setStyleSheet(f'color: {color}')
            btn.stateChanged.connect(lambda state, label=lab: self.set_XYZ(state, label))
            self.main.dict_plot_widgets['ROTOR'].append(btn)
            self.main.dict_plot_widgets['FREE'].append(btn)
            btn.setEnabled(False)
            H.addWidget(btn)

        VBox.addLayout(H)

        # Plot canvas and toolbar
        self.canvas  = MagneticPlotCanvas(self.main)
        self.toolbar = NavigationToolbar(self.canvas, self)
        VBox.addWidget(self.canvas)
        VBox.addWidget(self.toolbar)
        

    def set_XYZ(self, state, lab):
        '''
        Set which components (X, Y, Z) to plot for ROTOR_B and FREE data and replots the data.
        '''
        self.XYZ[lab] = state//2
        if self.main.curr_plt_info_B['func']:
            self.main.curr_plt_info_B['func']()


    def activate_plotButtons(self):
        '''
        Activate the plot buttons depending on the selected file (ROTOR or FREE)
        '''
        assert self.main.ROTOR_B_txt_file is not None
        
        file = self.main.ROTOR_B_txt_file.name
        if 'ROTOR' in file:
            tag = 'ROTOR'
        elif 'FREE' in file:
            tag = 'FREE'
            
        for key in self.main.dict_plot_widgets.keys():
            if key == tag:
                for btn in self.main.dict_plot_widgets[key]:
                    btn.setEnabled(True)
            
    def plot_ROTOR(self, colormap=False, fft=False, plot_superposed=False):
        '''
        Plot the ROTOR_B magnetic field using the selected file and options.
        '''
        if self.main.ROTOR_B_txt_file is None:
            return            
                            
        if colormap and len(self.list_pos) <  2:
            message = 'Data file must have at least 2 Zpos to plot a colormap\nPlease select another file'''
            QMessageBox.warning(self, 'Warning', message)
            self.list_pos = []
            return

        # Check there is at least one component to plot
        xyz = tuple(self.XYZ.values())
        if sum(xyz) == 0:
            message = 'You must select at least one component X,Y, or Z'
            QMessageBox.warning(self, 'Warning', message)
            return        
 
        # plot the data
        if colormap:
            self.main.curr_plt_info_B['func']  = lambda: self.plot_ROTOR(colormap=True)
            self.main.curr_plt_info_B['param'] = 'color'
            self.canvas.colormap_magField()
        else:
            if fft:
                self.main.curr_plt_info_B['func'] = lambda: self.plot_ROTOR(fft=True)
                self.main.curr_plt_info_B['param'] = 'fft'
            else:
                self.main.curr_plt_info_B['func'] = self.plot_ROTOR
                self.main.curr_plt_info_B['param'] = 'plot'                 
            self.canvas.plot_magField_at_positions()
                    
        if plot_superposed:
            # Plot also the ROTOR_B data in the SUPERPOSED ROTOR fields tab
            self.main.all_fields_tab.update_zpos_combo()
            self.main.all_fields_tab.plot_ROTOR_fields()

        return
        
    def plot_FREE(self):
        '''
        To plot the data from the FREE bench (.txt file)
        '''
        if self.main.ROTOR_B_txt_file is None:
            return
        
        DATA = read_file_FREE(self.main.ROTOR_B_txt_file)
        self.main.ROTOR_B_DATA = DATA
        
        # plot the data
        self.canvas.plot_magField()
        self.main.curr_plt_info_B['func'] = self.plot_FREE
        self.main.curr_plt_info_B['param'] = 'free'

        return 


    def save_current_plot(self):
        '''
        Save the current plot of the ROTOR_B data in a PNG file.  
        '''
        if self.main.ROTOR_B_txt_file is None:
            return
        
        fig       = self.canvas.figure
        png_dir   = Path(self.main.ROTOR_B_data_dir, 'PNG')
        file_name = self.main.ROTOR_B_txt_file.name
        
        if not png_dir.exists():
            png_dir.mkdir(exist_ok=True)
        
        XYZ = build_XYZ_name_with_tuple(self.XYZ)
        
        param = self.main.curr_plt_info_B['param']
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
            file_name, _ = QFileDialog.getSaveFileName(self, "Save plot", str(fig_path), "PNG files (*.png)")
            if file_name: 
                fig.savefig(file_name)
        else:
            QMessageBox.warning(self, 'Warning', 'No plot to save')
        return
    

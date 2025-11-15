#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#
from pathlib import Path

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QFileDialog, QMessageBox, QLabel)
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from magnetic_canvas import MagneticPlotCanvas
from FastSpinBox import FastStepSpinBox

from tools import build_XYZ_name_with_tuple

class RotorLilleTab(QWidget):
    '''
    Tab for displaying axial and radial components of magnetic field
    measured on the Lille ROTOR bench.
    '''
    # Declare attributes for memory optimization
    __slots__ = ('main', 'XYZ', 'ROTOR_L_sel_Zpos', 'canvas', 'toolbar')
    
    def __init__(self, main_window):
        '''
        Initialize the RotorLilleTab with buttons for plotting ROTOR_L data,    
        checkboxes for selecting components, and a matplotlib canvas for visualization.
        '''
        super().__init__()
        
        self.main = main_window                     # Reference to MainWindow for shared state and callbacks
        self.XYZ  = main_window.default_XYZ.copy() # Wether to plot the X,Y,Z components for ROTOR_B plots
        
        self.ROTOR_L_sel_Zpos = 0                   # The Zpos selected in the Lille ROTOR data
        
        # Main layout
        VBox = QVBoxLayout()
        self.setLayout(VBox)

        # Controls layout
        H = QHBoxLayout()
        H.addStretch()

        self.main.dict_plot_widgets['ROTOR_L'] = []

        btn = QPushButton('Plot ROTOR data')
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(120)
        btn.setCheckable(False)
        btn.clicked.connect(self.plot_ROTOR)
        self.main.dict_plot_widgets['ROTOR_L'].append(btn)
        btn.setEnabled(False)    
        H.addWidget(btn)

        # The SpinBox to choose the Zpos in the ROTOR_B_L data
        lab = QLabel('Zpos (mm)')
        self.ROTOR_L_Zpos = FastStepSpinBox()
        sb = self.ROTOR_L_Zpos
        sb.setRange(-7, 144)
        sb.setSingleStep(1)
        sb.setFastStep(10)
        sb.setValue(self.ROTOR_L_sel_Zpos)
        sb.setEnabled(False)
        sb.setFixedHeight(25)
        sb.setToolTip('Select the Zpos to plot')
        sb.valueChanged.connect(lambda value: self.zpos_L_changed(value))
        self.main.dict_plot_widgets['ROTOR_L'].append(lab)
        self.main.dict_plot_widgets['ROTOR_L'].append(sb)
        H.addWidget(lab)
        H.addWidget(sb)
        
        H.addStretch()
        
        btn = QPushButton('Save Plot')
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(80)
        btn.setCheckable(False)
        btn.clicked.connect(self.save_current_plot)
        H.addWidget(btn)
        self.main.dict_plot_widgets['ROTOR_L'].append(btn)
        btn.setEnabled(False)    
        
        H.addStretch()
        
        etiqs, colors = ('Radial (X)', 'Axial (Y)', 'tang. (Z)'), ('red', 'green', 'blue')
        for etiq, lab, color in zip(etiqs, ('X', 'Y', 'Z'), colors):
            btn = QCheckBox(etiq)
            btn.setChecked(self.XYZ[lab])
            btn.setStyleSheet(f'color: {color}')
            btn.stateChanged.connect(lambda state, label=lab: self.set_XYZ(state, label))
            self.main.dict_plot_widgets['ROTOR_L'].append(btn)
            btn.setEnabled(False) 
            H.addWidget(btn)
        VBox.addLayout(H)

        # Plot canvas and toolbar
        self.canvas  = MagneticPlotCanvas(self.main)
        self.toolbar = NavigationToolbar(self.canvas, self)
        VBox.addWidget(self.canvas)
        VBox.addWidget(self.toolbar)
 
    def set_XYZ(self, state, lab):
        self.XYZ[lab] = state//2
        self.plot_ROTOR()

    def zpos_L_changed(self, value):
        '''
        Handle Zpos selection in the ROTOR_L data (LILLE rotor bench).
        '''
        self.ROTOR_L_sel_Zpos = value
        self.plot_ROTOR()   

    def plot_ROTOR(self, plot_superposed=False):
        '''
        Plot the ROTOR_L magnetic field using the selected file and options.
        '''
        if self.main.ROTOR_L_txt_file is None : return
                        
        # Check there is currently at least one component to plot
        xyz = tuple(self.XYZ.values())
        if sum(xyz) == 0:
            message = f'You must select at least one component X,Y, or Z'
            QMessageBox.warning(self, 'Warning', message)
            return
        
        # plot the data that has been read when the file was selected
        self.canvas.plot_ROTOR_L_for_Zpos()
        
        if plot_superposed:
            # Plot also the SIMUL data in the SUPERPOSED ROTOR fields tab
            self.main.all_fields_tab.plot_ROTOR_fields()
      
        return

    def save_current_plot(self):
        '''
        Save the current plot as a PNG file in the PNG subdirectory of the data directory.
        The file name is based on the selected data file and the plot type.
        '''
        
        if self.main.ROTOR_L_txt_file is None : return
        
        fig       = self.canvas.figure
        png_dir   = Path(self.main.ROTOR_L_data_dir, 'PNG')
        file_name = self.main.ROTOR_L_txt_file.name
        
        if not png_dir.exists(): png_dir.mkdir(exist_ok=True)
        
        XYZ = build_XYZ_name_with_tuple(self.XYZ)
        
        fig_path = Path(png_dir, file_name.replace('.txt', f'_Lille_{XYZ}.png'))

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
    

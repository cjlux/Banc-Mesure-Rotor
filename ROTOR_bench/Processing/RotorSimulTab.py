#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QFileDialog, QMessageBox
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from magnetic_canvas import MagneticPlotCanvas

from tools import build_XYZ_name_with_tuple

class RotorSimulTab(QWidget):
    '''
    Tab for displaying axial and radial components of simulated magnetic field
    for different rotor-sensor distances.
    '''
    # Declare attributes for memory optimization
    __slots__ = ('main', 'XYZ', 'list_dist', 'canvas', 'toolbar')
    
    def __init__(self, main_window):
        '''
        Initialize the RotorSimulTab with buttons for plotting SIMUL data,
        checkboxes for selecting components, and a matplotlib canvas for visualization.
        '''
        super().__init__()
        
        self.main = main_window             # Reference to MainWindow for shared state and callbacks):
        self.XYZ  = main_window.default_XYZ # Wether to plot the X,Y,Z components for ROTOR_B plots

        self.list_dist = []                 # List of distances found in the SIMUL data file

        VBox = QVBoxLayout()
        self.setLayout(VBox)

        H = QHBoxLayout()
        H.addStretch()

        self.main.dict_plot_widgets['SIMUL'] = []

        btn = QPushButton('Plot SIMUL data')
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(120)
        btn.setCheckable(False)
        btn.clicked.connect(self.plot_SIMUL)
        self.main.dict_plot_widgets['SIMUL'].append(btn)
        btn.setEnabled(False)    
        H.addWidget(btn)
        H.addStretch()
        
        btn = QPushButton('Save Plot')
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(80)
        btn.setCheckable(False)
        btn.clicked.connect(self.save_current_plot)
        H.addWidget(btn)
        self.main.dict_plot_widgets['SIMUL'].append(btn)
        btn.setEnabled(False)    
        H.addStretch()

        etiqs, colors = ('Radial (X)', 'Axial (Y)', 'tang. (Z)'), ('red', 'green', 'blue')
        for etiq, lab, color in zip(etiqs, ('X', 'Y', 'Z'), colors):
            btn = QCheckBox(etiq)
            btn.setChecked(self.XYZ[lab])
            btn.setStyleSheet(f'color: {color}')
            btn.stateChanged.connect(lambda state, label=lab: self.set_XYZ(state, label))
            self.main.dict_plot_widgets['SIMUL'].append(btn)
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
        Set which components (X, Y, Z) to plot for SIMUL data and replots the data.
        '''
        self.XYZ[lab] = state//2
        self.plot_SIMUL()
        
        
    def plot_SIMUL(self, plot_superposed=False):
        """
        Plot axial and radial components from the selected SIMUL file in FilesTab.
        """
        if self.main.SIMUL_txt_file is None: return
                        
        # Check there is currently at least one component to plot
        xyz = tuple(self.XYZ.values())
        if sum(xyz) == 0:
            message = f'You must select at least one component X,Y, or Z'
            QMessageBox.warning(self, 'Warning', message)
            return

        # plot the data that has been read when the SIMUL file was selected
        ret = self.canvas.plot_SIMUL_magField()
        
        if ret == -1: return ret
        
        if plot_superposed:
            # Plot also the SIMUL data in the SUPERPOSED ROTOR fields tab
            self.main.all_fields_tab.update_dist_combo()
            self.main.all_fields_tab.plot_ROTOR_fields()
            
        return

    def save_current_plot(self):
        '''
        Save the current plot as a PNG file in the PNG subdirectory of the data directory.
        '''
        if self.main.SIMUL_txt_file is None: return
        
        fig       = self.canvas.figure
        png_dir   = Path(self.main.SIMUL_data_dir  , 'PNG')
        file_name = self.main.SIMUL_txt_file.name
        
        if not png_dir.exists(): png_dir.mkdir(exist_ok=True)
        
        XYZ = build_XYZ_name_with_tuple(self.XYZ)        
        fig_path = Path(png_dir, file_name.replace('.txt', f'_PLOT_{XYZ}.png'))            

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
    

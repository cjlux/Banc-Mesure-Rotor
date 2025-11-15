#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#
from pathlib import Path

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QFileDialog, QMessageBox, QGroupBox, QLabel, QComboBox)
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from magnetic_canvas import MagneticPlotCanvas
from PyQt5.QtCore import Qt

from tools import build_XYZ_name_with_tuple
from FastSpinBox import FastStepSpinBox


class RotorSuperposedTab(QWidget):
    '''
    Tab for superposing plots from ROTOR_B and ROTOR_L data files.
    '''
    # Declare attributes for memory optimization
    __slots__ = ('main', 'XYZ', 
                 'ROTOR_B_group_box', 'ROTOR_B_checkBtn', 'ROTOR_B_Zpos_combo', 'ROTOR_B_sel_Zpos',
                 'ROTOR_L_group_box', 'ROTOR_L_checkBtn', 'ROTOR_L_sel_Zpos', 'ROTOR_L_shift_angle',
                 'ROTOR_S_group_box', 'ROTOR_S_checkBtn', 'ROTOR_S_dist_combo', 'ROTOR_S_sel_dist',
                 'canvas', 'toolbar')
    
    def __init__(self, main_window):
        '''
        Initialize the RotorSuperposedTab with buttons for plotting ROTOR_B and ROTOR_L data,
        checkboxes for selecting components, and a matplotlib canvas for visualization.
        '''
        super().__init__()
        
        self.main = main_window             # Reference to MainWindow for shared state and callbacks
        self.XYZ  = main_window.default_XYZ.copy() # Wether to plot the X,Y,Z components for ROTOR_B plots
        
        self.ROTOR_B_group_box   = None   # GroupBox for ROTOR_B controls
        self.ROTOR_B_checkBtn    = None   # Whether the ROTOR_B must be displayed or not
        self.ROTOR_B_Zpos_combo  = None   # ComboBox to select the Zpos for the ROTOR_B data
        self.ROTOR_B_shift       = None   # the shift angle widget
        self.ROTOR_B_sel_Zpos    = 0      # The selected Zpos selected for ROTOR_B data
        self.ROTOR_B_shift_angle = 0      # the shift angle for the ROTOR_B file
        self.ROTOR_B_sel         = 1      # the flag associated to the ROTOR_B_checkBtn check button 
        
        self.ROTOR_L_group_box   = None   # GroupBox for ROTOR_L controls
        self.ROTOR_L_checkBtn    = None   # Whether the ROTOR_L must be displayed or not
        self.ROTOR_L_sel_Zpos    = 0      # the selected Z position in the ROTOR_L file
        self.ROTOR_L_shift_angle = 0      # the selected angle in the ROTOR_L file
        self.ROTOR_L_sel         = 1      # the flag associated to the ROTOR_L_checkBtn check button 
        
        self.ROTOR_S_group_box   = None   # GroupBox for the SIMULATION    
        self.ROTOR_S_checkBtn    = None   # Whether the SIMUL must be displayed or not
        self.ROTOR_S_dist_combo  = None   # ComboBox to select the distance for the SIMUL data
        self.ROTOR_S_sel_dist    = 0      # The selected distance for SIMUL data
        self.ROTOR_S_shift_angle = 0      # the shift angle for the ROTOR_B file
        self.ROTOR_S_sel         = 1      # the flag associated to the ROTOR_S_checkBtn check button 

        VBox = QVBoxLayout()
        self.setLayout(VBox)                

        H = QHBoxLayout()
        H.addStretch()
        
        self.main.dict_plot_widgets['ROTOR_B_L_S'] = []

        # The Button to plot the ROTOR_B data        
        btn = QPushButton('Replot')
        btn.setMinimumHeight(45)
        btn.setMinimumWidth(40)
        btn.setCheckable(False)
        btn.clicked.connect(self.plot_ROTOR_fields)
        H.addWidget(btn)
        btn.setEnabled(False)    
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(btn)

        #
        # The GroupBox for the ROTOR_B data plot:
        #
        self.ROTOR_B_group_box = QGroupBox('')
        ROTOR_B_layout = QHBoxLayout()
        self.ROTOR_B_group_box.setLayout(ROTOR_B_layout)
        H.addWidget(self.ROTOR_B_group_box)
        self.ROTOR_B_group_box.setFixedHeight(45)
        self.ROTOR_B_group_box.setStyleSheet("QGroupBox { background-color: #FFFAEE; }")

        # Add Zpos selection
        check = QCheckBox('ROTOR Bdx')
        check.setLayoutDirection(Qt.RightToLeft)
        check.setChecked(True)
        check.stateChanged.connect(lambda state, label='B': self.set_B_L_S(state, label))
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(check)
        ROTOR_B_layout.addWidget(check)
        self.ROTOR_B_checkBtn = check
        ROTOR_B_layout.addStretch()
        
        lab = QLabel(' Zpos:')
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(lab)
        ROTOR_B_layout.addWidget(lab)
        self.ROTOR_B_Zpos_combo =  QComboBox()
        cb = self.ROTOR_B_Zpos_combo
        cb.setEnabled(False)
        cb.setEditable(False)
        cb.setMaxVisibleItems(50)
        cb.setMaxCount(50)
        cb.currentIndexChanged.connect(self.zpos_B_selected)
        #cb.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        cb.setToolTip('Select the Zpos to plot')
        #cb.setStyleSheet('QComboBox { background-color: white; }')
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(cb)
        ROTOR_B_layout.addWidget(cb)
        
        # The SpinBox to choose the angle shift in the ROTOR_B_L data
        lab = QLabel('shift (°)')
        ROTOR_B_layout.addWidget(lab)
        self.ROTOR_B_shift = FastStepSpinBox()
        sb = self.ROTOR_B_shift
        sb.setRange(-180, 180)
        sb.setSingleStep(1)
        sb.setFastStep(10)
        sb.setValue(0)
        sb.setEnabled(False)
        sb.setFixedHeight(25)
        sb.setToolTip('Select the angle shift to apply to the plot of ROTOR Bdx')
        sb.valueChanged.connect(lambda value: self.angle_shift_changed('B', value))
        ROTOR_B_layout.addWidget(sb)
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(lab)
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(sb)
        
        #
        # The GroupBox for the ROTOR_L data
        #
        self.ROTOR_L_group_box = QGroupBox('')
        ROTOR_L_layout = QHBoxLayout()
        self.ROTOR_L_group_box.setStyleSheet("QGroupBox { background-color: #FFFAEE; }")
        self.ROTOR_L_group_box.setLayout(ROTOR_L_layout)
        H.addWidget(self.ROTOR_L_group_box)
        self.ROTOR_L_group_box.setFixedHeight(45)

        check = QCheckBox('ROTOR Lille')
        check.setLayoutDirection(Qt.RightToLeft)
        check.setChecked(True)
        check.stateChanged.connect(lambda state, label='L': self.set_B_L_S(state, label))
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(check)
        ROTOR_L_layout.addWidget(check)
        self.ROTOR_L_checkBtn = check
        ROTOR_L_layout.addStretch()
        
        # The SpinBox to choose the Zpos in the ROTOR_B_L data
        lab = QLabel('Zpos (mm)')
        ROTOR_L_layout.addWidget(lab)
        
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
        ROTOR_L_layout.addWidget(sb)
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(lab)
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(sb)
        
        # The SpinBox to choose the angle shift in the ROTOR_B_L data
        lab = QLabel('shift (°)')
        ROTOR_L_layout.addWidget(lab)
        self.ROTOR_L_shift = FastStepSpinBox()
        sb = self.ROTOR_B_shift
        sb.setRange(-180, 180)
        sb.setSingleStep(1)
        sb.setFastStep(10)
        sb.setValue(0)
        sb.setEnabled(False)
        sb.setFixedHeight(25)
        sb.setToolTip('Select the angle shift to apply to the plot of ROTOR_L')
        sb.valueChanged.connect(lambda value: self.angle_shift_changed('L', value))
        ROTOR_L_layout.addWidget(sb)
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(lab)
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(sb)

        #
        # The GroupBox pour the ROTOR simulation data
        #
        self.ROTOR_S_group_box = QGroupBox('')
        ROTOR_S_layout = QHBoxLayout()
        self.ROTOR_S_group_box.setStyleSheet("QGroupBox { background-color: #FFFAEE; }")
        self.ROTOR_S_group_box.setLayout(ROTOR_S_layout)
        H.addWidget(self.ROTOR_S_group_box)
        self.ROTOR_S_group_box.setFixedHeight(45)

        check = QCheckBox('ROTOR SIMU')
        check.setLayoutDirection(Qt.RightToLeft)
        check.setChecked(True)
        check.stateChanged.connect(lambda state, label='S': self.set_B_L_S(state, label))
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(check)
        ROTOR_S_layout.addWidget(check)
        self.ROTOR_S_checkBtn = check
        ROTOR_S_layout.addStretch()
        
        lab = QLabel(' dist:')
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(lab)
        ROTOR_S_layout.addWidget(lab)
        
        self.ROTOR_S_dist_combo =  QComboBox()
        cb = self.ROTOR_S_dist_combo
        cb.setEnabled(False)
        cb.setEditable(False)
        cb.setMaxVisibleItems(50)
        cb.setMaxCount(50)
        cb.currentIndexChanged.connect(self.dist_S_selected)
        #cb.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        cb.setToolTip('Select the distance')
        #cb.setStyleSheet('QComboBox { background-color: white; }')
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(cb)
        ROTOR_S_layout.addWidget(cb)

        # The SpinBox to choose the angle shift in the ROTOR_S data
        lab = QLabel('shift (°)')
        ROTOR_S_layout.addWidget(lab)
        self.ROTOR_S_shift = FastStepSpinBox()
        sb = self.ROTOR_S_shift 
        sb.setRange(-180, 180)
        sb.setSingleStep(1)
        sb.setFastStep(10)
        sb.setValue(0)
        sb.setEnabled(False)
        sb.setFixedHeight(25)
        sb.setToolTip('Select the angle shift to apply to the plot of simulated ROTOR')
        sb.valueChanged.connect(lambda value: self.angle_shift_changed('S', value))
        ROTOR_S_layout.addWidget(sb)
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(lab)
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(sb)

        H.addStretch()
        
        # The button to save the current plot as a PNG file
        btn = QPushButton('Save Plot')
        btn.setMinimumHeight(45)
        btn.setMinimumWidth(80)
        btn.setCheckable(False)
        btn.clicked.connect(self.save_current_plot)
        H.addWidget(btn)
        btn.setEnabled(False)    
        self.main.dict_plot_widgets['ROTOR_B_L_S'].append(btn)
        
        H.addStretch()        
        etiqs, colors = ('Radial (X)', 'Axial (Y)', 'tang (Z)'), ('red', 'green', 'blue')
        for etiq, lab, color in zip(etiqs, ('X', 'Y', 'Z'), colors):            
            btn = QCheckBox(etiq)
            btn.setChecked(self.XYZ[lab])
            btn.setStyleSheet(f'color: {color}')            
            btn.stateChanged.connect(lambda state, label=lab: self.set_XYZ(state, label))
            H.addWidget(btn)
            self.main.dict_plot_widgets['ROTOR_B_L_S'].append(btn)
        VBox.addLayout(H)
        
        self.canvas  = MagneticPlotCanvas(main_window)
        self.toolbar = NavigationToolbar(self.canvas, self)
        VBox.addWidget(self.canvas)
        VBox.addWidget(self.toolbar)
        
        self.main.set_state('ROTOR_B_L_S', False)

    def set_XYZ(self, state, lab):
        self.XYZ[lab] = state//2
        if self.main.curr_plt_info_B_L_S['func']:
            self.main.curr_plt_info_B_L_S['func']()
        
    def set_B_L_S(self, state, label):
        '''
        Set whether to display ROTOR_B, ROTOR_L or SIMUL data and replots the data.
        '''
        if label == 'B':
            self.ROTOR_B_sel = state//2
            self.ROTOR_B_Zpos_combo.setEnabled(self.ROTOR_B_sel)
            self.ROTOR_B_shift.setEnabled(self.ROTOR_B_sel)
            
        elif label == 'L':
            self.ROTOR_L_sel = state//2
            self.ROTOR_L_Zpos.setEnabled(self.ROTOR_L_sel==1)
            self.ROTOR_L_shift.setEnabled(self.ROTOR_L_sel)
            
        elif label == 'S':
            self.ROTOR_S_sel = state//2
            self.ROTOR_S_dist_combo.setEnabled(self.ROTOR_S_sel==1)
            self.ROTOR_S_shift.setEnabled(self.ROTOR_S_sel)
        
        if self.main.curr_plt_info_B_L_S['func']:
            self.main.curr_plt_info_B_L_S['func']()
        
    def update_zpos_combo(self):
        '''
        Update the Zpos ComboBox based on the list_pos in the ROTOR_Bdx tab.
        '''
        # Clear existing buttons
        self.ROTOR_B_Zpos_combo.clear()
        
        # Add new buttons
        if self.main.rotor_bdx_tab.list_pos:
            done = False
            for zpos in self.main.rotor_bdx_tab.list_pos:
                self.ROTOR_B_Zpos_combo.addItem(zpos)
                if not done:
                    # Select the first Zpos by default
                    value = int(zpos)
                    self.ROTOR_B_Zpos_combo.setCurrentIndex(0)
                    self.ROTOR_B_sel_Zpos = value
                    done = True

    def update_dist_combo(self):
        '''
        Update the Dist ComboBox based on the list_pos in the ROTOR_S tab.
        '''
        # Clear existing buttons
        self.ROTOR_S_dist_combo.clear()
        
        # Add new buttons
        if self.main.simul_tab.list_dist:
            done = False
            for dist in self.main.simul_tab.list_dist:
                self.ROTOR_S_dist_combo.addItem(dist)
                if not done:
                    # Select the first dist by default
                    value = int(dist)
                    self.ROTOR_S_dist_combo.setCurrentIndex(0)
                    self.ROTOR_S_sel_dist = value
                    done = True

    def zpos_B_selected(self, index):
        '''
        A new Zpos have been selected for ROTOR Bdx data.
        '''
        selected_zpos = self.ROTOR_B_Zpos_combo.itemText(index)
        if selected_zpos == '':
            return
        
        self.ROTOR_B_sel_Zpos = int(selected_zpos)
        # JLC_Debug: print(f"Selected ROTOR_B Zpos: {self.ROTOR_B_sel_Zpos}")
                
        self.plot_ROTOR_fields()
        
    def angle_shift_changed(self, rotor_selection, value):
        '''
        Handle angle shift selection in the ROTOR_Bdx data (BORDEAUX rotor bench).
        '''
        assert rotor_selection in ('B', 'L', 'S')
        
        match rotor_selection:
            case 'B':
                self.ROTOR_B_shift_angle = value
                # JLC_Debug: print(f"Selected ROTOR_B angle shift: {self.ROTOR_B_shift_angle}")                
            case 'L':
                self.ROTOR_L_shift_angle = value
                # JLC_Debug: print(f"Selected ROTOR_L angle shift: {self.ROTOR_L_shift_angle}")                
            case 'S':
                self.ROTOR_S_shift_angle = value
                # JLC_Debug: print(f"Selected ROTOR_S angle shift: {self.ROTOR_S_shift_angle}")
        
        # Update the plot with the new angle shift
        self.plot_ROTOR_fields()   
            
    def zpos_L_changed(self, value):
        '''
        A new Zpos has been selected for the ROTOR_L data (LILLE rotor bench).
        '''
        self.ROTOR_L_sel_Zpos = value
        # JLC_Debug: print(f"Selected ROTOR_L Zpos: {self.ROTOR_L_sel_Zpos}")
        
        self.plot_ROTOR_fields()   
        
    def dist_S_selected(self, index):
        '''
        A new distance have been selected for ROTOR simulation data.
        '''
        selected_dist = self.ROTOR_S_dist_combo.itemText(index)
        if selected_dist == '':
            return
        
        self.ROTOR_S_sel_dist = int(selected_dist)
        # JLC_Debug: print(f"Selected ROTOR_S distance: {self.ROTOR_S_sel_Dist}")
        
        self.plot_ROTOR_fields()   
        
    def plot_ROTOR_fields(self):        
        '''
        To plot a superposition af ROTOR_B,  ROTOR_L and ROTOR_S data versurs rotot angle.
        '''
        
        if self.main.ROTOR_B_txt_file is None:
            # Nothing to plot for ROTOR_B
            self.main.ROTOR_B_data = None
        
        if self.main.ROTOR_L_txt_file is  None:
            # Nothing to plot for ROTOR_L
            self.main.ROTOR_L_data = None

        if self.main.SIMUL_txt_file is None:
            # Nothing to plot for ROTOR SIMULATION
            self.main.ROTOR_S_data = None
        
        # Check there is currently at least one component to plot
        xyz = tuple(self.XYZ.values())
        if sum(xyz) == 0:
            message = 'You must select at least one component X,Y, or Z'
            QMessageBox.warning(self, 'Warning', message)
            return
        
        # plot the data
        self.canvas.plot_ROTOR_B_L_S_for_Zpos()
        self.main.curr_plt_info_B_L_S['func']  = self.plot_ROTOR_fields
        self.main.curr_plt_info_B_L_S['param'] = 'plot_B_L_S'

        return 
    
    def save_current_plot(self):
        '''
        Save the current plot of the superposition of the rotor fields.
        '''
        
        fig = self.canvas.figure
        
        # Create a PNG directory under the current working directory:
        png_dir   = Path.cwd() / 'PNG'
        if not png_dir.exists():
            png_dir.mkdir(exist_ok=True)
        
        XYZ = build_XYZ_name_with_tuple(self.XYZ)
        
        Zpos_B  = self.ROTOR_B_sel_Zpos
        Zpos_L  = self.ROTOR_L_sel_Zpos
        shift_L = self.ROTOR_L_shift_angle
        shift_B = self.ROTOR_B_shift_angle
        
        file_name = "Superposed_"
        if self.main.ROTOR_B_txt_file is not None:
            file_name  += f'{self.main.ROTOR_B_txt_file.name}@Zpos-{Zpos_B}mm___'
        if self.main.ROTOR_L_txt_file is not None:
            file_name += f'{self.main.ROTOR_L_txt_file.name}@Zpos-{Zpos_L}mm_shift-{shift_L}__'
        if self.main.SIMUL_txt_file is not None:
            file_name += f'{self.main.SIMUL_txt_file.name}@dist-{self.ROTOR_S_sel_dist}mm__'
        file_name += f'XYZ-{XYZ}.png'
        fig_path = Path(png_dir, file_name)

        if fig:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save plot", str(fig_path), "PNG files (*.png)")
            if file_name:
                fig.savefig(file_name)
        else:
            QMessageBox.warning(self, 'Warning', 'No plot to save')
        return

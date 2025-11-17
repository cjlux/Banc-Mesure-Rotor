#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#

import sys
from shutil import rmtree
from pathlib import Path
import numpy as np
import json

from PyQt5.QtWidgets import (QApplication, QTabWidget, QMainWindow, QCheckBox, 
                             QMessageBox, QAction, QWidgetAction, QColorDialog, QMenu, QWidget, QHBoxLayout)
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QComboBox

from files_tab import FilesTab
from RotorBdxTab import RotorBdxTab
from RotorSimulTab import RotorSimulTab
from RotorLilleTab import RotorLilleTab
from RotorSuperposed import RotorSuperposedTab
from WebBrowserTab import WebBrowserTab
from magnetic_canvas import MagneticPlotCanvas

class MainWindow(QMainWindow):
    ''' 
    Main window for the ROTOR bench data plotting application.  
    It contains tabs for different functionalities and manages shared state and options.
    '''
    # Declare attributes for memory optimization    
    __slots__ = ('saved_options_file', 'default_XYZ', 'dict_plot_widgets',
                 'ROTOR_B_data_dir', 'ROTOR_B_txt_file', 'ROTOR_B_DATA', 'ROTOR_B_list_pos',
                 'ROTOR_L_data_dir', 'ROTOR_L_txt_file', 'ROTOR_L_DATA',
                 'SIMUL_data_dir', 'SIMUL_txt_file', 'SIMUL_DATA',
                 'curr_plt_info_B', 'curr_plt_info_L', 'curr_plt_info_S', 'curr_plt_info_B_L_S',
                 'disp_fileName', 'dict_fileName_btn', 'dict_legend_btn', 
                 'tabs', 'file_tab', 'rotor_bdx_tab', 'rotor_lille_tab', 'simul_tab', 'all_fields_tab')     
    
    def __init__(self):
        super().__init__()
        
        self.saved_options_file    = Path('ROTOR_bench/Processing/saved_options.json')
        self.default_XYZ           = {'X': 1, 'Y': 0, 'Z':1} # The default values for XYZ_B and XYZ_B_L
        self.dict_plot_widgets     = {}

        self.ROTOR_B_data_dir      = Path('_') # the directory containing the ROTOR data files
        self.ROTOR_B_txt_file      = None      # the selected ROTOR_B file to plot (Path)
        self.ROTOR_B_DATA          = None      # The raw ROTOR_B magnetic field after reading file
        self.ROTOR_B_list_pos      = []        # The list of Z positions found in the ROTOR_B data file  

        self.ROTOR_L_data_dir      = Path('_') # the directory containing the LILLE ROTOR data files
        self.ROTOR_L_txt_file      = None      # the selected ROTOR_L file to plot
        self.ROTOR_L_DATA          = None      # The raw ROTOR_L magnetic field after readding file

        self.SIMUL_data_dir        = Path('_') # the directory containing the SIMULATION data files
        self.SIMUL_txt_file        = None      # the selected SIMULATION file to plot
        self.SIMUL_DATA            = None      # The raw SIMULATION magnetic field after reading file

        self.curr_plt_info_B       = {}        # Dictionary of infos on the current plot for the ROTOR_B tab
        self.curr_plt_info_L       = {}        # Dictionary of infos on the current plot for the ROTOR_L tab
        self.curr_plt_info_S       = {}        # Dictionary of infos on the current plot for the SIMUL tab
        self.curr_plt_info_B_L_S   = {}        # Dictionary of infos on the current plot for the ROTOR siperposition tab

        self.dict_fileName_btn     = None      # The checkbox button in the Options menu to display or not file names in plots
        self.disp_fileName         = True      # Flag: whether to display the file name in the plot title
        
        self.legend_inside_plot    = None      # Flag: whether to put legend inside plot or outside plot
        self.dict_legend_btn       = None      # The checkbox button in the Options menu to put legend inside/outside plots
        
        
        self.setWindowTitle("ROTOR bench data plot")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Load options from JSON
        self.load_options_from_json()

        # Initialize tabs
        self.file_tab = FilesTab(self)
        self.tabs.addTab(self.file_tab, "Choose Directory and files")
        self.rotor_bdx_tab = RotorBdxTab(self)
        self.tabs.addTab(self.rotor_bdx_tab, "ROTOR Bench @ENSAM Bdx")
        self.rotor_lille_tab = RotorLilleTab(self)
        self.tabs.addTab(self.rotor_lille_tab, "ROTOR Bench @ENSAM LILLE")
        self.simul_tab = RotorSimulTab(self)
        self.tabs.addTab(self.simul_tab, "ROTOR Simulation")
        self.all_fields_tab = RotorSuperposedTab(self)
        self.tabs.addTab(self.all_fields_tab, "Superposition of ROTOR fields")
        self.web_tab = WebBrowserTab()
        self.tabs.addTab(self.web_tab, "Web Browser")
        
        # Create the menu bar
        self.create_menu_bar()

        self.dict_fileName_btn.setChecked(self.disp_fileName)
        self.dict_legend_btn.setChecked(self.legend_inside_plot)

        # Select the first tab by default
        self.tabs.setCurrentIndex(0)        
        
        
    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Options menu
        options_menu = menu_bar.addMenu("Options")

        # "Show file name in plot title" option
        disp_filename_action = QWidgetAction(self)
        btn = QCheckBox("Show file names in plot titles")
        self.dict_fileName_btn = btn
        btn.setChecked(self.disp_fileName)
        btn.setStyleSheet("QCheckBox { padding-left: 5px; }")
        btn.toggled.connect(self.on_radio_btn_disp_filename)
        disp_filename_action.setDefaultWidget(btn)
        options_menu.addAction(disp_filename_action)

        # show legend insoide/outside plots
        legend_inside_plot_action = QWidgetAction(self)
        btn = QCheckBox("Show legends inside plots")
        self.dict_legend_btn = btn
        btn.setChecked(self.legend_inside_plot)
        btn.setStyleSheet("QCheckBox { padding-left: 5px; }")
        btn.toggled.connect(self.on_radio_btn_legend_inside_plot)
        legend_inside_plot_action.setDefaultWidget(btn)
        options_menu.addAction(legend_inside_plot_action)

        # Submenu for components to plot by default
        components_menu = options_menu.addMenu("Components to plot by default")

        # Plot X
        disp_X_action = QWidgetAction(self)
        btn_X = QCheckBox("Plot X component")
        btn_X.setChecked(self.default_XYZ['X'])
        btn_X.setStyleSheet("QCheckBox { padding-left: 5px; }")
        btn_X.toggled.connect(lambda state, button=btn_X: self.on_disp_XYZ_component(button, X=state))
        disp_X_action.setDefaultWidget(btn_X)
        components_menu.addAction(disp_X_action)

        # Plot Y
        disp_Y_action = QWidgetAction(self)
        btn_Y = QCheckBox("Plot Y component")
        btn_Y.setChecked(self.default_XYZ['Y'])
        btn_Y.setStyleSheet("QCheckBox { padding-left: 5px; }")
        btn_Y.toggled.connect(lambda state, button=btn_Y: self.on_disp_XYZ_component(button, Y=state))
        disp_Y_action.setDefaultWidget(btn_Y)
        components_menu.addAction(disp_Y_action)

        # Plot Z
        disp_Z_action = QWidgetAction(self)
        btn_Z = QCheckBox("Plot Z component")
        btn_Z.setChecked(self.default_XYZ['Z'])
        btn_Z.setStyleSheet("QCheckBox { padding-left: 5px; }")
        btn_Z.toggled.connect(lambda state, button=btn_Z: self.on_disp_XYZ_component(button, Z=state))
        disp_Z_action.setDefaultWidget(btn_Z)
        components_menu.addAction(disp_Z_action)

        # Submenu for color selection
        color_menu = QMenu("Magnetic field colors", self)

        # Helper to create color actions with colored labels
        def add_color_action(label, canvas_attr, comp):
            widget_action = QWidgetAction(self)
            color_label = QLabel(label)
            color_label.setStyleSheet(f"color: {getattr(MagneticPlotCanvas, canvas_attr)[comp]};")
            color_label.setMinimumWidth(140)
            btn = QPushButton("Change")
            btn.setMaximumWidth(70)
            def choose_color():
                dialog_title = f"Choose color for {label}"
                initial_color = QColor(getattr(MagneticPlotCanvas, canvas_attr)[comp])
                color = QColorDialog.getColor(initial_color, self, dialog_title)
                if color.isValid():
                    getattr(MagneticPlotCanvas, canvas_attr)[comp] = color.name()
                    color_label.setStyleSheet(f"color: {color.name()};")
                    self.redraw_all_canvases()
            btn.clicked.connect(choose_color)
            hbox = QHBoxLayout()
            hbox.addWidget(color_label)
            hbox.addWidget(btn)
            hbox.setContentsMargins(0, 0, 0, 0)
            widget = QWidget()
            widget.setLayout(hbox)
            widget_action.setDefaultWidget(widget)
            color_menu.addAction(widget_action)

        # ROTOR Bdx colors
        add_color_action("ROTOR_Bdx X color", "colors_B", "X")
        add_color_action("ROTOR_Bdx Y color", "colors_B", "Y")
        add_color_action("ROTOR_Bdx Z color", "colors_B", "Z")
        # ROTOR LILLE colors
        add_color_action("ROTOR_LILLE X color", "colors_L", "X")
        add_color_action("ROTOR_LILLE Y color", "colors_L", "Y")
        add_color_action("ROTOR_LILLE Z color", "colors_L", "Z")
        # SIMULATION colors
        add_color_action("SIMULATION X color", "colors_S", "X")
        add_color_action("SIMULATION Y color", "colors_S", "Y")
        add_color_action("SIMULATION Z color", "colors_S", "Z")

        options_menu.addMenu(color_menu)

        # Submenu for line style selection (per-component, per-source)
        linestyle_menu = QMenu("Magnetic field line type", self)

        def add_linestyle_action(label, canvas_attr, comp):
            widget_action = QWidgetAction(self)
            label_widget = QLabel(label)
            label_widget.setMinimumWidth(160)

            combo = QComboBox()
            styles = [("Solid", "-"), ("Dashed", "--"), ("DashDot", "-."), ("Dotted", ":")]
            for text, val in styles:
                combo.addItem(text, val)

            # determine current style (fallback to first)
            try:
                current_style = getattr(MagneticPlotCanvas, canvas_attr)[comp]
            except Exception:
                current_style = styles[0][1]
            idx = next((i for i, (_, v) in enumerate(styles) if v == current_style), 0)
            combo.setCurrentIndex(idx)

            def on_style_changed(index):
                style = combo.itemData(index)
                getattr(MagneticPlotCanvas, canvas_attr)[comp] = style
                self.redraw_all_canvases()

            combo.currentIndexChanged.connect(on_style_changed)

            hbox = QHBoxLayout()
            hbox.addWidget(label_widget)
            hbox.addWidget(combo)
            hbox.setContentsMargins(0, 0, 0, 0)
            widget = QWidget()
            widget.setLayout(hbox)
            widget_action.setDefaultWidget(widget)
            linestyle_menu.addAction(widget_action)

        # ROTOR Bdx line types
        add_linestyle_action("ROTOR B line style", 'line_styles', "B")
        add_linestyle_action("ROTOR_L line style", 'line_styles', "L")
        add_linestyle_action("SIMULATION line_style", 'line_styles', "S")

        options_menu.addMenu(linestyle_menu)

        # "Save options" action
        save_options_action = QAction("Save options", self)
        save_options_action.triggered.connect(self.save_options_to_json)
        options_menu.addAction(save_options_action)

        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")
        clean_png_action = QAction("Clean PNG directories", self)
        clean_png_action.triggered.connect(self.clean_png_directories)
        tools_menu.addAction(clean_png_action)

    def on_radio_btn_disp_filename(self, checked):
        '''
        Slot to handle the toggling of the button.
        '''
        if checked:
            print("Show file names in plot titles: Enabled")
            self.disp_fileName = True
        else:
            print("Show file names in plot titles: Disabled")
            self.disp_fileName = False

    def on_radio_btn_legend_inside_plot(self, checked):
        '''
        Slot to handle the toggling of the button.
        '''
        if checked:
            print("Show legends inside plots: Enabled")
            self.legend_inside_plot = True
        else:
            print("Show legends inside plots: Disabled")
            self.legend_inside_plot = False 
            
    def on_disp_XYZ_component(self, w, X=None, Y=None, Z=None):
        '''
        Slot to handle the toggling of the button.
        '''
        message = 'You must select at least one component X,Y, or Z'
        if X is not None: 
            if X + self.default_XYZ['Y'] + self.default_XYZ['Z'] == 0:
                QMessageBox.warning(self, 'Warning', message)            
                w.setChecked(True)
            else:
                self.default_XYZ['X'] = int(X)
                
        if Y is not None: 
            if Y + self.default_XYZ['X'] + self.default_XYZ['Z'] == 0:
                QMessageBox.warning(self, 'Warning', message)            
                w.setChecked(True)
            else:
                self.default_XYZ['Y'] = int(Y)
                
        if Z is not None: 
            if Z + self.default_XYZ['X'] + self.default_XYZ['Y'] == 0:
                QMessageBox.warning(self, 'Warning', message)            
                w.setChecked(True)
            else:
                self.default_XYZ['Z'] = int(Z)
        
    def clean_png_directories(self):
        '''
        Placeholder method for cleaning PNG directories.
        '''
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
                    if dir.exists(): 
                        rmtree(dir)
                    print(f'Deleted directory: {dir}')
        else:
            QMessageBox.information(self, 'Info', 'No PNG directories found')
            print('No PNG directories found')
        
        return
            
                    
    def set_state(self, key, state):
        '''
        Enable or disable the widgets in the dictionary:
        '''
        print(f'set_state: {key} to {state}')
        for widget in self.dict_plot_widgets[key]:
            widget.setEnabled(state)
                

    def ROTOR_B_reshape_magnetic_field(self, DATA, list_pos):
        '''
        Reshape the DATA of a ROTOR_B file to be a 2D array with shape (nb_angles, 1 + 3*nb_Zpos).
        DATA is reshaped to be an array with lines formatted like:
            "# angle[°]; X1_mag [mT]; Y1_mag [mT]; Z1_mag [mT]; X2_mag [mT]; Y2_mag [mT]; Z2_mag [mT];..."
        instead of:
            "# ZPos#; a[°]; X1_mag[mT]; Y1_mag[mT]; Z1_mag[mT]"
        '''
        if DATA.shape[1] == 5:
            nb_col = 1 + 3 * len(list_pos) #  angle col + (X , Y, Z) * nb_Zpo
            nb_row = int(len(DATA)/len(list_pos))
            newDATA = np.ndarray((nb_row, nb_col), dtype=float)

            # copy angle column
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
        
        DATA is already an array with lines formatted like:
            "# angle[°]; X1_mag [mT]; Y1_mag [mT]; Z1_mag [mT]; X2_mag [mT]; Y2_mag [mT]; Z2_mag [mT];..."
        '''
        
        #i_Zpos = list_pos.index(f'{Zpos:03d}')
        i_Zpos = -1
        for item in list_pos:
            i_Zpos += 1
            if int(item) == Zpos:
                break
        assert(i_Zpos >= 0)
        
        # copy X,Y,Z for all Zpos:
        nb_val = 3                  # 3 components X, Y and Z
        new_nb_col = 1 + nb_val     # the angle col + the 3 components X, Y and Z
        nb_row = DATA.shape[0]
        newDATA = np.ndarray((nb_row, new_nb_col), dtype=float)
        # Extract angle column:
        newDATA[:, 0] = DATA[:nb_row, 0].copy()
        # Extract X, Y, Z data for position Zpos:
        try:
            newDATA[:, 1:1+nb_val] = DATA[:, 1+i_Zpos*nb_val:1+(i_Zpos+1)*nb_val]
            DATA = newDATA.copy()
        except Exception as e:
            print(e)
            message = f'index of {Zpos:03d} not found in the list of Zpos:\n{list_pos}. Try another value'
            QMessageBox.warning(self, 'Warning', message)
                       
        return DATA


        
    def save_options_to_json(self):
        '''
        Save the current menu Options choices to saved_options.json.
        '''
        options = {
            "disp_fileName": self.disp_fileName,
            "legend_inside_plots": self.legend_inside_plot,
            "default_XYZ": self.default_XYZ.copy(),
            "colors_B": MagneticPlotCanvas.colors_B.copy(),
            "colors_L": MagneticPlotCanvas.colors_L.copy(),
            "colors_S": MagneticPlotCanvas.colors_S.copy(),
            "line_styles": MagneticPlotCanvas.line_styles.copy()
        }
        try:
            with open(self.saved_options_file, "w") as f:
                json.dump(options, f, indent=4)
            QMessageBox.information(self, "Options Saved", "Options have been saved to saved_options.json")
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save options:\n{e}")

    def load_options_from_json(self):
        '''
        Load the menu Options choices from saved_options.json.
        '''
        try:
            with open(self.saved_options_file, "r") as f:
                options = json.load(f)
            self.disp_fileName = options.get("disp_fileName", True)
            self.legend_inside_plot = options.get("legend_inside_plots", False) 
            self.default_XYZ   = options.get("default_XYZ", {'X': 1, 'Y': 0, 'Z': 1})
            # Load colors if present
            if "colors_B" in options:
                MagneticPlotCanvas.colors_B.update(options["colors_B"])
            if "colors_L" in options:
                MagneticPlotCanvas.colors_L.update(options["colors_L"])
            if "colors_S" in options:
                MagneticPlotCanvas.colors_S.update(options["colors_S"])
            # Load line styles if present
            if "line_styles" in options:
                MagneticPlotCanvas.line_styles.update(options["line_styles"])
        except Exception:
            pass  # Ignore if file doesn't exist or is invalid

    def redraw_all_canvases(self):
        """
        Redraw all MagneticPlotCanvas instances in your tabs.
        """
        try:
            self.rotor_bdx_tab.canvas_B.plot_magField_at_positions()
        except Exception:
            pass
        try:
            self.rotor_lille_tab.canvas_L.plot_ROTOR_L_for_Zpos()
        except Exception:
            pass
        try:
            self.simul_tab.canvas_S.plot_SIMUL_magField()
        except Exception:
            pass
        try:
            self.all_fields_tab.canvas_B_L.plot_ROTOR_B_L_S_for_Zpos()
        except Exception:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1500, 900)
    window.show()
    sys.exit(app.exec_())
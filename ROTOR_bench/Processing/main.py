import os, sys
from pathlib import Path
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QFileDialog,
    QTabWidget, QMainWindow, QLabel, QCheckBox, QScrollArea, QGroupBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from tools import read_file_ROTOR


def parse_data_file(filepath):
    angles, x_vals, y_vals, z_vals = [], [], [], []

    with open(filepath, 'r') as f:
        lines = f.readlines()

    data_started = False
    for line in lines:
        if data_started:
            if line.strip():
                parts = line.strip().split(';')
                if len(parts) == 4:
                    angle = float(parts[0].strip())
                    x = float(parts[1].strip())
                    y = float(parts[2].strip())
                    z = float(parts[3].strip())
                    angles.append(angle)
                    x_vals.append(x)
                    y_vals.append(y)
                    z_vals.append(z)
        elif line.strip().startswith("angle"):
            data_started = True

    return np.array(angles), np.array(x_vals), np.array(y_vals), np.array(z_vals)


class MagneticPlotCanvas(FigureCanvas):
    def __init__(self, main, parent=None):
        
        self.main = main
        self.fig  = Figure(figsize=(5, 4), dpi=100)
        self.ax   = None
        
        super().__init__(self.fig)

    def plot_data(self, angles, x_vals, y_vals, z_vals, title=""):
        self.ax = self.fig.add_subplot(111)
        self.ax.clear()
        self.ax.plot(angles, x_vals, label="X [mT]", marker='o')
        self.ax.plot(angles, y_vals, label="Y [mT]", marker='s')
        self.ax.plot(angles, z_vals, label="Z [mT]", marker='^')
        self.ax.set_xlabel("Angle (°)")
        self.ax.set_ylabel("Champ magnétique (mT)")
        self.ax.set_title(title if title else "Composantes magnétiques vs Angle")
        self.ax.legend()
        self.ax.grid(True)
        self.draw()

    def plot_magField_at_positions(self):
        '''
            To plot magnetic field versus angle, for different Z positions
            of the magnetic sensor.
        '''
        
        filename = self.main.selected_file.name        
        nb_Zpos  = len(self.main.list_pos)
        nb_comp, nb_angle_pos = self.main.ROTOR_magn_field.shape
        assert(nb_comp // 3 == nb_Zpos)
        xyz = (self.main.XYZ['X'], self.main.XYZ['Y'], self.main.XYZ['Z'])
        fft = self.main.plot_fft

        # Check how many magnetic field components to plot:
        nb_plot = sum(xyz)
        if nb_plot == 0: return

        self.fig.clear()
        self.fig.tight_layout = True
        
        if self.ax is not None:
            for ax in self.ax: ax.clear()
                
        self.ax = self.fig.subplots(nb_Zpos, 1, sharex=True, sharey=True)
        if nb_Zpos ==1 : self.ax = [self.ax]
        
        suptitle = ""
        if fft: suptitle += "Spectrum of "
        self.fig.suptitle(suptitle + "Rotor magnetic field", size=16)
        self.fig.text(0.5, .93, f"from <{filename}>", size=9, color="gray", horizontalalignment='center')
        magn_max, magn_min = self.main.ROTOR_magn_field.max(),self.main.ROTOR_magn_field.min()                
        ang_freq_done = False 
                       
        for n, (ax, Zpos) in enumerate(zip(self.ax, self.main.list_pos)):  
            X, Y, Z = self.main.ROTOR_magn_field[3*n:3*n+3]  
            title = ""
            if fft:
                X, Y, Z = np.abs(rfft(X)), np.abs(rfft(Y)), np.abs(rfft(Z))
                XYZmax = max(X.max(), Y.max(), Z.max())
                X, Y, Z = X/XYZmax, Y/XYZmax, Z/XYZmax
                title += "PSD "
                if not ang_freq_done:
                    nb_pt = len(X)
                    f_sampling = 1/(main.angles[1] - main.angles[0])     # sampling frequency in rd^-1
                    ang_freq = np.arange(nb_pt)*f_sampling
                    A = ang_freq
                    ang_freq_done = True

                for psd, color, label, xyz_flag in zip((X, Y, Z), 'rgb', 'XYZ', xyz):
                    if xyz_flag: 
                        markerline, stemlines, baseline = ax.stem(A, psd, color, label=label)
                        markerline.set_markerfacecolor('white')
                        markerline.set_markersize(3.5)
                        baseline.set_color('grey')
                        baseline.set_linewidth(0.5)
            else:
                if xyz[0]: ax.plot(self.main.angles, X, '-or', markersize=0.5, label='X')
                if xyz[1]: ax.plot(self.main.angles, Y, '-og', markersize=0.5, label='Y')
                if xyz[2]: ax.plot(self.main.angles, Z, '-ob', markersize=0.5, label='Z')
                
            title += f"Magnetic field at Z position #{n+1}: {int(Zpos):3d} mm"
            ax.set_title(title, loc='left', fontsize=9)
            if n == 0: 
                if fft: ax.set_ylabel("Normalized PSD")
                else:   ax.set_ylabel("[mT]")
            ax.legend(bbox_to_anchor=(1.1, 1), loc="upper right")
            ax.minorticks_on()
            ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
            ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)
            if fft: ax.set_ylim(0,1.1)
            else:   ax.set_ylim(1.1*magn_min, 1.1*magn_max)

            if n == nb_Zpos-1:
                if fft: ax.set_xlabel(r"Angular frequency [rd$^{-1}$]")
                else:   ax.set_xlabel("rotor angle [°]")
                
            #plt.subplots_adjust(hspace=0.37, right=0.87, top=0.8, bottom=0.12)
            
            '''png_dir = dirname.replace('TXT', 'PNG')
            if not os.path.exists(png_dir): os.mkdir(png_dir)
            XYZ = build_XYZ_name_with_tuple(xyz)
            if fft: fig_path = os.path.join(png_dir, filename.replace('.txt', f'_PSD_{XYZ}.png'))
            else:   fig_path = os.path.join(png_dir, filename.replace('.txt', f'_PLOT_{XYZ}.png'))
            if show == False: print(fig_path)
            plt.savefig(fig_path)
            if show: plt.show()
            plt.close()'''
            
        
        self.draw()
        return 0
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.XYZ              = {'X': 1, 'Y': 1, 'Z':1} # Wether to plot the X,Y,Z components
        self.dict_plot_btn    = {}
        self.data_dir         = None
        self.selected_file    = None   # the selected file to plot
        self.curr_plt_func    = None   # The current active plot function
        self.ROTOR_magn_field = None   # The ROTOR magnetic field
        self.list_pos         = None   # The list of the Z positions found in the ROTOR data file
        self.plot_fft         = False  # whether the plos is a DSP or not
        
        self.file_tab      = None   # The tab to choose a directory and list .txt files
        self.plot_tab      = None   # the tab to draw the plots"
        self.plot_txt_csv  = None   # The tab to superpose a .txt and a .csv plots
        
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
        self.folder_label = QLabel("Aucun dossier sélectionné.")
        self.select_button = QPushButton("Choisir un dossier")
        self.select_button.clicked.connect(self.select_folder)            
        VBox.addWidget(self.select_button)
        VBox.addWidget(self.folder_label)

        self.scroll_area = QScrollArea()
        self.file_list_widget = QGroupBox(".txt files")
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
        callbacks = (self.plot_ROTOR, None, self.colormap_ROTOR, (self.plot_FREE))
        for label, callback in zip(labels, callbacks):
            b = QPushButton(label)
            b.setMinimumHeight(40)
            b.setMinimumWidth(120)
            b.setCheckable(False)
            if label == 'Plot ROTOR PSD':
                b.clicked.connect(lambda: self.plot_ROTOR(fft=True))
            else:
                b.clicked.connect(callback)
            H.addWidget(b)
            if 'ROTOR' in label : 
                self.dict_plot_btn['ROTOR'].append(b)
            else:
                self.dict_plot_btn['FREE'].append(b)
            b.setEnabled(False)    
            
        H.addStretch()
        for lab in ("X", "Y", "Z"):
            c = QCheckBox(lab)
            c.toggle()
            c.stateChanged.connect(lambda state, label=lab: self.set_XYZ(state, label))
            H.addWidget(c)
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
        print(f'{self.XYZ=}')
        sum = self.XYZ['X'] + self.XYZ['Y'] + self.XYZ['Z']
        if sum and self.curr_plt_func: self.curr_plt_func()
        
    def activate_plotButtons(self):
        file = self.selected_file.name
        print(f'{file=}')
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
        

    def plot_ROTOR(self, fft=False):
        
        
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

        # transpose DATA to extract the different variables:
        self.angles, self.ROTOR_magn_field = DATA.T[0], DATA.T[1:]        
        
        self.canvas.plot_magField_at_positions()
        self.curr_plt_func = self.canvas.plot_magField_at_positions

        return
    
        
    def colormap_ROTOR(self):
        xyz = f"{self.XYZ['X']}{self.XYZ['Y']}{self.XYZ['Z']}"
        
    def plot_FREE(self):
        xyz = f"{self.XYZ['X']}{self.XYZ['Y']}{self.XYZ['Z']}"

    def select_folder(self):
        data_dir = QFileDialog.getExistingDirectory(self, "Choisir un dossier contenant des fichiers .txt")
        if data_dir:
            self.data_dir = Path(data_dir)
            self.folder_label.setText("Dossier sélectionné : {}".format(data_dir))
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
        print(f'{self.selected_file=}, {filepath=}')
        self.activate_plotButtons()
        self.tabs.setCurrentIndex(1)
        self.plot_ROTOR()       
        

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
    window.resize(1200, 900)
    window.show()
    sys.exit(app.exec_())

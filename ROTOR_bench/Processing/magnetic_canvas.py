#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#

import os, sys
from pathlib import Path
import numpy as np
from numpy.fft import rfft
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QFileDialog, QMessageBox)

class MagneticPlotCanvas(FigureCanvas):
    '''
    A matplotlib canvas for plotting magnetic field data.
    ''' 
    colors_B = {'X':'firebrick',  'Y':'green',      'Z': 'darkblue'}
    colors_L = {'X':'red',        'Y':'limegreen',  'Z': 'royalblue'}
    colors_S = {'X':'lightsalmon','Y':'yellowgreen','Z': 'skyblue'}
    
    def __init__(self, main, parent=None):
        '''
            Initialize the MagneticPlotCanvas with a reference to the main window.  
        '''    
        self.main = main
        self.fig  = Figure(figsize=(5, 4), dpi=100)
        self.ax   = None        
        super().__init__(self.fig)


    def clear(self):
        '''
            To clear all plots.
        '''        
        self.fig.clear()
        self.draw()
        return
    
    def plot_magField_at_positions(self):
        '''
            To plot ROTOR_B magnetic field versus angle, for different Z positions of the magnetic sensor.
        '''        
        self.fig.clear()
        self.fig.subplots_adjust(top=0.9, bottom=0.065, left=0.06, right=0.89, hspace=0.2, wspace=0.2)
        
        DATA = self.main.ROTOR_B_DATA
        angles, magn_field = DATA.T[0], DATA.T[1:]

        file_name  = self.main.ROTOR_B_txt_file.name       
        list_pos   = self.main.rotor_bdx_tab.list_pos
        nb_Zpos    = len(list_pos)
        nb_comp, _ = magn_field.shape
        assert(nb_comp // 3 == nb_Zpos)
        xyz = tuple(self.main.rotor_bdx_tab.XYZ.values())
        fft = self.main.curr_plt_info_B['param'] == 'fft'

        self.ax = self.fig.subplots(nb_Zpos, 1, sharex=True, sharey=True)
        fig, axes = self.fig, self.ax
        if nb_Zpos ==1 : axes = [axes]
        
        suptitle = "" if not fft else "Spectrum of "
        fig.suptitle(suptitle + "Rotor magnetic field", size=16)
        if self.main.disp_fileName:
            fig.text(0.5, .92, f"from <{file_name}>", size=9, color="gray", horizontalalignment='center')
        
        magn_max, magn_min = magn_field.max(), magn_field.min()                
        ang_freq_done = False 
        colors = MagneticPlotCanvas.colors_B
        
        for n, (ax, Zpos) in enumerate(zip(axes, list_pos)):  
            X, Y, Z = magn_field[3*n:3*n+3]  
            title = ""
            if fft:
                X, Y, Z = np.abs(rfft(X)), np.abs(rfft(Y)), np.abs(rfft(Z))
                XYZmax = max(X.max(), Y.max(), Z.max())
                X, Y, Z = X/XYZmax, Y/XYZmax, Z/XYZmax
                title += "PSD "
                if not ang_freq_done:
                    nb_pt = len(X)
                    f_sampling = 1/(angles[1] - angles[0])     # sampling frequency in rd^-1
                    ang_freq = np.arange(nb_pt)*f_sampling
                    A = ang_freq
                    ang_freq_done = True
                labels = ['Radial (X)', 'Axial (Y)', 'Tang (Z)']
                for psd, color, label, xyz_flag in zip((X, Y, Z), colors.values(), labels, xyz):
                    if xyz_flag: 
                        markerline, stemlines, baseline = ax.stem(A, psd, color, label=label)
                        markerline.set_markerfacecolor('white')
                        markerline.set_markersize(3.5)
                        baseline.set_color('grey')
                        baseline.set_linewidth(0.5)
            else:
                if xyz[0]: ax.plot(angles, X, '-o', color=colors['X'], markersize=0.5, label='radial (X)')
                if xyz[1]: ax.plot(angles, Y, '-o', color=colors['Y'], markersize=0.5, label='axial (Y)')
                if xyz[2]: ax.plot(angles, Z, '-o', color=colors['Z'], markersize=0.5, label='tang. (Z)')
                
            title += f"Magnetic field at Z position #{n+1}: {int(Zpos):3d} mm"
            ax.set_title(title, loc='left', fontsize=9)
            if n == 0: 
                if fft: ax.set_ylabel("Normalized PSD")
                else:   ax.set_ylabel("[mT]")
            ax.legend(bbox_to_anchor=(1.12, 1), loc="upper right")
            ax.minorticks_on()
            ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
            ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)

            if fft: ax.set_ylim(0,1.1)
            else:   ax.set_ylim(1.1*magn_min, 1.1*magn_max)

            if n == nb_Zpos-1:
                if fft: ax.set_xlabel(r"Angular frequency [rd$^{-1}$]")
                else:   ax.set_xlabel("rotor angle [°]")
                            
        self.draw()
        return 

    def plot_magField(self):
        '''
        To plot magnetic field versus time (free measurement).
        '''
        file_name = self.main.ROTOR_B_txt_file.name       
        xyz = tuple(self.main.rotor_bdx_tab.XYZ.values())

        self.fig.clear()
        self.fig.subplots_adjust(top=0.9, bottom=0.065, left=0.06, right=0.89, hspace=0.2, wspace=0.2)
        
        self.ax = self.fig.add_subplot(111)
        ax, fig = self.ax, self.fig
        
        
        # transpose DATA to extract the different variables:
        DATA = self.main.ROTOR_B_DATA
        T, magn_field = DATA.T[0], DATA.T[1:] 
        X, Y, Z = magn_field
                
        fig.suptitle(f"Rotor magnetic field", size=16)
        if self.main.disp_fileName:
            fig.text(0.5, .92, f"from <{file_name}>", size=10, color="gray", horizontalalignment='center')
        
        if xyz[0]: ax.plot(T, X, '-or', markersize=0.5, label='radial (X)')
        if xyz[1]: ax.plot(T, Y, '-og', markersize=0.5, label='axial (Y)')
        if xyz[2]: ax.plot(T, Z, '-ob', markersize=0.5, label='tang. (Z)')
        
        ax.legend(bbox_to_anchor=(1.12, 1), loc="upper right")
        ax.set_ylabel("[mT]")
        ax.set_xlabel("Time[s]")

        stat = self.main.rotor_bdx_tab.btn_free_stat.isChecked()
        if stat:
            sigmaX, sigmaY, sigmaZ = X.std(), Y.std(), Z.std()
            ymean = np.array(ax.get_ylim()).mean()
            yp2p  = np.ptp(np.array(ax.get_ylim()))
            if xyz[0]: ax.text(1.06*T.max(), ymean, r"$\sigma_X$: " + f"{sigmaX:5.2e} mT", color='r')
            if xyz[1]: ax.text(1.06*T.max(), ymean - 0.06*yp2p, r"$\sigma_Y$: " + f"{sigmaY:5.2e} mT", color='g')
            if xyz[2]: ax.text(1.06*T.max(), ymean - 0.12*yp2p, r"$\sigma_Z$: " + f"{sigmaZ:5.2e} mT", color='b')

        ax.minorticks_on()
        ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
        ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)

        self.draw()
        return 

    def colormap_magField(self):
        '''
            To draw the magnetic field color map versus angle & Zpos, for different 
            Z positions of the magnetic sensor.
        '''        

        file_name = self.main.ROTOR_B_txt_file.name       
        nb_Zpos    = len(self.main.rotor_bdx_tab.list_pos)

        DATA = self.main.ROTOR_B_DATA
        angles, magn_field = DATA[:, 0], DATA[:, 1:]

        _, nb_comp = magn_field.shape
        assert(nb_comp // 3 == nb_Zpos)
        
        xyz = tuple(self.main.rotor_bdx_tab.XYZ.values())

        self.fig.clear()
        self.fig.subplots_adjust(top=0.9, bottom=0.065, left=0.06, right=0.89, hspace=0.2, wspace=0.2)
        
        self.fig.suptitle(f"Rotor magnetic field", fontsize=16)
        if self.main.disp_fileName:
            self.fig.text(0.5, .92, f"from <{file_name}>", size=9, color="gray", horizontalalignment='center')        
        
        nb_plot   = sum(xyz)
        self.ax   = self.fig.subplots(nb_plot, 1, sharex=True)        
        fig, axes = self.fig, self.ax
        if nb_plot == 1: axes = [axes]        
        
        list_axes  = [None, None, None]
        num_axe = 0
        
        for n, todo in enumerate(xyz):
            if todo:
                list_axes[n] = axes[num_axe]
                num_axe +=1
        
        mag_labels = ["radial (X)", "axial (Y)", "tang. (Z)"]
        magnXYZ    = [magn_field[:, 0::3], magn_field[:, 1::3], magn_field[:, 2::3]]

        magn_min, magn_max = magn_field.min(), magn_field.max()

        z_pos_labels = file_name.split('_')[4:-1]
        z_pos_values = list(map(float, z_pos_labels))
        
        x = np.linspace(0, angles[-1], len(angles))
        y = np.array(z_pos_values)
        X, Y = np.meshgrid(x, y)

        first_plot = True
        for ax, todo, magn, label in zip(list_axes, xyz, magnXYZ, mag_labels):
            if todo:
                p = ax.pcolormesh(x, y, magn.T, cmap='seismic', shading='nearest', vmin=magn_min, vmax=magn_max)
                ax.set_title(f"Magnetic field - {label}", loc='left', fontsize=9)
                ax.set_yticks(z_pos_values[::-1], z_pos_labels)
                if first_plot: 
                    ax.set_ylabel("Z pos. from top [mm]")
                    first_plot = False
                last_ax = ax
        
        # write xlabel for the last plot:
        last_ax.set_xlabel("Rotor angle [°]")
        
        cax = fig.add_axes((0.93, 0.1, 0.02, 0.78))
        cbar = fig.colorbar(p, cax=cax, shrink=0.8)    #, location='right', anchor=(1.5, 0.5))
        cbar.ax.set_ylabel('Magnetic field [mT]', rotation=270)

        self.draw()

        return
    
    def plot_ROTOR_B_L_S_for_Zpos(self):
        '''
            To plot magnetic field versus angle, for different Z positions of the magnetic sensor.
        '''
        self.fig.clear(False)
        self.fig.subplots_adjust(top=0.9, bottom=0.065, left=0.05, right=0.87, hspace=0.2, wspace=0.2)
                
        # How many magnetic field components to plot:
        xyz = tuple(self.main.all_fields_tab.XYZ.values())
        nb_plot = sum(xyz)
        assert (nb_plot in (1,2,3))
        
        self.ax = self.fig.subplots(nb_plot, 1, sharex=True, sharey=False)
        fig, axes = self.fig, self.ax
        
        if nb_plot ==1 : axes = [axes]

        file_B_name = self.main.ROTOR_B_txt_file.name if self.main.ROTOR_B_txt_file else "No ROTOR_B file" 
        file_L_name = self.main.ROTOR_L_txt_file.name if self.main.ROTOR_L_txt_file else "No ROTOR_L file"
        file_S_name = self.main.SIMUL_txt_file.name if self.main.SIMUL_txt_file else "No SIMUL file"  
        
        title = f'Magnetic field: '
        files = ""
        
        # Flags to know which data files are available:
        ROTOR_B = self.main.ROTOR_B_txt_file is not None
        ROTOR_L = self.main.ROTOR_L_txt_file is not None
        ROTOR_S = self.main.SIMUL_txt_file is not None

        # Short names for the magnetc fileds of ROTOR Bdx, ROTOR Lille & SIMULAtion:        
        BX, BY, BZ = None, None, None
        R, T, A    = None, None, None
        SX, SY, SZ = None, None, None
                
        if ROTOR_B:  
            # Extract the data of the ROTOR_B corresponding to the selected Zpos:
            Zpos_B = self.main.all_fields_tab.ROTOR_B_sel_Zpos
            list_pos = self.main.rotor_bdx_tab.list_pos
            title += f'ROTOR_B [Zpos={Zpos_B}mm] '
            files += f'<{file_B_name}> '
                
            DATA = self.main.ROTOR_B_DATA
            DATA = self.main.ROTOR_B_extract_magnetic_field(DATA, list_pos, Zpos_B)
            # transpose DATA to extract the different variables:
            angles_B, magn_field_B = DATA.T[0], DATA.T[1:]       
            BX, BY, BZ = magn_field_B
        
        if ROTOR_L:            
            Zpos_L = self.main.all_fields_tab.ROTOR_L_sel_Zpos
            shift  = self.main.all_fields_tab.ROTOR_L_sel_angle
            title += f'ROTOR_L [Zpos={Zpos_L}mm, shift:={shift}°]'
            files += f'<{file_L_name}> '
            
            # The ROTOR_L data have already been read in the ROTOR_L tab:
            DATA = self.main.ROTOR_L_DATA
            # Extract the data of the ROTOR_L corresponding to the selected Zpos:
            try:
                i_range = np.where(DATA.T[2] == int(Zpos_L))
                DATA  = DATA[i_range]
            except:
                message = f'Zpos: {Zpos_L} not found in the LILLE ROTOR data file.\nPlease select another value'
                QMessageBox.warning(self, 'Warning', message)
                return

            # Apply shift angle on ROTOR_L data if required:
            #if self.ROTOR_L_sel_Angle != 0:
            nb_angle = len(DATA)
            new_DATA = DATA.copy()
            #new_DATA[:nb_angle - shift, 3:] = DATA[shift:, 3:]
            #new_DATA[nb_angle - shift:, 3:] = DATA[:shift, 3:]
            if shift > 0:
                new_DATA[:nb_angle - shift, 3:] = DATA[shift:, 3:]
                new_DATA[nb_angle - shift:, 3:] = DATA[:shift, 3:]
            elif shift < 0:
                shift = -shift
                new_DATA[shift:, 3:] = DATA[:nb_angle - shift, 3:]
                new_DATA[:shift, 3:] = DATA[nb_angle - shift:, 3:]
            DATA = new_DATA
            angles_L, mag_field_L = DATA.T[1], DATA.T[3:]
            R, T, A = mag_field_L * 1e3 # Lille rotor bench: Radial, Tangent, Axial are in Tesla
        
        if ROTOR_S:
            list_dist = self.main.simul_tab.list_dist
            dist      = self.main.all_fields_tab.ROTOR_S_sel_dist
            nb_dist = len(list_dist)
            
            title += f' SIMUL [dist={dist}mm]'
            files += f'<{file_S_name}>'
            
            DATA = self.main.SIMUL_DATA
            # We expect a magn filed with 3 components in teh SIMUL data file:
            if DATA.shape[1] != 1 + nb_dist * 3:     # "angle" column + "3*nb_dist" columns
                mess = '''SIMULATION file must have 3 magnetic components (Br, Bt, Ba)\nPlease choose another file.'''
                QMessageBox.warning(self, 'Warning', mess)
                return -1
            DATA = self.main.ROTOR_B_extract_magnetic_field(DATA, list_dist, dist)
                        
            # Transpose DATA to extract the different variables:
            angles_S, magn_field = DATA.T[0], DATA.T[1:]*1e3 # Simulated field is in Tesla
            
            # Number of components of the magnetic field that have been read in the file:
            nb_comp_magn_field = magn_field.shape[0]  # we expect 2 or 3 components: radial (X), possibly axial (Y) and tangential (Z)
            assert nb_comp_magn_field in (2,3)   

            SY = None
            if nb_comp_magn_field == 2:
                # The SIMULE file has ony the 2 components Br (X) and Bt (Z) of the magnetic field:
                SX, SZ = magn_field  
            elif nb_comp_magn_field == 3:
                # The SIMULE file has the 3 components Br (X), Bt (Z) and Ba (Y) of the magnetic field:
                SX, SZ, SY = magn_field
            
        # Dicts for labels, fields and colors:
        lab_B    = {'X':'radial (X)', 'Y':'axial (Y)',  'Z':'tang. (Z)'}
        lab_L    = {'X':'radial',     'Y':'axial',      'Z':'tang.'}
        lab_S    = {'X':'radial',     'Y':'axial',      'Z':'tang.'}
        field_B  = {'X': BX,          'Y':BY,           'Z':BZ}
        field_L  = {'X': R,           'Y':A,            'Z':T}
        field_S  = {'X': SX,          'Y':SY,           'Z':SZ}
        colors_B = MagneticPlotCanvas.colors_B
        colors_L = MagneticPlotCanvas.colors_L
        colors_S = MagneticPlotCanvas.colors_S
        
        fig.suptitle(title, fontsize=15)
        if self.main.disp_fileName:
            fig.text(0.5, .92, files, size=9, color="gray", horizontalalignment='center')

        n = 0
        for c, offset in zip(('X', 'Y', 'Z'), (1.165, 1.16, 1.165)):
            if self.main.all_fields_tab.XYZ[c]: 
                ax = axes[n]
                if ROTOR_B: ax.plot(angles_B, field_B[c], '-o', markersize=0.5, color=colors_B[c], label=f'ROTOR_B {lab_B[c]}')
                if ROTOR_L: ax.plot(angles_L, field_L[c], '-o', markersize=0.5, color=colors_L[c], label=f'ROTOR_L {lab_L[c]}')
                if ROTOR_S: 
                    if field_S[c] is not None:
                        ax.plot(angles_S, field_S[c], '-', markersize=0.5, color=colors_S[c], label=f'ROTOR_S {lab_S[c]}')
                    else:
                        ax.plot(np.NaN, np.NaN, '-', markersize=0.5, color=colors_S[c], label=f'ROTOR_S {lab_S[c]}')
                        print(f"Warning: no {lab_S[c]} component in the SIMUL data file <{self.main.SIMUL_txt_file.name}>.")
                ax.set_ylabel("[mT]")        
                ax.legend(bbox_to_anchor=(offset, 1), loc="upper right")
                ax.minorticks_on()
                ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
                ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)
                n += 1
        ax.set_xlabel("rotor angle [°]")
        
        self.draw()
        return


    def plot_SIMUL_magField(self):
        '''
            To plot the simulated magnetic field versus angle, for different distances rotor-magnetic sensor.
        '''        
        self.fig.clear()
        self.fig.subplots_adjust(top=0.9, bottom=0.065, left=0.06, right=0.89, hspace=0.2, wspace=0.2)
        
        file_name  = self.main.SIMUL_txt_file.name
        list_dist = self.main.simul_tab.list_dist
        nb_dist    = len(list_dist)
               
        self.ax = self.fig.subplots(nb_dist, 1, sharex=True, sharey=True)
        fig, axes = self.fig, self.ax
        if nb_dist ==1 : axes = [axes]
        
        # short names for the data to plot:
        DATA = self.main.SIMUL_DATA
        # We expect a magn filed with 3 components in teh SIMUL data file:
        if DATA.shape[1] != 1 + nb_dist * 3:     # "angle" column + "3*nb_dist" columns
            mess = '''SIMULATION file must have 3 magnetic components (Br, Bt, Ba)\nPlease choose another file.'''
            QMessageBox.warning(self, 'Warning', mess)
            return -1
        
        # transpose DATA to extract the different variables:
        angles, magn_field = DATA.T[0], DATA.T[1:] * 1e3 # Simulated field is in Tesla

        # Number of componets of the magnetic field that have been read in the file:
        nb_comp_magn_field = magn_field.shape[0]//nb_dist
        # we expect 2 or 3 components: radial (X), tangential (Z) and possibly axial (Y)
        assert(nb_comp_magn_field in (2,3))   
        
        # The titles:
        fig.suptitle("Simulated Rotor magnetic field", size=16)
        if self.main.disp_fileName:
            fig.text(0.5, .92, f"from <{file_name}>", size=9, color="gray", horizontalalignment='center')
        
        xyz = tuple(self.main.simul_tab.XYZ.values())
        colors_S = MagneticPlotCanvas.colors_S
        
        for n, (ax, dist) in enumerate(zip(axes, list_dist)):  
            Y = None
            if nb_comp_magn_field == 2:
                # The SIMULE file has ony the 2 components Br (X) and Bt (Z) of the magnetic field:
                X, Z = magn_field[2*n:2*n+2]  
            elif nb_comp_magn_field == 3:
                # The SIMULE file has the 3 components Br (X), Bt (Z) and Bz (Y) of the magnetic field:
                X, Z, Y = magn_field[3*n:3*n+3]
                
            if xyz[0]: ax.plot(angles, X, '-o', markersize=0.5, color=colors_S['X'], label='radial (X)')
            if xyz[1]: 
                if Y is not None:
                    ax.plot(angles, Y, '-o', markersize=0.5, color=colors_S['Y'], label='axial (Y)')
                else:
                    ax.plot(np.NaN, np.NaN, '-o', markersize=0.5, color=colors_S['Y'], label='axial (Y)')
                    print(f"Warning: no axial (Y) component in the SIMUL data file <{self.main.SIMUL_txt_file.name}>.")
            
            if xyz[2]:  ax.plot(angles, Z, '-o', markersize=0.5, color=colors_S['Z'], label='tang. (Z)')
                
            title = f"Simulated Magnetic Field for distance={int(dist):d} mm"
            ax.set_title(title, loc='left', fontsize=9)
            ax.legend(bbox_to_anchor=(1.12, 1), loc="upper right")
            ax.minorticks_on()
            ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
            ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)
            magn_max, magn_min = magn_field.max(), magn_field.min()                  
            ax.set_ylim(1.1*magn_min, 1.1*magn_max)
            
        axes[0].set_ylabel("[mT]")
        axes[-1].set_xlabel("rotor angle [°]")
                            
        self.draw()
        return 


    def plot_ROTOR_L_for_Zpos(self):
        '''
            To plot ROTOR L magnetic field versus angle, for different Z positions of the magnetic sensor.
        '''
        self.fig.clear(False)
        self.fig.subplots_adjust(top=0.9, bottom=0.065, left=0.05, right=0.87, hspace=0.2, wspace=0.2)
                
        file_L_name = self.main.ROTOR_L_txt_file.name
        Zpos_L = self.main.rotor_lille_tab.ROTOR_L_sel_Zpos

        # Check how many magnetic field components to plot:
        XYZ = tuple(self.main.rotor_lille_tab.XYZ.values())
        nb_plot = sum(XYZ)
        assert (nb_plot in (1,2,3))
        
        self.ax = self.fig.subplots(nb_plot, 1, sharex=True, sharey=False)
        fig, axes = self.fig, self.ax        
        if nb_plot ==1 : axes = [axes]
                
        # The ROTOR_L data have already been read when the file was selected:
        DATA = self.main.ROTOR_L_DATA
        
        # Extract the data of the ROTOR_L corresponding to the selected Zpos:
        try:
            i_range = np.where(DATA.T[2] == int(Zpos_L))
            DATA  = DATA[i_range]
        except:
            message = f'Zpos: {Zpos_L} not found in the LILLE ROTOR data file.\nPlease select another value'
            QMessageBox.warning(self, 'Warning', message)
            return

        angles_L, mag_field_L = DATA.T[1], DATA.T[3:]
        R, T, A = mag_field_L * 1e3 # Lille rotor bench: Radial, Tangent, Axial are in Tesla

        title = f'Magnetic field: ROTOR_L  (Zpos:{Zpos_L:03d}mm)'
        fig.suptitle(title, fontsize=15)
        message = f'<{file_L_name}>'
        if self.main.disp_fileName:
            fig.text(0.5, .92, message, size=9, color="gray", horizontalalignment='center')
            
        lab_L   = {'X':'radial',     'Y':'axial',     'Z':'tang.'}
        field_L = {'X': R,           'Y':A,           'Z':T}
        colors  = MagneticPlotCanvas.colors_L
        
        n = 0
        for c, offset in zip(('X', 'Y', 'Z'), (1.165, 1.16, 1.165)):
            if self.main.rotor_lille_tab.XYZ[c]: 
                ax = axes[n]
                ax.plot(angles_L, field_L[c], '-o', markersize=0.5, color=colors[c], label=f'ROTOR_L {lab_L[c]}')
                ax.set_ylabel("[mT]")        
                ax.legend(bbox_to_anchor=(offset, 1), loc="upper right")
                ax.minorticks_on()
                ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
                ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)
                n += 1
                
        self.draw()
        return

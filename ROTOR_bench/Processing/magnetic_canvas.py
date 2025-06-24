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


from tools import build_XYZ_name_with_tuple

class MagneticPlotCanvas(FigureCanvas):
    def __init__(self, main, parent=None):
        
        self.main = main
        self.fig  = Figure(figsize=(5, 4), dpi=100)
        self.ax   = None        
        super().__init__(self.fig)


    def plot_magField_at_positions(self):
        '''
            To plot magnetic field versus angle, for different Z positions
            of the magnetic sensor.
        '''
        print(f'MagneticPlotCanvas.plot_magField_at_positions')
        
        dir_name   = self.main.ROTOR_B_data_dir
        file_name  = self.main.ROTOR_B_txt_file.name       
        nb_Zpos    = len(self.main.list_pos)
        nb_comp, _ = self.main.ROTOR_B_magn_field.shape
        assert(nb_comp // 3 == nb_Zpos)
        xyz = self.main.convert_XYZ_B_to_tuple()
        fft = self.main.curr_plt_info_B['param'] == 'fft'

        self.fig.clear()
        self.fig.subplots_adjust(top=0.9, bottom=0.065, left=0.06, right=0.89, hspace=0.2, wspace=0.2)
                
        self.ax = self.fig.subplots(nb_Zpos, 1, sharex=True, sharey=True)
        fig, axes = self.fig, self.ax
        if nb_Zpos ==1 : axes = [axes]

        angles, magn_field, list_pos = self.main.angles_B, self.main.ROTOR_B_magn_field, self.main.list_pos
        
        suptitle = "" if not fft else "Spectrum of "
        fig.suptitle(suptitle + "Rotor magnetic field", size=16)
        fig.text(0.5, .92, f"from <{file_name}>", size=9, color="gray", horizontalalignment='center')
        
        # Check how many magnetic field components to plot:
        nb_plot = sum(xyz)
        if nb_plot == 0: 
            self.draw()
            return

        magn_max, magn_min = magn_field.max(), magn_field.min()                
        ang_freq_done = False 
                       
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
                labels = ['X (radial)', 'Y (axial)', 'Z (tang)']
                for psd, color, label, xyz_flag in zip((X, Y, Z), 'rgb', labels, xyz):
                    if xyz_flag: 
                        markerline, stemlines, baseline = ax.stem(A, psd, color, label=label)
                        markerline.set_markerfacecolor('white')
                        markerline.set_markersize(3.5)
                        baseline.set_color('grey')
                        baseline.set_linewidth(0.5)
            else:
                if xyz[0]: ax.plot(angles, X, '-or', markersize=0.5, label='X (radial)')
                if xyz[1]: ax.plot(angles, Y, '-og', markersize=0.5, label='Y (axial)')
                if xyz[2]: ax.plot(angles, Z, '-ob', markersize=0.5, label='Z (tang)')
                
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
        print(f'MagneticPlotCanvas.plot_magField')
        
        dir_name  = self.main.ROTOR_B_data_dir
        file_name = self.main.ROTOR_B_txt_file.name       
        xyz = self.main.convert_XYZ_B_to_tuple()

        self.fig.clear()
        self.fig.subplots_adjust(top=0.9, bottom=0.065, left=0.06, right=0.89, hspace=0.2, wspace=0.2)
        
        self.ax = self.fig.add_subplot(111)
        
        ax, fig = self.ax, self.fig
        T, magn_field = self.main.time_values, self.main.ROTOR_B_magn_field

        X, Y, Z = magn_field
                
        fig.suptitle(f"Rotor magnetic field", size=16)
        fig.text(0.5, .92, f"from <{file_name}>", size=10, color="gray", horizontalalignment='center')
        
        # Check how many magnetic field components to plot:
        nb_plot = sum(xyz)
        if nb_plot == 0: 
            self.draw()
            return

        if xyz[0]: ax.plot(T, X, '-or', markersize=0.5, label='X (radial)')
        if xyz[1]: ax.plot(T, Y, '-og', markersize=0.5, label='Y (axial)')
        if xyz[2]: ax.plot(T, Z, '-ob', markersize=0.5, label='Z (tang)')
        
        ax.legend(bbox_to_anchor=(1.12, 1), loc="upper right")
        ax.set_ylabel("[mT]")
        ax.set_xlabel("Time[s]")

        stat = self.main.btn_free_stat.isChecked()
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
        print(f'MagneticPlotCanvas.colormap_magField')
        
        dir_name  = self.main.ROTOR_B_data_dir
        file_name = self.main.ROTOR_B_txt_file.name       
        nb_Zpos    = len(self.main.list_pos)
        _, nb_comp = self.main.ROTOR_B_magn_field.shape
        assert(nb_comp // 3 == nb_Zpos)
        xyz = self.main.convert_XYZ_B_to_tuple()

        self.fig.clear()
        #self.fig.tight_layout = True
        self.fig.subplots_adjust(top=0.9, bottom=0.065, left=0.06, right=0.89, hspace=0.2, wspace=0.2)
        
        self.fig.suptitle(f"Rotor magnetic field", fontsize=16)
        self.fig.text(0.5, .92, f"from <{file_name}>", size=9, color="gray", horizontalalignment='center')        
        
        # Check how many magnetic field components to plot:
        nb_plot    = sum(xyz)
        if nb_plot == 0: 
            self.ax = self.fig.subplots(1, 1)
            self.draw() 
            return

        self.ax = self.fig.subplots(nb_plot, 1, sharex=True)        
        fig, axes = self.fig, self.ax
        angles, magn_field = self.main.angles_B, self.main.ROTOR_B_magn_field

        if nb_plot == 1: axes = [axes]
        
        list_axes  = [None, None, None]
        num_axe = 0
        for n, todo in enumerate(xyz):
            if todo:
                list_axes[n] = axes[num_axe]
                num_axe +=1
        
        mag_labels = ["X (radial)", "Y (axial)", "Z (tang)"]
        magnXYZ    = [magn_field[:, 0::3], magn_field[:, 1::3], magn_field[:, 2::3]]

        magn_max = magn_field.max()
        magn_min = magn_field.min()

        z_pos_labels = file_name.split('_')[4:-1]
        z_pos_values = list(map(float, z_pos_labels))
        
        x = np.linspace(0, angles[-1], len(angles))
        y = np.array(z_pos_values)
        X, Y = np.meshgrid(x, y)

        first_plot = True
        for ax, todo, magn, label in zip(list_axes, xyz, magnXYZ, mag_labels):
            if todo:
                p = ax.pcolormesh(x, y, magn.T, cmap='seismic', shading='nearest', vmin=magn_min, vmax=magn_max)
                ax.set_title(f"Magnetic field {label}", loc='left', fontsize=9)
                ax.set_yticks(z_pos_values[::-1], z_pos_labels)
                if first_plot: 
                    ax.set_ylabel("Z pos. from top [mm]")
                    first_plot = False
                last_ax = ax
        
        # write xlabel for the last plot:
        last_ax.set_xlabel("Rotation angle [°]")
        
        cax = fig.add_axes((0.93, 0.1, 0.02, 0.78))
        cbar = fig.colorbar(p, cax=cax, shrink=0.8)    #, location='right', anchor=(1.5, 0.5))
        cbar.ax.set_ylabel('Magnetic field [mT]', rotation=270)

        self.draw()

        return
    
    def plot_ROTOR_B_L_for_Zpos(self):
    
        # angles1, field1, Zpos, filename1, angles2, field2, filename2
        '''
            To plot magnetic field versus angle, for different Z positions
            of the magnetic sensor.
        '''
        print(f'MagneticPlotCanvas.plot_ROTOR_CSV_magField_at_positions')
        
        dir_B_name  = self.main.ROTOR_B_data_dir
        file_B_name = self.main.ROTOR_B_txt_file.name       
        dir_L_name  = self.main.ROTOR_L_data_dir
        file_L_name = self.main.ROTOR_L_txt_file.name       

        self.fig.clear()
        self.fig.subplots_adjust(top=0.9, bottom=0.065, left=0.06, right=0.89, hspace=0.2, wspace=0.2)
                
        # Check how many magnetic field components to plot:
        xyz = self.main.convert_XYZ_B_L_to_tuple()
        nb_plot = sum(xyz)
        if nb_plot == 0: 
            self.ax = self.fig.subplots(1, 1)
            self.fig.draw()
            return

        self.ax = self.fig.subplots(nb_plot, 1, sharex=True, sharey=False)
        fig, axes = self.fig, self.ax
        
        if nb_plot ==1 : axes = [axes]

        angles_B, magn_field_B, = self.main.angles_B, self.main.ROTOR_B_magn_field
        angles_L, magn_field_L  = self.main.angles_L, self.main.ROTOR_L_magn_field
        
        Zpos_B = self.main.ROTOR_B_sel_Zpos
        Zpos_L = self.main.ROTOR_L_sel_Zpos
        shift  = self.main.ROTOR_L_sel_Angle
        title = f'Magnetic field ROTOR_B@Zpos:{Zpos_B}mm & ROTOR_L@Zpos:{Zpos_L}mm,shift:{shift}°'
        fig.suptitle(title, fontsize=15)
        message = f'<{file_B_name}@{Zpos_B}mm and '
        message += f'<{file_L_name}@{Zpos_L}mm_shifted:{shift}°>'
        fig.text(0.5, .92, message, size=9, color="gray", horizontalalignment='center')
                            
        X, Y, Z = magn_field_B
        R, T, A = magn_field_L * 1e3 # Lille rotor bench: Radial, Tangent, Axial are in Tesla
            
        lab_B   = {'X':'X', 'Y':'Y', 'Z':'Z'}
        lab_L   = {'X':'rad',     'Y':'axial',     'Z':'tan'}
        field_B = {'X': X,           'Y':Y,           'Z':Z}
        field_L = {'X': R,           'Y':A,           'Z':T}
        colors  = {'X':'red',        'Y':'green',     'Z': 'blue'}
        
        n = 0
        for c in ('X', 'Y', 'Z'):
            if self.main.XYZ_B_L[c]: 
                ax = axes[n]
                ax.plot(angles_B, field_B[c], '-o', markersize=0.5, color=colors[c], label=f'ROTOR_B {lab_B[c]}')
                ax.plot(angles_L, field_L[c], ':o', markersize=0.5, color=colors[c], label=f'ROTOR_L {lab_L[c]}')
                ax.set_ylabel("[mT]")        
                ax.legend(bbox_to_anchor=(1.12, 1), loc="upper right")
                ax.minorticks_on()
                ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
                ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)
                n += 1
        ax.set_xlabel("rotor angle [°]")
        
        self.draw()
        return

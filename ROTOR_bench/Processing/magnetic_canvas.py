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
        
        dir_name   = self.main.data_dir
        file_name  = self.main.selected_file.name        
        nb_Zpos    = len(self.main.list_pos)
        nb_comp, _ = self.main.ROTOR_magn_field.shape
        assert(nb_comp // 3 == nb_Zpos)
        xyz = self.main.convert_XYZ_to_tuple()
        fft = self.main.plot_fft

        self.fig.clear()
        self.fig.tight_layout = True
                
        self.ax = self.fig.subplots(nb_Zpos, 1, sharex=True, sharey=True)
        fig, axes = self.fig, self.ax
        if nb_Zpos ==1 : axes = [axes]

        angles, magn_field, list_pos = self.main.angle_values, self.main.ROTOR_magn_field, self.main.list_pos
        
        suptitle = "" if not fft else "Spectrum of "
        fig.suptitle(suptitle + "Rotor magnetic field", size=16)
        fig.text(0.5, .93, f"from <{file_name}>", size=9, color="gray", horizontalalignment='center')

        self.draw()
        
        # Check how many magnetic field components to plot:
        nb_plot = sum(xyz)
        if nb_plot == 0: return

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
                if xyz[0]: ax.plot(self.main.angle_values, X, '-or', markersize=0.5, label='X (radial)')
                if xyz[1]: ax.plot(self.main.angle_values, Y, '-og', markersize=0.5, label='Y (axial)')
                if xyz[2]: ax.plot(self.main.angle_values, Z, '-ob', markersize=0.5, label='Z (tang)')
                
            title += f"Magnetic field at Z position #{n+1}: {int(Zpos):3d} mm"
            ax.set_title(title, loc='left', fontsize=9)
            if n == 0: 
                if fft: ax.set_ylabel("Normalized PSD")
                else:   ax.set_ylabel("[mT]")
            ax.legend(bbox_to_anchor=(1.13, 1), loc="upper right")
            ax.minorticks_on()
            ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
            ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)

            if fft: ax.set_ylim(0,1.1)
            else:   ax.set_ylim(1.1*magn_min, 1.1*magn_max)

            if n == nb_Zpos-1:
                if fft: ax.set_xlabel(r"Angular frequency [rd$^{-1}$]")
                else:   ax.set_xlabel("rotor angle [°]")
                
            #plt.subplots_adjust(hspace=0.37, right=0.87, top=0.8, bottom=0.12)
        
        png_dir = Path(dir_name, 'PNG')
        if not png_dir.exists(): png_dir.mkdir(exist_ok=True)
        XYZ = build_XYZ_name_with_tuple(xyz)
        if fft:
            fig_path = Path(png_dir, file_name.replace('.txt', f'_PSD_{XYZ}.png'))
        else:
            fig_path = Path(png_dir, file_name.replace('.txt', f'_PLOT_{XYZ}.png'))            
        fig.savefig(fig_path)
                    
        self.draw()
        return 0

    def plot_magField(self):
        '''
            To plot magnetic field versus time (free measurement).
        '''
        print(f'MagneticPlotCanvas.plot_magField')
        
        dir_name  = self.main.data_dir
        file_name = self.main.selected_file.name       
        xyz = self.main.convert_XYZ_to_tuple()

        self.fig.clear()
        self.fig.tight_layout = True
        
        self.ax = self.fig.add_subplot(111)
        
        ax, fig = self.ax, self.fig
        T, magn_field = self.main.time_values, self.main.ROTOR_magn_field

        X, Y, Z = magn_field
                
        fig.suptitle(f"Rotor magnetic field", size=16)
        fig.text(0.5, .92, f"from <{file_name}>", size=10, color="gray", horizontalalignment='center')

        self.draw()
        
        # Check how many magnetic field components to plot:
        nb_plot = sum(xyz)
        if nb_plot == 0: return

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

        png_dir = Path(dir_name, 'PNG')
        if not png_dir.exists(): png_dir.mkdir(exist_ok=True)
        XYZ = build_XYZ_name_with_tuple(xyz)
        fig_path = Path(png_dir, file_name.replace('.txt', f'_FREE_{XYZ}.png'))
        fig.savefig(fig_path)

        self.draw()
        return 0

    def colormap_magField(self):
        '''
            To draw the magnetic field color map versus angle & Zpos, for different 
            Z positions of the magnetic sensor.
        '''
        print(f'MagneticPlotCanvas.colormap_magField')
        
        dir_name   = self.main.data_dir
        file_name  = self.main.selected_file.name        
        nb_Zpos    = len(self.main.list_pos)
        _, nb_comp = self.main.ROTOR_magn_field.shape
        assert(nb_comp // 3 == nb_Zpos)
        xyz = self.main.convert_XYZ_to_tuple()

        self.fig.clear()
        self.fig.tight_layout = True
        
        self.fig.suptitle(f"Rotor magnetic field", size=16)
        self.fig.text(0.5, .93, f"from <{file_name}>", size=9, color="gray", horizontalalignment='center')        
        
        self.draw()

        # Check how many magnetic field components to plot:
        nb_plot    = sum(xyz)
        if nb_plot == 0: return

        self.ax = self.fig.subplots(nb_plot, 1, sharex=True)        
        fig, axes = self.fig, self.ax
        angles, magn_field = self.main.angle_values, self.main.ROTOR_magn_field

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
        
        #plt.subplots_adjust(hspace=0.37, right=0.87, top=0.8, bottom=0.12)

        png_dir = Path(dir_name, 'PNG')
        if not png_dir.exists(): png_dir.mkdir(exist_ok=True)
        XYZ = build_XYZ_name_with_tuple(xyz)
        fig_path = Path(png_dir, file_name.replace('.txt', f'_CMAP_{XYZ}.png'))
        fig.savefig(fig_path)

        self.draw()
        return
    
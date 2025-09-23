#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#

import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import rfft
import sys, os
from os.path import join
from pathlib import Path
from stat import ST_CTIME

def build_XYZ_name_with_tuple(xyz:tuple|dict):
    labels = ("X", "Y", "Z")
    label = ""
    if isinstance(xyz, dict): xyz = tuple(xyz.values())
    for x, lab in zip(xyz, labels):
        if x: label+= lab
    return label

def get_files_by_date(directory, PREFIX):
    d = directory
    files = [(os.stat(join(d, f))[ST_CTIME], f) for f in os.listdir(directory) \
             if f.lower().endswith('.txt') and f.startswith(PREFIX)]
    files.sort()
    return  [f for s, f in files]
  
def read_file_SIMUL_ROTOR(file_path):
    
    with open(file_path, 'r', encoding='utf8') as F:
        lines = F.readlines()

    try:
        # process the name of the file like <Bsimul_r-71_d-1-5-10.txt>
        file_name = Path(file_path).name
        list_dist = file_name.replace('.txt', '').split('d-')[1].split('-')
        
        # now read the sensor data lines:
        DATA = []
        for line in lines:
            # skip comments:
            if line[0] == "#": continue            
            # transform strings into numbers:
            data = [float(x) for x in line.strip().split()]
            DATA.append(data)
        DATA = np.array(DATA)
        
    except Exception as err:
        print(f"Unexpected error {err=} occurs when reading file <{file_name}>")
        DATA, list_dist = None, None
    
    return DATA, list_dist
    
def read_file_ROTOR(file_path):
    
    with open(file_path, 'r', encoding='utf8') as F:
        lines = F.readlines()

    # process the name of the file <ROTOR_YYYY-MM-DD_hh_mm_ss_ROTSTEP-aa_ZZZ_ZZZ-...txt>
    # Example: <ROTOR_2024-07-09-13-59_WDIST-12_ROTSTEP-4.8_000_030_060_090_1of1.txt
    file_name = Path(file_path).name
    if file_name.startswith('ROTOR_'):
        list_pos = file_name.replace('.txt', '').split('_')[4:-1]
    else:
        list_pos = []
        
    # now read the sensor data lines:
    DATA = []
    for line in lines:
      # skip comments or empty lines:
      if line[0] == "#" or line == '\n': continue
      
      # transform strings into numbers:
      data = [float(x) for x in line.strip().split(';')]
      DATA.append(data)
    
    DATA = np.array(DATA)
    return DATA, list_pos

def read_file_ROTOR_L(file_path):
    
    # discover the correct encoding to read the CSV file:
    for code in ('utf8', 'cp1252'):
        try:
            with open(file_path, 'r', encoding=code) as F:
                lines = F.readlines()
            break
        except:
            pass

    # now read the sensor data lines:
    DATA = []
    for line in lines:
        # skip comments:
        if line[0] == "#": continue
        line = line.replace(',','.')
        try:
            r, phi, z, Bradial, Btang, Baxial = map(float, line.split(';'))
            DATA. append([r, phi, z, Bradial, Btang, Baxial])
        except:
            continue    
    DATA = np.array(DATA)
    return DATA

def read_file_FREE(file_path):
    
    with open(file_path, 'r', encoding='utf8') as F:
        lines = F.readlines()
    
    # now read the sensor data lines:
    DATA = []
    for line in lines:
      # skip comments:
      if line == '\n' or line[0] == "#": continue
      # transform strings into numbers:
      data = [float(x) for x in line.strip().split(';')]
      DATA.append(data)
    
    DATA = np.array(DATA)
    return DATA
    
def plot_magField(angle, field, filename, figsize=(8,6), stat=None, show=True, xyz=(1,1,1)):
    '''
        To plot magnetic field versus time (free measurement).

        Parameters:
        angle:    the list of angle values
        filename: the name of the data file
        figsize:  the width & height of the figure to draw (inch)
        stat:     whether to write some statistics or not
        show:     whether to run the plt.show() or not
        xyz:      a tuple of 3 digits 0/1 to display or not the components
                  X, Y and Z of the magnetic field.
            
    '''
    dirname  = os.path.dirname(filename)
    filename = os.path.basename(filename)

    X, Y, Z = field
    sigmaX, sigmaY, sigmaZ = X.std(), Y.std(), Z.std()
    if stat == None:
        if sigmaX > 0.5 or sigmaY > 0.5 or sigmaZ > 0.5:
            stat = False
        else:
            stat = True
    
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    fig.suptitle(f"Rotor magnetic field", size=16)
    fig.text(0.5, .92, f"from <{filename}>", size=10, color="gray",
                horizontalalignment='center')
    if xyz[0]: ax.plot(angle, X, '-or', markersize=0.5, label='X')
    if xyz[1]: ax.plot(angle, Y, '-og', markersize=0.5, label='Y')
    if xyz[2]: ax.plot(angle, Z, '-ob', markersize=0.5, label='Z')
    
    ax.legend(bbox_to_anchor=(1.15, 1), loc="upper right")
    ymean = np.array(ax.get_ylim()).mean()
    yp2p  = np.ptp(np.array(ax.get_ylim()))
    if stat:
        if xyz[0]: ax.text(1.07*angle.max(), ymean, r"$\sigma_X$: " + f"{sigmaX:5.2e} mT", color='r')
        if xyz[0]: ax.text(1.07*angle.max(), ymean - 0.06*yp2p, r"$\sigma_Y$: " + f"{sigmaY:5.2e} mT", color='g')
        if xyz[0]: ax.text(1.07*angle.max(), ymean - 0.12*yp2p, r"$\sigma_Z$: " + f"{sigmaZ:5.2e} mT", color='b')
    
    ax.minorticks_on()
    ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
    ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)
    ax.set_ylabel("[mT]")
    ax.set_xlabel("Time[s]")
    plt.subplots_adjust(right=0.84)
    
    png_dir = dirname.replace('TXT', 'PNG')
    if not os.path.exists(png_dir): os.mkdir(png_dir)
    XYZ = build_XYZ_name_with_tuple(xyz)
    fig_path = os.path.join(png_dir, filename.replace('.txt', f'_FREE_{XYZ}.png'))
    if show == False: print(fig_path)
    plt.savefig(fig_path)
    if show: plt.show()
    plt.close()
    return 0


def plot_magField_at_positions(A, field, list_pos, filename, figsize=(8,6), mode=None, xyz=(1,1,1), show=True, fft= False):
    '''
        To plot magnetic field versus angle, for different Z positions
        of the magnetic sensor.
    '''
    dirname  = os.path.dirname(filename)
    filename = os.path.basename(filename)
    
    nb_Zpos = len(list_pos)
    nb_comp, nb_angle_pos = field.shape
    assert(nb_comp // 3 == nb_Zpos)

    # Check how many magnetic field components to plot:
    nb_plot = sum(xyz)
    if nb_plot == 0: return

    try:
        fig, axes = plt.subplots(nb_Zpos, 1, figsize=figsize, sharex=True, sharey=True)
        if nb_Zpos ==1 : axes = [axes]
        suptitle = ""
        if fft: suptitle += "Spectrum of "
        fig.suptitle(suptitle + "Rotor magnetic field", size=16)
        fig.text(0.5, .88, f"from <{filename}>", size=9, color="gray",
                    horizontalalignment='center')
        
        magn_max = field.max()
        magn_min = field.min()                
        ang_freq_done = False 
                       
        for n, (ax, Zpos) in enumerate(zip(axes, list_pos)):    
            
            X, Y, Z = field[3*n:3*n+3]  
            title = ""
            
            if fft:
                X, Y, Z = np.abs(rfft(X)), np.abs(rfft(Y)), np.abs(rfft(Z))
                XYZmax = max(X.max(), Y.max(), Z.max())
                X, Y, Z = X/XYZmax, Y/XYZmax, Z/XYZmax
                title += "PSD "
                if not ang_freq_done:
                    nb_pt = len(X)
                    f_sampling = 1/(A[1] - A[0])     # sampling frequency in rd^-1
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
                if xyz[0]: ax.plot(A, X, '-or', markersize=0.5, label='X')
                if xyz[1]: ax.plot(A, Y, '-og', markersize=0.5, label='Y')
                if xyz[2]: ax.plot(A, Z, '-ob', markersize=0.5, label='Z')
                
            title += f"Magnetic field at Z position #{n+1}: {int(Zpos):3d} mm"
            ax.set_title(title, loc='left', fontsize=9)
            if n == 0: 
                if fft: ax.set_ylabel("Normalized PSD")
                else:   ax.set_ylabel("[mT]")
            ax.legend(bbox_to_anchor=(1.15, 1), loc="upper right")
            ax.minorticks_on()
            ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
            ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)
            if fft: ax.set_ylim(0,1.1)
            else:   ax.set_ylim(1.1*magn_min, 1.1*magn_max)

            if n == nb_Zpos-1:
                if fft: ax.set_xlabel(r"Angular frequency [rd$^{-1}$]")
                else:   ax.set_xlabel("rotor angle [°]")
            
        plt.subplots_adjust(hspace=0.37, right=0.87, top=0.8, bottom=0.12)
        
        png_dir = dirname.replace('TXT', 'PNG')
        if not os.path.exists(png_dir): os.mkdir(png_dir)
        XYZ = build_XYZ_name_with_tuple(xyz)
        if fft: fig_path = os.path.join(png_dir, filename.replace('.txt', f'_PSD_{XYZ}.png'))
        else:   fig_path = os.path.join(png_dir, filename.replace('.txt', f'_PLOT_{XYZ}.png'))
        if show == False: print(fig_path)
        plt.savefig(fig_path)
        if show: plt.show()
        plt.close()
        return 0
    
    except Exception as err:
        print(f"Unexpected error {err=}, {type(err)=}")
        return 1
        
        
def colormap_magField(A, field, list_pos, filename, 
                      figsize=(8,6), mode=None, xyz=(1,1,1), show=True):
    '''
        To draw the magnetic field color map versus angle & Zpos, for diffrent 
        Z positions of the magnetic sensor.
    '''
    dirname = os.path.dirname(filename)
    filename = os.path.basename(filename)

    nb_Zpos = len(list_pos)
    nb_angle_pos, nb_comp = field.shape
    assert(nb_comp // 3 == nb_Zpos)
    
    # Check how many magnetic field components to plot:
    nb_plot = sum(xyz)
    if nb_plot == 0: return

    try:
        fig, axes = plt.subplots(nb_plot, 1, figsize=figsize, sharex=True)
        if nb_plot == 1: axes = [axes]
        fig.suptitle(f"Rotor magnetic field", size=16)
        fig.text(0.5, .88, f"from <{filename}>", size=9, color="gray",
                    horizontalalignment='center')
        
        # build the list of required axes depending on xyz pattern:
        list_axes  = [None, None, None]
        num_axe = 0
        for n, todo in enumerate(xyz):
            if todo:
                list_axes[n] = axes[num_axe]
                num_axe +=1
                    
        mag_labels = ["X", "Y", "Z"]
        magnXYZ    = [field[:, 0::3], field[:, 1::3], field[:, 2::3]]

        magn_max = field.max()
        magn_min = field.min()

        z_pos_labels = filename.split('_')[4:-1]
        z_pos_values = list(map(float, z_pos_labels))
        print(z_pos_values)
        x = np.linspace(0, A[-1], len(A))
        y = np.array(z_pos_values)
        X, Y = np.meshgrid(x, y)

        first_plot = True
        for ax, todo, magn, label in zip(list_axes, xyz, magnXYZ, mag_labels):
            if todo:
                p = ax.pcolormesh(x, y, magn.T, cmap='seismic', 
                              shading='nearest', vmin=magn_min, vmax=magn_max)
                ax.set_title(f"Magnetic field {label}", loc='left', fontsize=9)
                ax.set_yticks(z_pos_values[::-1], z_pos_labels)
                if first_plot: 
                    ax.set_ylabel("Z pos. from top [mm]")
                    first_plot = False
                last_ax = ax
        
        # write xlabel for the last plot:
        last_ax.set_xlabel("Rotation angle [°]")
        
        cax = plt.axes((0.9, 0.1, 0.02, 0.75))
        cbar = fig.colorbar(p, cax=cax, shrink=0.8)    #, location='right', anchor=(1.5, 0.5))
        cbar.ax.set_ylabel('Magnetic field [mT]', rotation=270)
        
        plt.subplots_adjust(hspace=0.37, right=0.87, top=0.8, bottom=0.12)

        png_dir = dirname.replace('TXT', 'PNG')
        if not os.path.exists(png_dir): os.mkdir(png_dir)
        XYZ = build_XYZ_name_with_tuple(xyz)
        fig_path = os.path.join(png_dir, filename.replace('.txt', f'_CMAP_{XYZ}.png'))
        if show == False: print(fig_path)
        plt.savefig(fig_path)
        if show: plt.show()
        plt.close()
        return 0
    
    except Exception as err:
        print(f"Unexpected error {err=}, {type(err)=}")
        return 1

def plot_ROTOR_CSV_magField_at_positions(angles1, field1, Zpos, filename1,
                                         angles2, field2, filename2,
                                         figsize=(8,6), xyz=(1,1,1), show=True, verbose=0):
    '''
        To plot magnetic field versus angle, for different Z positions
        of the magnetic sensor.
    '''
    filename1 = Path(filename1)
    filename2 = Path(filename2)
    assert(filename1.parent == filename2.parent)
    data_dir  = filename1.parent
    filename_ROTOR = filename1.name
    filename_CSV   = filename2.name
    
    # Check how many magnetic field components to plot:
    nb_plot = sum(xyz)
    if nb_plot == 0: return

    if not figsize: figsize = (11, 8)
    fig, axes = plt.subplots(nb_plot, 1, figsize=figsize, sharex=True, sharey=False)
    if nb_plot ==1 : axes = [axes]
    suptitle = ""
    fig.suptitle(suptitle + "Rotor magnetic field", size=16)
    fig.text(0.5, .90, f"from <{filename_ROTOR}>\n and <{filename_CSV}>", size=9, color="gray",
                horizontalalignment='center')
    
    magn_max = max(field1.max(), field2.max())
    magn_min = min(field1.min(), field2.min())
                   
    X, Y, Z = field1  
    R, T, A = field2 * 1e3 # Lille rotor bench: Radial, Tangent, Axial are in Tesla
    
    if verbose:
        print(f'{X.shape=}, {Y.shape=}, {Z.shape=}')
        print(f'{R.shape=}, {A.shape=}, {T.shape=}')
        print(f'{X.max()=}, {Y.max()=}, {Z.max()=}')
        print(f'{R.max()=}, {A.max()=}, {T.max()=}')

    title = f'Magnetic field at Zpos={Zpos:3d} mm'
    fig.suptitle(title, fontsize=15)
        
    lab_B   = {'X':'X', 'Y':'Y', 'Z':'Z'}
    lab_L   = {'X':'rad',     'Y':'axial',     'Z':'tan'}
    field_B = {'X': X,           'Y':Y,           'Z':Z}
    field_L = {'X': R,           'Y':A,           'Z':T}
    colors  = {'X':'red',        'Y':'green',     'Z': 'blue'}
    XYZ_B_L = {'X': xyz[0], 'Y': xyz[1], 'Z': xyz[2]}
    angles_B, angles_L = angles1, angles2
    n = 0
    for c in ('X', 'Y', 'Z'):
        if XYZ_B_L[c]: 
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

    plt.subplots_adjust(hspace=0.2, right=0.88, top=0.88, bottom=0.12)
    
    png_dir = Path(data_dir, 'PNG')
    print(f'{png_dir=}')
    if not png_dir.exists(): png_dir.mkdir()
    
    XYZ = build_XYZ_name_with_tuple(xyz)
    fig_file_name = filename_ROTOR + '__' + filename_CSV + '__.png'
    fig_path = Path(png_dir, fig_file_name)
    print(f'Image file saved as <{fig_path.name}> in <{fig_path.parent}')
    plt.savefig(fig_path)
    if show: plt.show()
    plt.close()
    return 0

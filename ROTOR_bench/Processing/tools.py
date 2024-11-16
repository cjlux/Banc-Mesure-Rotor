import matplotlib.pyplot as plt
import numpy as np
import sys, os
from os.path import join
from stat import ST_CTIME

def build_XYZ_name_with_tuple(xyz):
    labels = ("X", "Y", "Z")
    label = ""
    for x, lab in zip(xyz, labels):
        if x: label+= lab
    return label

def get_files_by_date(directory, PREFIX):
    d = directory
    files = [(os.stat(join(d, f))[ST_CTIME], f) for f in os.listdir(directory) \
             if f.lower().endswith('.txt') and f.startswith(PREFIX)]
    files.sort()
    return  [f for s, f in files]
  
def read_file_ROTOR(fileName):
    
    with open(fileName, 'r', encoding='utf8') as F:
        lines = F.readlines()

    # process the name of the fie <ROTOR_YYYY-MM-DD_hh_mm_ss_ROTSTEP-aa_ZZZ_ZZZ-...txt>
    # Example: <ROTOR_2024-07-09-13-59_WDIST-12_ROTSTEP-4.8_000_030_060_090_1of1.txt
    list_pos = fileName.replace('.txt', '').split('_')[4:-1]
    
    # now read the sensor data lines:
    DATA = []
    for line in lines:
      # skip comments:
      if line[0] == "#": continue
      
      # transform strings into numbers:
      data = [float(x) for x in line.strip().split(';')]
      DATA.append(data)
    
    DATA = np.array(DATA)
    return DATA, list_pos

def read_file_FREE(fileName):
    
    with open(fileName, 'r', encoding='utf8') as F:
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
    
def plot_magField(T, field, filename, figsize=(8,6), stat=None, show=True):
    '''
        To plot magnetic field versus time (free measurement).    
    '''
    dirname = os.path.dirname(filename)
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
    fig.text(0.5, .92, f"from file <{filename}>", size=10, color="gray",
                horizontalalignment='center')
    ax.plot(T, X, '-or', markersize=0.5, label='X')
    ax.plot(T, Y, '-og', markersize=0.5, label='Y')
    ax.plot(T, Z, '-ob', markersize=0.5, label='Z')
    ax.legend(bbox_to_anchor=(1.15, 1), loc="upper right")
    ymean = np.array(ax.get_ylim()).mean()
    yp2p = np.ptp(np.array(ax.get_ylim()))
    if stat:
        ax.text(1.07*T.max(), ymean, r"$\sigma_X$: " + f"{sigmaX:5.2e} mT", color='r')
        ax.text(1.07*T.max(), ymean - 0.06*yp2p, r"$\sigma_Y$: " + f"{sigmaY:5.2e} mT", color='g')
        ax.text(1.07*T.max(), ymean - 0.12*yp2p, r"$\sigma_Z$: " + f"{sigmaZ:5.2e} mT", color='b')
    ax.minorticks_on()
    ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
    ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)
    ax.set_ylabel("[mT]")
    ax.set_xlabel("Time[s]")
    plt.subplots_adjust(right=0.84)
    figPath = os.path.join(dirname, filename.replace('.txt', '.png'))
    if show == False: print(figPath)
    plt.savefig(figPath)
    if show: plt.show()
    plt.close()
    return 0

def plot_magField_at_positions(A, field, list_pos, filename, 
                               figsize=(8,6), mode='', xyz=(1,1,1), show=True):
    '''
        To plot magnetic field versus angle, for diffrent Z positions
        of the magnetic sensor.
    '''
    dirname = os.path.dirname(filename)
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
        fig.suptitle(f"Rotor magnetic field", size=16)
        fig.text(0.5, .88, f"from file <{filename}> (scan: {mode})", size=10, color="gray",
                    horizontalalignment='center')
        
        magn_max = field.max()
        magn_min = field.min()
        
        for n, (ax, Zpos) in enumerate(zip(axes, list_pos)):      
            X, Y, Z = field[3*n:3*n+3]
            if xyz[0]: ax.plot(A, X, '-or', markersize=0.5, label='X')
            if xyz[1]: ax.plot(A, Y, '-og', markersize=0.5, label='Y')
            if xyz[2]: ax.plot(A, Z, '-ob', markersize=0.5, label='Z')
            ax.set_title(f"Magnetic field at Z position #{n+1}: {int(Zpos):3d} mm",
                         loc='left', fontsize=9)
            if n == 0: 
                ax.legend(bbox_to_anchor=(1.15, 1), loc="upper right")
                ax.set_ylabel("[mT]")
            ax.minorticks_on()
            ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
            ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)
            ax.set_ylim(1.1*magn_min, 1.1*magn_max)

            if n == nb_Zpos-1:
                ax.set_xlabel("rotor angle [°]")
            
        plt.subplots_adjust(hspace=0.37, right=0.87, top=0.8, bottom=0.12)
        XYZ = build_XYZ_name_with_tuple(xyz)
        figPath = os.path.join(dirname, filename.replace('.txt', f'_PLOT_{XYZ}.png'))
        if show == False: print(figPath)
        plt.savefig(figPath)
        if show: plt.show()
        plt.close()
        return 0
    
    except:
        print("A problem occured when processing data file....")
        return 1
        
        
def colormap_magField(A, field, list_pos, filename, 
                      figsize=(8,6), mode='', xyz=(1,1,1), show=True):
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
        fig.text(0.5, .88, f"from file <{filename}> (scan: {mode})", size=10, color="gray",
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
        XYZ = build_XYZ_name_with_tuple(xyz)
        figPath = os.path.join(dirname, filename.replace('.txt', f'_CMAP_{XYZ}.png'))
        if show == False: print(figPath)
        plt.savefig(figPath)
        if show: plt.show()
        plt.close()
        return 0
    
    except:
        print("A problem occured when processing data file....")
        return 1

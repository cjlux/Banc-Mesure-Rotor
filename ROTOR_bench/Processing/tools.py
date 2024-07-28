import matplotlib.pyplot as plt
import numpy as np
import sys, os
from os.path import join
from stat import ST_CTIME

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

def plot_magField_at_positions(A, field, list_pos, filename, figsize=(8,6), show=True):

    nb_Zpos = len(list_pos)
    nb_comp, nb_angle_pos = field.shape
    assert(nb_comp // 3 == nb_Zpos)

    dirname = os.path.dirname(filename)
    filename = os.path.basename(filename)

    fig, axes = plt.subplots(nb_Zpos, 1, figsize=figsize, sharex=False)
    fig.suptitle(f"Rotor magnetic field", size=16)
    fig.text(0.5, .92, f"from file <{filename}>", size=10, color="gray",
                horizontalalignment='center')
    for n, p in enumerate(list_pos):
      if nb_Zpos >=2:
          ax = axes[n]
      else:
          ax = axes

      X, Y, Z = field[3*n:3*n+3]
      ax.plot(A, X, '-or', markersize=0.5, label='X')
      ax.plot(A, Y, '-og', markersize=0.5, label='Y')
      ax.plot(A, Z, '-ob', markersize=0.5, label='Z')
      ax.set_title(f"Magnetic field at position #{n+1}: {int(p):3d} mm")
      ax.legend(bbox_to_anchor=(1.15, 1), loc="upper right")
      ax.minorticks_on()
      ax.grid(which='major', color='xkcd:cool grey',  linestyle='-',  alpha=0.7)
      ax.grid(which='minor', color='xkcd:light grey', linestyle='--', alpha=0.5)
      ax.set_ylabel("[mT]")

      if n == nb_Zpos-1:
         ax.set_xlabel("rotor angle [°]")

    plt.subplots_adjust(right=0.86, hspace=0.4)
    figPath = os.path.join(dirname, filename.replace('.txt', '.png'))
    if show == False: print(figPath)
    plt.savefig(figPath)
    if show: plt.show()
    plt.close()
    

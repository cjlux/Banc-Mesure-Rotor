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
    
def plot_magField(T, field, filename, figsize=(8,6)):

    dirname = os.path.dirname(filename)
    filename = os.path.basename(filename)

    X, Y, Z = field
    sigmaX, sigmaY, sigmaZ = X.std(), Y.std(), Z.std()
    
    fig, ax = plt.subplots(1, 1, figsize=figsize, sharex=True)
    fig.suptitle(f"Rotor magnetic field", size=16)
    ax.set_title(f"from file <{filename}>", color="grey", size=12)
    ax.plot(T, X, '-or', markersize=0.5, label='X')
    ax.plot(T, Y, '-og', markersize=0.5, label='Y')
    ax.plot(T, Z, '-ob', markersize=0.5, label='Z')
    ax.legend(bbox_to_anchor=(1.15, 1), loc="upper right")
    ymean = np.array(ax.get_ylim()).mean()
    yp2p = np.ptp(np.array(ax.get_ylim()))
    ax.text(1.07*T.max(), ymean, r"$\sigma_X$: " + f"{sigmaX:5.2e} mT", color='r')
    ax.text(1.07*T.max(), ymean - 0.06*yp2p, r"$\sigma_Y$: " + f"{sigmaY:5.2e} mT", color='g')
    ax.text(1.07*T.max(), ymean - 0.12*yp2p, r"$\sigma_Z$: " + f"{sigmaZ:5.2e} mT", color='b')
    ax.grid()
    ax.set_ylabel("[mT]")
    ax.set_xlabel("Time[s]")
    plt.subplots_adjust(right=0.84)
    figPath = os.path.join(dirname, filename.replace('.txt', '.png'))
    print(figPath)
    plt.savefig(figPath)
    plt.show()

def plot_magField_at_positions(A, field, list_pos, filename, figsize=(8,6)):

    nb_Zpos = len(list_pos)
    nb_comp, nb_angle_pos = field.shape
    assert(nb_comp // 3 == nb_Zpos)

    dirname = os.path.dirname(filename)
    filename = os.path.basename(filename)

    fig, axes = plt.subplots(nb_Zpos, 1, figsize=figsize, sharex=True)
    fig.suptitle(f"Rotor magnetic field\nfrom file <{filename}>", size=16)

    for n, p in enumerate(list_pos):
      if nb_Zpos >=2:
          ax = axes[n]
      else:
          ax = axes
      
      X, Y, Z = field[3*n:3*n+3]
      ax.plot(A, X, '-or', markersize=0.5, label='X')
      ax.plot(A, Y, '-og', markersize=0.5, label='Y')
      ax.plot(A, Z, '-ob', markersize=0.5, label='Z')
      ax.set_title(f"Magnetic field at position #{n+1}: {p} mm")
      ax.legend(bbox_to_anchor=(1.15, 1), loc="upper right")
      ax.grid()
      ax.set_ylabel("[mT]")

      if n == nb_Zpos-1:
         ax.set_xlabel("rotor angle [°]")

    plt.subplots_adjust(right=0.86)
    figPath = os.path.join(dirname, filename.replace('.txt', '.png'))
    print(figPath)
    plt.savefig(figPath)
    plt.show()
    
if __name__ == "__main__":
    
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', action="store", dest='data_dir', 
                         help="Optional, the relative path of the data directory")
    args = parser.parse_args()
    data_dir = "./" if not args.data_dir else args.data_dir
        
    list_file = get_files_by_date(data_dir, 'ROTOR')

    if not list_file:
       print(f"No .txt file found in directory <{data_dir}>, tchao")
    else:    
        while True:
            for i, file in enumerate(list_file):
                print(f'{i:2d} -> {os.path.join(data_dir, file)}')
            rep = input("Fichier choisi [Q->Quit, RET->Choose last file]: ")
            if rep.lower() == 'q':
                break
            elif rep == "":
                i = len(list_file)-1
            else:
                i = int(rep)

            fileName = os.path.join(data_dir, list_file[i])
            DATA, list_pos = read_file_ROTOR(fileName)
            # transpose DATA to extract the different variables:
            A, magnField = DATA.T[0], DATA.T[1:]        
            # plot the data
            plot_magField_at_positions(A, magnField, list_pos, fileName, figsize=(10,8))


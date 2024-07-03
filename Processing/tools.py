import matplotlib.pyplot as plt
import numpy as np
import sys, os
from os.path import join
from stat import ST_CTIME

def get_files_by_date(directory):
    d = directory
    files = [(os.stat(join(d, f))[ST_CTIME], f) for f in os.listdir(directory) \
             if join(d, f).lower().endswith('.txt') ]
    files.sort()
    return  [f for s, f in files]
  
def read_file(fileName):
    
    with open(fileName, 'r', encoding='utf8') as F:
        lines = F.readlines()

    # process the name of the fie <ROTOR_YYYY-MM-DD_hh_mm_ss_ROTSTEP-aa_ZZZ_ZZZ-...txt>
    # Example: <ROTOR_2024-07-03-16-54_ROTSTEP-6_010_030_040.txt>
    list_pos = fileName.replace('.txt', '').split('_')[4:]
    
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

def plot_magField_at_positions(A, field, list_pos, filename, figsize=(8,6)):

    nb_Zpos = len(list_pos)
    nb_comp, nb_angle_pos = field.shape
    assert(nb_comp // 3 == nb_Zpos)

    dirname = os.path.dirname(filename)
    filename = os.path.basename(filename)

    fig, axes = plt.subplots(nb_Zpos, 1, figsize=figsize, sharex=True)
    fig.suptitle(f"Rotor magnetic field from file <{filename}>", size=14)

    component_prop = (('X','r'), ('Y','g'), ('Z','b'))
    for n, p in enumerate(list_pos):
      ax = axes[n]
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
        
    list_file = get_files_by_date(data_dir)

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
            DATA, nb_Zpos = read_file(fileName)
            # transpose DATA to extract the different variables:
            A, magnField = DATA.T[0], DATA.T[1:]        
            # plot the data
            plot_magField_at_positions(A, magnField, nb_Zpos, fileName, figsize=(10,8))


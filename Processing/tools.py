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
    return  [f for s,f in files]

def user_choose_file(data_dir):
    list_file = get_files_by_date(data_dir)
    if not list_file:
       print(f"No .txt file found in directory <{data_dir}>, tchao")
       return
    while True:
        for i, file in enumerate(list_file):
            print(f'{i:2d} -> {os.path.join(data_dir, file)}')
        i = input("Fichier choisi [Q -> Quit]: ")
        if i.lower() in ('', 'q'):
            break
        i = int(i)     
        fileName = os.path.join(data_dir, list_file[i])
        DATA, nb_Z_pos = read_file(fileName)
        break

    return fileName, DATA, nb_Z_pos

  
def read_file(fileName):
    
    with open(fileName, 'r', encoding='utf8') as F:
        lines = F.readlines()

    # process the header line
    line0 = lines[0]
    header_fields = line0.strip().split(';')

    nb_Z_pos = len(header_fields[2:])//3
    Z_pos = []
    for n in range(1, nb_Z_pos+1):
       line = lines[n].strip()
       Z_pos.append(line.split(':')[1].strip())
    
    DATA = []
    for line in lines[nb_Z_pos+1:]:
      # skip comments:
      if line[0] == "#":
        raise Exception("Error occured while reading data: '#' char detected")
      # transform strings into numbers:
      data = [float(x) for x in line.strip().split(';')[1:]]
      DATA.append(data)
    
    DATA = np.array(DATA)
    return DATA, nb_Z_pos

def plot_magField_at_positions(A, field, nb_Z_pos, filename, figsize=(8,6)):
   nb_cols, nb_angle_pos = field.shape
   assert(nb_cols // 3 == nb_Z_pos)

   filename = os.path.basename(filename)

   fig, axes = plt.subplots(nb_Z_pos, 1, figsize=figsize, sharex=True)
   fig.suptitle(f"Rotor magnetic field from file <{filename}>", size=14)

   component_prop = (('X','r'), ('Y','g'), ('Z','b'))
   for p in range(nb_Z_pos):
      ax = axes[p]
      X, Y, Z = field[3*p:3*p+3]
      ax.plot(A, X, '-or', markersize=0.5, label='X')
      ax.plot(A, Y, '-og', markersize=0.5, label='Y')
      ax.plot(A, Z, '-ob', markersize=0.5, label='Z')
      ax.set_title(f"Magnetic field at position #{p+1}")
      ax.legend(bbox_to_anchor=(1.15, 1), loc="upper right")
      ax.grid()

      if p == nb_Z_pos-1:
         ax.set_xlabel("rotor angle [°]")

   plt.subplots_adjust(right=0.86)
   plt.show()
    
if __name__ == "__main__":
    
    import argparse
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--dir', action="store", dest='data_dir', 
                         help="Optional, the relative path of the data directory")
    
    args = parser.parse_args()
    data_dir = "../" if not args.data_dir else args.data_dir
    
    
    fileName, DATA, nb_Z_pos = user_choose_file(data_dir)

    # transpose DATA to exxtract the different variables:
    A, magnField = DATA.T[0], DATA.T[1:]

    # plot the data
    plot_magField_at_positions(A, magnField, nb_Z_pos, fileName, figsize=(10,8))


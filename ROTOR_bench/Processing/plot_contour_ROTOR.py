from tools import get_files_by_date, read_file_ROTOR, read_file_FREE, plot_magField_at_positions
import matplotlib.pyplot as plt
import numpy as np
import sys, os
from os.path import join

if __name__ == "__main__":
    
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', action="store", dest='data_dir', 
                         help="Optional, the relative path of the data directory")
    args = parser.parse_args()
    data_dir = "../../" if not args.data_dir else args.data_dir
        
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
            magn_X = DATA[:, 1::3]
            magn_Y = DATA[:, 2::3]
            magn_Z = DATA[:, 3::3]
            magn_max = DATA[:, 1:].max()
            magn_min = DATA[:, 1:].min()

            rotation_step = float(fileName.split('_')[3].split('-')[-1])
            z_pos_labels = fileName.split('_')[4:-1]
            z_pos_values = list(map(float, z_pos_labels))
            x = np.arange(0, 360+rotation_step, rotation_step)
            y = np.array(z_pos_values)
            X, Y = np.meshgrid(x, y)
            figsize=(10,8)
            fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)
            fig.suptitle(f"Rotor magnetic field", size=16)

            for i, (ax, magn, label) in enumerate(
                zip(axes,
                    (magn_X, magn_Y, magn_Z),
                    ("X", "Y", "Z"))):
                p = ax.pcolor(X, Y, magn.T, cmap='seismic',
                              vmin=magn_min, vmax=magn_max)
                ax.set_title(f"Magnetic field {label}")
                ax.set_yticks(z_pos_values[::-1], z_pos_labels)
                if i == 0: ax.set_ylabel("Z pos. from top [mm]")
                if i == 2: ax.set_xlabel("Rotation angle [°]")
            
            cax = plt.axes((0.9, 0.1, 0.02, 0.8))
            cbar = fig.colorbar(p, cax=cax, shrink=0.8)    #, location='right', anchor=(1.5, 0.5))
            cbar.ax.set_ylabel('Magnetic field [mT]', rotation=270)
            
            #plt.tightlayout()
            plt.subplots_adjust(hspace=0.37, right=0.87)
            plt.show()

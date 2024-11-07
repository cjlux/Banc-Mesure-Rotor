from tools import get_files_by_date, read_file_ROTOR, plot_magField_at_positions
import matplotlib.pyplot as plt
import numpy as np
import sys, os
from os.path import join
from stat import ST_CTIME

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', action="store", dest='data_dir', 
                         help="Optional, the relative path of the data directory")
    parser.add_argument('-a', '--all', action="store_true", dest='all_file', 
                         help="Optional, to draw the plots for all of the .txt in the directory")

    args = parser.parse_args()
    data_dir = "./TXT" if not args.data_dir else args.data_dir
    all_file = args.all_file
        
    #JLC_was: list_file = get_files_by_date(data_dir, 'ROTOR')
    list_file = [f for f in os.listdir(data_dir) \
             if f.lower().endswith('.txt') and f.startswith('ROTOR')]
    list_file.sort()
    print(list_file)
    if not list_file:
        print(f"No .txt file found in directory <{data_dir}>, tchao")
        
    elif not all_file:    
        while True:
            for i, file in enumerate(list_file):
                print(f'{i:3d} -> {os.path.join(data_dir, file)}')
            rep = input("Fichier choisi [Q->Quit, RET->Choose last file]: ")
            if rep.lower() == 'q':
                break
            elif rep == "":
                i = len(list_file)-1
            else:
                i = int(rep)

            fileName = os.path.join(data_dir, list_file[i])
            DATA, list_pos = read_file_ROTOR(fileName)

            if DATA.shape[1] == 5:
                print("Plot ByAngle")
                # re-arrange DATA to be an array with lines formated like:
                # "# angle[°]; X1_magn [mT]; Y1_magn [mT]; Z1_magn [mT]; X2_magn [mT]; Y2_magn [mT]; Z2_magn [mT];..."
                # instead of:
                # "# ZPos#; a[°]; X1_magn[mT]; Y1_magn[mT]; Z1_magn[mT]"
                nb_col = 1 + 3 * len(list_pos) #  angle col + (X , Y, Z) * nb_Zpo
                nb_row = int(len(DATA)/len(list_pos))
                newDATA = np.ndarray((nb_row, nb_col), dtype=float)

                # copy angle column
                newDATA[ :, 0] = DATA[ : nb_row, 1]
                # copy X,Y,Z for all Zpos:
                nb_val = 3 # the 3 components X, Y and Z
                for n in range(len(list_pos)):
                    newDATA[ : , 1 + n*nb_val : 1 + (n+1)*nb_val] = DATA[n*nb_row : (n+1)*nb_row, 2:]

                DATA = newDATA

                A, magnField = DATA.T[0], DATA.T[1:]
                plot_magField_at_positions(A, magnField, list_pos, fileName, figsize=(10,8))

            else:
                print("plot ByPos")
                # transpose DATA to extract the different variables:
                A, magnField = DATA.T[0], DATA.T[1:]        
                # plot the data
                plot_magField_at_positions(A, magnField, list_pos, fileName, figsize=(10,8))
            
    else:
        for f in list_file:
            fileName = os.path.join(data_dir, f)
            DATA, list_pos = read_file_ROTOR(fileName)
            # transpose DATA to extract the different variables:
            A, magnField = DATA.T[0], DATA.T[1:]        
            # plot the data
            plot_magField_at_positions(A, magnField, list_pos, fileName, figsize=(10,8), show=False)
        

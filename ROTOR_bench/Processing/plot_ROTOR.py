#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#

try:
    from .tools import read_file_ROTOR, plot_magField_at_positions
except:
    from tools import read_file_ROTOR, plot_magField_at_positions
import numpy as np
import sys, os
from os.path import join

def plot_ROTOR(file_path, xyz=(1,1,1), figsize=None, show=True, fft=False):
    
    DATA, list_pos = read_file_ROTOR(file_path)

    if DATA.shape[1] == 5:
        mode="ByAngle"
        # re-arrange DATA to be an array with lines formated like:
        # "# angle[°]; X1_magn [mT]; Y1_magn [mT]; Z1_magn [mT]; X2_magn [mT]; Y2_magn [mT]; Z2_magn [mT];..."
        # instead of:
        # "# ZPos#; a[°]; X1_magn[mT]; Y1_magn[mT]; Z1_magn[mT]"
        nb_col = 1 + 3 * len(list_pos) #  angle col + (X , Y, Z) * nb_Zpo
        nb_row = int(len(DATA)/len(list_pos))
        newDATA = np.ndarray((nb_row, nb_col), dtype=float)

        # copy angle columngit config pull.rebase false
        newDATA[ :, 0] = DATA[ : nb_row, 1]
        # copy X,Y,Z for all Zpos:
        nb_val = 3 # the 3 components X, Y and Z
        for n in range(len(list_pos)):
            newDATA[ : , 1 + n*nb_val : 1 + (n+1)*nb_val] = DATA[n*nb_row : (n+1)*nb_row, 2:]
        DATA = newDATA
    else:
        mode="ByZPos"

    # transpose DATA to extract the different variables:
    A, magnField = DATA.T[0], DATA.T[1:]        
    # plot the data
    if not figsize:
        H, nb_Zpos = 8, len(list_pos)
        if nb_Zpos == 1:
            H = 4
        elif nb_Zpos == 2:
            H = 6
        figsize = (10, H)
    ret = plot_magField_at_positions(A, magnField, list_pos, file_path, figsize=figsize, mode=mode, show=show, xyz=xyz, fft=fft)
    return ret
    
    
def main(parser):

    args = parser.parse_args()

    all_file = args.all_file
    file     = args.file
    FFT      = args.FFT
    data_dir = "./TXT" if not args.data_dir else args.data_dir
    xyz = "111" if not args.xyz else str(args.xyz)
 
    Lxyz = []
    for n in xyz:
        Lxyz.append(int(n))
    Txyz = tuple(Lxyz)

    ret = 0
    if file:
        ret = plot_ROTOR(file, xyz=Txyz, fft=FFT)
    else:        
        #JLC_was: list_file = get_files_by_date(data_dir, 'ROTOR')
        list_file = [f for f in os.listdir(data_dir) \
                 if f.lower().endswith('.txt') and f.startswith('ROTOR')]
        list_file.sort()
        
        if not list_file:
            print(f"No .txt file found in directory <{data_dir}>, tchao")
            ret = 1
            
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

                file_path = os.path.join(data_dir, list_file[i])
                ret = plot_ROTOR(file_path, xyz=Txyz, fft=FFT)
                
        else:
            for f in list_file:
                f_path = os.path.join(data_dir, f)
                ret = plot_ROTOR(f_path, xyz=Txyz, show=False, fft=FFT)
    
    return ret
        
    
if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', action="store", dest='data_dir', 
                         help="Optional, the relative path of the data directory")
    parser.add_argument('--xyz', action="store", dest='xyz', 
                         help="Which component of the magnetic field to plot : '101' plots X and Z")
    parser.add_argument('--file', action="store", dest='file', 
                         help="Which component of the magnetic field to plot : '101' plots X and Z")

    parser.add_argument('-a', '--all', action="store_true", dest='all_file', 
                         help="Optional, to draw the plots for all of the .txt in the directory")
    parser.add_argument('-fft', '--fft', action="store_true", dest='FFT', 
                         help="Wether to plot the spectral DSP or not")
    
        
    sys.exit(main(parser))

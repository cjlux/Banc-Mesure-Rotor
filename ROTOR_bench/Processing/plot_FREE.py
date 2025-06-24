#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#

from tools import get_files_by_date, read_file_FREE, plot_magField
import matplotlib.pyplot as plt
import numpy as np
import sys, os
from os.path import join
from stat import ST_CTIME

def plot_FREE(file_path, xyz=(1,1,1), show=True):
    
    DATA = read_file_FREE(file_path)

    # transpose DATA to extract the different variables:
    T, magnField = DATA.T[0], DATA.T[1:]            

    # plot the data
    ret = plot_magField(T, magnField, file_path, figsize=(10,8), show=show, xyz=xyz)
    return ret
    

def main(parser):

    args = parser.parse_args()

    all_file = args.all_file
    file     = args.file
    data_dir = "./TXT" if not args.data_dir else args.data_dir
    xyz = "111" if not args.xyz else str(args.xyz)
 
    Lxyz = []
    for n in xyz:
        Lxyz.append(int(n))
    Txyz = tuple(Lxyz)

    ret = 0
    if file:
        ret = plot_FREE(file, xyz=Txyz)
    else:        
        #JLC_was: list_file = get_files_by_date(data_dir, 'ROTOR')
        list_file = [f for f in os.listdir(data_dir) \
                 if f.lower().endswith('.txt') and f.startswith('FREE')]
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
                ret = plot_FREE(file_path, xyz=Txyz)
                
        else:
            for f in list_file:
                f_path = os.path.join(data_dir, f)
                ret = plot_FREE(f_path, xyz=Txyz, show=False)
    
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
    
        
    sys.exit(main(parser))
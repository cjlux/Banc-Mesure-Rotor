from tools import get_files_by_date, read_file_ROTOR, read_file_FREE, plot_magField_at_positions
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


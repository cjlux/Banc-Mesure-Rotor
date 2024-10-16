from tools import get_files_by_date, read_file_FREE, plot_magField
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
    
    list_file = get_files_by_date(data_dir, 'FREE')

    if not list_file:
       print(f"No .txt file found in directory <{data_dir}>, tchao")
       
    elif not all_file: 
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
            DATA = read_file_FREE(fileName)
            # transpose DATA to extract the different variables:
            T, magnField = DATA.T[0], DATA.T[1:]        
            # plot the data
            plot_magField(T, magnField, fileName, figsize=(10,8))

    else:
        for f in list_file:
            fileName = os.path.join(data_dir, f)
            DATA = read_file_FREE(fileName)
            # transpose DATA to extract the different variables:
            T, magnField = DATA.T[0], DATA.T[1:]            
            # plot the data
            plot_magField(T, magnField, fileName, figsize=(10,8), show=False)

#
# Copyright 2024-2025 Jean-Luc.CHARLES@mailo.com
#

try:
    from .tools import read_file_ROTOR, read_file_ROTOR_L, plot_ROTOR_CSV_magField_at_positions
except:
    from tools import read_file_ROTOR, read_file_ROTOR_L, plot_ROTOR_CSV_magField_at_positions
    
import numpy as np
import sys, os
from os.path import join

def plot_CSV_ROTOR(CSV_num:int,
                   TXT_num:int,
                   Zpos: int,
                   data_dir:str,
                   xyz:tuple=(1,1,1),
                   figsize:tuple=None,
                   show:bool=True,
                   verbose=0):
    '''
    To plot the ROTOR data (.txt file) and the data from the Lille bench (.csv file) 
    '''
    
    file_list = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f[-4:] in ('.csv','.txt')]
    file_list.sort(reverse=True)

    CSV_file = file_list[CSV_num]
    ROT_file = file_list[TXT_num]
    
    print(f'{ROT_file=}, {CSV_file=}')
                    
    ROTOR_DATA, list_pos, step_angle = read_file_ROTOR(ROT_file)
    CSVbench_DATA = read_file_ROTOR_L(CSV_file)
    
    if ROTOR_DATA.shape[1] == 5:
        mode="ByAngle"
        # re-arrange DATA to be an array with lines formated like:
        # "# angle[°]; X1_magn [mT]; Y1_magn [mT]; Z1_magn [mT]; X2_magn [mT]; Y2_magn [mT]; Z2_magn [mT];..."
        # instead of:
        # "# ZPos#; a[°]; X1_magn[mT]; Y1_magn[mT]; Z1_magn[mT]"
        nb_col = 1 + 3 #  angle col + (X , Y, Z)
        nb_row = int(len(ROTOR_DATA)/len(list_pos))
        newDATA = np.ndarray((nb_row, nb_col), dtype=float)

        # copy angle column
        newDATA[ :, 0] = ROTOR_DATA[ : nb_row, 1]
        # copy X,Y,Z for all Zpos:
        nb_val = 3 # the 3 components X, Y and Z
        try:
            index_Zpos = list_pos.index(f'{Zpos:03d}')
        except:
            print(f'Zpos: {Zpos} not found in the list of Zpos: {list_pos}. Try anaother value')
            return 1
        
        for n in range(len(list_pos)):
            if n != index_Zpos: continue
            newDATA[ : , 1 : 1 + nb_val] = ROTOR_DATA[n*nb_row : (n+1)*nb_row, 2:]
        ROTOR_DATA = newDATA
    else:
        mode="ByZPos"

    i_range = np.where(CSVbench_DATA.T[2] == int(Zpos))
    CSVbench_DATA  = CSVbench_DATA[i_range]


    # transpose DATA to extract the different variables:
    angles1, magnField1 = ROTOR_DATA.T[0], ROTOR_DATA.T[1:]       
    angles2, magnField2 = CSVbench_DATA.T[1], CSVbench_DATA.T[3:]
    
    ret = plot_ROTOR_CSV_magField_at_positions(angles1, magnField1, Zpos, ROT_file, 
                                               angles2, magnField2, CSV_file,
                                               figsize=figsize, show=show, xyz=xyz,
                                               verbose=verbose)
    return ret
    
    
def main(parser):

    args     = parser.parse_args()
    data_dir = args.data_dir
    xyz      = str(args.xyz)
    Zpos     = args.Zpos
    verbose  = args.verbose
 
    Lxyz = []
    for n in xyz:
        Lxyz.append(int(n))
    Txyz = tuple(Lxyz)

    # List the *.csv and *.txt files in the datadir directory:
    ret = 0
    list_file = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f[-4:] in ('.csv','.txt')]
    list_file.sort()
    
    # display the numeroted list of siles:
    if not list_file:
        print(f"No .txt file found in directory <{data_dir}>, tchao")
        ret = 1
    else:
        while True:
            for i, file in enumerate(list_file): print(f'{i:3d} -> {os.path.join(data_dir, file)}')
            rep = input("Please input: num_csv, num_rotor [Q->Quit]: ")
            if rep.lower() == 'q': break
            rep = rep.replace(',',' ')
            csv_num, txt_num = map(int, rep.split())
            ret = plot_CSV_ROTOR(csv_num, txt_num, Zpos, data_dir, xyz=Txyz, verbose=verbose)    
            
    return ret
        
    
if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', action="store", dest='data_dir', default='./avril2025',
                         help="The relative path of the data directory")
    parser.add_argument('--zpos', action="store", dest='Zpos', default=60, type=int,
                         help="The relative path of the data directory")
    parser.add_argument('--xyz', action="store", dest='xyz', default='111',
                         help="Which component of the magnetic field to plot : '101' plots X and Z")
    parser.add_argument('-v', '--verbose', action="store", dest='verbose', default=1, type=int,
                         help="The verbosity required")
            
    sys.exit(main(parser))

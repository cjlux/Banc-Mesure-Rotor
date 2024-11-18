try:
    from .tools import read_file_ROTOR, colormap_magField
except:
    from tools import read_file_ROTOR, colormap_magField
import numpy as np
import sys, os

def colormap_ROTOR(fille_path, xyz=(1,1,1), show=True):
    
    DATA, list_pos = read_file_ROTOR(fille_path)
    
    if DATA.shape[1] == 5:
        mode="ByAngle"
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
    else:
        mode="ByZPos"

    if list_pos == ['000']:
        print("Cannot draw color map with just one Z_pos = 0, sorry....")
        return 2
    
    # Extract the different variables:
    A, magnField = DATA[:, 0], DATA[:, 1:]  
    # plot the colormap:
    heights = (None, 4, 6, 8)
    height  = heights[sum(xyz)]
    ret = colormap_magField(A, magnField, list_pos, fille_path, figsize=(10, height), mode=mode, show=show, xyz=xyz) 
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
        ret = colormap_ROTOR(file, xyz=Txyz)
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
                ret = colormap_ROTOR(file_path, xyz=Txyz)    
                 
        else:
            for f in list_file:
                f_path = os.path.join(data_dir, f)
                ret = colormap_ROTOR(f_path, xyz=Txyz, show=False)
                
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
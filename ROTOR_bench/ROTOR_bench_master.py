#
# Copyright Jean-Luc.CHARLES@mailo.com
#
 
import sys, os
import numpy as np
from time import sleep, time
from Tools import get_RotStep, get_ZPOS, open_Serial, uniq_fileName, write_header
from ROTOR_config import STEPPER_ANGLE1, RATIO1

def main(params:dict = None):

    serialPort = open_Serial()
    sleep(1)

    if params is None:
        rot_step, NBSTEP1 = get_RotStep()
        Zpos_mm = get_ZPOS()
    else:
        rot_step = params['ROTSTEP_DEG']
        NBSTEP1 = round(rot_step*RATIO1/STEPPER_ANGLE1)
        Zpos_mm = params['ZPOS_MM']
        
    nb_sensor_pos = len(Zpos_mm)
    
    # Build the parameters string to send to the Arduino:
    mess2mega = f'NBSTEP1:{NBSTEP1};'
    for (n, z)  in enumerate(Zpos_mm, 1):
        mess2mega += f'POS:{n}%ZMM:{z};'
        mess2mega += '\n'        
    print(f'Sending to MEGA2560: <{mess2mega.strip()}>')    
    data_w = bytes(mess2mega, encoding="ascii")
    serialPort.write(data_w)
    serialPort.flush()

    # Define the unique file name for the data
    fileName = uniq_fileName(rot_step, Zpos_mm)

    # write the header lines in the data file
    write_header(fileName, rot_step, Zpos_mm)
    

    fOut = open(fileName, "a", encoding="utf8")
    t0 = time()

    while True:            
        # read Arduino measurement
        data_m = serialPort.readline()          # read data measurement
        data_m = data_m.decode().strip()        # clean data
        
        if data_m.startswith("[DATA]"):
             fOut.write(data_m.replace('[DATA] ', '')+'\n')
             fOut.flush()
        elif "EMERGENCY-STOP" in data_m:
            print("EMERGENCY-STOP resquested from ARDUINO, Tcho !")
            break
        elif "END of measure" in data_m: break
        
        print(data_m)
        
    t1 = time()-t0  
    fOut.write(f"# Measurement duration: {round(t1,1):.1f} sec\n")
    # close data file:
    fOut.close()

    # clean serial port before closing
    serialPort.flushOutput()
    sleep(1)

    #close serial
    serialPort.close()

    return (fileName)


if __name__ == '__main__':

    params = {'ROTSTEP_DEG': 24, 'ZPOS_MM':[10]}
    main(params)
    print("\nAGAIN\n")
    main(params)
    
    

#
# Copyright 2024 Jean-Luc.CHARLES@mailo.com
#
import os
import numpy as np
from dataclasses import dataclass

import matplotlib.pyplot as plt
from serial import Serial
from time import sleep, time
from datetime import datetime
from ROTOR_config import StepperMotor, Param, Zaxis

    
def get_RotStep():
    while True:
        question = f"Rotation step (must be a multiple of 1.2°) ? "
        rot_step = get_param_from_user(question, float, 1.2, 120, True)

        if 10*rot_step % 12 != 0:
            print(f"the rotation step {rot_step}, {type(rot_step)} is not a multiple of 1.2° !")
            continue
        else:
            NBSTEP1 = round(rot_step*RATIO1/STEPPER_ANGLE1)
            break
        
    return rot_step, NBSTEP1

def get_ZPOS():

    Zpos_mm = []
    while True:
      question = f"# of vertical positions for the sensor in range [{MIN_NB_ZPOS}, {MAX_NB_ZPOS}] ? "
      nb_sensor_pos = get_param_from_user(question, int, MIN_NB_ZPOS, MAX_NB_ZPOS, False)

      for n in range(1, nb_sensor_pos+1):
        question = F"position #{n} from top in mm ? "
        z_mm = get_param_from_user(question, int, ZPOS_MIN, ZPOS_MAX, False)
        Zpos_mm.append(z_mm)

      print("\nPositions along Z (from top):")
      
      for n in range(1, nb_sensor_pos+1):
        print(f"   pos #{n}: {Zpos_mm[n]:03d} mm")
        
      rep = input("Do you confirm these values ? y/n ?")
      if rep.lower() == 'y':
        break

    return Zpos_mm
    
def get_param_from_user(mess:str,
                        data_type,
                        min_value:int,
                        max_value:int,
                        confirm:bool):
    '''
    To get value for some usefull parameters.
    The value must be in the range [min_value, max_value].
    If confirm is True, a confirmation yes/no about the value is proposed
    '''
    while True:
        value = input(mess)
        try:
            value = data_type(value)
        except:
            print("Incorrect value... please type in a new value")
            continue
        else:
            if value < min_value or value > max_value:
                print('value must be in [{min_value}, {max_value}]')
                continue
        if confirm:
            rep = input(f'You typed <{value}>, confirm: [y]/n ? ')
            if rep.lower() == 'y': break
        else:
            break
    return value

def uniq_file_name(prefix='ROTOR', rot_step=None, Zpos_mm=None):
    '''
    Defines a uniq file name mixing date info and parameters info.
    '''
    now = datetime.now() # current date and time
    fileName = f'{prefix}_{now.strftime("%Y-%m-%d-%H-%M")}'
    if rot_step is not None: fileName += f'_ROTSTEP-{rot_step}'
    if Zpos_mm is not None:
        for z in Zpos_mm:
            fileName += f'_{z:03d}'
    fileName += '.txt'

    return fileName


            
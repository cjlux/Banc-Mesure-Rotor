#
# Copyright 2024 Jean-Luc.CHARLES@mailo.com
#
import os
import numpy as np
import matplotlib.pyplot as plt
from serial import Serial
from time import sleep, time
from datetime import datetime
from ROTOR_config import (MIN_NB_ZPOS, MAX_NB_ZPOS, ZPOS_MIN, ZPOS_MAX,
                          STEPPER_ANGLE1, RATIO1)

def open_Serial():
    
    ################################
    # Connexion to serial port :
    ################################
    # Name of the serial port  :
    #   Windows  : "COM3" or "COM4"....
    #   PC-Linux : "/dev/ttyACM0" 
    #   RPi      : same as PC-Linux
    #   Mac OS X : see the title  bar of the wmonitor window.
    #
    # Parameters : Nb data bits  -> 8
    #              Nb STOP bits  -> 1
    #              Parity        -> Sans (None)
    #              baud rate     -> 9600, 14400, 19200, 28800, 38400,
    #                               57600, 115200, 250000
    
    listUSBports = ["/dev/ttyACM0", "/dev/ttyACM1"]

    for port in listUSBports:
        try:
            print(f"Trying {port}")
            serialPort = Serial(port, baudrate=115200, timeout=None)
            break
        except:
            continue
    print(serialPort)    

    # Open serial serial if needed:
    sleep(0.5)
    if not serialPort.is_open :
        serialPort.open()

    # wait for Arduino ready:
    print("Waiting for ARDUINO ... ")
    data = b""
    t0 = time()
    data =""
    while "Arduino OK" not in data :
        try:
            data = serialPort.readline().decode().strip()
        except:
            data = ""
        if "INFO" in data:
            print(data)
        elif "ERROR" in data:
            sys.exit()

    print("Found <Arduino OK> : good !",flush=True)

    return serialPort
    
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

def uniq_fileName(rot_step, Zpos_mm):
    '''
    Defines a uniq file name mixing date info and parameters info.
    '''
    now = datetime.now() # current date and time
    fileName = 'ROTOR_'+now.strftime("%Y-%m-%d-%H-%M")
    fileName += f'_STEP-{rot_step}'
    for z in Zpos_mm:
        fileName += f'_{z:03d}'
    fileName += '.txt'

    return fileName

def write_header(fileName, rot_step, Zpos_mm):
    '''
    Write the header in file based on parameters values
    '''
    NBSTEP1 = round(rot_step*RATIO1/STEPPER_ANGLE1)
    nb_sensor_pos = len(Zpos_mm)
    with open(fileName, "w", encoding="utf8") as fOut:
        line1 = f'# YYMMDD_hh:mm:ss ; Angle[°]'
        line2 = f'# rotation step angle: {rot_step}°, NBSTEP1: {NBSTEP1}\n'
        line3 = f'# {nb_sensor_pos} Z_POS:'
        for (n, z) in enumerate(Zpos_mm, 1):
            line1 += f'; Xmag{n} [mT]; Ymagn{n} [mT]; Zmagn{n} [mT]'
            line3 += f' {z} mm;'
        line = line1 + '\n' + line2 + line3 + '\n'
        fOut.write(line)
            
def get_KeyPressed():
    '''Wait for a key pressed and returns it.'''

    key_pressed = "="
    
    if os.name == 'nt':
        import msvcrt
        key_ressed = msvcrt.getch()
    else:
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key_pressed = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
    return key_pressed

     

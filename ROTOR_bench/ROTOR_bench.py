#
# v1.0 2019/11    JLC initial version
#
# v1.1 2019/11/06 JLC set baudrate to 57600 for RPi.
#                     Improve Emergency STOP processing.
# v1.2 2021/04/28 Guillaume added creation of a file "user_guided_flight.txt"
#                     which register datas (Time [s], Z [m], PWM)
#
# v2.0 2023/06/13 JLC: new architecture with ROS
#
 
import sys, os
import numpy as np
from time import sleep, time
from serial import Serial
from datetime import datetime
from Utils import get_KeyPressed, get_param_from_user

#
# This program must be run from terminal to work !!!
#

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

# JLC 2023/06/13: IIDRE is on /dev/ttyACM0

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
while "Arduino OK" not in data.decode().strip() :
    data = serialPort.readline()
    print(data.decode().strip())
    if "ERROR" in data.decode().strip():
        sys.exit()
print("Found <Arduino OK> : good !",flush=True)

sleep(1)

now = datetime.now() # current date and time
fileName = 'user_guided_flight-'+now.strftime("%Y_%m_%d_%H_%M")+'.txt'

MIN_NB_ZPOS = 1   # The min number of vertical position for the magnetic field sensor
MAX_NB_ZPOS = 5   # The max number of vertical position for the magnetic field sensor
ZPOS_MIN    = 0   # The minimum value of Zpos [mm] for the sensor
ZPOS_MAX    = 130 # The maximum value of Zpos [mm] for the sensor
Zpos_mm     = [0]

while True:
  question = f"# of vertical positions for the sensor in range [{MIN_NB_ZPOS}, {MAX_NB_ZPOS}] ? "
  nb_sensor_pos = get_param_from_user(question, MIN_NB_ZPOS, MAX_NB_ZPOS, False)

  for n in range(1, nb_sensor_pos+1):
    question = F"position #{n} from top in mm ? "
    z_mm = get_param_from_user(question, ZPOS_MIN, ZPOS_MAX, False)
    Zpos_mm.append(z_mm)

  print("\nPositions along Z (from top):")
  mess2mega = ''
  for n in range(1, nb_sensor_pos+1):
    print(f"   pos #{n}: {Zpos_mm[n]:03d} mm")
    mess2mega += f'POS:{n}%ZMM:{Zpos_mm[n]};'
  mess2mega += '\n'
  
  rep = input("Do you confirm these values ? y/n ?")
  if rep.lower() == 'y':
    break
    
print(f'Sending to MEGA2560: <{mess2mega}>')    

data_w = bytes(mess2mega, encoding="ascii")
serialPort.write(data_w)
serialPort.flush()
  
with open(fileName, "w", encoding="utf8") as fOut:
  line = '# YYMMDD_hh:mm:ss ; Angle[°]'
  for n in range(1, nb_sensor_pos+1):
    line += f' ; X{n}_magn [mT] ; Y{n}_magn [mT] ; Z{n}_magn [mT]'
  line += '\n'
  fOut.write(line)
  fOut.flush()
  print(line)

t0 = time()

while True:            
    # read Arduino measurement
    data_m = serialPort.readline()          # read data measurement
    data_m = data_m.decode().strip()        # clean data
    
    if data_m.startswith("ERROR") \
       or data_m.startswith("DEBUG") \
       or data_m.startswith("INFO"):
         print(data_m)
    elif "EMERGENCY-STOP" in data_m:
        print("EMERGENCY-STOP resquested from ARDUINO, Tcho !")
        break
    else:
      pass
    
    print(data_m)
    
#t1 = time()-t0  
#fileOut.write(data_to_write)  
#fileOut.write("# Flight duration: {:.1f} s\n".format(round(t1,1)))
print("\n     >>> End of transmission")

# clean serial port before closing
serialPort.flushOutput()
sleep(0.5)

#close serial
serialPort.close()          

# close data file:
fileOut.close()

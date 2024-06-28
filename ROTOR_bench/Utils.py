#
# 2023/06/16    JLC : plot tabkes only 3 values (time, PWM and z)
#

import os
import numpy as np
import matplotlib.pyplot as plt
from select import select

def plot_file(fileName):
    f_out = open(fileName, "r", encoding="utf8")
    data = []
    for line in f_out:
        try:
            datas = [float(x) for x in line.split()]
            data.append(datas)
        except:
            print("skiping <{}>".format(line.strip()))
            
    data = np.array(data)    
    plot_Z_PWM(data[:,0], data[:,1], data[:,2], fileName)
    return data
    
def plot_Z_PWM(T, PWM, Ztvalues, fileName=None):
    T, PWM, Ztvalues = np.array(T), np.array(PWM), np.array(Ztvalues)
    plt.figure("Flight 1A",  figsize = (10,6) )
    plt.subplots_adjust(left=0.12, bottom=0.11,
                        right=0.90, top=.88,
                        wspace=0.2, hspace=0.4)
    plt.subplot(211)
    plt.title("Position Z versus time")
    plt.plot(T,Ztvalues,"b.-",label ="Zt(t)")
    plt.ylabel("Position $z$ [$m$]")
    plt.xlabel("Time [sec]")
    M1 = Ztvalues.max()
    plt.ylim(0,1.1*M1)
    plt.grid()  
    plt.legend()

    plt.subplot(212)
    plt.title("PWM turbines command versus time")
    plt.plot(T,PWM,"g.-",label ="PWM(t)")
    plt.ylabel("PWM [%]")
    plt.xlabel("Time [sec]")
    plt.ylim(0,100)
    plt.grid()
    plt.legend()
    if fileName is not None:
        imageName = fileName.replace(".txt",".png")
        print("saving plot in file <{}>".format(imageName))
        plt.savefig(imageName)
    plt.show()
    
    
def get_param_from_user(mess:str, min_value:int, max_value:int, confirm:bool):
  '''
  To get value for some usefull parameters.
  The value must be in the range [min_value, max_value].
  If confirm is True, a confirmation yes/no about the value is proposed
  '''
  while True:
    value = min_value -1;                      
    while value < min_value or value > max_value:
      value = input(mess)
      try:
        value = int(value)
      except:
        print('you must type a value in range[{min_value}, {max_value}]')
        continue
        
    if confirm:
      rep = input(f'You typed {value}, confirm: [y]/n ? ')
      if rep.lower() == 'y': break
    else:
      break
  return value
    
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

     

import os
import pigpio    # https://abyz.me.uk/rpi/pigpio/
import numpy as np
import matplotlib.pyplot as plt
from serial import Serial
from time import sleep, time
from datetime import datetime
import sys, subprocess
from pigpio import pi, OUTPUT, PUD_UP, LOW, HIGH

from ROTOR_config import StepperMotor, Zaxis, Param
from Tools import uniq_file_name

class ROTOR_bench:

    def __init__(self, stepper1, stepper2):

        self.stepper1 = stepper1    # the stepper motor for rotating the shaft
        self.stepper2 = stepper2    # the stepper motor for the sensorZ motion
        
        self.emergencyStopRequired = False
        self.serialPort = None      # The serial port connect to the USB link with the magnetic sensor.

        self.Z_pos_mm = []          # The list of the sensorZ positions, the first one is 0.
        
        self.pi = pigpio.pi()       # the driver to the GPIOport of the RPi

        # open the seriallink with the sensor:
        self.open_Serial(5)
        if self.serialPort is None:
            print('[ERROR] cannot open any USB port, tchao!')
            sys.exit()

        # noww let's configure the magnetic sensor:
        ret = self.config_USBsensor()
        if ret !=0:
            print('[ERROR] while configuring the USBsensor, tchao!')
            sys.exit()
        else:
            print('[INFO] Sensor configuration OK')

        # Send someunused command to clean the serial buffer:
        self.serialPort.write(b'HI')
        sleep(1)
        self.serialPort.read_all()

        # Now get the sensor calibration data after the sensor calibration:
        self.serialPort.write(b'PC')
        sleep(1)
        data = self.serialPort.read_all().decode().replace('\r', '')
        print('[INFO] Configuration of the sensor USB25103:')
        print(data)
        self.calibration_data = '# ' + data.replace('\n', '\n# ') +'\n'

    def open_Serial(self, timeout:int = 1):
        '''
        To open the serial link to the magnetic sensor.
        '''
        listUSBports = ["/dev/ttyUSB0", "/dev/ttyUSB1"]
        serialPort = None
        for port in listUSBports:
            try:
                print(f"[INFO] Trying to open {port}")
                serialPort = Serial(port, baudrate=115200, timeout=timeout)
                break
            except:
                continue
        if serialPort is None:
            return
        self.serialPort = serialPort
        
        # read the magnetic sensor banner:
        sleep(3)
        data = self.serialPort.read_all().decode().strip()            
        print(f"[INFO] Found:\n{data}\n[INFO] Sound good !")


    def config_USBsensor(self):
        if self.serialPort is None:
            print('[ERROR] SeialPort is not opened, cannot configure the USBsensor')
            return -1
        self.serialPort.write(f"NS {Param['SENSOR_NB_SAMPLE']}".encode('ascii'))
        sleep(0.5)
        self.serialPort.write(f"PG {Param['SENSOR_GAIN']}".encode('ascii'))
        return 0
        
    @staticmethod
    def Launch_pigpio():
      '''Launch the 'pigpiod' process if needed'''
      out = subprocess.run(['ps','-axu'], capture_output=True, text=True)
      if 'pigpiod' not in out.stdout:
         command = "sudo pigpiod"
         print(f"[INFO] Lauching '{command}'")
         out = subprocess.run(command.split(), capture_output=True, text=True)
      else:
         print(f"[INFO] Process 'pigpiod' already launched...")

    def GPIO_config(self):
        # set up the stepper motor1 (rotation of the ROTOR):
        self.pi.set_mode(self.stepper1.GPIO_DIR, OUTPUT)
        self.pi.set_mode(self.stepper1.GPIO_STEP, OUTPUT)
        self.pi.set_mode(self.stepper1.GPIO_ENA, OUTPUT)

        self.pi.write(self.stepper1.GPIO_DIR, LOW)
        self.pi.write(self.stepper1.GPIO_ENA, HIGH) # disable torque
        self.pi.write(self.stepper1.GPIO_PUL, LOW)

        # set up the stepper motor2 (sensor Z motion):
        self.pi.set_mode(self.stepper2.GPIO_DIR, OUTPUT)
        self.pi.set_mode(self.stepper2.GPIO_STEP, OUTPUT)
        self.pi.set_mode(self.stepper2.GPIO_ENA, OUTPUT)

        self.pi.write(self.stepper2.GPIO_DIR, LOW)
        self.pi.write(self.stepper2.GPIO_ENA, HIGH) # disable torque
        self.pi.write(self.stepper2.GPIO_PUL, LOW)

        # The limit switch sensor is normally closed, connected between GND and pinLimitSwitch.
        # pinLimitSwitch is set as INPUT pulled up to tge 5V. Normally the input is connected to GND
        # du to the limit switch; and when the switch is pressed yhe input goes to 5V (HIGH).
        self.pi.set_mode(Zaxis.GPIO_LimitSwitch.value, OUTPUT)
        self.pi.set_pull_up_down(Zaxis.GPIO_LimitSwitch.value, PUD_UP)

    def write_header(self, file_name:str, work_dist:float=None, rot_step:float = None, NBSTEP1:int = None, Zpos:list = None):

        with open(file_name, "w", encoding="utf8") as fOut:

            # write calibration data:
            fOut.write(self.calibration_data)

            # write sensorparameters
            for k in Param.keys():
                if'SENSOR' in k: fOut.write(f'# {k}: {Param[k]} \n')
            
            if work_dist is not None:
                # write infos on 'work_dist':
                fOut.write(f'# working dist: {work_dist} mm\n')

            if rot_step is not None:
                # write infos on 'rot_step' angle:
                fOut.write(f'# Rotation step angle: {rot_step}°\n')

            if Zpos is not None:
                nb_pos = len(Zpos)
                
                # Write all the Z positions in the header file:
                for n, p in enumerate(Zpos, 1):
                    fOut.write(f"# sensor pos #{n}: {p} mm\n")
                    
                # Write columns header:
                line = "#\n# angle[°]"
                for n in range(1, nb_pos+1):
                    line += f"; X{n}_magn [mT]; Y{n}_magn [mT]; Z{n}_magn [mT]"
                fOut.write(line + '\n')

            else:
                # write simplified header:
                fOut.write('\n# Xmagn [mT]; Ymagn [mT]; Zmagn [mT];\n')
                    


    def Zref_sensor(self, hold_torque:bool = False, verbose:bool = False):
        '''
        To make the stepper motor move the sensor until it reaches the limit switch sensor
        '''
        print("[INFO] Stepper motor Z referencing...");

        # move upward:
        self.pi.write(self.stepper2.GPIO_DIR, LOW)

        # apply the motor holding torque:
        self.pi.write(self.stepper2.GPIO_ENA, LOW)

        #  the required revolution speed [revol/sec] and corresponding period:
        N_Hz  = 2 * Zaxis.Zref_velocity.value / (np.pi * self.stepper2.DIAM_MM
                                                 )
        T_sec = 1 / (N_Hz * self.stepper2.NB_STEP_PER_REVOL)
        if verbose: print(f"[INFO] N_Hz: {N_Hz:.2f}, T_ms: {T_sec*1e3:.2f}")

        limit_state = self.pi.read(Zaxis.GPIO_LimitSwitch.value)
        while limit_state != HIGH:
            # Send a pulse with period equals to Tms:
            t0 = time()
            self.pi.write(self.stepper2.GPIO_STEP, HIGH)
            limit_state = self.pi.read(Zaxis.GPIO_LimitSwitch.value)
            self.pi.write(self.stepper2.GPIO_STEP, LOW)
            while True:
                if time() - t0 > T_sec: break

        if hold_torque == False: 
            # disable the motor holding torque:
            self.pi.write(self.stepper2.GPIO_ENA, HIGH)

        if verbose: print("[INFO] OK !")
        return 0

    def Do_Zmove_sensor(self, curr_pos_mm:float, n:int, hold_torque:bool = False, verbose:bool = False):
        '''
        To move the sensor carriage along the Z axis.
        Parameters:
        - curr_pos_mm: the current position (in mm) of the sensor along the Z axis,
        - n: the rank of the Z position
        Returns: the new value of 'curr_pos_mm'.
        '''

        target_Z_pos = self.Z_pos_mm[n]
        # compute the distance of the move to do:
        dist = target_Z_pos - curr_pos_mm

        if verbose:
            mess = f"[INFO] Current pos is {curr_pos_mm} mm, moving to pos#{n} at {target_Z_pos} mm"
            mess += f" - dist: {dist} mm"
            if dist == 0: mess += " SKIPPING"
            print(mess)    

        # make the displacement for real: 
        # (Z_velocity & hold_stepper_torque are global variables)
        self.Zmove_sensor(dist, Zaxis.Z_velocity.value, hold_torque, verbose)

        # return the new value of the Z position
        return target_Z_pos

    def Zmove_sensor(self, dist_mm: int, speed_mm_per_sec:int, hold_torque:bool = False, verbose:bool = False):
        '''    
        To make the sensor cart move of 'dist_mm' upward if 'dist_mm' < 0, 
        downward if it is > 0. 
        '''

        if verbose: print(f"[INFO] Zmove_sensor, dist: {dist_mm} mm")

        # nothing to do if dist is null:
        if dist_mm == 0: return

        # Set the direction of move:
        if dist_mm > 0:
            self.pi.write(self.stepper2.GPIO_DIR, HIGH)  # direction of move is downward:
        elif dist_mm < 0:
            self.pi.write(self.stepper2.GPIO_DIR, LOW)   # direction of move is upward:
            dist_mm = -dist_mm
            
        # the required revolution speed [revol/sec] and corresponding period:
        N_Hz  = 2. * speed_mm_per_sec / (np.pi *  self.stepper2.DIAM_MM)
        T_sec = 1 / (N_Hz * self.stepper2.NB_STEP_PER_REVOL)
        if verbose: print(f"[INFO] N_Hz: {N_Hz:.2f}, T_ms: {T_sec*1e3:.2f}")

        # the required number of steps: 
        nb_step = int(2. * 180 * dist_mm / (self.stepper2.STEPPER_ANGLE * np.pi * self.stepper2.DIAM_MM))

        # Let's do the job:

        # apply the motor holding torque:
        self.pi.write(self.stepper2.GPIO_STEP, LOW)

        self.pi.write(self.stepper2.GPIO_STEP, LOW)
        for n in range(nb_step):
            t0 = time()
            # Send a pulse with period equals to Tms:
            self.pi.write(self.stepper2.GPIO_STEP, HIGH)
            sleep(20e-6)
            self.pi.write(self.stepper2.GPIO_STEP, LOW)
            while True:
                if time() - t0 > T_sec: break

        if hold_torque == False: 
            # disable the motor holding torque:
            self.pi.write(self.stepper2.GPIO_ENA, HIGH)        

    def Do_sensor_measurement(self, fake=False):
        '''
        Do the measurement of the magnetic field. If fake is True, randomvalues are returned
        (useful fordebugging).
        returns the string 'line' completed with the values of the magnetic field.
        '''
        if fake:
            #  make tke measure (simulations only for now):
            X = np.random.randint(1, 2000)/1.2
            Y = np.random.randint(1, 2000)/1.2
            Z = np.random.randint(1, 2000)/1.2
        else:
            # send a 'Read Manual' (RM) command to the sensor:
            self.serialPort.write(b'RM')
            sleep(Param['SENSOR_READ_DELAY'])
            data = self.serialPort.read_all()
            data = data.decode().replace('\r','').split('RD')[-1].strip()
            X, Y, Z = map(float, data.split(','))
            
        return X, Y, Z

    def EmergencyStop(self): 
        print("[INFO] EMERGENCY-STOP required")
        self.emergencyStopRequired = True
        self.Stop_ROTOR_Bench()

    def Stop_ROTOR_Bench(self):
        '''
        This function is called when the emergency-stop button is pressed.
        It should stop the motors and left the ROTOR bench in s safe state.
        '''
        self.pi.write(self.stepper1.GPIO_ENA, HIGH)     # release the torque of the shaft stepper motor
        self.pi.write(self.stepper2.GPIO_ENA, HIGH)     # release the torque of the Z stepper motor
        print("[INFO] All motor released")
        
    def continuous_reccord(self, params):
        '''
        To measure continuously the magnetic field ans write the data in a CALIB_...txt file.
        '''
        
        duration = params["DURATION"]
        sampling = params['SAMPLING']
        
        SAMPLE = params.get('SENSOR_NB_SAMPLE', Params['SENSOR_NB_SAMPLE'])
        GAIN = params.get('SENSOR_GAIN', Params['SENSOR_GAIN'])
        DELAY = params.get('SENSOR_READ_DELAY', Params['SENSOR_READ_DELAY'])
        
        Zpos_mm   =  parameters['Z_POS_MM']
        nb_repet  = parameters['NB_REPET']

        # Define the unique file name for the data
        fileName = uniq_file_name_FREE(duration, sampling, SAMPLE, GAIN, DELAY, repet):

        if SENSOR_READ_DELAY is None:
            SENSOR_READ_DELAY = Param['SENSOR_READ_DELAY']
        
        # write the header lines in the data file
        with open(fileName, "w", encoding="utf8") as fOut:

            
            # write sensorparameters
            for k in Param.keys():
                if'SENSOR' in k: fOut.write(f'# {k}: {Param[k]} \n')
            
            # Send unused command to clean the buhher:
            self.serialPort.write(b'HI')
            sleep(1)
            self.serialPort.read_all()

            '''# make a first write/read to throw unanted characters in the read buffer
            self.serialPort.write(b'RM')
            sleep(SENSOR_READ_DELAY)'''
                
            t0 = time()
            while True:
                t1 = time()

                # send a 'Read Manual' (RM) command to the sensor:
                self.serialPort.write(b'RM')
                sleep(SENSOR_READ_DELAY)
                data = self.serialPort.read_all().decode().replace('\r','')
                data = data.split('RD')[-1].strip()
                X, Y, Z = map(float, data.split(','))
                coeff = Param['SENSOR_Oe_mT']
                X *= coeff
                Y *= coeff
                Z *= coeff

                line = f'{X:12.6f};{Y:12.6f};{Z:12.6f}\n'
                fOut.write(line)
                fOut.flush()
                print(f'[DATA] {line}', end="")

                # set measurement time period to 1 sec:
                while True:
                    if time() - t1 >= 1: break

                # quit the loop when the elapsed time reaches furation:
                if time() - t0 >= duration: break

        # release ressourc/tmp/ROTOR_LAUNCH.txtes:
        self.Stop_ROTOR_Bench()


                        
        
    def run(self, parameters:dict, verbose:bool =False):

        work_dist = parameters["WORK_DIST"]
        rot_step  = parameters['ROT_STEP_DEG']
        Zpos_mm   =  parameters['Z_POS_MM']
        nb_repet  = parameters['NB_REPET']

        nb_sensor_pos = len(Zpos_mm)
        self.Z_pos_mm      = [0] + parameters["Z_POS_MM"]
        
        NBSTEP1  = round(rot_step * self.stepper1.RATIO / self.stepper1.STEPPER_ANGLE)    
        T_stepper1_sec = 1 / (self.stepper1.NB_REVOL_PER_SEC * self.stepper1.NB_STEP_PER_REVOL);
        if verbose:
            print(f'[INFO] ROT_STEP_DEG: {rot_step}, NBSTEP1: {NBSTEP1}, T_stepper1_sec:{T_stepper1_sec:.3f}')
        
        for repet in range(1, nb_repet+1):
          
          # Define the unique file name for the data
          fileName = uniq_file_name('ROTOR', work_dist, rot_step, Zpos_mm, (repet, nb_repet))

          # write the header lines in the datarotor file
          self.write_header(fileName, work_dist, rot_step, NBSTEP1, Zpos_mm)
          
          # Enable the shaft stepper motor torque:
          self.pi.write(self.stepper1.GPIO_ENA, LOW) 

          # open the data file with the uniq name:
          fOut = open(fileName, "a", encoding="utf8")
          
          # scan angle from 0 to 360°:
          count = 0
          curr_Zpos_mm = 0

          # Send unused command to clean the buhher:
          self.serialPort.write(b'HI')
          sleep(1)
          self.serialPort.read_all()

          '''# make a first write/read to throw unanted characters in the read buffer
          self.serialPort.write(b'RM')
          sleep(Param.SENSOR_READ_DELAY.value)'''

          while True:
              t0 = time()
              angle = rot_step*count
              if angle > 360: break

              # Now make the mmagnetic field measurement for all the positions of the sensor:
              line = f'{angle:5.1f}'

              Zpos_move_required = count % Zaxis.ZREF_EVERY_ROTSTEP.value

              if Zpos_move_required == 0: curr_Zpos_mm = self.Zref_sensor(hold_torque=True);

              go = count % 2
              if go == 0:
                  start, stop, step = 1, nb_sensor_pos+1, 1
              else:
                  start, stop, step = nb_sensor_pos, 0, -1

              # Move the sensor donward along Z axis:
              for n in range(start, stop, step):
                  # Move the sensor to the right Z position:
                  curr_Zpos_mm = self.Do_Zmove_sensor(curr_Zpos_mm, n, hold_torque=True);
                  # Make the sensor measuremnts:
                  X, Y, Z = self.Do_sensor_measurement();
                  coeff = Param['SENSOR_Oe_mT']
                  X *= coeff
                  Y *= coeff
                  Z *= coeff
                  line += f';{X:12.6f};{Y:12.6f};{Z:12.6f}'

              # Write data:
              fOut.write(line + '\n')
              fOut.flush()
              line = "[DATA] " + line
              print(line)
              # Make the stepper motor do the steps to turn the ROTOR of the 'rotor_step' value:
              for i in range(0, NBSTEP1):
                  top = time()
                  self.pi.write(self.stepper1.GPIO_STEP, HIGH)
                  sleep(20e-6)
                  self.pi.write(self.stepper1.GPIO_STEP, LOW)
                  while True:
                      if time() - top > T_stepper1_sec: break
              
              # If there is only one Z position for the sensor, wait 1 seconde:
              if nb_sensor_pos == 1:
                  t1 = time();
                  while t1 - t0 < 1:
                      t1 = millis()

              count += 1;

          # release all motor torques:
          self.Stop_ROTOR_Bench()

          # close the data file:
          fOut.close();

          print("END of measure")
          
        self.serialPort.close()

if __name__ == "__main__":

    print("Nothing to do here !!!")

    

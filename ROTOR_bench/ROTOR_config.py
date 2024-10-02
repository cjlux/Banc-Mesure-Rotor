from dataclasses import dataclass
from enum import Enum

@dataclass
class StepperMotor:
    INFO:str                # some infos on the moror
    STEP_MODE:int           # used for 1/2, 1/4, 1/8.... microstep mode
    STEPPER_ANGLE: float    # the angle of one step of the stepper motor
    RATIO:int = None        # The ratio of the stepper motor reductor
    NB_STEP_PER_REVOL:int   # The number of steps for a full revolution	
    NB_REVOL_PER_SEC:float  # the number of revolution per seconde
    GPIO_DIR:int            # the pin numberfor the Direction signal
    GPIO_STEP:int           # the pin numberfor the Step signal
    GPIO_ENA:int            # the pin numberfor the Enable signal
    DIAM_MM:float = None    # The diameter of the pulley if any 

    def time_delay_ms(self):
        return 1.e3 / (self.NB_REVOL_PER_SEC * self.NBSTEP_PER_REVOL)


Param = {
    'MIN_NB_ZPOS':      1,    # The min number of vertical position for the magnetic field sensor
    'MAX_NB_ZPOS':      10,   # The max number of vertical position for the magnetic field sensor
    'ZPOS_MIN':         0,    # The minimum value of Zpos [mm] for the sensor
    'ZPOS_MAX':         130,  # The maximum value of Zpos [mm] for the sensor
    
    'SENSOR_NB_SAMPLE': 10,   # the number of samples the sensor will get to give an average
    'SENSOR_GAIN':      1,    # the sensor gain: can be 1,2,4 or 8
    'SENSOR_READ_DELAY':0.7,
    'SENSOR_Oe_mT':     0.1,  # multiplicative coeff to convert sensor Oe unit to milli-Tesla [mT]
    }
    
class Zaxis(Enum):
    ZREF_EVERY_ROTSTEP  = 10    # make a Z referencing every ZMOVE_EVERY_ROTATIONSTEP rotations of the ROTOR
    Zref_velocity       = 5     # the velocity [mm/s] for reaching the limit switch sensor
    Z_velocity          = 15    # the velocity [mm/s] for reaching the limit switch sensor
    GPIO_LimitSwitch    = 8     # The GPIO pin number of the limit switch on the Z axis
